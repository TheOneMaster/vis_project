import tkinter as tk
from tkinter import ttk, font, filedialog, messagebox

import numpy as np
from pandas import read_csv
import re
from copy import deepcopy

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import wordcloud as wc

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
        style.layout("CustomNotebook", [
                     ("CustomNotebook.client", {"sticky": "nswe"})])
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
                                    ("CustomNotebook.label", {
                                     "side": "left", "sticky": ''}),
                                    ("CustomNotebook.close", {
                                     "side": "left", "sticky": ''}),
                                ]
                            })
                        ]
                    })
                ]
            })
        ])


class NotebookTab(ttk.Frame):

    def __init__(self, master, data, kind, options, labels, *args, **kwargs):
        super().__init__(master=master, **kwargs)

        plot_types = {
            'Barplot': self.barplot,
            'Wordcloud': self.wordcloud,
            'Icicle': self.icicle
        }

        # plot_types[kind](data, options)

        info = ttk.Frame(self, borderwidth=1, relief='sunken')
        info.pack(side=tk.BOTTOM, fill=tk.X)

        graph_type = f'Graph type: {kind}'
        info_label = ttk.Label(info, text=graph_type)
        info_label.pack(side=tk.LEFT)

        self.figure = plot_types[kind](data=data, options=options, labels=labels)

        title = labels['Title'].get()
        title = title if title != '' else None
        
        if title is not None:
            self.figure.suptitle(title)

        self.figure.set_tight_layout(True)

        canvas = FigureCanvasTkAgg(self.figure, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill='both', expand=True)
        
    def wordcloud(self, data, options, labels):
        figure = plt.Figure(figsize=(7, 5))
        groupby_column = options['Column'].get()

        # Data manipulation
        names = data.groupby(groupby_column).count().iloc[:, 0]
        names = names[names.index.str.match(r"^[a-zA-Z ']+$")]
        names = names.to_dict()

        self.wordcloud = wc.WordCloud(width=2100, height=1500).generate_from_frequencies(names)
        ax = figure.add_subplot()
        ax.imshow(self.wordcloud, interpolation='bilinear')
        ax.set_axis_off()

        return figure

    def barplot(self, data, options, labels):
        pass

    def icicle(self, data, options, labels):
        pass


class LabelFrameInput(ttk.LabelFrame):

    key = {
        'entry': ttk.Entry,
        'optionmenu': ttk.OptionMenu,
        'button': ttk.Button
    }

    def __init__(self, master, inputs, primary=None, **kwargs):
        command = kwargs.pop('command') if 'command' in kwargs else None

        super().__init__(master, **kwargs)
        self.is_data = False
        self.inputs = inputs

        if primary == 'graph_options':

            self.frames = {}
            self.values = {}

            frame = ttk.Frame(self)
            graph_options_lab = ttk.Label(frame, text='Graph Type', width=15)
            options = ['Barplot', 'Wordcloud', 'Line', 'Node', 'Icicle']
            self.graph_type = tk.StringVar()
            graph_options_opt = ttk.OptionMenu(
                frame, self.graph_type, options[0], *options, command=self.update)
            graph_options_lab.pack(side=tk.LEFT)
            graph_options_opt.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            frame.pack(side=tk.TOP, fill=tk.X, padx=5)

            for i in options:
                if i in inputs:
                    data = self.create_frame(inputs[i])
                    self.frames[i] = data[0]
                    self.values[i] = data[1]

            self.current = self.frames['Barplot']
            self.current.pack(side=tk.TOP, fill=tk.X, padx=5)

        else:

            if primary == 'data_input':
                frame = ttk.Frame(self)
                data_input = ttk.Button(frame, text='Select data file', command=command)
                data_input.pack(fill='both')
                frame.pack(side=tk.TOP, fill=tk.X, pady=5, padx=5)

            self.frames, self.values = self.create_frame(inputs)
            self.frames.pack(side=tk.TOP, fill=tk.X, padx=5)

    def create_frame(self, entries):

        frame_master = ttk.Frame(self)
        inputs = deepcopy(entries)
        entry_widget = {}

        for widget, kwargs in inputs:
            frame = ttk.Frame(frame_master)
            label_str = kwargs.pop('label')
            label = ttk.Label(frame, text=label_str, width=15, anchor='sw')

            if widget == 'optionmenu':
                stringvar = tk.StringVar()
                options = kwargs.pop('options')
                widget = self.key[widget](
                    frame, stringvar, options[0], *options, **kwargs)
                entry_widget[label_str] = stringvar

            elif widget == 'combo':
                pass
            else:
                widget = self.key[widget](frame, **kwargs)
                entry_widget[label_str] = widget

            if not self.is_data:
                widget.config(state='disabled')

            label.pack(side=tk.LEFT)
            widget.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            frame.pack(fill=tk.X, pady=5)

        return frame_master, entry_widget

    def update(self, name=None):

        if name is None:

            if type(self.frames) is dict:
                name = self.graph_type.get()
                self.values = {}

                for i in self.frames:
                    self.frames[i].destroy()
                    self.frames[i], self.values[i] = self.create_frame(
                        self.inputs[i])
                    if i == name:
                        self.current = self.frames[i]
                        self.current.pack(side=tk.TOP, fill=tk.X, padx=5)

            else:
                self.frames.destroy()
                self.frames, self.values = self.create_frame(self.inputs)
                self.frames.pack(side=tk.TOP, fill=tk.X, padx=5)

        else:
            self.current.pack_forget()

            if name in self.frames:
                self.current = self.frames[name]
                self.current.pack(side=tk.TOP, fill=tk.X, padx=5)


