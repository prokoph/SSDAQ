# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: log.proto

import sys

_b = sys.version_info[0] < 3 and (lambda x: x) or (lambda x: x.encode("latin1"))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor.FileDescriptor(
    name="log.proto",
    package="chec",
    syntax="proto2",
    serialized_options=None,
    serialized_pb=_b(
        '\n\tlog.proto\x12\x04\x63hec"\xbb\x02\n\x07LogData\x12\x12\n\nsystemType\x18\x01 \x02(\x05\x12(\n\x08severity\x18\x02 \x02(\x0e\x32\x16.chec.LogData.Severity\x12\x0e\n\x06sender\x18\x03 \x02(\t\x12\x0f\n\x07message\x18\x04 \x02(\t\x12\x0c\n\x04time\x18\x05 \x02(\x03\x12\x0b\n\x03pid\x18\x06 \x02(\x05\x12\x12\n\nsourceFile\x18\x07 \x02(\t\x12\x0c\n\x04line\x18\x08 \x02(\x05\x12\x10\n\x08position\x18\t \x01(\t\x12\r\n\x05geoid\x18\n \x01(\t\x12\r\n\x05seqid\x18\x0b \x01(\x05\x12\x14\n\x0c\x63\x61meraPcTime\x18\x0c \x01(\x03"N\n\x08Severity\x12\n\n\x06NOTSET\x10\x00\x12\t\n\x05\x44\x45\x42UG\x10\n\x12\x08\n\x04INFO\x10\x14\x12\x0b\n\x07WARNING\x10\x1e\x12\t\n\x05\x45RROR\x10(\x12\t\n\x05\x46\x41TAL\x10\x32'
    ),
)


_LOGDATA_SEVERITY = _descriptor.EnumDescriptor(
    name="Severity",
    full_name="chec.LogData.Severity",
    filename=None,
    file=DESCRIPTOR,
    values=[
        _descriptor.EnumValueDescriptor(
            name="NOTSET", index=0, number=0, serialized_options=None, type=None
        ),
        _descriptor.EnumValueDescriptor(
            name="DEBUG", index=1, number=10, serialized_options=None, type=None
        ),
        _descriptor.EnumValueDescriptor(
            name="INFO", index=2, number=20, serialized_options=None, type=None
        ),
        _descriptor.EnumValueDescriptor(
            name="WARNING", index=3, number=30, serialized_options=None, type=None
        ),
        _descriptor.EnumValueDescriptor(
            name="ERROR", index=4, number=40, serialized_options=None, type=None
        ),
        _descriptor.EnumValueDescriptor(
            name="FATAL", index=5, number=50, serialized_options=None, type=None
        ),
    ],
    containing_type=None,
    serialized_options=None,
    serialized_start=257,
    serialized_end=335,
)
_sym_db.RegisterEnumDescriptor(_LOGDATA_SEVERITY)


_LOGDATA = _descriptor.Descriptor(
    name="LogData",
    full_name="chec.LogData",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name="systemType",
            full_name="chec.LogData.systemType",
            index=0,
            number=1,
            type=5,
            cpp_type=1,
            label=2,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="severity",
            full_name="chec.LogData.severity",
            index=1,
            number=2,
            type=14,
            cpp_type=8,
            label=2,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="sender",
            full_name="chec.LogData.sender",
            index=2,
            number=3,
            type=9,
            cpp_type=9,
            label=2,
            has_default_value=False,
            default_value=_b("").decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="message",
            full_name="chec.LogData.message",
            index=3,
            number=4,
            type=9,
            cpp_type=9,
            label=2,
            has_default_value=False,
            default_value=_b("").decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="time",
            full_name="chec.LogData.time",
            index=4,
            number=5,
            type=3,
            cpp_type=2,
            label=2,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="pid",
            full_name="chec.LogData.pid",
            index=5,
            number=6,
            type=5,
            cpp_type=1,
            label=2,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="sourceFile",
            full_name="chec.LogData.sourceFile",
            index=6,
            number=7,
            type=9,
            cpp_type=9,
            label=2,
            has_default_value=False,
            default_value=_b("").decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="line",
            full_name="chec.LogData.line",
            index=7,
            number=8,
            type=5,
            cpp_type=1,
            label=2,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="position",
            full_name="chec.LogData.position",
            index=8,
            number=9,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=_b("").decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="geoid",
            full_name="chec.LogData.geoid",
            index=9,
            number=10,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=_b("").decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="seqid",
            full_name="chec.LogData.seqid",
            index=10,
            number=11,
            type=5,
            cpp_type=1,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="cameraPcTime",
            full_name="chec.LogData.cameraPcTime",
            index=11,
            number=12,
            type=3,
            cpp_type=2,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[_LOGDATA_SEVERITY],
    serialized_options=None,
    is_extendable=False,
    syntax="proto2",
    extension_ranges=[],
    oneofs=[],
    serialized_start=20,
    serialized_end=335,
)

_LOGDATA.fields_by_name["severity"].enum_type = _LOGDATA_SEVERITY
_LOGDATA_SEVERITY.containing_type = _LOGDATA
DESCRIPTOR.message_types_by_name["LogData"] = _LOGDATA
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

LogData = _reflection.GeneratedProtocolMessageType(
    "LogData",
    (_message.Message,),
    dict(
        DESCRIPTOR=_LOGDATA,
        __module__="log_pb2"
        # @@protoc_insertion_point(class_scope:chec.LogData)
    ),
)
_sym_db.RegisterMessage(LogData)


# @@protoc_insertion_point(module_scope)
