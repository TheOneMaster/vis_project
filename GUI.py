import tkinter as tk
from tkinter import ttk, font
from PIL import ImageTk, Image
import numpy as np
import pickle
import re


class Window1:

    values = ["Johannes", "Johanna", "Maria", "Cornelis", "Adriana", "Petronella", "Cornelia", "Anna Maria",
              "Johanna Maria", "Adrianus"]
    with open('names.pickle', 'rb') as names:
        all_names = pickle.load(names)
        all_names = np.array(all_names)

    def __init__(self, parent):

        self.parent = parent
        self.titleFont = font.Font(family='Helvetica', size=18, weight=font.BOLD, underline=1)

        # Frame Stuff
        self.leftFrame()
        self.midFrame()
        self.rightFrame()

    def update(self, e):
        """ Update the names available in the dropdown box for the names. Return the top 10 names that match the
        input. """

        val = self.text_val.get()
        self.entry['values'] = self.getnames(val)

    def getnames(self, val):

        if val == '':
            return self.values

        else:
            regex = re.compile(f'{val}')
            values = list(filter(regex.match, self.all_names))
            if len(values) > 10:
                values = values[0:10]
                return values

            elif len(values) == 0:
                regex = re.compile(f'[{val}]')
                values = list(filter(regex.match, self.all_names))

                if len(values) > 10:
                    values = values[0:10]

                return values

    def leftFrame(self):
        """ Creates the left Frame for the input and the widgets to be placed in it"""

        left_frame = tk.Frame(self.parent, height=500, width=250, borderwidth=1)
        left_frame.pack(side=tk.LEFT, fill='both')

        # Title (Top of Frame)
        title_frame = ttk.Frame(left_frame)
        title_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        title = ttk.Label(title_frame, text="Input", font=self.titleFont)
        title.pack()

        # Plot Button (Bottom of Frame)
        plt_button = ttk.Button(left_frame, text='PLOT')
        plt_button.pack(side=tk.BOTTOM, fill=tk.X)

        # Plot options (Middle of Frame)
        plot_options_frame = tk.Frame(left_frame)
        plot_options_frame.pack(side=tk.BOTTOM, fill='both', expand=True)

        # Select Graph Type
        select_frame = tk.Frame(plot_options_frame, borderwidth=1)
        select_frame.pack(side=tk.TOP, fill=tk.X, padx=40, pady=20)
        label_names = ttk.Label(select_frame, text='Select graph type', borderwidth=1, font=('Comic Sans', 11))
        label_names.pack(side='top')
        graph_list = ['Node', "Hist", "Line"]
        graph_name = tk.StringVar()
        graph_box = ttk.OptionMenu(select_frame, graph_name, graph_list[0], *graph_list)
        graph_box.pack(fill=tk.X, pady=5, ipady=5)

        # Select Names
        select_names_frame = tk.Frame(plot_options_frame)
        select_names_frame.pack(side=tk.TOP, fill='both')

        select_names_label = ttk.Label(select_names_frame, text='Select Name')
        select_names_label.pack(side=tk.LEFT)
        self.text_val = tk.StringVar()
        self.entry = ttk.Combobox(select_names_frame, textvariable=self.text_val, values=self.values)
        self.entry.pack(side=tk.LEFT, fill=tk.X, padx=5)
        self.entry.bind('<KeyRelease>', self.update)

    def midFrame(self):
        mid_frame = tk.Frame(self.parent, height=500, width=500, borderwidth=1, relief='sunken')
        mid_frame.pack(side=tk.LEFT, fill='both', expand=True)

        # Notebook stuff
        graph_main = ttk.Notebook(mid_frame)
        graph_main.pack(fill='both', expand=True)

        # Page 1 (In notebook)
        page1 = ttk.Frame(graph_main)
        graph1_image = Image.open('Images/living.jpg')
        graph1_tkimage = ImageTk.PhotoImage(graph1_image, width=500)
        graph1 = tk.Label(page1, image=graph1_tkimage)
        graph1.image = graph1_tkimage
        graph1.pack(expand=True, fill='both')
        graph_main.add(page1, text='Population per year')

        # Page 2 (In notebook)
        page2 = ttk.Frame(graph_main)
        graph2_image = ImageTk.PhotoImage(Image.open('Images/death.jpg'))
        graph2 = tk.Label(page2, image=graph2_image)
        graph2.image = graph2_image
        graph2.pack(expand=True, fill='both')
        graph_main.add(page2, text='Deaths per year')

        # Graph info
        info = tk.Frame(mid_frame, borderwidth=1, relief='sunken')
        info.pack(side=tk.BOTTOM, fill='both')

        info_label = ttk.Label(info, text='Graph Type', font='Times 12')
        info_label.pack(side=tk.LEFT)

        # Save graph
        save_image = Image.open('Images/save.png')
        save_image = ImageTk.PhotoImage(save_image)
        graph_save = ttk.Button(info, image=save_image)
        graph_save.image = save_image
        graph_save.pack(side=tk.RIGHT)

    def rightFrame(self):

        right_frame = tk.Frame(self.parent, height=500, width=250, borderwidth=1)
        right_frame.pack(side=tk.LEFT, fill='both', expand=True)

        # Title
        title_frame = tk.Frame(right_frame, borderwidth=1)
        title_frame.pack(side=tk.TOP, fill='both', expand=True)
        title = ttk.Label(title_frame, text="Output", font=self.titleFont)
        title.pack()

    def save_graph(self):
        pass


def main():

    # Root Window Configuration
    root = tk.Tk()
    root.title('GUI Implementation')
    root.geometry('1200x500')
    root.update()
    root.resizable(False, False)

    Window1(root)
    root.mainloop()


if __name__ == "__main__":
    main()
