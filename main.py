import time
import gc
import errno
import microcontroller

from lib.picosplit.config_loader  import ConfigLoader
from lib.picosplit.badger_keypad  import BadgerKeypad
from lib.picosplit.badger_display import BadgerDisplay

# Sleep for a bit to avoid a race condition on some systems
time.sleep(1)

# load the configuration from the layout.js file
keypad = BadgerKeypad()

inverted = False
# inverted = True
configFile = "layout.js"
mapping_file_name = "mapping.js"
if not keypad.has_external_keys:
	configFile = "standalone_layout.js"
	mapping_file_name = "standalone_mapping.js"
	inverted = True

loader  = ConfigLoader(configFilePath=configFile) 
display = BadgerDisplay(inverted=inverted)
	 
keyboard = None
while True:
	while True:
		try:
			keyboard = loader.create_keyboard(keypad, display, mapping_file_name)
			break
		except Exception as e:
			time.sleep(1)
		gc.collect()

		try:
			keyboard.start()
		except OSError as e:
			# This error is thrown if the badge is removed from the external keyboard
			if e.errno == errno.ENODEV: 
				microcontroller.reset()
		except Exception as e:
			print(e)
			pass	
		


