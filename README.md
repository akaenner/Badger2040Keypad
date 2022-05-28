# Badger2040Keypad
Turn the Badger 2040 E Ink display into a programmable and extensible Macro Keypad using CircuitPython. The firmware for the Badger 2040 keypad is a derivative of my PicoSplit firmware. This firmware certainly has fewer features than some other firmware, but it comes with everything for configuration. You don't need to install any additional software on your computer. A simple text editor and a web browser is all you need. I provide the firmware for free under the **MIT license**. 

## Firmware features

* Time-saving system for wiring the switches.
* No need to install any other software on your computer. 
* Readable configuration file format.
* Easily modifiable with some Python knowledge.
* Advanced keyboard layouts are possible.
* Supports multiple layouts and each layout can have multiple layers.

## Installing the firmware

The Badger 2040 Keypad firmware is based on CircuitPython version 7.3. Previous versions do not work. Go to https://circuitpython.org/board/pimoroni_badger2040/ and install CircuitPython on your badge. Then proceed with the next steps.

1. Connect the badge with a USB cable to your computer. 
2. A USB memory drive with the name CIRCUITPY appears inside the Finder (macOS) or Explorer (Windows).
3. Copy the files and folders of this repository to that drive.

! If you do not want to use an external keypad module skip 'Keypad module setup’ and ‘Mapping hardware keys'.

## Keypad module setup

### Quick function test with the keypad module

1. Open an text editor
2. Press all the keys on your keypad one after the other. 

Each time you press a key, a number should appear in the text editor and then the cursor should jump to the next line. **If no number appears when you press a key, check the wiring of the corresponding key.**

## Mapping hardware keys

When we talk about a keyboard layout, we often mean two things: The arrangement of keys on a keyboard and the key assignment. **In the Badger 2040 keypad firmware the layout term is used for the key assignment.**

This firmware is designed to make the wiring as simple as possible. For example: the keys don't have to be connected to specific input pins of the MCP23017 in order to match a certain key arrangement (you can use all inputs except the last four: B4, B5, B6 and B7). This makes it easier to build handwired keyboards, because you can connect any key to any pin, as long as you use the pins you specified in the firmware.

The numbers you see when doing the quick function test are hardware key numbers. These hardware key numbers are mapped to standardized key numbers, which are used in the keyboard layout definition file (**layout.js**). This way you can use the same layout with differently wired keyboards. 

The mapping from hardware key numbers to layout key numbers cannot be done automatically, because the system does not know how the keys are wired. But there is a tool for this task. Open the file **PinMapper.html** in a web browser and you will see the following page:

![Image](./images/badger-pin-mapper_a.jpg)

These are all the keys on the Badger 2040 when it is attached to the keypad module. The small number in the top left corner is the key number which is used inside the layout definition file (**layout.js**). The grayed-out keys built in to the badge have a fixed mapping that cannot be changed. They are displayed for reference purposes only. To map the hardware key numbers to the numbers used in layout.js, press the key on your keypad that is highlighted in blue. 

![Image](./images/badger-pin-mapper_b.jpg)

The recorded hardware key number is now visible at the center of the key (**12**). Then the next key is highlighted. Continue until you have pressed all the keys. You can always select a key with the mouse to change incorrect entries. When you have pressed all the keys, click the *Download* button. This will save a **mapping.js** file in your downloads folder. Copy this file to your keyboard. 

If a **mapping.js** file is availabe on the keyboard, the keyboard stops emitting hardware key numbers and instead emits the key codes defined by the rules in **layout.js**.

### Layout definition files

The badge can be operated in two modes: 

* Without the keypad module. In that case, the description is read from ** standalone_layout.js**. 
* With the keypad module, the description is read from **layout.js**.

If you wonder why these and other files have the extension **.js**: They can be loaded as Javascript into a locally opened HTML page. For example: **PinMapper.html** uses this mechanism to read the key positions from **keypositions.js**. 

! There is actually no HTML based tool for managing **layout.js** and **standalone_layout.js**, but maybe there will be one in the future. 

#### Sections

