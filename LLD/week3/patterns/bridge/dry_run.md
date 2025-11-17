# Dry Run: Bridge Pattern

## Setup
```python
tv = Television()
remote = BasicRemote(tv)
```

Memory:
```
0x6001: Television
  on: False
  channel: 1

0x6002: BasicRemote
  _device: → 0x6001 (Television)
  current_channel: 1
```

## Operation: remote.power()

**Call**: `BasicRemote.power()`
```
self = BasicRemote at 0x6002
self._device = Television at 0x6001
```

**Delegate to implementation**:
```
self._device.turn_on()
→ Television.turn_on()
  self.on = True
  Output: "TV is ON"
```

## Operation: remote.channel_up()

**Call**: `BasicRemote.channel_up()`
```
self.current_channel += 1  # 1 → 2
self._device.set_channel(2)
→ Television.set_channel(2)
  self.channel = 2
  Output: "TV channel: 2"
```

## Key: Bridge Connection

**Abstraction** (BasicRemote) holds reference to **Implementation** (Television)

**Bridge** = `self._device` reference

Changes to RemoteControl hierarchy don't affect Device hierarchy
Changes to Device hierarchy don't affect RemoteControl hierarchy

This is decoupling through composition.
