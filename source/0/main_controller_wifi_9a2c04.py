# https://github.com/ordmoj/qrasp/blob/470e167979fb421034871f9f4d39beda63cd1ead/main_controller_wifi.py
# Main controller for Qiskit on Raspberry PI SenseHat.

# Start by importing and simplifying required modules. 
from sense_hat import SenseHat
#from sense_emu import SenseHat
hat = SenseHat()
import time

from qiskit import IBMQ, Aer, execute


import Qconfig_IBMQ_experience
# from qiskit.tools.monitor import job_monitor

# Enable the account based on the stored API key
IBMQ.enable_account(Qconfig_IBMQ_experience.APItoken)

# Set default SenseHat configuration.
hat.clear()
hat.low_light = True

# Background icon
X = [255, 0, 255]  # Magenta
Y = [255,192,203] # Pink
O = [0, 0, 0]  # Black
B = [0,0,255] # Blue
#B = [70,107,176] # IBM Blue
W = [255, 255, 255] #White

super_position = [
O, O, O, Y, X, O, O, O,
O, O, Y, X, X, Y, O, O,
O, Y, O, O, X, O, Y, O,
O, Y, O, O, X, O, Y, O,
O, Y, O, O, X, O, Y, O,
O, Y, O, O, X, O, Y, O,
O, O, Y, O, X, Y, O, O,
O, O, O, X, X, X, O, O
]

IBMQ_super_position = [
O, O, O, Y, B, O, O, O,
O, O, Y, B, B, Y, O, O,
O, Y, O, O, B, O, Y, O,
O, Y, O, O, B, O, Y, O,
O, Y, O, O, B, O, Y, O,
O, Y, O, O, B, O, Y, O,
O, O, Y, O, B, Y, O, O,
O, O, O, B, B, B, O, O
]


IBM_Q = [
B, B, B, W, W, B, B, B,
B, B, W, B, B, W, B, B,
B, W, B, B, B, B, W, B,
B, W, B, B, B, B, W, B,
B, W, B, B, B, B, W, B,
B, B, W, B, B, W, B, B,
B, B, B, W, W, B, B, B,
B, B, B, W, W, W, B, B
]


IBM_AER = [
O, O, W, W, W, W, O, O,
O, W, W, O, O, W, W, O,
W, W, W, O, O, W, W, W,
W, W, O, W, W, O, W, W,
W, W, O, O, O, O, W, W,
W, O, W, W, W, W, O, W,
O, W, O, O, O, O, W, O,
O, O, W, W, W, W, O, O
]

# Understand which direction is down, and rotate the SenseHat display accordingly.
def set_display():
        acceleration = hat.get_accelerometer_raw()
        x = acceleration['x']
        y = acceleration['y']
        z = acceleration['z']
        x=round(x,0)
        y=round(y,0)
        z=round(z,0)
        if x == 1:
            hat.set_rotation(270)
        else:
            if x == -1:
                hat.set_rotation(90)
            else:
                if y == 1:
                    hat.set_rotation(0)
                else:
                    hat.set_rotation(180)

set_display()                

# Function to set the backend
def set_backend(back):
    global backend
    if back == "ibmq":
        backend = IBMQ.get_backend('ibmqx4')
    else:
        backend = Aer.get_backend('qasm_simulator')    
    print(backend.name)
    
# Load the Qiskit function files. Showing messages when starting and when done.
hat.show_message("Qiskit")

import q2_calling_sense_func
import q3_calling_sense_func
import bell_calling_sense_func
import GHZ_calling_sense_func
#import set_backend

# Initialize the backend to AER
back = "aer" 
set_backend(back)
hat.show_message(backend.name())
hat.set_pixels(IBM_AER)

# The main loop.
# Use the joystick to select and execute one of the Qiskit function files.

while True:
    joy_event = hat.stick.get_events()
    if len(joy_event) > 0 and joy_event[0][2]=="pressed":
        set_display()
        if joy_event[0][1]=="up":
            hat.show_message("Bell")
            #hat.show_message(backend.name())
            if back == "ibmq":
                hat.set_pixels(IBMQ_super_position)
            else:
                hat.set_pixels(super_position)
            bell_calling_sense_func.execute(backend,back)
        else:
            if joy_event[0][1]=="down":
                hat.show_message("GHZ")
                #hat.show_message(backend.name())
                if back == "ibmq":
                    hat.set_pixels(IBMQ_super_position)
                else:
                    hat.set_pixels(super_position)
                GHZ_calling_sense_func.execute(backend,back)
            else:
                if joy_event[0][1]=="left":
                    hat.show_message("2Q")
                    #hat.show_message(backend.name())
                    if back == "ibmq":
                        hat.set_pixels(IBMQ_super_position)
                    else:
                        hat.set_pixels(super_position)
                    q2_calling_sense_func.execute(backend,back)
                else:
                    if joy_event[0][1]=="right":
                        hat.show_message("3Q")
                        #hat.show_message(backend.name())
                        if back == "ibmq":
                            hat.set_pixels(IBMQ_super_position)
                        else:
                            hat.set_pixels(super_position)
                        q3_calling_sense_func.execute(backend,back)
                    else:
                        if joy_event[0][1]=="middle":
                            if back == "aer":
                                back = "ibmq"
                                #hat.show_message("IBMQ")
                                set_backend(back)
                                hat.show_message(backend.name())
                                hat.set_pixels(IBM_Q)
                            else:
                                back = "aer"
                                #hat.show_message("AER")
                                set_backend(back)
                                hat.show_message(backend.name())
                                hat.set_pixels(IBM_AER)
                                    

