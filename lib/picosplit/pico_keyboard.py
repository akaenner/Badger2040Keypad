# This file is part of the PicoSplit-Keyboard project, http://kaenner.de/PicoSplit.html/
# 
# The MIT License (MIT)
# 
# Copyright (c) 2021 Andreas Känner
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import usb_hid
import time
import microcontroller
from adafruit_hid.keyboard import Keyboard as AdafruitKeyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

# ----------------------------------------------------------------------------------------------------------------------
# The term "Button" is associated with physical buttons on the keyboard.
# The term "Key" is associated with (virtual) keyboard keys, sent to the computer.
# ----------------------------------------------------------------------------------------------------------------------

class PicoKeyboard:
    """
    PicoKeyboard runs the main loop. It reads button states and emits
    key presses and releases conforming to the rules given in layout.
    """
    def __init__(self, keypad, layouts, tap_timeout, long_tap_timeout, emitHardwareKeyNumbers, logicalToRealKey, display):

        self.logicalToRealKey = logicalToRealKey

        # Display
        self.display = display

        # Keys are considered active if they are down. See comment in key_state_changed.
        self.active_keys = {}

        # Configuration
        self.keypad = keypad
        self.layouts = layouts         
        self.use_layout_at_index(0) # TODO: Load from preferences. If the stored layout no longer exists, use the first layout.
        self.long_tap_timeout = long_tap_timeout
        self.tap_timeout = tap_timeout
        self.emitHardwareKeyNumbers = emitHardwareKeyNumbers
        
        # HID
        self.hid_keyboard = AdafruitKeyboard(usb_hid.devices)
        self.hid_keyboard_layout = KeyboardLayoutUS(self.hid_keyboard)
        
        # Runntime
        self.isRunning = False     
        self.active_layer_index = 0
        
        # The time a button was pressed
        self.down = [0.0] * self.keypad.button_count

        # True for a button if a long down button has been detected during a down/up cycle of a Key.
        self.long_down = [False] * self.keypad.button_count

        # True for a button if a long button press has been detected during a down/up cycle of a Key.
        self.long_press = [False] * self.keypad.button_count

    def start(self):
        if not self.isRunning:
            self.isRunning = True
            button_count = self.keypad.button_count

            start = time.monotonic()
            # loops = 0
            # measured = False

            while self.isRunning:
                pressed = self.keypad.pressed_buttons()
                t = time.monotonic()
                for i in range(0, button_count):
                    down_time = self.down[i]
                    diff = t-down_time
                    button_pressed = pressed & (1 << i)
                    if button_pressed:
                        if down_time == 0.0:
                            self.down[i] = t
                            self.key_state_changed(i, Key.DOWN)    
                        elif diff >= self.tap_timeout:
                            if not self.long_down[i] and diff < self.long_tap_timeout:
                                self.long_down[i] = True
                                self.key_state_changed(i, Key.LONG_DOWN)
                            elif not self.long_press[i] and diff >= self.long_tap_timeout:
                                self.long_press[i] = True
                                self.key_state_changed(i, Key.LONG_PRESS)
                    elif down_time > 0.0:
                        self.key_state_changed(i, Key.UP)
                        self.down[i] = 0.0
                        self.long_press[i] = False
                        self.long_down[i] = False

                # if not measured:
                #     if time.monotonic() - start > 1.0:
                #         measured = True
                #         print("loops per second: ", loops)
                #     loops = loops + 1
                           
    def stop(self):
        self.isRunning = False

    def switch_to_layer_with_index(self, layer_index):
        """
        The next button down event fetches a key from the layer at the given index.
        """
        self.active_layer_index = layer_index

    def switch_to_layer_with_title(self, title):
        """
        The next button down event fetches a key from the layer with the given title.
        """
        self.active_layer_index = self.layout.layer_index_by_title[title]

    def key_state_changed(self, button_index, state):
        """
        Is called everytime a physical button on the device is pressed or released.
        Possible state values are Key.DOWN, Key.LONG_DOWN, Key.LONG_PRESS or Key.UP
        """

    	# Usually if no mapping.js file is present, the keyboard emits hardware key numbers.
        if self.emitHardwareKeyNumbers:
            if state == Key.UP:
                self.hid_keyboard_layout.write(f"{button_index}\n")
                print("emit: ", button_index)
            return
            
        # Make sure that the key which started to handle a button down event always handles the following button up event.
        # This is needed because the layer could have changed between the two events and we would then 
        # possibly get another key inside a button up event.
        key = self.key_for_button(button_index)
        if key:
            # Let the key handle the changed button state
            key.key_state_changed(self, state)
            
            # Track active keys
            if state == Key.DOWN:
                self.active_keys[button_index] = key
            elif state == Key.UP:   
                self.active_keys.pop(button_index)

    def key_for_button(self, button_index):
        key = self.active_keys[button_index] if button_index in self.active_keys else None
        if not key:
            key = self.layout.get_key(button_index, self.active_layer_index)
        # Fall back to the base layer if we did not find any key
        if not key:
            key = self.layout.get_key(button_index, 0)
        return key

    # Layout
            
    def use_layout_at_index(self, index):
        length = len(self.layouts)
        if length == 0:
            return
        if index >= length:
            index = 0
        self.layout = self.layouts[index]
        self.layoutIndex = index
        # Todo: use saved layer index
        self.active_layer_index = 0
        self.display.refresh(self)
        # Todo: save to prefs

    def use_next_layout(self):
        newIndex = self.layoutIndex + 1
        if newIndex >= len(self.layouts):
            newIndex = 0
        self.use_layout_at_index(newIndex)

    def use_previous_layout(self):
        newIndex = self.layoutIndex - 1
        if newIndex < 0:
            newIndex = len(self.layouts) - 1
        self.use_layout_at_index(newIndex)

    # Layers

    def use_layer_at_index(self, index):
        if not self.layout:
            return
        layers = self.layout.layers
        length = len(layers)
        if length == 0:
            return
        if index >= length:
            index = 0
        self.switch_to_layer_with_index(index)
        self.display.refresh(self)
        # Todo: save to prefs

    def use_next_layer(self):
        if not self.layout:
            return
        newIndex = self.active_layer_index + 1
        if newIndex >= len(self.layout.layers):
            newIndex = 0
        self.use_layer_at_index(newIndex)

    def use_previous_layer(self):
        if not self.layout:
            return
        newIndex = self.active_layer_index - 1
        if newIndex < 0:
            newIndex = len(self.layout.layers) - 1
        self.use_layer_at_index(newIndex)


