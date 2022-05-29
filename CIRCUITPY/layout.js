var layout = `
// Do not modify the content above this line

keyboard
tap_timeout=0.15
long_tap_timeout=0.4


layout
title=Rhino 3D

layer
title=Base
  1 : tap=PreviousLayout
  2 : tap=NextLayout
  3 : tap=Codes[ ENTER ] : long_tap=ResetKeyboard
  4 : tap=PreviousLayer
  5 : tap=NextLayer
  6 : tap=Sequence[ Codes[ ESCAPE ] ; Text[ distance ] ; Codes[ ENTER ] ] : title=Distance
  7 : tap=Sequence[ Codes[ ESCAPE ] ; Text[ line ] ; Codes[ ENTER ] ] : title=Line
  8 : tap=Codes[ ESCAPE ] : title=Escape
  9 : tap=Codes[ ENTER ]  : title=Enter
 10 : tap=Sequence[ Codes[ ESCAPE ] ; Text[ PrevViewport ] ; Codes[ ENTER ] ] : title=Previous\nViewport
 11 : tap=Sequence[ Codes[ ESCAPE ] ; Text[ NextViewport ] ; Codes[ ENTER ] ] : title=Next\nViewport

layer
title=Other
  1 : tap=PreviousLayout
  
layout
title=Number Pad

layer
title=Base
  1 : tap=PreviousLayout
  2 : tap=NextLayout
  3 : tap=Codes[ ENTER ] : long_tap=ResetKeyboard
  4 : tap=PreviousLayer
  5 : tap=NextLayer
  6 : tap=Codes[ KEYPAD_SEVEN ] : title=7
  7 : tap=Codes[ KEYPAD_EIGHT ] : long_tap=Codes[ KEYPAD_FORWARD_SLASH ] : title=8\n/
  8 : tap=Codes[ KEYPAD_NINE ]  : long_tap=Codes[ KEYPAD_ASTERISK ] : title=9\n*
  9 : tap=Codes[ KEYPAD_MINUS ] : long_tap=Codes[ BACKSPACE ] : title=-\nBack\nspace
 10 : tap=Codes[ KEYPAD_FOUR ]  : title=4
 11 : tap=Codes[ KEYPAD_FIVE ]  : title=5
 12 : tap=Codes[ KEYPAD_SIX ]   : title=6
 13 : tap=Codes[ KEYPAD_PLUS ]  : title=+
 14 : tap=Codes[ KEYPAD_ONE ]   : title=1
 15 : tap=Codes[ KEYPAD_TWO ]   : title=2
 16 : tap=Codes[ KEYPAD_THREE ] : title=3
 17 : tap=Codes[ KEYPAD_ENTER ] : title=Enter


// Do not modify the content below this line 
`