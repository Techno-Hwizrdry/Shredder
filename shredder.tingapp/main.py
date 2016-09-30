__author__  = "Alexan Mardigian"
__version__ = "0.1"

import shlex
import subprocess
import time
import tingbot
from tingbot import *


BGCOLOR = 'black'
PASSES  = 0  # Modify this value to change the amount of passes 'shred' does.
PAUSE   = 5  # In seconds.
INSTR_LABEL = "(Tap the screen to begin.)"
START_LABEL = "Shred USB Drive"


state = { 'prompt':  START_LABEL,
          'subtext': INSTR_LABEL,
          'show_yes_no': False
}

def clearscreen():
    screen.fill(color=BGCOLOR)
    screen.update()

@touch()
def on_touch(xy, action):
    if action == 'down':
        state['prompt']  = "Are you sure?"
        state['subtext'] = ''
        state['show_yes_no']  = True

@right_button.press
def cancel_shredding():
    state['prompt']      = START_LABEL
    state['subtext']     = INSTR_LABEL
    state['show_yes_no'] = False
    
@left_button.press
def start_shredding():
    if state['show_yes_no']:
        VALID_DISKS = "/dev/sd"
        SHRED = 'sudo shred -z -v -n'
        FDISK = 'sudo fdisk -l'
 
        proc    = subprocess.Popen(shlex.split(FDISK), stdout=subprocess.PIPE)
        out,err = proc.communicate()
        dev_str = out.strip().split('\n')[-1]
        device  = dev_str[:dev_str.find(' ')]

        clearscreen()

        # First, check to see if there is a valid USB flash
        # drive plugged into the Tingbot.  This check is done
        # to make sure we will not wipe the SD card the OS
        # (and this app) is running from.

        if VALID_DISKS not in device:
            screen.text("Plug in USB flash drive.")
            screen.update()
        else:
            screen.text("Shredding...")
            screen.text("Please wait.", xy=(160, 180), font_size=17)
            screen.update()
            time.sleep(5)
           
            proc = subprocess.Popen(shlex.split(SHRED + str(PASSES) + ' ' + device), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
            clearscreen()

            while True:
                line = proc.stdout.readline()
                if not line: break
            
                clearscreen()
                screen.text(line, xy=(160, 116), font_size=20, max_width=140)
                screen.update()
                time.sleep(0.1)
    
            clearscreen()
    
            screen.text("Done!")
            screen.update()
        
        time.sleep(PAUSE)
        state['prompt']  = START_LABEL
        state['subtext'] = INSTR_LABEL
        state['show_yes_no'] = False

@every(seconds=1.0/30)
def loop():
    screen.fill(color=BGCOLOR)
    screen.text(state['prompt'], xy=(160,115))
    screen.text(state['subtext'], xy=(160, 180), font_size=20)

    if state['show_yes_no']:
        screen.text('YES', xy=(30,20), font_size=24)
        screen.text('NO', xy=(295, 20), font_size=24)

tingbot.run()