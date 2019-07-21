from blinker import signal

hub_discovered = signal("hub-discovered")

hub_connected = signal("hub-connected")
hub_disconnected = signal("hub-disconnected")

hub_io_connected = signal("hub-io-connected")
hub_io_disconnected = signal("hub-io-disconnected")

hub_battery_level = signal("hub-battery-level")
