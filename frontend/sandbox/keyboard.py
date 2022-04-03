import tkinter
import pyautogui
import os
from pydispatch import Dispatcher

"""
class FeaturePredictor(Dispatcher):
    _events_ = ['double_blink', 'left_wink', 'right_wink']
    def do_predict(self):
        model = kwargs.get('model')
        signalling_cond = kwargs.get('cond')
        while True:
            signalling_cond.acquire()
            signalling_cond.wait()
            signalling_cond.release()
            # do model prediction

            # idk
            prediction = model.get_prediction(...)

            if (prediction == 'double_blink'):
                self.emit('double_blink', data=data)
            if (prediction == 'left_wink'):
                self.emit('left_wink', data=data)
            if (prediction == 'right_wink'):
                self.emit('right_wink', data=data)
"""

# # trying to open application on chrome
# import webbrowser

# url = 'http://docs.python.org/'
# chrome_path = 'open -a /Applications/Google\ Chrome.app %s'

# webbrowser.get(chrome_path).open(url)


class KeyboardApplication():
    BUTTON_TEXTS = [
        ['`','1','2','3','4','5','6','7','8','9','0','-','=','Delete'],
        ['Tab','q','w','e','r','t','y','u','i','o','p','[',']','\\',],
        ['Shift','a','s','d','f','g','h','j','k','l',';',"'",'Enter'],
        ['z','x','c','v','b','n','m',',','.','/','Cursor','Siri'],
        ['Space']
    ]
    BUTTON_TEXTS_SHIFT = [
        ['~','!','@','#','$','%','^','&','*','(',')','-','=','Delete'],
        ['Tab','Q','W','E','R','T','Y','U','I','O','P','{','}','|'],
        ['Shift','A','S','D','F','G','H','J','K','L',':','"','Enter'],
        ['Z','X','C','V','B','N','M','<','>','?','Cursor','Siri'],
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
        self.focus_row = 0
        self.focus_col = 0
        self.is_shift = False # whether the shift modifier is active
        
        self.display_cursor = False # initialize display_cursor
        self.set_cursor(True) # set display_cursor value
        
        self.horizontal = False # default mapping for shoulder directions

        # initialize buttons
        self.display_buttons()
        self.buttons[0][0].focus_set()
        self.parent.bind('<KeyPress>', self.on_key_press)

    def on_double_blink(self, *args, **kwargs):
        # special behavior for space button row
        effective_col = 0 if self.focus_row == len(self.buttons) - 1 else self.focus_col
        self.buttons[self.focus_row][effective_col].invoke()

    PY_AUTO_DISTANCE = 0
    PY_AUTO_DURATION = 0.5

    def on_left_wink(self, *args, **kwargs):
        """
        self.focus_col = max(0, self.focus_col - 1)
        pyautogui.moveRel(-self.PY_AUTO_DISTANCE, 0, self.PY_AUTO_DURATION)
        # special behavior for space button row
        effective_col = 0 if self.focus_row == len(self.buttons) - 1 else self.focus_col
        self.buttons[self.focus_row][effective_col].focus_set()
        """
        os.popen('open /System/Applications/Siri.app')

    # move right
    def on_right_wink(self, *args, **kwargs):
        """
        self.focus_col = min(len(self.BUTTON_TEXTS[self.focus_row]) - 1, self.focus_col + 1)
        pyautogui.moveRel(self.PY_AUTO_DISTANCE, 0, self.PY_AUTO_DURATION)
        # special behavior for space button row
        effective_col = 0 if self.focus_row == len(self.buttons) - 1 else self.focus_col
        self.buttons[self.focus_row][effective_col].focus_set()
        """
        self.horizontal = not self.horizontal

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

    def set_cursor(self, val):
        self.display_cursor = val
        if self.display_cursor:
            self.parent.config(cursor='left_ptr')
            self.entry.config(cursor='xterm')
        else:
            self.parent.config(cursor='none')
            self.entry.config(cursor='none')
        
    def toggle_cursor(self):
        self.set_cursor(not self.display_cursor)

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
            self.entry.insert(tkinter.END, value)
            
def main(dispatcher):
    root = tkinter.Tk()
    root.title('Keyboard')
    root['bg']='grey'
    root.resizable(0,0)
    root.wm_attributes("-topmost", "true")
    listener = KeyboardApplication(root)
    root.mainloop()

    
    emitter = dispatcher

    emitter.bind(double_blink=listener.on_double_blink)
    emitter.bind(left_wink=listener.on_left_wink)
    emitter.bind(right_wink=listener.on_right_wink)
    
    
if __name__ == '__main__':
    main()
