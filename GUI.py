# Random imports
import numpy as np
import pickle
import re
import pandas as pd
import os

# Tkinter imports
import tkinter as tk
from tkinter import ttk, font, filedialog, messagebox
from PIL import ImageTk, Image

# Matplotlib libraries
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as anim


# Custom Tkinter Widgets
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

    def __init__(self, parent, entry):
        """Creates a tab for the custom Notebook.

         Variables
         parent: A CustomNotebook Instance
         title:  The title for the tab
         graph_type: String representation of the type of graph (ex: bar)
         """
        tk.Frame.__init__(self, parent)
        self.entries = entry
        self.title = entry['Title'].get()
        self.graph_type = entry['graph type'].get()

        # Graph info
        info = tk.Frame(self, borderwidth=1, relief='sunken')
        info.pack(side=tk.BOTTOM, fill='both')
        graph_type = f"Graph type: {self.graph_type}"
        info_label = ttk.Label(info, text=graph_type, font='Times 12')
        info_label.pack(side=tk.LEFT)

        # Save graph
        save_image = Image.open('Images/save.png')
        save_image = ImageTk.PhotoImage(save_image)
        graph_save = ttk.Button(info, image=save_image, command=self.save)
        graph_save.image = save_image
        graph_save.pack(side=tk.RIGHT)

    def plot(self, data, mode, *kwargs):
        names = data.groupby('FirstName')['Lastname'].count().nlargest(10)
        self.fig, ax = plt.subplots(figsize=(7, 5))
        names.plot(kind='bar', ax=ax, title=self.title)
        xlab = self.entries['X Label'].get()
        ylab = self.entries['Y Label'].get()
        ax.set_xlabel()
        ax.set_ylabel()
        self.fig.tight_layout()
        canvas = FigureCanvasTkAgg(self.fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, expand=True, fill='both')

    def save(self):
        file_types = [('JPEG file', '.jpg'), ('PNG file', '.png')]

        filename = filedialog.asksaveasfilename(title='Select file name',
                                                filetypes=file_types)
        self.fig.savefig(filename)

        # except:
        #     pass


# Window classes
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
        self.entries = None

        # Frame Stuff
        self.left_frame = self.leftFrame()
        self.mid_frame = self.midFrame()
        self.right_frame = self.rightFrame()

        self.left_frame.pack(side=tk.LEFT, fill='both')
        self.mid_frame.pack(side=tk.LEFT, fill='both', expand=True)
        self.right_frame.pack(side=tk.LEFT, fill='both')

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

        # Change plot label
        plot_label_frame = ttk.LabelFrame(plot_options_frame, text='Labels', height=100)
        plot_label_frame.pack(side=tk.BOTTOM, fill='both', pady=5, padx=1)

        self.entries = self.label_entries(plot_label_frame)

        # Select Graph Type
        select_frame = tk.Frame(plot_options_frame, borderwidth=1)
        select_frame.pack(side=tk.TOP, fill=tk.X, padx=40, pady=20)
        label_names = ttk.Label(select_frame, text='Select graph type', borderwidth=1, font=('Comic Sans', 11))
        label_names.pack(side='top')
        graph_list = ["Hist", "Node", "Line"]
        graph_name = tk.StringVar()
        graph_type = ttk.OptionMenu(select_frame, graph_name, graph_list[0], *graph_list)
        graph_type.pack(fill=tk.X, pady=5, ipady=5)
        self.entries['graph type'] = graph_name

        # Select Names
        select_names_frame = tk.Frame(plot_options_frame)
        select_names_frame.pack(side=tk.TOP, fill='both')
        select_names_label = ttk.Label(select_names_frame, text='Select Name')
        select_names_label.pack(side=tk.LEFT, padx=5)
        text_val = tk.StringVar()
        entry = ttk.Combobox(select_names_frame, textvariable=text_val, values=self.values)
        entry.pack(side=tk.LEFT, fill=tk.X, padx=5)
        entry.bind('<KeyRelease>', lambda event: self.update(text_val, entry))
        self.entries['name'] = text_val

        # entries =

        # Change Plot Labels
        # change_labels = ttk.Button(plot_options_frame, text='Change Labels', command=self.label_info)
        # change_labels.pack(side=tk.BOTTOM, padx=5, pady=10)

        return left_frame

    def midFrame(self):

        mid_frame = tk.Frame(self.parent, borderwidth=2, relief='sunken')
        label = ttk.Label(mid_frame, text='Plots', font=self.titleFont)
        label.place(x=100, width=100)

        # Notebook stuff
        self.graph_notebook = CustomNotebook(mid_frame)
        self.graph_notebook.pack(fill='both', expand=True)

        a = tk.Frame(self.graph_notebook)
        self.graph_notebook.add(a, text='Introduction')

        return mid_frame

    def rightFrame(self):

        right_frame = tk.Frame(self.parent, borderwidth=1)

        # Title
        title_frame = tk.Frame(right_frame, borderwidth=1)
        title_frame.pack(side=tk.TOP, fill='both', expand=True)
        title = ttk.Label(title_frame, text="Output", font=self.titleFont)
        title.pack()

        return right_frame

    def update(self, stringvar, entrybox):
        """ Update the names available in the dropdown box for the names. Return the top 10 names that match the
        input. """

        val = stringvar.get()
        entrybox['values'] = self.getnames(val)

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

    def label_entries(self, parent):

        return_dict = {}
        entries = ['Title', 'X Label', 'Y Label']

        for entry in entries:
            row = tk.Frame(parent)
            lab = ttk.Label(row, width=15, text=entry, anchor='w')
            ent = ttk.Entry(row)
            row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            lab.pack(side=tk.LEFT)
            ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
            return_dict[entry] = ent

        return return_dict

    def plot(self):

        if self.data is None:
            error_message = """There is no data provided to the application."""
            messagebox.showerror('Data', error_message)
        else:
            tab = NotebookTab(self.graph_notebook, entry=self.entries)
            tab.plot(self.data, mode='')
            self.graph_notebook.add(tab, text=self.entries['Title'].get())
            self.graph_notebook.select(tab)

    def get_data(self):

        try:
            file_types = [('CSV file', '.csv')]
            file_name = filedialog.askopenfilename(filetypes=file_types)

            with open(file_name, 'r', encoding='latin-1') as data_file:
                df = pd.read_csv(data_file)

            self.data = df
            file_name = os.path.basename(file_name)
            title = "Reading data"
            message = f"The file ({file_name}) has been read."
            messagebox.showinfo(title, message)

        except FileNotFoundError:
            pass


def main():
    # Root Window Configuration
    root = tk.Tk()
    root.title('GUI Implementation')
    root.geometry('1200x500')
    root.update()
    # root.resizable(False, False)

    Window1(root)
    root.mainloop()


if __name__ == "__main__":
    main()
