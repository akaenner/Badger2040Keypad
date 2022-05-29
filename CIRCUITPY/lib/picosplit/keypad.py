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

class Keypad:
    """
    Base class for accessing the state of physical buttons.
    Must be subclassed to be usefull. Subclasses have to implement
    _count() and pressed_buttons()
    """
    def __init__(self):

        # Make sure to adjust this value in your subclass
        self.button_count = 0

    def pressed_buttons(self):
        """
        Returns an bit array where each bit with a 1 represents a pressed button.
        Overwrite this in your subclass.
        """    
        return b''

    def set_button_color(self, button_index, color):
        pass
        
    def set_brightness(self, brightness):
        pass

    # Used for defining actions for on board switches.
    # Contains instances of Key by key number.
    def fixed_button_keys(self):
        return {}

    