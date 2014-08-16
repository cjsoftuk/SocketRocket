#! /usr/bin/env python

"""
This project is based on Retaliation by Chris Dance at Papercut Software

This version written by Chris Malton (on a somewhat idle Friday)

Requirements:
   * A Dream Cheeky Thunder USB Missile Launcher
   * Python 2.6+
   * Python PyUSB Support and its dependencies 
      http://sourceforge.net/apps/trac/pyusb/
      (on Mac use brew to "brew install libusb")
   * Should work on Windows, Mac and Linux

"""

import sys
import logging
import platform
import time
try:
    import socketserver
except:
    import SocketServer as socketserver
import re
import json
import urllib2
import base64

import usb.core
import usb.util

class RocketLauncher:
    DOWN    = 0x01
    UP      = 0x02
    LEFT    = 0x04
    RIGHT   = 0x08
    FIRE    = 0x10
    STOP    = 0x20

    def __init__(self, device, rl_type):
        self.log = logging.getLogger("Launcher")
        if not rl_type in ["thunder", "original"]:
            raise ValueError("rl_type")
        self._type = rl_type
        self._device = device

    def _send_cmd(self, cmd):
        if "thunder" == self._type:
            self._device.ctrl_transfer(0x21, 0x09, 0, 0, [0x02, cmd, 0x00,0x00,0x00,0x00,0x00,0x00])
        elif "original" == self._type:
            self._device.ctrl_transfer(0x21, 0x09, 0x0200, 0, [cmd])

    def _send_led(self, cmd):
        if "thunder" == self._type:
            self._device.ctrl_transfer(0x21, 0x09, 0, 0, [0x03, cmd, 0x00,0x00,0x00,0x00,0x00,0x00])
        elif "original" == self._type:
            logging.warn("No LED on original launcher")

    def _send_move(self, cmd, ms):
        self._send_cmd(cmd)
        time.sleep(ms / 1000.0)
        self._send_cmd(RocketLauncher.STOP)

    def left(self, ms):
        self._send_move(RocketLauncher.LEFT, ms)

    def right(self, ms):
        self._send_move(RocketLauncher.RIGHT, ms)

    def up(self, ms):
        self._send_move(RocketLauncher.UP, ms)

    def down(self, ms):
        self._send_move(RocketLauncher.DOWN, ms)

    def home(self):
        self.down(2000)
        self.left(8000)

    def fire(self, how_many):
        if how_many < 1 and how_many > 4:
            how_many = 1
        time.sleep(0.5)
        for i in range(how_many):
            self._send_cmd(RocketLauncher.FIRE)
            time.sleep(4.5)        

class SocketRocket(socketserver.BaseRequestHandler):
    def handle(self):
        launcher = self.server.launcher
        while True:
            data = self.request.recv(1024).strip()
            # Data is a command to issue to the launcher
            for line in data.split("\n"):
                cmd = line.strip()
                logging.info("Received command string '%s'" % cmd)
                command = cmd.split(" ")[0]
                if len(cmd.split(" ")) > 1:
                    value = int(cmd.split(" ")[1])
                command = command.lower()
                if command == "right":
                    launcher.right(value)
                elif command == "left":
                    launcher.left(value)
                elif command == "up":
                    launcher.up(value)
                elif command == "down":
                    launcher.down(value)
                elif command == "zero" or command == "park" or command == "reset" or command == "home":
                    launcher.home()
                elif command == "pause" or command == "sleep":
                    time.sleep(value / 1000.0)
                elif command == "led":
                    if value == 0:
                        led(0x00)
                    else:
                        led(0x01)
                elif command == "fire" or command == "shoot":
                    launcher.fire(value)
                else:
                    self.request.sendall("ERR Invalid command\r\n")
                    continue
                self.request.sendall("OK\r\n")

def setup_usb():
    # Tested only with the Cheeky Dream Thunder
    # and original USB Launcher

    DEVICE = usb.core.find(idVendor=0x2123, idProduct=0x1010)

    if DEVICE is None:
        DEVICE = usb.core.find(idVendor=0x0a81, idProduct=0x0701)
        if DEVICE is None:
            raise ValueError('Missile device not found')
        else:
            DEVICE_TYPE = "original"
    else:
        DEVICE_TYPE = "thunder"

    

    # On Linux we need to detach usb HID first
    if "Linux" == platform.system():
        try:
            DEVICE.detach_kernel_driver(0)
        except Exception, e:
            pass # already unregistered    

    DEVICE.set_configuration()
    return (DEVICE, DEVICE_TYPE)

logging.basicConfig(level=logging.INFO)

dev, dtype = setup_usb()

server = socketserver.TCPServer( ("localhost", 54321), SocketRocket)
server.launcher = RocketLauncher(dev, dtype)
server.serve_forever()