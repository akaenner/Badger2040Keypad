var layout = `
// Do not modify the content above this line

keyboard
tap_timeout=0.15
long_tap_timeout=0.4

layout
title=Booklover

layer
title=General
1 : tap=NextLayout : long_tap=NextLayer : title=Next Layout\nNext Layer
2 : tap=Codes[ ESCAPE ] : title=Escape
3 : tap=Codes[ ENTER ] : long_tap=ResetKeyboard : title=Enter\nReset
4 : tap=Codes[ RIGHT_ARROW ] : title=->  
5 : tap=Codes[ LEFT_ARROW ] : title=<-
 
layout
title=Clip Studio

layer
title=General
1 : tap=NextLayout : long_tap=NextLayer : title=Next Layout\nNext Layer 
2 : tap=Codes[ GUI, Z ] : long_tap=Codes[ GUI, SHIFT, Z ] : title=Undo\nRedo 
3 : tap=Codes[ P ] : long_tap=Codes[ E ] : title=Pen\nEraser 
4 : tap=Codes[ GUI, KEYPAD_PLUS ] : title=Zoom In  
5 : tap=Codes[ GUI, KEYPAD_MINUS ] : title=Zoom Out

layer
title=Selection
2 : tap=Codes[ GUI, A ] : title=Select All 
3 : tap=Codes[ GUI, D ] : title=Deselect 
4 : tap=Codes[ SHIFT, GUI, D ] : title=Reselect  
5 : tap=Codes[ SHIFT, GUI, I] : title=Invert\nselected\narea

// Do not modify the content below this line 
`
