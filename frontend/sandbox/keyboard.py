import tkinter
import pyautogui
import os
from pydispatch import Dispatcher
from pynput import mouse, keyboard

import time

class KeyboardApplication():
    BUTTON_TEXTS = [
        ['Cursor','1','2','3','4','5','6','7','8','9','0','-','=','Delete'],
        ['Tab','q','w','e','r','t','y','u','i','o','p','[',']','\\',],
        ['Shift','a','s','d','f','g','h','j','k','l',';',"'",'Enter'],
        ['z','x','c','v','b','n','m',',','.','/','`','Siri'],
        ['Space']
    ]
    BUTTON_TEXTS_SHIFT = [
        ['Cursor','!','@','#','$','%','^','&','*','(',')','-','=','Delete'],
        ['Tab','Q','W','E','R','T','Y','U','I','O','P','{','}','|'],
        ['Shift','A','S','D','F','G','H','J','K','L',':','"','Enter'],
        ['Z','X','C','V','B','N','M','<','>','?','~','Siri'],
        ['Space']
    ]

    def __init__(self, parent):
        # initialize keyboard layout
        self.label = tkinter.Label(parent, text='Keyboard', font=('arial', 30, 'bold'), bg='grey') 
        self.label.grid(row = 0, columnspan = 15)
        self.entry = tkinter.Text(parent, width = 100, height = 10, font = ('arial', 20, 'bold'))
        self.entry.grid(row = 1, columnspan = 15)

        # initialize keyboard attributes
        self.parent = parent
        self.buttons = [] # list of tkinter Buttons
        self.focus_row = 0 # TODO: merge row and col into a tuple?
        self.focus_col = 0
        self.is_shift = False # whether the shift modifier is active
        
        # orientation of controls
        self.horizontal = False # default mapping for shoulder directions
        self.mouse_mode = True

        # initialize buttons
        self.display_buttons()
        self.buttons[0][0].focus_set()
        self.parent.bind('<KeyPress>', self.on_key_press)

        # initialize mouse and keyboard controllers
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()

    # either a left click in mouse mode or a key press in keyboard mode
    def on_double_blink(self, *args, **kwargs):
        if self.mouse_mode:
            self.mouse_controllers(keyboard.Button.left)
            self.mouse_controllers.release(keyboard.Button.left)
        else:
            # special behavior for space button row
            effective_col = 0 if self.focus_row == len(self.buttons) - 1 else self.focus_col
            self.buttons[self.focus_row][effective_col].invoke()

    # right click
    def on_triple_blink(self, *args, **kwargs):
        self.mouse_controllers(keyboard.Button.right)
        self.mouse_controllers.release(keyboard.Button.right)

    PY_AUTO_DISTANCE = 0
    PY_AUTO_DURATION = 0.5

    # toggle between mouse mode and keyboard mode
    def on_left_wink(self, *args, **kwargs):
        self.mouse_mode = not self.mouse_mode

    # toggle between horizontal controls and vertical controls
    def on_right_wink(self, *args, **kwargs):
        self.horizontal = not self.horizontal

    def on_left_emg(self, *args, **kwargs):
        if self.mouse_mode:
            if self.horizontal:
                pyautogui.moveRel(-self.PY_AUTO_DISTANCE, 0, self.PY_AUTO_DURATION)
            else:
                pyautogui.moveRel(0, self.PY_AUTO_DISTANCE, self.PY_AUTO_DURATION)
        else:
            if self.horizontal:
                #left
                self.focus_col = max(0, self.focus_col - 1)
                pyautogui.moveRel(-self.PY_AUTO_DISTANCE, 0, self.PY_AUTO_DURATION)
                # special behavior for space button row
                effective_col = 0 if self.focus_row == len(self.buttons) - 1 else self.focus_col
                self.buttons[self.focus_row][effective_col].focus_set()
            else:
                #down
                self.focus_row = min(len(self.BUTTON_TEXTS) - 1, self.focus_row + 1)
                pyautogui.moveRel(0, self.PY_AUTO_DISTANCE, self.PY_AUTO_DURATION)
                # special behavior for space button row
                effective_col = 0 if self.focus_row == len(self.buttons) - 1 else self.focus_col
                self.buttons[self.focus_row][effective_col].focus_set()

    def on_right_emg(self, *args, **kwargs):
        if self.mouse_mode:
            if self.horizontal:
                pyautogui.moveRel(self.PY_AUTO_DISTANCE, 0, self.PY_AUTO_DURATION)
            else:
                pyautogui.moveRel(0, -self.PY_AUTO_DISTANCE, self.PY_AUTO_DURATION)
        else:
            if self.horizontal:
                #right
                self.focus_col = min(len(self.BUTTON_TEXTS[self.focus_row]) - 1, self.focus_col + 1)
                pyautogui.moveRel(self.PY_AUTO_DISTANCE, 0, self.PY_AUTO_DURATION)
                # special behavior for space button row
                effective_col = 0 if self.focus_row == len(self.buttons) - 1 else self.focus_col
                self.buttons[self.focus_row][effective_col].focus_set()
            else:
                #up
                self.focus_row = max(0, self.focus_row - 1)
                pyautogui.moveRel(0, -self.PY_AUTO_DISTANCE, self.PY_AUTO_DURATION)
                # special behavior for space button row
                effective_col = 0 if self.focus_row == len(self.buttons) - 1 else self.focus_col
                self.buttons[self.focus_row][effective_col].focus_set()

    def on_key_press(self, event):
        # modify focus row and column according to key input

        # handle keyboard arrows
        """
        if event.keysym == 'Up':
            self.focus_row = max(0, self.focus_row - 1)
            pyautogui.moveRel(0, -self.PY_AUTO_DISTANCE, self.PY_AUTO_DURATION)
        elif event.keysym == 'Down':
            self.focus_row = min(len(self.BUTTON_TEXTS) - 1, self.focus_row + 1)
            pyautogui.moveRel(0, self.PY_AUTO_DISTANCE, self.PY_AUTO_DURATION)
        elif event.keysym == 'Left':
            self.focus_col = max(0, self.focus_col - 1)
            pyautogui.moveRel(-self.PY_AUTO_DISTANCE, 0, self.PY_AUTO_DURATION)
        elif event.keysym == 'Right':
            self.focus_col = min(len(self.BUTTON_TEXTS[self.focus_row]) - 1, self.focus_col + 1)
            pyautogui.moveRel(self.PY_AUTO_DISTANCE, 0, self.PY_AUTO_DURATION)
        """

        print("event", event.keysym)

        # simulate left shoulder and right shoulder
        if event.keysym == 'Left':
            if self.horizontal:
                self.focus_col = max(0, self.focus_col - 1)
            else:
                self.focus_row = min(len(self.BUTTON_TEXTS) - 1, self.focus_row + 1)
        elif event.keysym == 'Right':
            if self.horizontal:
                self.focus_col = min(len(self.BUTTON_TEXTS[self.focus_row]) - 1, self.focus_col + 1)
            else:
                self.focus_row = max(0, self.focus_row - 1)
            
        # special behavior for space button row
        effective_col = 0 if self.focus_row == len(self.buttons) - 1 else self.focus_col

        # handle enter key
        if event.keysym == 'Return':
            self.buttons[self.focus_row][effective_col].invoke()

        # set focus according to new focus row and col
        self.buttons[self.focus_row][effective_col].focus_set()

    def display_buttons(self):
        # delete existing button objects
        for button_row in self.buttons:
            for button in button_row:
                button.destroy()
        self.buttons.clear()

        button_texts = self.BUTTON_TEXTS_SHIFT if self.is_shift else self.BUTTON_TEXTS
        # populate `buttons` list and grid with buttons of corresponding text
        for row in range(len(button_texts)):
            self.buttons.append([])
            for col in range(len(button_texts[row])):
                button_text = button_texts[row][col]
                command = lambda x = button_text: self.handle_button(x)
                if button_text == 'Space':
                    button = tkinter.Button(self.parent, text = button_text, width = 80, height = 4, 
                        bg = 'grey', fg = '#000000', relief = 'raised', padx = 4, pady = 4, bd = 4, 
                        font = ('arial', 12, 'bold'), command = command)
                    button.grid(row = 7, columnspan = 14)
                else:
                    button = tkinter.Button(self.parent, text = button_text, width = 5, height = 4, 
                        bg = 'grey', fg = '#000000', relief = 'raised', padx = 4, pady = 4, bd = 4, 
                        font = ('arial', 12, 'bold'), command = command)
                    button.grid(row = row + 3, column = col)
                self.buttons[row].append(button)

    def handle_button(self, value):
        if value == 'Delete':
            text = self.entry.get(1.0, tkinter.END)
            self.entry.delete(1.0, tkinter.END)
            self.entry.insert(tkinter.END, text[:-2])
        elif value == 'Space':
            self.entry.insert(tkinter.END, ' ')
        elif value == 'Tab':
            self.entry.insert(tkinter.END, '\t')
        elif value == 'Enter':
            self.entry.insert(tkinter.END, '\n')
        elif value == 'Shift':
            self.is_shift = not self.is_shift
            self.display_buttons()
        elif value == 'Cursor':
            self.toggle_cursor()
        elif value == 'Siri':
            os.popen('open /System/Applications/Siri.app')
        else:
            print("button", value)
            if value.isupper():
                with pyautogui.hold('shift'):
                    pyautogui.press(value.lower())
            else:
                pyautogui.press(value.lower())

            self.entry.insert(tkinter.END, value)
            
def main(dispatcher, events):
    root = tkinter.Tk()
    root.title('Keyboard')
    root['bg']='grey'
    root.resizable(0,0)
    root.wm_attributes("-topmost", "true")
    listener = KeyboardApplication(root)
    
    emitter = dispatcher
    emitter.bind(double_blink=listener.on_double_blink)
    emitter.bind(left_wink=listener.on_left_wink)
    emitter.bind(right_wink=listener.on_right_wink)
    emitter.bind(left_emg=listener.on_left_emg)
    # emitter.bind(right_emg=listener.on_right_emg)
    emitter.bind(right_emg=listener.on_left_wink)
    emitter.bind(triple_blink=listener.on_triple_blink)

    root.mainloop()
    
    
if __name__ == '__main__':
    main()