import tkinter
import pyautogui

class KeyboardApplication():
    BUTTON_TEXTS = [
        ['`','1','2','3','4','5','6','7','8','9','0','-','=','Delete'],
        ['Tab','q','w','e','r','t','y','u','i','o','p','[',']','\\',],
        ['Shift','a','s','d','f','g','h','j','k','l',';',"'",'Enter'],
        ['z','x','c','v','b','n','m',',','.','/'],
        ['Space']
    ]
    BUTTON_TEXTS_SHIFT = [
        ['~','!','@','#','$','%','^','&','*','(',')','-','=','Delete'],
        ['Tab','Q','W','E','R','T','Y','U','I','O','P','{','}','|'],
        ['Shift','A','S','D','F','G','H','J','K','L',':','"','Enter'],
        ['Z','X','C','V','B','N','M','<','>','?'],
        ['Space']
    ]

    def __init__(self, parent):
        self.parent = parent
        self.label = tkinter.Label(parent, text='Keyboard', font=('arial', 30, 'bold'), bg='grey') 
        self.label.grid(row = 0, columnspan = 15)
        self.entry = tkinter.Text(parent, width = 100, height = 10, font = ('arial', 20, 'bold'))
        self.entry.grid(row = 1, columnspan = 15)
        self.focus_row = 0
        self.focus_col = 0
        self.is_shift = False
        self.buttons = []

        self.display_buttons()
        self.buttons[0][0].focus_set()
        self.parent.bind('<KeyPress>', self.onKeyPress)

    def onKeyPress(self, event):
        if event.keysym == 'Up':
            self.focus_row = max(0, self.focus_row - 1)
            pyautogui.moveRel(0, -75, duration = 1)
        elif event.keysym == 'Down':
            self.focus_row = min(len(self.BUTTON_TEXTS) - 1, self.focus_row + 1)
            pyautogui.moveRel(0, 75, duration = 1)
        elif event.keysym == 'Left':
            self.focus_col = max(0, self.focus_col - 1)
            pyautogui.moveRel(-75, 0, duration = 1)
        elif event.keysym == 'Right':
            self.focus_col = min(len(self.BUTTON_TEXTS[self.focus_row]) - 1, self.focus_col + 1)
            pyautogui.moveRel(75, 0, duration = 1)
        
        if self.focus_row == 3:
            self.buttons[self.focus_row][0].focus_set()
        else:
            self.buttons[self.focus_row][self.focus_col].focus_set()

    def display_buttons(self):
        self.buttons.clear()
        button_texts = self.BUTTON_TEXTS_SHIFT if self.is_shift else self.BUTTON_TEXTS
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
        else:
            self.entry.insert(tkinter.END, value)
            
def main():
    root = tkinter.Tk()
    root.title('Keyboard')
    root['bg']='grey'
    root.resizable(0,0)
    KeyboardApplication(root)
    root.mainloop()

if __name__ == '__main__':
    main()

