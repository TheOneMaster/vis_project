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

        left_frame = tk.Frame(self.parent, height=500, width=250, borderwidth=1)
        left_frame.pack(side=tk.LEFT, fill='both')

        # Title
        title_frame = ttk.Frame(left_frame)
        title_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        title = ttk.Label(title_frame, text="Input", font=self.titleFont)
        title.pack()

        # Plot Button
        plt_button = ttk.Button(left_frame, text='PLOT')
        plt_button.pack(side=tk.BOTTOM, fill=tk.X)

        # Plot options
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


        # Textbox for names
        # self.text_val = tk.StringVar()
        # self.entry = ttk.Combobox(select_frame, textvariable=self.text_val, values=self.values)
        # self.entry.pack(fill=tk.X)
        # self.entry.bind('<KeyRelease>', self.update)

    def midFrame(self):
        mid_frame = tk.Frame(self.parent, height=500, width=500, borderwidth=1, relief='sunken')
        mid_frame.pack(side=tk.LEFT, fill='both')

        # Notebook stuff
        graph_main = ttk.Notebook(mid_frame)
        graph_main.pack(fill='both', expand=True)
        page1 = ttk.Frame(graph_main)
        graph1_image = Image.open('Images/NASDAQ-composite.png')
        graph1_tkimage = ImageTk.PhotoImage(graph1_image, width=500)
        graph1 = tk.Label(page1, image=graph1_tkimage)
        graph1.image = graph1_tkimage
        graph1.pack(expand=True, fill='both')
        graph_main.add(page1, text='Graph 1')

        # Graph info
        info = tk.Frame(mid_frame, borderwidth=1, relief='sunken')
        info.pack(side=tk.BOTTOM, fill='both')

        info_label = ttk.Label(info, text='Graph Type', font='Times 12')
        info_label.pack(side=tk.LEFT)

        # Save graph
        graph_save = ttk.Button(info, text='Save')
        graph_save.pack(side=tk.RIGHT)

    def rightFrame(self):

        right_frame = tk.Frame(self.parent, height=500, width=250, borderwidth=1)
        right_frame.pack(side=tk.LEFT, fill='both')

        # Title
        title_frame = ttk.Frame(right_frame, borderwidth=1)
        title_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        title = ttk.Label(title_frame, text="Output", font=self.titleFont)
        title.pack()

    def save_graph(self):
        pass


def main():
    root = tk.Tk()

    root.title('GUI Implementation')
    root.geometry('1200x500')
    root.update()



    Window1(root)
    root.mainloop()


if __name__ == "__main__":
    main()
