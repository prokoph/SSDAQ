import asyncio
from ssdaq.core.receiver_server import ReceiverServer

import zmq

from ssdaq.core.timestamps import CDTS_pb2


class TimestampReceiver(ReceiverServer):
    def __init__(self, ip: str, port: int, publishers: list):
        super().__init__(ip, port, publishers, "TimestampReceiver")

        self.running = True
        # The ReceiverServer already has a zmq context
        self.receiver = self._context.socket(zmq.SUB)
        connectionstr = "tcp://{}:{}".format(ip, port)
        self.log.info(
            "Setting timestamp zmq subscriber server at {}".format(connectionstr)
        )
        self.receiver.connect(connectionstr)
        self.receiver.setsockopt_string(zmq.SUBSCRIBE, "")
        self._setup = True

    async def ct_subscribe(self):
        print("Running")
        while self.running:
            packet = await self.receiver.recv()
            print("Packet received")
            tb = CDTS_pb2.TriggerBunch()
            tb.ParseFromString(packet)
            for tm in tb.triggers:
                await self.publish(tm.SerializeToString())


if __name__ == "__main__":
    from ssdaq.core import publishers

    trpl = TimestampReceiver(
        port=6666,
        ip="192.168.101.102",
        publishers=[publishers.ZMQTCPPublisher(ip="127.0.0.101", port=9999)],
    )
    trpl.run()
