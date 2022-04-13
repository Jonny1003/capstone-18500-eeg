import tkinter as tk
import cortex.cortex as cortex 

CANVAS_WIDTH = 400
CANVAS_HEIGHT = 400
CIRCLE_WIDTH = 50
CIRCLE_HEIGHT = 50



def update_position(event):



if __name__=='__main__':
    # setup cortex to read facial expression data
    cortex_instance = cortex.Cortex()


    # setup output interface
    root = tk.Tk()
    mainframe = tk.Frame(root)
    
    interface = tk.Canvas(mainframe, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg='cyan')
    interface.create_oval(175,175,225,225, fill='light green')

    interface.pack()
    mainframe.pack()


    root.mainloop()
