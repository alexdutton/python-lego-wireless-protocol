from __future__ import annotations

import struct
import typing

from .enums import ColorNo
from .enums import IOType
from .enums import MessageType


class HubIOMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        cls = type.__new__(mcs, name, bases, attrs)
        if getattr(cls, "io_type", None):
            cls.registry[cls.io_type] = cls
        return cls


class HubIO(metaclass=HubIOMetaclass):
    io_type: IOType
    registry: typing.Dict[IOType, HubIO] = {}

    def __init__(self, hub, port):
        self.hub = hub
        self.port = port


class TrainMotor(HubIO):
    io_type = IOType.TrainMotor

    def set_speed(self, value):
        self.hub.send_message(
            struct.pack(
                "BBBBBBBB",
                MessageType.PortOutput,
                self.port,
                0x00,
                0x60,
                0x00,
                value,
                0x00,
                0x00,
            )
        )


class LEDLight(HubIO):
    io_type = IOType.LEDLight

    def set_brightness(self, value):
        self.hub.send_message(
            struct.pack(
                "BBBBBBBB",
                MessageType.PortOutput,
                self.port,
                0x00,
                0x60,
                0x00,
                value,
                0x00,
                0x00,
            )
        )


class Voltage(HubIO):
    io_type = IOType.Voltage


class RGBLight(HubIO):
    io_type = IOType.RGBLight

    def set_rgb_color_no(self, color_no: ColorNo):
        self.hub.send_message(
            struct.pack(
                "BBBBBB", MessageType.PortOutput, self.port, 0x01, 0x51, 0x00, color_no
            )
        )


class Current(HubIO):
    io_type = IOType.Current