class MainWindow(ttk.Frame):

    def __init__(self, master, **kw):
        """ Creates the frame for the main window of the application. It consists of 3 subframes: 
        The left frame(input), midframe(plots), and the right frame(output)
        """
        super().__init__(master, **kw)

        self.left_frame = ttk.Frame(self)
        self.mid_frame = ttk.Frame(self)
        self.right_frame = ttk.Frame(self)
        self.data = None

        """
        Left frame widgets
        """
        # Data entry

        input_options = [('entry', {'label': 'test'})]

        self.data_input = LabelFrameInput(
            self.left_frame, input_options, 'data_input', command=self.get_data, text='Data entry and preprocessing')

        # Graph Options
        barplot_widgets = [('optionmenu', {'label': 'Column', 'options': ['Not available']}),
                           ('entry', {'label': '# of categories'})]

        wordcloud_widgets = [
            ('optionmenu', {'label': 'Column', 'options': ['Not available']})]

        graph_options = {
            'Barplot': barplot_widgets,
            'Wordcloud': wordcloud_widgets
        }
        self.graph_options = LabelFrameInput(
            self.left_frame, graph_options, text='Graph Options', primary='graph_options')

        # Plot labels
        plot_labels = [('entry', {'label': 'Title'}), ('entry', {'label': 'Subtitle'}), ('entry', {
            'label': 'Y Label'}), ('entry', {'label': 'X Label'})]
        self.plot_labels = LabelFrameInput(
            self.left_frame, plot_labels, text='Graph Labels')

        plot_btn = ttk.Button(self.left_frame, text='Plot', command=self.plot)
        plot_btn.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.data_input.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.plot_labels.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        self.graph_options.pack(side=tk.TOP, fill='both',
                                expand=True, padx=5, pady=5)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        """
        Middle frame widgets
        """
        # Notebook
        self.notebook = CustomNotebook(self.mid_frame)
        self.notebook.bind("<<NotebookTabClosed>>", self.check_tabs)
        self.notebook.pack(fill='both', expand=True)

        self.mid_frame.pack(side=tk.LEFT, fill='both', expand=True)

    def get_data(self):

        try:
            file_types = [('CSV files', '.csv')]
            filename = filedialog.askopenfilename(filetypes=file_types)

            with open(filename, 'r', encoding='utf-8') as data_file:
                data = read_csv(data_file)
                self.data = data
 
            df_columns = data.columns

            barplot_widgets = [('optionmenu', {'label': 'Column', 'options': df_columns}),
                               ('entry', {'label': '# of categories'})]

            wordcloud_widgets = [
                ('optionmenu', {'label': 'Column', 'options': df_columns})]

            self.graph_options.inputs = {
                'Barplot': barplot_widgets,
                'Wordcloud': wordcloud_widgets
            }

            self.data_input.is_data = True
            self.graph_options.is_data = True
            self.plot_labels.is_data = True

            messagebox.showinfo(title='Data entry', message='File has been read.')

            self.data_input.update()
            self.graph_options.update()
            self.plot_labels.update()

        except FileNotFoundError:
            title = 'Data entry'
            message = 'File was not selected properly. Please select file properly.'
            messagebox.showerror(title=title, message=message)
            
        except:
            title = 'Unknown Error'
            message = 'If you are seeing this, I don\'t know how you got here'
            messagebox.showerror(title=title, message=message)

    def plot(self):
        
        if self.data is None:
            title = 'No Data'
            message = 'There is no data provided to the application.'
            messagebox.showerror(title=title, message=message)
        else:
            kind = self.graph_options.graph_type.get()
            options = self.graph_options.values[kind]
            labels = self.plot_labels.values

            frame = NotebookTab(self.notebook, data=self.data, kind=kind, options=options, labels=labels)
            print(frame)
            title = labels['Title'].get()
            title = title if title != '' else f'graph {len(self.notebook.tabs()) + 1}'
            title = f'{kind} - {title}'
            self.notebook.add(frame, text=title)
            self.notebook.select(frame)

    def check_tabs(self, event):
        tabs = self.notebook.tabs()
        num = len(tabs)

        if num > 0:

            self.notebook.pack(fill='both', expand=True)
        else:
            self.notebook.pack_forget()

def main():
    root = tk.Tk()
    root.title('GUI Implementation')
    root.geometry('1200x500')

    window_1 = MainWindow(root)
    window_1.pack(expand=True, fill='both')

    root.mainloop()

if __name__ == "__main__":
    main()
