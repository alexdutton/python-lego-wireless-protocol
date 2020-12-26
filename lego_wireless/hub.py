import logging
import struct
import threading
import typing

import gatt

from lego_wireless import signals
from lego_wireless.constants import CHARACTERISTIC_UUID
from lego_wireless.enums import HubAttachedIOEvent
from lego_wireless.enums import HubProperty
from lego_wireless.enums import HubPropertyOperation
from lego_wireless.enums import MessageType
from lego_wireless.hub_io import HubIO
from lego_wireless.hub_io import LEDLight
from lego_wireless.hub_io import RGBLight
from lego_wireless.hub_io import TrainMotor
from lego_wireless.messages import HubAttachedIO
from lego_wireless.messages import HubProperties
from lego_wireless.messages import message_classes

logger = logging.getLogger(__name__)

DEFAULT_NAME = "HUB NO.4"


class Hub(gatt.Device):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ports = {}
        self.hub_characteristic = None
        self._battery_level = None
        self._connected = False

    @property
    def battery_level(self):
        return self._battery_level

    @property
    def connected(self):
        return self._connected

    @property
    def train_motor(self):
        for hub_io in self.ports.values():
            if isinstance(hub_io, TrainMotor):
                return hub_io

    @property
    def led_light(self):
        for hub_io in self.ports.values():
            if isinstance(hub_io, LEDLight):
                return hub_io

    @property
    def rgb_light(self) -> typing.Optional[RGBLight]:
        for hub_io in self.ports.values():
            if isinstance(hub_io, RGBLight):
                return hub_io
        return None

    def connect_succeeded(self):
        super().connect_succeeded()
        self._connected = True
        self.manager.hubs.add(self)
        logger.info("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        logger.warning("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        self._connected = False
        signals.hub_disconnected.send(self)

    def characteristic_enable_notification_succeeded(self, *args, **kwargs):
        super().characteristic_enable_notification_succeeded(*args, **kwargs)
        logger.info(
            "[%s] Characteristic enable notification_succeeded: %s %s"
            % (self.mac_address, str(args), str(kwargs))
        )

    def characteristic_value_updated(self, characteristic, value):
        super().characteristic_value_updated(characteristic, value)
        logger.debug("[%s] Message received: %r", self.mac_address, value)
        message = self.parse_message(value)
        logger.debug("[%s] Parsed message received: %r", self.mac_address, message)
        print(message)
        if isinstance(message, HubAttachedIO):
            if message.event in (
                HubAttachedIOEvent.AttachedIO,
                HubAttachedIOEvent.AttachedVirtualIO,
            ):
                if message.io_type in HubIO.registry:
                    self.ports[message.port] = HubIO.registry[message.io_type](
                        self, message.port
                    )
                    logger.info("New IO on port %d: %s", message.port, message.io_type)
                    signals.hub_io_connected.send(self, hub_io=self.ports[message.port])
                    self.hub_io_connected(self.ports[message.port])
                else:
                    logger.warning(
                        "Unimplemented IOType on port %d: %s",
                        message.port,
                        message.io_type,
                    )
            else:
                if message.port in self.ports:
                    logger.debug(
                        "Removed IO on port %d: %s",
                        message.port,
                        self.ports[message.port].io_type,
                    )
                    signals.hub_io_disconnected.send(
                        self, hub_io=self.ports[message.port]
                    )
                    self.hub_io_disconnected(self.ports[message.port])
                    del self.ports[message.port]
        elif (
            isinstance(message, HubProperties)
            and message.property == HubProperty.BatteryVoltage
            and message.operation == HubPropertyOperation.Update
        ):
            self._battery_level = int(message.payload[0])
            logger.debug(
                "[%s] Hub battery level: %d%%", self.mac_address, self._battery_level
            )
            signals.hub_battery_level.send(self, battery_level=self._battery_level)
        else:
            logger.warning("Unexpected message: %s", message)

    def hub_io_connected(self, hub_io):
        pass

    def hub_io_disconnected(self, hub_io):
        pass

    def send_message(self, message):
        if hasattr(message, "to_bytes"):
            logger.info("Sending message: %r", message)
            message = message.to_bytes()

        assert isinstance(message, bytes)

        length = len(message) + 2
        message = bytes([length, 0x00]) + message
        logger.info("Sending serialized message: %r", message)
        self.hub_characteristic.write_value(message)

    def parse_message(self, message):
        length = message[0]
        if not len(message) == length:
            logger.warning("Unexpected message length: %r", message)
            return
        message_type = MessageType(message[2])
        try:
            message_cls = message_classes[message_type]
        except KeyError:
            logger.warning("Unexpected message type: %s %r", message_type, message)
        else:
            return message_cls.from_bytes(message[3:])

    @property
    def name(self) -> typing.Optional[str]:
        try:
            return self._name
        except AttributeError:
            name = self._properties.Get("org.bluez.Device1", "Name")
            self._name: typing.Optional[str] = name if name != DEFAULT_NAME else None
            return self._name

    @name.setter
    def name(self, value: typing.Optional[str]):
        if not value:
            self.send_message(
                HubProperties(
                    property=HubProperty.AdvertisingName,
                    operation=HubPropertyOperation.Reset,
                    payload=b"",
                )
            )
            self._name = None
        elif len(value.encode()) > 14:
            raise ValueError("name cannot be longer than 14 characters")
        else:
            self.send_message(
                HubProperties(
                    property=HubProperty.AdvertisingName,
                    operation=HubPropertyOperation.Set,
                    payload=value.encode(),
                )
            )
            self._name = value

    def services_resolved(self):
        logger.debug("Services resolved for %s", self.mac_address)
        super().services_resolved()

        for service in self.services:
            for characteristic in service.characteristics:
                if str(characteristic.uuid) == CHARACTERISTIC_UUID:

                    self.hub_characteristic = characteristic
                    self.hub_characteristic.enable_notifications()

                    self.send_message(
                        struct.pack(
                            "BBB",
                            MessageType.HubProperties,
                            HubProperty.BatteryVoltage,
                            HubPropertyOperation.EnableUpdates,
                        )
                    )
                    self.send_message(
                        struct.pack(
                            "BBB",
                            MessageType.HubProperties,
                            HubProperty.Button,
                            HubPropertyOperation.EnableUpdates,
                        )
                    )
                    signals.hub_connected.send(self)
                    return
        logger.debug("Device %s is not a LWP Hub", self.mac_address)

    def async_connect(self):
        threading.Thread(target=self.connect).run()

    def async_disconnect(self):
        threading.Thread(target=self.disconnect).run()