**layout.js** and **standalone_layout.js** consist of sections. Each section begins with a section keyword in one line and ends with the next empty line. These are the three available section types:

- keyboard
- layout
- layer

The order and count is important. It starts with a single keyboard section, followed by one ore more layout sections which each containing one or more layer sections.

#### Keyboard section

The keyboard section defines some timeouts which apply to all keys. 

```
keyboard
tap_timeout=0.15
long_tap_timeout=0.4
```






To describe these values, I would like to briefly discuss various action triggers. The firmware supports three triggers for each key:

- tap
- long_tap
- hold

A **tap action** is triggered when you press and release a key before `tap_timeout` (in seconds).

A **long tap action** is triggered when you press a key longer than `tap_timeout` but release it before `long_tap_timeout` (in seconds). In combination with the Shift action, which will be described later, you can for example type a capital letter, just by holding the key down a little longer.

A **hold action** is immediately triggered when you press a key. If you release the key before `long_tap_timeout` the hold action is released before a tap or long tap is triggered. If you press the key longer than `long_tap_timeout`, the hold action is released when you release the key. Its action does not affect a tap or long tap if it emits modifier keys or switches to another layer.

You are probably wondering what this is good for? With the hold action you can assign modifiers to keys which are normally used to type characters. Hold actions are also used to activate some layers. 

#### Layout section

A layout section has just one property, the title of the layout. This title can be used in a ChangLayer() action to reference a layer. 

```
layout
title=Booklover
```

#### Layer section

A layer has a title. It contains rules for action triggers (`tap`, `long_tap` or `hold`). There must be at least one layer - the base layer - and you can define multiple additional layers. Only one layer can be active at any time. However, rules do not have to be defined for all keys on each layer. For keys without a rule, the rule from the base layer is used.

Here is an example with all three action triggers and some of the actions:

```
layer
title=Base
1 : tap=NextLayout : long_tap=NextLayer : title=Next Layout\nNext Layer
2 : tap=Codes[ ESCAPE ] : title=Escape
3 : tap=Codes[ ENTER ] : long_tap=ResetKeyboard : title=Enter\nReset
4 : tap=Codes[ RIGHT_ARROW ] : title=-&gt;  
5 : tap=Codes[ LEFT_ARROW ] : title=&lt;-
```

A line which describes rules for a key starts with the key number followed by at least one rule. A rule consists of the action trigger name (`tap`, `long_tap` or `hold`) followed by the equal sign and the action. Rules are separated by colons. 

Each line can have a optional title part. If a title is given it is shown up on the display for the key. You can use up to three lines by specifying line breaks with \n.

##### Available actions:

**Codes[ &lt; Keycode &gt;, &lt; Keycode &gt;, … ]**
Emits the given key codes at the same time. See **Keycodes.html** for all available key codes.  

**Sequence[ &lt; Action &gt; ; &lt; Action &gt; ]**
Emits the given actions one after the other. Sequences are currently not nestable and are only tested with Code actions. Note: The separator between actions inside sequences is a semicolon.

**Shift**
Can be triggered by a `long_tap` and is only usefull if a `tap` action exists. It triggers the tap action and emits the key code for the shift key at the same time. This is used to emit capitalized letters on a long tap.

**NextLayout** activates the first layer of the next layout.

**PreviousLayout** activates the first layer of the previous layout.

**NextLayer** activates the next layer of the active layout.

**Previous Layer** activates the previous layer of the active layout.

**ResetKeyboard** restarts / resets the badge. 

**ChangeLayer( &lt; layer name &gt; )** temporarily activates the layer with the given name as long as the trigger (tap or hold) is active.  **Note:** the display does not show temporary layer changes because it is too slow for that. 

## Boot behavior

The firmware has a maintenance mode in which a USB memory drive with all configuration files shows up. The keyboard is automatically in maintenance mode if no **mapping.js** file is on the memory drive. You can manually enter maintenance mode by resetting or reconnecting the keyboard to the computer while pressing and holding one of the badge's built-in buttons. 

If you want to always boot the keyboard in maintenance mode set maintenance_mode to True at the beginning of **boot.py**.

```
maintenance_mode = True
```