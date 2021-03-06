import asyncio
import struct
import numpy as np
from datetime import datetime, timedelta
from ssdaq.data._dataimpl import slowsignal_format as dc
from ssdaq.data import SSReadout
from ssdaq.core.receiver_server import ReceiverServer
from .mon_sender import ReceiverMonSender

READOUT_LENGTH = (
    dc.N_TM_PIX * 2 + 2 * 8
)  # 64 2-byte channel amplitudes and 2 8-byte timestamps


class SlowSignalDataProtocol(asyncio.Protocol):
    def __init__(self, loop, log, relaxed_ip_range, mon, packet_debug_stream_file=None):
        self._buffer = asyncio.Queue()
        self.loop = loop
        self.log = log.getChild("SlowSignalDataProtocol")
        self.relaxed_ip_range = relaxed_ip_range
        self.mon = mon
        if packet_debug_stream_file != None:
            self.log.info(
                "Opening a packet_debug_stream_file at %s" % packet_debug_stream_file
            )
            self.packet_debug_stream_file = open(packet_debug_stream_file, "w")
            self.packet_debug_stream = True
        else:
            self.packet_debug_stream = False
        self.dt = timedelta(seconds=0.1)
        self.packet_format = struct.Struct(">Q32HQ32H")

    def connection_made(self, transport):
        self.log.info("Connected to port")
        self.transport = transport

    def datagram_received(self, data, addr):
        cpu_time = datetime.utcnow()
        self.mon.register_data_packet()
        if len(data) % (READOUT_LENGTH) != 0:
            self.log.warn("Got unsuported packet size, skipping packet")
            self.log.info("Bad package came from %s:%d" % tuple(data[0]))
            return
        nreadouts = int(len(data) / (READOUT_LENGTH))

        # getting the module number from the last two digits of the ip
        ip = addr[0]
        module_nr = int(ip[-ip[::-1].find(".") :]) % 100
        if module_nr > dc.N_TM - 1 and self.relaxed_ip_range:
            # ensure that the module number is in the allowed range
            # (mostly important for local or standalone setups simulations)
            module_nr = module_nr % dc.N_TM
            # self.log.debug('Got data from ip %s which is outsie the allowed range'%ip)
        elif module_nr > dc.N_TM - 1:
            self.log.error("Error: got packets from ip out of range:")
            self.log.error("   %s" % ip)
            self.log.error("This can be supressed if relaxed_ip_range=True")
            raise RuntimeError

        # self.log.debug("Got data from %s assigned to module %d"%(str(ip),module_nr))
        for i in range(nreadouts):
            unpacked_data = self.packet_format.unpack_from(data, i * (READOUT_LENGTH))
            self.loop.create_task(
                self._buffer.put((module_nr, unpacked_data[0], unpacked_data, cpu_time))
            )
            cpu_time += self.dt

            if self.packet_debug_stream:
                self.packet_debug_stream_file.write(
                    "%d  %d  %d\n"
                    % (
                        unpacked_data[0],
                        int(datetime.utcnow().timestamp() * 1e9),
                        module_nr,
                    )
                )
        # self.log.debug('Front buffer length %d'%(self._buffer.qsize()))
        if self._buffer.qsize() > 1000:
            self.log.warning("Front buffer length %d" % (self._buffer.qsize()))


class PartialReadout:
    int_counter = 0

    def __init__(self, tm_num, data, cpu_t):
        self.data = [None] * dc.N_TM
        self.data[tm_num] = data
        self.timestamp = data[0]
        self.cpu_time = [cpu_t]
        self.tm_parts = [0] * dc.N_TM
        self.tm_parts[tm_num] = 1
        PartialReadout.int_counter += 1
        self.readout_number = PartialReadout.int_counter

    def add_part(self, tm_num, data, cpu_t):
        self.data[tm_num] = data
        self.tm_parts[tm_num] = 1
        self.cpu_time.append(cpu_t)


