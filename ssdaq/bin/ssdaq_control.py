from ssdaq import SSReadoutAssembler, ZMQTCPPublisher
from ssdaq.utils import daemon
import ssdaq
from ssdaq.core import publishers
from ssdaq import sslogger
from logging.handlers import SocketHandler

from ssdaq.core.logging import handlers

sslogger.addHandler(handlers.ChecSocketLogHandler("127.0.0.1", 10001))


class ReadoutAssemblerDaemonWrapper(daemon.Daemon):
    def __init__(
        self,
        stdout="/dev/null",
        stderr="/dev/null",
        set_taskset=False,
        core_id=0,
        log_level="INFO",
        **kwargs
    ):
        # Deamonizing the server
        daemon.Daemon.__init__(
            self, "/tmp/ssdaq_daemon.pid", stdout=stdout, stderr=stderr
        )
        self.kwargs = kwargs
        self.set_taskset = set_taskset
        self.core_id = str(core_id)
        import logging

        eval("sslogger.setLevel(logging.%s)" % log_level)
        sslogger.info("Set logging level to {}".format(log_level))

    def run(self):
        from subprocess import call
        import os

        if self.set_taskset:
            # forces the process to one particular CPU core
            call(["taskset", "-cp", self.core_id, "%s" % (str(os.getpid()))])
        eps = []
        i = 1
        for epname, epconf in self.kwargs["Publishers"].items():
            epconf["name"] = epname
            pubclass = getattr(publishers, epconf["class"])
            del epconf["class"]
            eps.append(pubclass(**epconf))
            i += 1
        roa = SSReadoutAssembler(publishers=eps, **self.kwargs["SSReadoutAssembler"])
        roa.run()


class ReadoutFileWriterDaemonWrapper(daemon.Daemon):
    def __init__(self, stdout="/dev/null", stderr="/dev/null", **kwargs):
        # Deamonizing the server
        daemon.Daemon.__init__(
            self, "/tmp/ssdaq_writer_daemon.pid", stdout=stdout, stderr=stderr
        )
        self.kwargs = kwargs

    def run(self):
        from ssdaq.subscribers.slowsignal import SSFileWriter
        import signal
        import sys

        data_writer = SSFileWriter(**self.kwargs)

        def signal_handler_fact(data_writer, self):
            def signal_handler(sig, frame):
                # print new line so that the next log message will
                # have a fresh line to print to
                if sig == signal.SIGINT:
                    print()
                data_writer.close()

            return signal_handler

        signal.signal(signal.SIGHUP, signal_handler_fact(data_writer, self))
        signal.signal(signal.SIGINT, signal_handler_fact(data_writer, self))
        data_writer.start()




class RecieverDaemonWrapper(daemon.Daemon):
    def __init__(
        self,
        receiver_cls,
        stdout="/dev/null",
        stderr="/dev/null",
        set_taskset=False,
        core_id=0,
        log_level="INFO",
        **kwargs
    ):
        # Deamonizing the server
        daemon.Daemon.__init__(
            self, "/tmp/{}_daemon.pid".format(receiver_cls.__name__), stdout=stdout, stderr=stderr
        )
        self.receiver_cls = receiver_cls
        self.kwargs = kwargs
        self.set_taskset = set_taskset
        self.core_id = str(core_id)
        import logging

        eval("sslogger.setLevel(logging.%s)" % log_level)
        sslogger.info("Set logging level to {}".format(log_level))

    def run(self):
        from subprocess import call
        import os

        if self.set_taskset:
            # forces the process to one particular CPU core
            call(["taskset", "-cp", self.core_id, "%s" % (str(os.getpid()))])
        eps = []
        i = 1
        for epname, epconf in self.kwargs["Publishers"].items():
            epconf["name"] = epname
            pubclass = getattr(publishers, epconf["class"])
            del epconf["class"]
            eps.append(pubclass(**epconf))
            i += 1
        reciever = self.receiver_cls(publishers=eps, **self.kwargs["Receiver"])
        reciever.run()


import yaml
import click

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


class MyGroup(click.Group):
    def parse_args(self, ctx, args):
        if args[0] in self.commands:
            if len(args) == 1 or args[1] not in self.commands:
                args.insert(0, "")
        super(MyGroup, self).parse_args(ctx, args)


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(ssdaq.__version__)
    ctx.exit()


