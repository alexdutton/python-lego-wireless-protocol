import enum


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
