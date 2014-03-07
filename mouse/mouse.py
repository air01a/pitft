from evdev import InputDevice
from select import select
import threading
import traceback
import fcntl, termios, struct, os

class MouseDriver:
	_event=[]
	_blocking=True
	_listener=None
	
	def __init__(self,inputDevice,xpixel=320,ypixel=240):
		self._inputDevice=inputDevice
		self._xPixel=xpixel
		self._yPixel=ypixel
		self._dev = InputDevice(inputDevice)
		a,b=self._dev.capabilities(False,True)[3][0]
		self._maxX=b[2]
		a,b=self._dev.capabilities(False,True)[3][1]
		self._maxY=b[2]
		

	def calculateCoord(self,x,y):
		tmp=x
		x=self._xPixel-self._xPixel*y/self._maxY
		y=self._yPixel*tmp/self._maxX
		return (x,y)

	def _newEvent(self):
		return {'x':-1,'y':-1,'pression':-1}

	def _listenEvent(self):	
		currentEvent = self._newEvent()
		self._loop=True
		btnclick=False
		try:
			while self._loop==True:
				r,w,x = select([self._dev], [], [])
				for event in self._dev.read():
					if event.type==3:
						if event.code==0:
							currentEvent['x']=event.value
						elif event.code==1:
							currentEvent['y']=event.value

						elif event.code==24:
							currentEvent['pression']=event.value
					elif event.type==1:
						if event.code==330:
							btnclick=True


					complete=btnclick
					for (key,ev) in currentEvent.items():
						if ev==-1:
							complete=False
					if complete:
						(currentEvent['x'],currentEvent['y'])=self.calculateCoord(currentEvent['x'],currentEvent['y'])
						if self._blocking:
							return currentEvent
						self._callback(self,currentEvent)
						currentEvent = self._newEvent()
		except:
			print traceback.format_exc()
			return

	def setBlocking(self,blockMode):
		self._blocking=blockMode	

	def listenEvent(self,callback=None):
		if self._blocking:
			ret = None
			while ret == None:
				ret = self._listenEvent()
			return ret
		else:
			if self._listener==None:
				self._listener = threading.Thread(target=self._listenEvent)
				self._callback=callback
        	                self._listener.start()


	def _getTerminalSize(self):
    		env = os.environ
		def ioctl_GWINSZ(fd):
       			try:
            			cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,'1234'))
        		except:
            			return
        		return cr
    		cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    		if not cr:
        		try:
            			fd = os.open(os.ctermid(), os.O_RDONLY)
            			cr = ioctl_GWINSZ(fd)
            			os.close(fd)
       	 		except:
            			pass
    		if not cr:
        		cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

    		return int(cr[1]), int(cr[0])

	def translateToText(self,x,y):
		(width,height) = self._getTerminalSize()
		x = width*x/self._xPixel
		y = height*y/self._yPixel
		return (x,y)

#def test(mousehandler,event):
#	print "OK"
#	mousehandler._loop=False
#	print event
#	raise KeyboardInterrupt
def main():

	md = MouseDriver('/dev/input/touchscreen')
	while True:
		event=md.listenEvent()
		print event
		print md.translateToText(event['x'],event['y'])
	#md.setBlocking(False)
	#md.listenEvent(test)
	#raw_input('...')

if __name__ == "__main__":
	main()
