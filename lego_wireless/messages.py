import collections
import struct

from .enums import ErrorCode
from .enums import HubAttachedIOEvent
from .enums import HubProperty
from .enums import HubPropertyOperation
from .enums import IOType
from .enums import MessageType


class HubAttachedIO(
    collections.namedtuple("HubAttachedIO", ("port", "event", "io_type"))
):
    @classmethod
    def from_bytes(cls, value):
        port, event = struct.unpack("BB", value[:2])
        event = HubAttachedIOEvent(event)
        if event in (
            HubAttachedIOEvent.AttachedIO,
            HubAttachedIOEvent.AttachedVirtualIO,
        ):
            io_type = IOType(struct.unpack("<H", value[2:4])[0])
        else:
            io_type = None
        return cls(port=port, event=event, io_type=io_type)

    def __repr__(self):
        return f"{type(self).__name__}({self.port!r}, {self.event!r}, {self.io_type!r})"


class HubProperties(
    collections.namedtuple("HubProperties", ("property", "operation", "payload"))
):
    def to_bytes(self):
        return (
            struct.pack(
                "BBB", MessageType.HubProperties, self.property, self.operation,
            )
            + self.payload
        )

    @classmethod
    def from_bytes(cls, value):
        return cls(
            property=HubProperty(value[0]),
            operation=HubPropertyOperation(value[1]),
            payload=value[2:],
        )

    def __repr__(self):
        return f"{type(self).__name__}({self.property!r}, {self.operation!r}, {self.payload!r})"


class PortOutputMessage(
    collections.namedtuple(
        "PortOutputMessage", ("port", "startup", "completion", "sub_command")
    )
):
    def to_bytes(self):
        return (
            struct.pack(
                "BBB", MessageType.PortOutput, self.startup << 4 + self.completion,
            )
            + self.sub_command.to_bytes()
        )


class StartPowerSubCommand(
    collections.namedtuple("StartPowerSubCommand", ("start_power",))
):
    def to_bytes(self):
        return struct.pack("BB",)


class ErrorMessage(
    collections.namedtuple("ErrorMessage", ("command_type", "error_code"))
):
    @classmethod
    def from_bytes(cls, value):
        return cls(command_type=MessageType(value[0]), error_code=ErrorCode(value[1]),)

    def __repr__(self):
        return f"{type(self).__name__}({self.command_type!r}, {self.error_code!r})"


message_classes = {
    MessageType.HubProperties: HubProperties,  # 0x01
    # MessageType.HubActions: HubActions,  # 0x02
    # MessageType.HubAlerts: HubAlerts, # 0x03
    MessageType.HubAttachedIO: HubAttachedIO,  # 0x04
    MessageType.ErrorMessage: ErrorMessage,  # 0x05
}
