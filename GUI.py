# Random imports
import numpy as np
import pickle
import re
import pandas as pd

# Tkinter imports
import tkinter as tk
from tkinter import ttk, font, filedialog, messagebox
from PIL import ImageTk, Image

# Matplotlib libraries
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as anim


class CustomNotebook(ttk.Notebook):
    """A ttk Notebook with close buttons on each tab"""

    __initialized = False

    def __init__(self, *args, **kwargs):
        if not self.__initialized:
            self.__initialize_custom_style()
            self.__inititialized = True

        kwargs["style"] = "CustomNotebook"
        ttk.Notebook.__init__(self, *args, **kwargs)

        self._active = None

        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)

    def on_close_press(self, event):
        """Called when the button is pressed over the close button"""

        element = self.identify(event.x, event.y)

        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(['pressed'])
            self._active = index

    def on_close_release(self, event):
        """Called when the button is released over the close button"""
        if not self.instate(['pressed']):
            return

        element = self.identify(event.x, event.y)
        index = self.index("@%d,%d" % (event.x, event.y))

        if "close" in element and self._active == index:
            self.forget(index)
            self.event_generate("<<NotebookTabClosed>>")

        self.state(["!pressed"])
        self._active = None

    def __initialize_custom_style(self):
        style = ttk.Style()
        self.images = (
            tk.PhotoImage("img_close", data='''
                R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
                '''),
            tk.PhotoImage("img_closeactive", data='''
                R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAA
                AAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs=
                '''),
            tk.PhotoImage("img_closepressed", data='''
                R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
            ''')
        )

        style.element_create("close", "image", "img_close",
                             ("active", "pressed", "!disabled", "img_closepressed"),
                             ("active", "!disabled", "img_closeactive"), border=8, sticky='')
        style.layout("CustomNotebook", [("CustomNotebook.client", {"sticky": "nswe"})])
        style.layout("CustomNotebook.Tab", [
            ("CustomNotebook.tab", {
                "sticky": "nswe",
                "children": [
                    ("CustomNotebook.padding", {
                        "side": "top",
                        "sticky": "nswe",
                        "children": [
                            ("CustomNotebook.focus", {
                                "side": "top",
                                "sticky": "nswe",
                                "children": [
                                    ("CustomNotebook.label", {"side": "left", "sticky": ''}),
                                    ("CustomNotebook.close", {"side": "left", "sticky": ''}),
                                ]
                            })
                        ]
                    })
                ]
            })
        ])


class NotebookTab(tk.Frame):

    def __init__(self, parent, title, graph_type):
        """Creates a tab for the custom Notebook.

         Variables
         parent: A CustomNotebook Instance
         title:  The title for the tab
         graph_type: String representation of the type of graph (ex: bar)
         """
        tk.Frame.__init__(self, parent)
        self.title = title
        self.graph_type = graph_type

        # Graph info
        info = tk.Frame(self, borderwidth=1, relief='sunken')
        info.pack(side=tk.BOTTOM, fill='both')
        info_label = ttk.Label(info, text=graph_type, font='Times 12')
        info_label.pack(side=tk.LEFT)

        # Save graph
        save_image = Image.open('Images/save.png')
        save_image = ImageTk.PhotoImage(save_image)
        graph_save = ttk.Button(info, image=save_image)
        graph_save.image = save_image
        graph_save.pack(side=tk.RIGHT)

    def plot(self, data):

        names = data.groupby('FirstName')['Lastname'].count().nlargest(10)
        fig, ax = plt.subplots(figsize=(7, 5))
        names.plot(kind='bar', ax=ax, title=self.title)
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, expand=True, fill='both')


class CustomProgressBar(tk.Toplevel):

    def __init__(self):
        tk.Toplevel.__init__(self)
        progress_bar = ttk.Progressbar(self, mode='indeterminate')




