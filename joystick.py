#!/usr/bin/env python

from pygame import *
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

def main():
    init()
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    win = display.set_mode([1,1])

    msg = {'D': '0', 'T': '0', 'V': '0'}

    #let's turn on the joysticks just so we can play with em
    for x in range(joystick.get_count()):
        j = joystick.Joystick(x)
        j.init()
        print 'Enabled joystick: ' , j.get_name(), x
    if not joystick.get_count():
        print 'No Joysticks to Initialize'


    going = True
    while going:

        msg = {'D': 0, 'T': 0, 'V': 0}
        txt = {}

        for e in event.get():

            txt = e.dict

            if e.type == JOYAXISMOTION:
                #txt = '%s: %s' % (event.event_name(e.type), e.dict)
                #txt = 't: %s' % (e.dict)

                if txt['joy'] == 0:
                    msg['D'] = 1

                elif txt['joy'] == 1:
                    msg['D'] = 2

                if txt['axis'] == 0:
                    msg['T'] = 1

                elif txt['axis'] == 1:
                    msg['T'] = 2

                msg['V'] = int(txt['value'])
                jsonObj = json.dumps(msg)
                ws.send(jsonObj)
                print jsonObj


            elif e.type == JOYBUTTONDOWN:
                if txt['joy'] == 0:
                    msg['D'] = 1

                elif txt['joy'] == 1:
                    msg['D'] = 2

                msg['T'] = 3
                msg['V'] = 1

                jsonObj = json.dumps(msg)
                ws.send(jsonObj)
                print jsonObj

            elif e.type == KEYDOWN:
                msg['D'] = 3

                if txt['key'] == 273:
                    msg['T'] = 1
                    msg['V'] = 1

                elif txt['key'] == 274:
                    msg['T'] = 1
                    msg['V'] = -1

                elif txt['key'] == 275:
                    msg['T'] = 2
                    msg['V'] = 1

                elif txt['key'] == 276:
                    msg['T'] = 2
                    msg['V'] = -1

                elif txt['key'] == 32:
                    msg['T'] = 3
                    msg['V'] = 1

                elif txt['key'] == 27:
                    print "KILL! KILL IT WITH FIRE!!"
                    exit()

                jsonObj = json.dumps(msg)
                ws.send(jsonObj)
                print jsonObj



            else:
                msg['D'] = 0
                msg['T'] = 0
                msg['V'] = 0
                jsonObj = json.dumps(msg)
                ws.send(jsonObj)
                print jsonObj





if __name__ == '__main__':

    try:
        #start websocket
        ws = DummyClient('ws://localhost:8888/ws', protocols=['http-only', 'chat'])
        ws.connect()
        print "Connected to websocket"
        ws.send("{\"input\":true, \"output\":false}")
        main()


    #CTRL-C
    except KeyboardInterrupt:
        print "User cancelled"
        ws.close()

    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise

    finally:
        exit()
