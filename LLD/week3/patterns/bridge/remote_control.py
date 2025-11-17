"""Bridge Pattern - Remote Control Example"""

from abc import ABC, abstractmethod


# Implementation (Device)
class Device(ABC):
    @abstractmethod
    def turn_on(self):
        pass

    @abstractmethod
    def turn_off(self):
        pass

    @abstractmethod
    def set_channel(self, channel):
        pass


class Television(Device):
    def __init__(self):
        self.on = False
        self.channel = 1

    def turn_on(self):
        self.on = True
        print("TV is ON")

    def turn_off(self):
        self.on = False
        print("TV is OFF")

    def set_channel(self, channel):
        if self.on:
            self.channel = channel
            print(f"TV channel: {channel}")


class Radio(Device):
    def __init__(self):
        self.on = False
        self.frequency = 88.0

    def turn_on(self):
        self.on = True
        print("Radio is ON")

    def turn_off(self):
        self.on = False
        print("Radio is OFF")

    def set_channel(self, channel):
        if self.on:
            self.frequency = 88.0 + channel
            print(f"Radio frequency: {self.frequency} FM")


# Abstraction (Remote)
class RemoteControl(ABC):
    def __init__(self, device: Device):
        self._device = device

    @abstractmethod
    def power(self):
        pass

    @abstractmethod
    def channel_up(self):
        pass


class BasicRemote(RemoteControl):
    def __init__(self, device: Device):
        super().__init__(device)
        self.current_channel = 1

    def power(self):
        self._device.turn_on()

    def channel_up(self):
        self.current_channel += 1
        self._device.set_channel(self.current_channel)


if __name__ == "__main__":
    print("BRIDGE PATTERN DEMONSTRATION")
    print("="*60)

    # Basic remote controlling TV
    tv = Television()
    tv_remote = BasicRemote(tv)
    tv_remote.power()
    tv_remote.channel_up()

    print()

    # Same remote controlling Radio
    radio = Radio()
    radio_remote = BasicRemote(radio)
    radio_remote.power()
    radio_remote.channel_up()

    print("\n" + "="*60)
    print("Key Observations:")
    print("  - Same remote works with different devices")
    print("  - Add new devices without changing remotes")
    print("  - Add new remotes without changing devices")
    print("  - 2 remotes × 2 devices = 4 classes (not 4 combinations)")
    print("="*60)