class Window1:
    values = ["Johannes", "Johanna", "Maria", "Cornelis", "Adriana", "Petronella", "Cornelia", "Anna Maria",
              "Johanna Maria", "Adrianus"]

    with open('names.pickle', 'rb') as names:
        all_names = pickle.load(names)
        all_names = np.array(all_names)

    def __init__(self, parent):

        # Instance variables
        self.parent = parent
        self.titleFont = font.Font(family='Helvetica', size=18, weight=font.BOLD, underline=1)
        self.data = None

        # Frame Stuff
        self.left_frame = self.leftFrame()
        self.mid_frame = self.midFrame()
        self.right_frame = self.rightFrame()

        self.left_frame.pack(side=tk.LEFT, fill='both')
        self.mid_frame.pack(side=tk.LEFT, fill='both', expand=True)
        self.right_frame.pack(side=tk.LEFT, fill='both')

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

        left_frame = tk.Frame(self.parent, borderwidth=1)

        # Title (Top of Frame)
        title_frame = ttk.Frame(left_frame)
        title_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        title = ttk.Label(title_frame, text="Input", font=self.titleFont)
        title.pack()

        # Get Data
        data_button = ttk.Button(left_frame, command=self.get_data, text='Input data file')
        data_button.pack(side=tk.TOP)

        # Plot Button (Bottom of Frame)
        plt_button = ttk.Button(left_frame, text='PLOT', command=self.plot)
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
        self.graph_type = ttk.OptionMenu(select_frame, graph_name, graph_list[0], *graph_list)
        self.graph_type.pack(fill=tk.X, pady=5, ipady=5)

        # Select Names
        select_names_frame = tk.Frame(plot_options_frame)
        select_names_frame.pack(side=tk.TOP, fill='both')
        select_names_label = ttk.Label(select_names_frame, text='Select Name')
        select_names_label.pack(side=tk.LEFT, padx=5)
        self.text_val = tk.StringVar()
        self.entry = ttk.Combobox(select_names_frame, textvariable=self.text_val, values=self.values)
        self.entry.pack(side=tk.LEFT, fill=tk.X, padx=5)
        self.entry.bind('<KeyRelease>', self.update)

        # Change Plot Labels
        change_labels = ttk.Button(plot_options_frame, text='Change Labels', command=self.label_info)
        change_labels.pack(side=tk.BOTTOM, padx=5, pady=10)

        return left_frame

    def midFrame(self):

        mid_frame = tk.Frame(self.parent, borderwidth=2, relief='sunken')
        label = ttk.Label(mid_frame, text='Plots', font=self.titleFont)
        label.place(x=100, width=100)

        # Notebook stuff
        self.graph_notebook = CustomNotebook(mid_frame)
        self.graph_notebook.pack(fill='both', expand=True)

        a = NotebookTab(self.graph_notebook, 'test_1', 'bar')
        self.graph_notebook.add(a)

        return mid_frame

    def rightFrame(self):

        right_frame = tk.Frame(self.parent, borderwidth=1)

        # Title
        title_frame = tk.Frame(right_frame, borderwidth=1)
        title_frame.pack(side=tk.TOP, fill='both', expand=True)
        title = ttk.Label(title_frame, text="Output", font=self.titleFont)
        title.pack()

        return right_frame

    def label_info(self):

        window = tk.Toplevel()
        self.plot_title = tk.Entry(window)
        self.plot_title.pack()

        set_button = ttk.Button(window, text="Save and Exit", command=window.destroy)
        set_button.pack()

    def plot(self):

        if self.data is None:
            error_message = """There is no data provided to the application."""
            messagebox.showerror('Data', error_message)
        else:
            title = 'test 2'
            tab = NotebookTab(self.graph_notebook, title=title, graph_type='hist')
            tab.plot(self.data)
            self.graph_notebook.add(tab, text=title)
            print(self.graph_notebook.index('test'))

    def get_data(self):

        file_name = filedialog.askopenfilename()

        with open(file_name, 'r', encoding='latin-1') as data_file:
            df = pd.read_csv(data_file)

        self.data = df

def main():
    # Root Window Configuration
    root = tk.Tk()
    root.title('GUI Implementation')
    # root.geometry('1200x500')
    root.update()
    # root.resizable(False, False)

    Window1(root)
    root.mainloop()


if __name__ == "__main__":
    main()