class ReadoutAssembler(ReceiverServer):
    """
    Slow signal readout assembler. Constructs
    slow signal readouts from data packets recieved from
    Target Modules.
    """

    def __init__(
        self,
        relaxed_ip_range: bool = False,
        readout_tw: float = 0.0001 * 1e9,
        listen_ip: str = "0.0.0.0",
        listen_port: int = 2009,
        buffer_length: int = 1000,
        buffer_time: float = 10 * 1e9,
        publishers: list = None,
        packet_debug_stream_file: str = None,
    ):
        super().__init__(listen_ip, listen_port, publishers, "ReadoutAssembler")
        self.relaxed_ip_range = relaxed_ip_range
        self.transport, self.ss_data_protocol = self.setup_udp(
            lambda: SlowSignalDataProtocol(
                self.loop,
                self.log,
                self.relaxed_ip_range,
                ReceiverMonSender("ReadoutAssembler", self.loop, self._context),
                packet_debug_stream_file=packet_debug_stream_file,
            )
        )

        # settings
        self.readout_tw = int(readout_tw)
        self.listen_addr = (listen_ip, listen_port)
        self.buffer_len = buffer_length
        self.buffer_time = buffer_time

        # counters
        self.nprocessed_packets = 0
        self.nconstructed_readouts = 0
        self.readout_count = 1
        self.packet_counter = {}
        self.readout_counter = {}

        # controlers
        self.publish_readouts = True

        # buffers
        self.inter_buff = []
        self.partial_ro_buff = asyncio.queues.collections.deque(maxlen=self.buffer_len)

    def cmd_reset_ro_count(self, arg):
        self.log.info("Readout count has been reset")
        self.readout_count = 1
        return b"Readout count reset"

    def cmd_set_publish_readouts(self, arg):
        if arg[0] == "false" or arg[0] == "False":
            self.publish_readouts = False
            self.log.info("Pause publishing readouts")
            return b"Paused readout publishing"
        elif arg[0] == "true" or arg[0] == "True":
            self.publish_readouts = True
            self.log.info("Pause publishing readouts")
            return b"Unpaused readout publishing"
        else:
            self.log.info(
                "Unrecognized command for command `set_publish_readouts` \n    no action taken"
            )
            return (
                "Unrecognized arg `%s` for command `set_publish_readouts` \nno action taken"
                % arg[0]
            ).encode("ascii")

    async def ct_assembler(self):
        n_packets = 0
        self.log.info("Empty socket buffer before starting readout building")
        packet = await self.ss_data_protocol._buffer.get()
        got_packet = True
        while got_packet:
            got_packet = False
            self.log.info("Thrown away %d packets in buffer before start" % n_packets)
            try:
                while True:
                    await asyncio.wait_for(
                        self.ss_data_protocol._buffer.get(), timeout=0
                    )
                    n_packets += 1
                    got_packet = True
            except:
                pass
        self.log.info("Thrown away %d packets in buffer before start" % n_packets)
        self.log.info("Starting readout build loop")
        packet = await self.ss_data_protocol._buffer.get()
        self.partial_ro_buff.append(PartialReadout(packet[0], packet[2], packet[3]))
        while True:
            packet = await self.ss_data_protocol._buffer.get()
            # self.log.debug('Got packet from front buffer with timestamp %f and tm id %d'%(packet[1]*1e-9,packet[0]))
            pro = self.partial_ro_buff[-1]
            dt = pro.timestamp - packet[1]

            if abs(dt) < self.readout_tw and pro.tm_parts[packet[0]] == 0:  #
                self.partial_ro_buff[-1].add_part(packet[0], packet[2], packet[3])
                # self.log.debug('Packet added to the tail of the buffer')

            elif dt < 0:
                self.partial_ro_buff.append(
                    PartialReadout(packet[0], packet[2], packet[3])
                )
                # self.log.debug('Packet added to a new readout at the tail of the buffer')

            else:
                if self.partial_ro_buff[0].timestamp - packet[1] > 0:
                    self.partial_ro_buff.appendleft(
                        PartialReadout(packet[0], packet[2], packet[3])
                    )
                    # self.log.debug('Packet added to a new readout at the head of the buffer')
                else:
                    # self.log.debug('Finding right readout in buffer')
                    found = False
                    for i in range(len(self.partial_ro_buff) - 1, 0, -1):
                        pro = self.partial_ro_buff[i]
                        dt = pro.timestamp - packet[1]

                        if abs(dt) < self.readout_tw:  #
                            if pro.tm_parts[packet[0]] == 1:
                                self.log.warning(
                                    "Doublette packet with timestamp %f and tm id %d with cpu timestamp %f"
                                    % (
                                        packet[1] * 1e-9,
                                        packet[0],
                                        packet[3].timestamp() * 1e-9,
                                    )
                                )
                            self.partial_ro_buff[i].add_part(
                                packet[0], packet[2], packet[3]
                            )
                            # self.log.debug('Packet added to %d:th readout in buffer'%i)
                            found = True
                            break
                        elif dt < 0:
                            self.partial_ro_buff.insert(
                                i + 1, PartialReadout(packet[0], packet[2], packet[3])
                            )
                            found = True
                            break

                    if not found:
                        self.log.warning(
                            "No partial readout found for packet with timestamp %f and tm id %d"
                            % (packet[1] * 1e-9, packet[0])
                        )
                        self.log.info(
                            "Newest readout timestamp %f"
                            % (self.partial_ro_buff[-1].timestamp * 1e-9)
                        )
                        self.log.info(
                            "Next readout timestamp %f"
                            % (self.partial_ro_buff[0].timestamp * 1e-9)
                        )
            if abs(
                float(self.partial_ro_buff[-1].timestamp)
                - float(self.partial_ro_buff[0].timestamp)
            ) > (self.buffer_time):
                # self.log.debug('First %f and last %f timestamp in buffer '%(self.partial_ro_buff[0].timestamp*1e-9,self.partial_ro_buff[-1].timestamp*1e-9))
                readout = self.assemble_readout(self.partial_ro_buff.popleft())
                if self.nconstructed_readouts % 10 == 0:
                    # for d in self.partial_ro_buff:
                    # print(d.timestamp*1e-9,d.timestamp,d.readout_number, d.tm_parts)
                    self.log.debug("Built readout %d" % self.nconstructed_readouts)
                    self.log.debug(
                        "Newest readout timestamp %f"
                        % (self.partial_ro_buff[-1].timestamp * 1e-9)
                    )
                    self.log.debug(
                        "Next readout timestamp %f"
                        % (self.partial_ro_buff[0].timestamp * 1e-9)
                    )
                    self.log.debug(
                        "Last timestamp dt %f"
                        % (
                            (
                                self.partial_ro_buff[-1].timestamp
                                - self.partial_ro_buff[0].timestamp
                            )
                            * 1e-9
                        )
                    )
                    # self.log.debug('Number of TMs participating %d'%(sum(readout.timestamps[:,0]>0)))
                    self.log.debug("Buffer lenght %d" % (len(self.partial_ro_buff)))
                # self.log.debug('Built readout %d'%self.nconstructed_readouts)
                await self.publish(readout.pack())

    def assemble_readout(self, pro):
        # construct readout
        r_cpu_time = np.min(pro.cpu_time)
        cpu_time_s = int(r_cpu_time.timestamp())
        cpu_time_ns = int((r_cpu_time.timestamp() - cpu_time_s) * 1e9)
        readout = SSReadout(
            int(pro.timestamp), self.readout_count, cpu_time_s, cpu_time_ns
        )
        for i, tmp_data in enumerate(pro.data):
            if tmp_data == None:
                continue
            if i in self.readout_counter:
                self.readout_counter[i] += 1
            else:
                self.readout_counter[i] = 1
            # put data into a temporary array of uint type
            tmp_array = np.empty(dc.N_TM_PIX, dtype=np.uint64)
            tmp_array[: dc.N_TM] = tmp_data[1 : dc.N_TM + 1]
            tmp_array[dc.N_TM :] = tmp_data[dc.N_TM + 2 :]

            # converting counts to mV
            m = tmp_array < 0x8000
            tmp_array[m] += 0x8000
            tmp_array[~m] = tmp_array[~m] & 0x7FFF
            readout.data[i] = tmp_array * 0.03815 * 2.0

        self.nconstructed_readouts += 1
        self.readout_count += 1
        return readout


if __name__ == "__main__":
    from ssdaq import sslogger
    import logging
    import os
    from subprocess import call
    from ssdaq.core.publishers.zmq_tcp_publisher import ZMQTCPPublisher

    call(["taskset", "-cp", "0,4", "%s" % (str(os.getpid()))])
    sslogger.setLevel(logging.INFO)
    zmq_pub = ZMQTCPPublisher("127.0.0.101", 5555)
    ro_assembler = ReadoutAssembler(publishers=[zmq_pub])
    ro_assembler.run()
