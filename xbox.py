import pygame
from pygame.locals import *
import os, sys
import threading
import time
import json
from ws4py.client.threadedclient import WebSocketClient

class DummyClient(WebSocketClient):
    def opened(self):

        def closed(self, code, reason=None):
            print "closed socket"

        def received_message(self, m):
            print m

#Main class for reading the xbox controller values
class XboxController(threading.Thread):

    #internal ids for the xbox controls
    class XboxControls():
        A = 0
        DPAD = 1

    #pygame constants for the buttons of the xbox controller
    class PyGameButtons():
        A = 0

    #map between pygame buttons ids and xbox contorl ids
    BUTTONCONTROLMAP = {PyGameButtons.A: XboxControls.A}

    #setup xbox controller class
    def __init__(self,
                 controllerCallBack = None,
                 joystickNo = 0,
                 deadzone = 0.1,
                 scale = 1,
                 invertYAxis = False):

        #setup threading
        threading.Thread.__init__(self)

        #persist values
        self.running = False
        self.controllerCallBack = controllerCallBack
        self.joystickNo = joystickNo
        self.lowerDeadzone = deadzone * -1
        self.upperDeadzone = deadzone
        self.scale = scale
        self.invertYAxis = invertYAxis
        self.controlCallbacks = {}

        #setup controller properties
        self.controlValues = {self.XboxControls.A:0,
                              self.XboxControls.DPAD:(0,0)}

        #setup pygame
        self._setupPygame(joystickNo)

    #Create controller properties
    @property
    def A(self):
        return self.controlValues[self.XboxControls.A]

    @property
    def DPAD(self):
        return self.controlValues[self.XboxControls.DPAD]

    #setup pygame
    def _setupPygame(self, joystickNo):
        # Set "null" videodriver
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        # init pygame
        pygame.init()
        # hack because display size needs to be set
        screen = pygame.display.set_mode((1, 1))
        # init the joystick control
        pygame.joystick.init()
        # how many joysticks are there
        print 'Joysticks attached: ', pygame.joystick.get_count()
        # get the first joystick
        joy = pygame.joystick.Joystick(joystickNo)
        # init that joystick
        joy.init()

    #called by the thread
    def run(self):
        self._start()

    #start the controller
    def _start(self):

        self.running = True

        #run until the controller is stopped
        while(self.running):
            #react to the pygame events that come from the xbox controller
            for event in pygame.event.get():

                #d pad
                if event.type == JOYHATMOTION:
                    #update control value
                    self.updateControlValue(self.XboxControls.DPAD, event.value)

                #button pressed and unpressed
                elif event.type == JOYBUTTONUP or event.type == JOYBUTTONDOWN:
                    #is this button on our xbox controller
                    if event.button in self.BUTTONCONTROLMAP:
                        #update control value
                        self.updateControlValue(self.BUTTONCONTROLMAP[event.button],
                                                self._sortOutButtonValue(event.type))

    #stops the controller
    def stop(self):
        self.running = False

    #updates a specific value in the control dictionary
    def updateControlValue(self, control, value):
        #if the value has changed update it and call the callbacks
        if self.controlValues[control] != value:
            self.controlValues[control] = value
            self.doCallBacks(control, value)

    #calls the call backs if necessary
    def doCallBacks(self, control, value):
        #call the general callback
        if self.controllerCallBack != None: self.controllerCallBack(control, value)

        #has a specific callback been setup?
        if control in self.controlCallbacks:
            self.controlCallbacks[control](value)

    #used to add a specific callback to a control
    def setupControlCallback(self, control, callbackFunction):
        # add callback to the dictionary
        self.controlCallbacks[control] = callbackFunction

    #turns the event type (up/down) into a value
    def _sortOutButtonValue(self, eventType):
        #if the button is down its 1, if the button is up its 0
        value = 1 if eventType == JOYBUTTONDOWN else 0
        return value

#tests
if __name__ == '__main__':

    #generic call back
    def controlCallBack(xboxControlId, value):
        if xboxControlId == 0:
            xboxControlId = "A"
        else:
            xboxControlId = 'DPAD'
        obj = {u"Button": xboxControlId, u"value": value}
        #print(json.dumps(obj))
        jsonObj = json.dumps(obj)
        ws.send(jsonObj)

    xboxCont = XboxController(controlCallBack)

    try:
        #start websocket
        ws = DummyClient('ws://localhost:8888/ws', protocols=['http-only', 'chat'])
        ws.connect()

        #start the controller
        xboxCont.start()
        print "xbox controller running"
        while True:
            time.sleep(1)


    #Ctrl C
    except KeyboardInterrupt:
        print "User cancelled"
        ws.close()

    #error
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise

    finally:
        #stop the controller
        xboxCont.stop()
