import board
import terminalio
import displayio
import vectorio

import gc
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.line import Line
from adafruit_bitmap_font import bitmap_font

class BadgerDisplay:
    
    def __init__(self, inverted=False):
        # self.act = digitalio.DigitalInOut(board.USER_LED)
        # self.act.direction = digitalio.Direction.OUTPUT
        self.inverted = inverted
        self.fontBold = bitmap_font.load_font("fonts/amstrad_cpc_extended.bdf")
        # self.fontBold = terminalio.FONT
        self.font = self.fontBold
        self.palette = displayio.Palette(2)
        if self.inverted:
            self.palette[0] = 0xFFFFFF
            self.palette[1] = 0x000000
        else:
            self.palette[0] = 0x000000
            self.palette[1] = 0xFFFFFF
        self.display = board.DISPLAY
        self.padding_top    = 2
        self.padding_bottom = 2
        self.padding_left   = 2
        self.padding_right  = 1
        self.bar_height = 15
        self.min_x = self.padding_left
        self.max_x = self.display.width - self.padding_right
        self.width = self.max_x - self.min_x
        self.min_y = self.padding_top + self.bar_height
        self.max_y = self.display.height - self.padding_bottom
        self.height = self.max_y - self.min_y
    
    def refresh(self, keyboard):
        # Drawing is a memory intensive task.
        # Make sure, we have enough free memory.
        gc.collect()
        if keyboard.keypad.has_external_keys:
            self.draw_for_external_keyboard(keyboard)
        else:
            self.draw_for_builtin_keyboard(keyboard)
        gc.collect()

    def draw_for_builtin_keyboard(self, keyboard):
        display = board.DISPLAY
        group = displayio.Group()
        self.add_background(group)

        block_width = round(self.width / 3)
        x = self.min_x + (block_width * 2) 
        block_height = round(self.display.height / 3)
        y = block_height
        group.append(vectorio.Rectangle(pixel_shader=self.palette, color_index=0, width=self.width+2, height=1, x=x, y=y))
        y = y + block_height + 2
        
        group.append(vectorio.Rectangle(pixel_shader=self.palette, color_index=0, width=self.width+2, height=1, x=self.min_x, y=y))
        group.append(vectorio.Rectangle(pixel_shader=self.palette, color_index=0, width=1, height=self.height+4, x=x, y=self.min_y-2))
        x = x - block_width
        group.append(vectorio.Rectangle(pixel_shader=self.palette, color_index=0, width=1, height=round(block_width), x=x, y=y))

        group.append(vectorio.Rectangle(pixel_shader=self.palette, color_index=0, width=self.width-block_width+4, height=2 + block_height * 2, x=0, y=0))

        # White line
        y = block_height
        group.append(vectorio.Rectangle(pixel_shader=self.palette, color_index=1, width=self.width-block_width+4, height=1, x=0, y=y))

        # Create the layout title
        x_label = 10
        layout = keyboard.layout
        layout_label = label.Label(self.fontBold, text=layout.title, color=self.palette[1], scale=2)
        layout_label.anchor_point = (0.0, 0.0)
        layout_label.anchored_position = (x_label, 14)
        group.append(layout_label)

        # Create the layer title
        layer = layout.get_layer_at_index(keyboard.active_layer_index)
        layer_label = label.Label(self.fontBold, text=layer.title, color=self.palette[1], scale=2)
        layer_label.anchor_point = (0.0, 0.0)
        layer_label.anchored_position = (x_label, 60)
        group.append(layer_label)
    
        # Buttons
        x = self.min_x
        y = 2 * block_height + 2
        self.add_labels_for_key(keyboard, 1, x, y, block_width, block_height, self.font, self.palette[0], group)
        self.add_labels_for_key(keyboard, 2, x + block_width, y, block_width, block_height, self.font, self.palette[0], group)
        self.add_labels_for_key(keyboard, 3, x + 2 * block_width, y, block_width, block_height, self.font, self.palette[0], group)
        self.add_labels_for_key(keyboard, 4, x + 2 * block_width, y - block_height, block_width, block_height, self.font, self.palette[0], group)
        self.add_labels_for_key(keyboard, 5, x + 2 * block_width, y - 2 * block_height, block_width, block_height, self.font, self.palette[0], group)

        # self.add_left_line(group)

        # Show the group and refresh the screen to see the result
        display.show(group)
        display.refresh()
        del group

    def draw_for_external_keyboard(self, keyboard):
        # self.act.value = True
        
        # Create the display group and append objects to it
        group = displayio.Group()
        self.add_background(group)

        # The button grid
        button_padding = 0
        button_width = int((self.width - button_padding * 3) / 4)
        button_height = int((self.height - button_padding * 2) / 3)        
        key_index = 6

        # Button help text
        y = self.min_y
        for iy in range(0,3):
            x = self.min_x
            for ix in range(0,4):
                description_lines = self.labels_for_key(keyboard, key_index)
                if description_lines:
                    self.add_button_labels(description_lines, x, y, button_width, button_height, self.font, self.palette[0], group)
                key_index = key_index + 1
                x = x + button_width + button_padding
            y = y + button_height + button_padding

        # Draw the grid
        x = self.min_x + button_width
        for ix in range(0,3):
            group.append(vectorio.Rectangle(pixel_shader=self.palette, color_index=0, width=1, height=self.max_y-self.min_y+4, x=x, y=self.min_y-2))
            x = x + button_width + button_padding
        
        y = self.min_y + button_height
        for iy in range(0,2):
            group.append(vectorio.Rectangle(pixel_shader=self.palette, color_index=0, width=self.max_x-self.min_x+2, height=1, x=self.min_x, y=y))
            y = y + button_height + button_padding

        self.add_layout_and_layer(keyboard, group)
        # self.add_left_line(group)
        
        # Show the group and refresh the screen to see the result
        self.display.show(group)
        self.display.refresh()
        del group
        # self.act.value = False
    
    def add_labels_for_key(self,keyboard,key_index, x, y, width, height, font, color, group):
        labels = self.labels_for_key(keyboard, key_index)
        if labels:
            self.add_button_labels(labels, x, y, width, height, font, color, group)

    def labels_for_key(self, keyboard, key_index):
        key = keyboard.key_for_button(keyboard.logicalToRealKey.get(key_index), False)
        if key and len(key.description_lines) > 0:
            return key.description_lines
        return None

    def add_button_labels(self, lines, x, y, width, height, font, color, group):
        x = x + int(width / 2)
        y = y + int(height / 2)
        y_center_offset = 7
        if len(lines) == 1:
            self.add_button_label(lines[0], font, color, x, y, group)
        elif len(lines) == 2:
            self.add_button_label(lines[0], font, color, x, y - y_center_offset, group)
            self.add_button_label(lines[1], font, color, x, y + y_center_offset, group)
        elif len(lines) >= 3: # more than three lines are not shown
            y_center_offset = 12
            self.add_button_label(lines[0], font, color, x, y - y_center_offset, group)
            self.add_button_label(lines[1], font, color, x, y, group)
            self.add_button_label(lines[2], font, color, x, y + y_center_offset, group)

    def add_button_label(self, text, font, color, x, y, group):
        l = label.Label(font, text=text, color=color)
        l.anchor_point = (0.5, 0.5)
        l.anchored_position = (x, y)
        group.append(l)

    def add_layout_and_layer(self, keyboard, group):
        
        rectangle = vectorio.Rectangle(pixel_shader=self.palette, color_index=0, width=self.display.width + 2, height=self.bar_height, x=0, y=0)
        group.append(rectangle)
        
        # Create the layout title
        layout = keyboard.layout
        layout_label = label.Label(self.fontBold, text=layout.title, color=self.palette[1], scale=1)
        layout_label.anchor_point = (0.0, 0.5)
        layout_label.anchored_position = (self.min_x + 3, self.padding_top + (self.bar_height / 2) - 1)
        group.append(layout_label)

        # Create the layer title
        layer = layout.get_layer_at_index(keyboard.active_layer_index)
        layer_label = label.Label(self.fontBold, text=layer.title, color=self.palette[1], scale=1)
        layer_label.anchor_point = (1.0, 0.5)
        layer_label.anchored_position = (self.max_x-1, self.padding_top + (self.bar_height / 2) - 1)
        group.append(layer_label)
    
    def add_left_line(self, group):
        # Draw a line at the left edge in order to adjust for my hardware screen-offset (todo fix plastic parts)
        if self.inverted:
            group.append(vectorio.Rectangle(pixel_shader=self.palette, color_index=0, width=2, height=self.max_y-self.min_y+4, x=1, y=self.min_y-2))
        else:
            group.append(vectorio.Rectangle(pixel_shader=self.palette, color_index=1, width=2, height=self.display.height+4, x=2, y=0))

    def add_background(self, group):
        group.append(vectorio.Rectangle(pixel_shader=self.palette, color_index=1, width=self.display.width + 2, height=self.display.height + 2, x=0, y=0))
        