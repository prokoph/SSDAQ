import logging
import os
from datetime import datetime
from threading import Thread
from ssdaq import sslogger
from ssdaq.core.basicsubscriber import (
    BasicSubscriber,
    WriterSubscriber,
    AsyncSubscriber,
    AsyncWriterSubscriber,
)
from ssdaq import logging as handlers
from ssdaq.data import (
    io,
    TriggerPacketData,
    TriggerMessage,
    SSReadout,
    MonitorData,
    TelData,
)
from ssdaq.core.utils import get_si_prefix


class SSReadoutSubscriber(BasicSubscriber):
    def __init__(self, ip: str, port: int, logger: logging.Logger = None):
        super().__init__(ip=ip, port=port, unpack=SSReadout.from_bytes)


class AsyncSSReadoutSubscriber(AsyncSubscriber):
    def __init__(self, ip: str, port: int, logger: logging.Logger = None, loop=None):
        super().__init__(ip=ip, port=port, unpack=SSReadout.from_bytes, loop=loop)




class BasicTriggerSubscriber(BasicSubscriber):
    def __init__(self, ip: str, port: int, logger: logging.Logger = None):
        super().__init__(ip=ip, port=port, unpack=TriggerPacketData.unpack)

class AsyncTriggerSubscriber(AsyncSubscriber):
    def __init__(self, ip: str, port: int, logger: logging.Logger = None, loop=None):
        super().__init__(ip=ip, port=port, unpack=TriggerPacketData.unpack, loop=loop)


logunpack = lambda x: handlers.protb2logrecord(handlers.parseprotb2log(x))


class BasicLogSubscriber(BasicSubscriber):
    def __init__(self, ip: str, port: int, logger: logging.Logger = None):
        super().__init__(ip=ip, port=port, unpack=logunpack)

class AsyncLogSubscriber(AsyncSubscriber):
    def __init__(self, ip: str, port: int, logger: logging.Logger = None,loop=None):
        super().__init__(ip=ip, port=port, unpack=logunpack,loop=loop)

def timeunpack(x):
    tmsg = TriggerMessage()
    tmsg.ParseFromString(x)
    return tmsg


class BasicTimestampSubscriber(BasicSubscriber):
    def __init__(self, ip: str, port: int, logger: logging.Logger = None):
        super().__init__(ip=ip, port=port, unpack=timeunpack)

class AsyncTimestampSubscriber(AsyncSubscriber):
    def __init__(self, ip: str, port: int, logger: logging.Logger = None,loop=None):
        super().__init__(ip=ip, port=port, unpack=timeunpack,loop=loop)

def monunpack(x):
    monmsg = MonitorData()
    monmsg.ParseFromString(x)
    return monmsg


class BasicMonSubscriber(BasicSubscriber):
    def __init__(self, ip: str, port: int, logger: logging.Logger = None):
        super().__init__(ip=ip, port=port, unpack=monunpack)
class AsyncMonSubscriber(AsyncSubscriber):
    def __init__(self, ip: str, port: int, logger: logging.Logger = None,loop=None):
        super().__init__(ip=ip, port=port, unpack=monunpack,loop=loop)

logprotounpack = lambda x: handlers.parseprotb2log(x)


class LogProtoSubscriber(BasicSubscriber):
    def __init__(self, ip: str, port: int, logger: logging.Logger = None):
        super().__init__(ip=ip, port=port, unpack=logprotounpack)

class AsyncLogProtoSubscriber(AsyncSubscriber):
    def __init__(self, ip: str, port: int, logger: logging.Logger = None,loop=None):
        super().__init__(ip=ip, port=port, unpack=logprotounpack,loop=loop)

# These are locals in init that we want to skip
# when creating the kwargs dict
skip = ["self", "__class__"]


