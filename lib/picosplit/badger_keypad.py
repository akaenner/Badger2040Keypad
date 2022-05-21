import board
import busio
import time
from adafruit_binascii import hexlify, unhexlify, a2b_base64, b2a_base64
from digitalio import DigitalInOut, Direction, Pull
from adafruit_debouncer import Debouncer
from adafruit_mcp230xx.mcp23017 import MCP23017
from .keypad import Keypad
from .pico_keyboard import *

class BadgerKeypad(Keypad):
    """
    Subclass of Keypad to be used with the Badger 2040.
    """
    def __init__(self):
        super().__init__()
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.has_external_keys = self.detect_external_keypad()
        self.badge_key_pins = list() 
        if self.has_external_keys:
            self.mcp = MCP23017(self.i2c)
            self.mcp_key_pins   = list() 
            self.button_count   = 17
        else:
            self.button_count   = 5
        
        # On board switches
        self.badge_key_pins.append(self.debounced_pin(DigitalInOut(board.SW_A),    True))
        self.badge_key_pins.append(self.debounced_pin(DigitalInOut(board.SW_B),    True))
        self.badge_key_pins.append(self.debounced_pin(DigitalInOut(board.SW_C),    True))
        self.badge_key_pins.append(self.debounced_pin(DigitalInOut(board.SW_DOWN), True))
        self.badge_key_pins.append(self.debounced_pin(DigitalInOut(board.SW_UP),   True))
        
        if self.has_external_keys:
            # Switches connected to the MCP2017
            for i in range(0, 12):
                self.mcp_key_pins.append(self.debounced_pin(self.mcp.get_pin(i), False))
            
            # Predefined actions for on board switches
            self.fixed_keys = {0:Key(tap=PreviousLayout()),  # SW_A
                               1:Key(tap=NextLayout()),      # SW_B
                               2:Key(tap=SpecialAction()),   # SW_C
                               3:Key(tap=PreviousLayer()),   # SW_DOWN
                               4:Key(tap=NextLayer())}       # SW_UP
        else:
            self.last_i2c_check_time = time.monotonic()
    
    def fixed_button_keys(self):
        if self.has_external_keys:
            return self.fixed_keys
        else:
            return []

    def pressed_buttons(self):
        i = 0
        value = 0
        for pin in self.badge_key_pins:
            pin.update()
            if pin.value:
                value += 1 << i
            i = i+1
        if self.has_external_keys:
            # TODO: can be improved by reading a byte at once, but this is fast enough.
            for pin in self.mcp_key_pins:
                pin.update()
                if not pin.value:
                    value += 1 << i
                i = i+1
        else: 
            # Check every second if the badge has been connected with an external keyboard 
            # and restart the badge if necessary.
            i2c_check_time = time.monotonic()
            if i2c_check_time - self.last_i2c_check_time > 1.0:
                self.last_i2c_check_time = i2c_check_time
                if self.detect_external_keypad():
                    microcontroller.reset()

        return value

    def debounced_pin(self, pin, pullDown):
        pin.direction = Direction.INPUT
        if pullDown:
            pin.pull = Pull.DOWN
        else:
            pin.pull = Pull.UP
        return Debouncer(pin)

    def detect_external_keypad(self):
        # Wait for I2C lock
        while not self.i2c.try_lock():
            pass
        # Scan for devices on the I2C bus
        for x in self.i2c.scan():
            self.i2c.unlock() 
            return True
        self.i2c.unlock() 
        return False