# ----------------------------------------------------------------------------------------------------------------------
# Layout
# ----------------------------------------------------------------------------------------------------------------------

class Layout:
    def __init__(self, title, layers):
        self.title = title
        self.layers = layers
        self.layer_index_by_title = {}
        for index, layer in enumerate(layers):
            self.layer_index_by_title[layer.title] = index

    def get_key(self, key_index, layer_index):
        layer = self.get_layer_at_index(layer_index)
        return layer.get_key_at_index(key_index) if layer else None

    def get_layer_at_index(self, layer_index):
        layers = self.layers
        layer_count = len(layers)
        if layer_count != 0 and layer_index >= 0 and layer_index < layer_count:
            return layers[layer_index]
        return None

    def get_layer_with_title(self, title):
        return self.get_layer_at_index(self.layer_index_by_title(title))

class Layer:
    def __init__(self, title, keys):
        self.title = title
        self.keys = keys
    
    def get_key_at_index(self, key_index): 
        return self.keys[key_index] if key_index in self.keys else None

class Key:

    # Key states
    DOWN = 1
    LONG_DOWN = 2
    LONG_PRESS = 3
    UP = 4
    
    def __init__(self, tap, long_tap=None, hold=None, description=''):
        self.tap = tap
        self.long_tap = long_tap
        self.hold = hold
        self.state = Key.UP
        self.is_simple_key = self.tap and not self.long_tap and not self.hold
        self.hold_is_active = False
        self.tap_is_active = False
        self.description_lines = description.splitlines()

    def key_state_changed(self, controller, state ):
        """
        Triggers the appropriate action handler on a key state change.
        """
        if state == Key.DOWN: 
            Key.last_pressed = self

        if state == Key.UP:
            if self.hold_is_active:
                self.hold.on_key_up(self, controller)
                self.hold_is_active = False
            elif self.tap_is_active:
                self.tap.on_key_up(self, controller)

            if self.state == Key.LONG_DOWN or ( self.state == Key.LONG_PRESS and not self.hold ):                
                if self.long_tap and Key.last_pressed == self:
                    self.long_tap.on_key_down(self, controller)
                    self.long_tap.on_key_up(self, controller)                            
            elif self.state == Key.DOWN: 
                if not self.tap_is_active and self.tap:
                    self.tap.on_key_down(self, controller)
                    self.tap.on_key_up(self, controller)
            self.tap_is_active = False
        
        elif state == Key.DOWN and self.hold and self.hold.is_pretriggerable:
            self.hold.on_key_down(self, controller)
            self.hold_is_active = True
        elif state == Key.DOWN and self.is_simple_key:
            self.tap_is_active = True
            self.tap.on_key_down(self, controller)

        self.state = state
 