class LogWriter(WriterSubscriber):
    def __init__(
        self,
        file_prefix: str,
        ip: str,
        port: int,
        folder: str = "",
        file_enumerator: str = None,
        filesize_lim: int = None,
    ):
        super().__init__(
            subscriber=LogProtoSubscriber,
            writer=io.LogWriter,
            file_ext=".prt",
            name="LogWriter",
            **{k: v for k, v in locals().items() if k not in skip}
        )


class TimestampWriter(WriterSubscriber):
    def __init__(
        self,
        file_prefix: str,
        ip: str,
        port: int,
        folder: str = "",
        file_enumerator: str = None,
        filesize_lim: int = None,
    ):

        super().__init__(
            subscriber=BasicTimestampSubscriber,
            writer=io.TimestampWriter,
            file_ext=".prt",
            name="TimestampWriter",
            **{k: v for k, v in locals().items() if k not in skip}
        )
        print(locals())


class TriggerWriter(WriterSubscriber):
    def __init__(
        self,
        file_prefix: str,
        ip: str,
        port: int,
        folder: str = "",
        file_enumerator: str = None,
        filesize_lim: int = None,
    ):
        super().__init__(
            subscriber=BasicTriggerSubscriber,
            writer=io.TriggerWriter,
            file_ext=".prt",
            name="TriggerWriter",
            **{k: v for k, v in locals().items() if k not in skip}
        )


class SSFileWriter(WriterSubscriber):
    def __init__(
        self,
        file_prefix: str,
        ip: str,
        port: int,
        folder: str = "",
        file_enumerator: str = None,
        filesize_lim: int = None,
    ):
        super().__init__(
            subscriber=SSReadoutSubscriber,
            writer=io.SSDataWriter,
            file_ext=".hdf5",
            name="SSFileWriter",
            **{k: v for k, v in locals().items() if k not in skip}
        )

    def data_cond(self, data):
        return data.iro == 1 and self.data_counter > 0


class ATriggerWriter(AsyncWriterSubscriber):
    def __init__(
        self,
        file_prefix: str,
        ip: str,
        port: int,
        folder: str = "",
        file_enumerator: str = None,
        filesize_lim: int = None,
        loop=None,
    ):
        super().__init__(
            subscriber=AsyncTriggerSubscriber,
            writer=io.TriggerWriter,
            file_ext=".prt",
            name="ATriggerWriter",
            **{k: v for k, v in locals().items() if k not in skip}
        )


def teldataunpack(data):
    teldata = TelData()
    teldata.ParseFromString(data)
    return teldata


class ASlowSignalWriter(AsyncWriterSubscriber):
    def __init__(
        self,
        file_prefix: str,
        ip: str,
        port: int,
        folder: str = "",
        file_enumerator: str = None,
        filesize_lim: int = None,
        loop=None,
    ):
        print(AsyncSSReadoutSubscriber)
        super().__init__(
            subscriber=AsyncSSReadoutSubscriber,
            writer=io.SSDataWriter,
            file_ext=".hdf5",
            name="ASlowSignalWriter",
            **{k: v for k, v in locals().items() if k not in skip}
        )

        self._teldatasub = AsyncSubscriber(
            ip="127.0.0.101",
            port=9006,
            unpack=teldataunpack,
            logger=self.log,
            zmqcontext=self._subscriber.context,
            loop=self.loop,
            passoff_callback=self.write_tel_data,
        )

    def write_tel_data(self, data):

        self._writer.write_tel_data(
            ra=data.ra,
            dec=data.dec,
            time=data.time.sec + data.time.nsec * 1e-9,
            seconds=data.time.sec,
            ns=data.time.nsec,
        )

    async def close(self, hard: bool = False):
        """ Stops the writer by closing the subscriber.

            args:
                hard (bool): If set to true the subscriber
                             buffer will be dropped and the file
                             will be immediately closed. Any data still
                             in the subscriber buffer will be lost.
        """
        await super().close(hard)
        self.log.info("Stopping TelData subscriber")
        await self._teldatasub.close(hard=False)