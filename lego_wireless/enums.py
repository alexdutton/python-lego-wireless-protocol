import enum
from gettext import gettext as _


class MessageType(enum.IntEnum):
    HubProperties = 0x01
    HubActions = 0x02
    HubAlerts = 0x03
    HubAttachedIO = 0x04
    ErrorMessage = 0x05
    PortOutput = 0x81


class OutputSubCommand(enum.IntEnum):
    StartPower = 0x01


class IOType(enum.IntEnum):
    Motor = 0x0001
    TrainMotor = 0x0002
    Button = 0x0005
    LEDLight = 0x0008
    Voltage = 0x0014
    Current = 0x0015
    PiezoTone = 0x0016
    RGBLight = 0x0017


class HubAttachedIOEvent(enum.IntEnum):
    DetachedIO = 0x00
    AttachedIO = 0x01
    AttachedVirtualIO = 0x02


class ColorNo(enum.IntEnum):
    Off = 0
    Magenta = 1
    Purple = 2
    Blue = 3
    Cyan = 4
    Turquoise = 5
    Green = 6
    Yellow = 7
    Orange = 8
    Red = 9
    White = 10


color_names = {
    ColorNo.Off: _("off"),
    ColorNo.Magenta: _("magenta"),
    ColorNo.Purple: _("purple"),
    ColorNo.Blue: _("blue"),
    ColorNo.Cyan: _("cyan"),
    ColorNo.Turquoise: _("turquoise"),
    ColorNo.Green: _("green"),
    ColorNo.Yellow: _("yellow"),
    ColorNo.Orange: _("orange"),
    ColorNo.Red: _("red"),
    ColorNo.White: _("white"),
}


class HubProperty(enum.IntEnum):
    AdvertisingName = 0x01
    Button = 0x02
    FWVersion = 0x03
    HWVersion = 0x04
    RSSI = 0x05
    BatteryVoltage = 0x06
    BatteryType = 0x07
    ManufacturerName = 0x08
    RadioFirmwareVersion = 0x09
    WirelessProtocolVersion = 0x0A
    SystemTypeID = 0x0B
    HWNetworkID = 0x0C
    PrimaryMACAddress = 0x0D
    SecondaryMACAddress = 0x0E
    HardwareNetworkFamily = 0x0F


class HubPropertyOperation(enum.IntEnum):
    Set = 0x01
    EnableUpdates = 0x02
    DisableUpdates = 0x03
    Reset = 0x04
    RequestUpdate = 0x05
    Update = 0x06


class Startup(enum.IntEnum):
    BufferIfNecessary = 0b0000
    ExecuteImmediately = 0b0001


class Completion(enum.IntEnum):
    NoAction = 0b0000
    CommandFeedback = 0b0001


class MotorControl(enum.IntEnum):
    Float = 0
    Brake = 127


class ErrorCode(enum.IntEnum):
    ACK = 0x01
    MACK = 0x02
    BufferOverflow = 0x03
    Timeout = 0x04
    CommandNotRecognized = 0x05
    InvalidUse = 0x06
    Overcurrent = 0x07
    InternalError = 0x08