@click.group(context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.option(
    "--version",
    "-v",
    is_flag=True,
    help="Show version",
    callback=print_version,
    expose_value=False,
    is_eager=True,
)
def cli(ctx):
    """Start, stop and control ssdaq readout assembler and writer daemons"""
    ctx.ensure_object(dict)

    from pkg_resources import resource_stream, resource_string, resource_listdir

    ctx.obj["CONFIG"] = yaml.safe_load(
        resource_stream("ssdaq.resources", "ssdaq-default-config.yaml")
    )
    pass


@click.group()
@click.pass_context
def start(ctx):  # ,config):
    """Start a readout assembler or data writer """
    ctx.ensure_object(dict)


@start.command()
@click.option("--daemon/--no-daemon", "-d", default=False, help="run as daemon")
@click.argument("config", required=False)
@click.pass_context
def roa(ctx, daemon, config):
    """Start a readout assembler with an optional custom CONFIG file"""

    print("Starting readout assembler...")
    if daemon:
        print("Run as deamon")
    if config:
        ctx.obj["CONFIG"] = yaml.safe_load(open(config, "r"))
    config = ctx.obj["CONFIG"]
    readout_assembler = ReadoutAssemblerDaemonWrapper(
        **config["ReadoutAssemblerDaemon"], **config["ReadoutAssembler"]
    )
    readout_assembler.start(daemon)


@start.command()
@click.option("--daemon/--no-daemon", "-d", default=False, help="run as daemon")
@click.argument("config", required=False)
@click.option(
    "--filename-prefix",
    "-f",
    default=None,
    help="Set filename prefix (over-rides the loaded configuration)",
)
@click.option(
    "--output-folder",
    "-o",
    default=None,
    help="Set output folder (over-rides the loaded configuration)",
)
@click.pass_context
def dw(ctx, filename_prefix, output_folder, daemon, config):
    """Start a data writer with an optional custom CONFIG file"""
    print("Starting readout writer...")
    if daemon:
        print("Run as deamon")
    if config:
        ctx.obj["CONFIG"] = yaml.safe_load(open(config, "r"))
    config = ctx.obj["CONFIG"]

    if filename_prefix:
        config["SSFileWriter"]["file_prefix"] = filename_prefix
    if output_folder:
        config["SSFileWriter"]["folder"] = output_folder
    readout_writer = ReadoutFileWriterDaemonWrapper(
        **config["ReadoutFileWriterDaemon"], **config["SSFileWriter"]
    )
    readout_writer.start(daemon)


@click.group()
@click.pass_context
def stop(ctx):
    """Stop a running readout assembler or writer"""
    pass


@stop.command()
@click.pass_context
def roa(ctx):
    """Stop a running readout assembler"""
    config = ctx.obj["CONFIG"]
    readout_assembler = ReadoutAssemblerDaemonWrapper(
        **config["ReadoutAssemblerDaemon"], **config["ReadoutAssembler"]
    )
    readout_assembler.stop()


@stop.command()
@click.pass_context
def dw(ctx):
    """Stop a running readout writer"""
    config = ctx.obj["CONFIG"]
    readout_writer = ReadoutFileWriterDaemonWrapper(
        **config["ReadoutFileWriterDaemon"], **config["SSFileWriter"]
    )
    import os
    import signal

    try:
        dwpid = readout_writer.getpid()
    except:
        return
    if dwpid != None:
        os.kill(dwpid, signal.SIGHUP)


# @stop.command()
# @click.pass_context
# def all(ctx):
#     '''Stop both the readout assembler and writer'''
#     roa(ctx)
#     dw(ctx)


@click.group(name="roa-ctrl")
@click.pass_context
def roa_ctrl(ctx):
    """Send control commands to a running readout assembler daemon"""
    pass


@roa_ctrl.command()
@click.pass_context
def reset_count(ctx):
    """Resets the readout counter in the readout assembler"""
    import zmq

    zmqctx = zmq.Context()
    sock = zmqctx.socket(zmq.REQ)
    sock.connect("ipc:///tmp/ssdaq-control")
    sock.send(b"reset_ro_count 1")
    print(sock.recv())


@roa_ctrl.command()
@click.pass_context
def pause_pub(ctx):
    """Pauses readout publishing"""
    import zmq

    zmqctx = zmq.Context()
    sock = zmqctx.socket(zmq.REQ)
    sock.connect("ipc:///tmp/ssdaq-control")
    sock.send(b"set_publish_readouts False")
    print(sock.recv())


@roa_ctrl.command()
@click.pass_context
def restart_pub(ctx):
    """Restart readout publishing"""
    import zmq

    zmqctx = zmq.Context()
    sock = zmqctx.socket(zmq.REQ)
    sock.connect("ipc:///tmp/ssdaq-control")
    sock.send(b"set_publish_readouts True")
    print(sock.recv().decode("ascii"))

from multiprocessing import Process
from ssdaq import receivers

def f(receiver,comp_config):
    receiver = RecieverDaemonWrapper(receiver,**comp_config["Daemon"], **comp_config)
    receiver.start(daemon)

@start.command()
@click.option("--daemon/--no-daemon", "-d", default=False, help="run as daemon")
@click.argument("config", required=False)
@click.pass_context
def config(ctx, config,daemon):
    """Start daemons from CONFIG file"""
    # print("Starting readout writer...")
    if daemon:
        print("Run as deamon")

    if config:
        ctx.obj["CONFIG"] = yaml.safe_load(open(config, "r"))
    config = ctx.obj["CONFIG"]
    for component, comp_config in config.items():
        receiver = getattr(receivers, comp_config["Receiver"]['class'])
        del comp_config["Receiver"]['class']
        print("Starting {} ....".format(component))
        p = Process(target=f, args=(receiver,comp_config))
        p.start()
        p.join()

    # readout_writer = ReadoutFileWriterDaemonWrapper(
    #     **config["ReadoutFileWriterDaemon"], **config["SSFileWriter"]
    # )
    # readout_writer.start(daemon)






cli.add_command(start)
cli.add_command(stop)
cli.add_command(roa_ctrl)



def main():

    cli()


if __name__ == "__main__":
    # control()
    main()