# ----------------------------------------------------------------------------------------------------------------------
# Actions
# ----------------------------------------------------------------------------------------------------------------------

class Action:
    def __init__(self):
        super().__init__()
        self.is_pretriggerable = False        

    def on_key_down(self, key, controller):
        pass

    def on_key_up(self, key, controller):
        pass

class EmitKeyCodes(Action):
    def __init__(self, key_codes):
        super().__init__()
        self.key_codes = key_codes     
        self.is_pretriggerable = self.contains_only_modifiers() 

    def contains_only_modifiers(self):
        if len(self.key_codes) == 0:
            return False
        for key_code in self.key_codes:
            if Keycode.modifier_bit(key_code) == 0:
                return False
        return True

    def on_key_down(self, key, controller): 
        self.modifier_bits_before_key_down = controller.hid_keyboard.report[0];
        controller.hid_keyboard.press(*self.key_codes)

    def on_key_up(self, key, controller):
        # We make sure, that we do not release a modifier that we did not press.
        for key_code in self.key_codes:
            bit = Keycode.modifier_bit(key_code)
            if not (self.modifier_bits_before_key_down & bit):
                controller.hid_keyboard.release(*[key_code])

class Autoshift(Action):
    def __init__(self):
        super().__init__()
        self._key_codes = None

    def _shifted_key_codes(self, key):
        if self._key_codes:
            return self._key_codes        
        if key.tap and isinstance(key.tap, EmitKeyCodes):
            self._key_codes = key.tap.key_codes.copy()
            self._key_codes.append(Keycode.LEFT_SHIFT)
            return self._key_codes
        return None

    def on_key_down(self, key, controller):
        key_codes = self._shifted_key_codes(key)
        if key_codes:
            controller.hid_keyboard.press(*key_codes)

    def on_key_up(self, key, controller):
        key_codes = self._shifted_key_codes(key)
        if key_codes:
            controller.hid_keyboard.release(*key_codes)

class EmitSequence(Action):
    def __init__(self, sequence):
        super().__init__()
        self.sequence = sequence

    def on_key_down(self, key, controller):
        for action in self.sequence:
            action.on_key_down(key, controller)
            action.on_key_up(key, controller)

class EmitText(Action):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def on_key_down(self, key, controller):
        controller.hid_keyboard_layout.write(self.text)

class ChangeLayer(Action):
    def __init__(self, layer_title):
        super().__init__()
        self.layer_title = layer_title
        self.is_pretriggerable = True
        self.previous_layer_index = 0

    def on_key_down(self, key, controller):
        self.previous_layer_index = controller.active_layer_index
        controller.switch_to_layer_with_title(self.layer_title)

    def on_key_up(self, key, controller):
        controller.switch_to_layer_with_index(self.previous_layer_index)
              
class ResetKeyboard(Action):    
    def on_key_down(self, key, controller):
        microcontroller.reset()
        
class NextLayout(Action):    
    def on_key_up(self, key, controller):
        controller.use_next_layout()

class PreviousLayout(Action):    
    def on_key_up(self, key, controller):
        controller.use_previous_layout()

class NextLayer(Action):    
    def on_key_up(self, key, controller):
        controller.use_next_layer()
        

class PreviousLayer(Action):    
    def on_key_up(self, key, controller):
        controller.use_previous_layer()

class SpecialAction(Action):    
    def on_key_down(self, key, controller):
        pass
