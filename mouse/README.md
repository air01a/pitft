This script is used for controlling the touchscreen as if it was a mouse in text mode.

Because the correct driver (tslib) does not exists for gpm, it is the only way I found for managing text based interface using the touch screen capabilities.
This script uses the InputDevice library (pip install InputDevice) to open a pointer to the screen (normally, pitft should be referenced as /dev/input/touchscreen) if you completed the pitft guide successfully.


Usage : 
from mouse import MouseDriver

md = MouseDriver('/dev/input/touchscreen')  # Create instance
while True:
                event=md.listenEvent() # Listen for keypressed in blocking mode
                print event  # print event (dict form) {'x':xpos,'y':ypos,'pression':pression}
                print md.translateToText(event['x'],event['y']) # print coordonnate in text mode
                
You can also use a non blocking call :

def callBackFunction(mousehandler,event):
       print "OK"
       mousehandler._loop=False
       print event

md.setBlocking(False)
md.listenEvent(callBackFunction)
raw_input('...')

the callBackFunction receive as parameter mousehandler and event. By default, the mousehandler will continue to listen to touchscreen events.
If you want to break the loop, set the mousehandler._loop to False.
