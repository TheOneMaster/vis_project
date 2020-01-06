import tkinter as tk
from tkinter import ttk, font, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from copy import deepcopy

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

    def __init__(self, master, notebook, data, kind, options, labels, *args, **kwargs):
        super().__init__(master=master, **kwargs)

        self.is_empty = True
        self.is_wordcloud = False

        plot_types = {
            'Barplot': self.barplot,
            'Wordcloud': self.wordcloud,
            'Icicle': self.icicle
        }

        figure = plot_types[kind](data=data, options=options, labels=labels)

        if figure is None:
            pass
        else:
            self.is_empty = False
            title = labels['Title'].get()
            title = title if title != '' else None

            if title is not None:
                figure.suptitle(title)

            figure.set_tight_layout(True)

            canvas = FigureCanvasTkAgg(figure, master=self)
            # canvas.get_tk_widget().pack(side=tk.TOP, fill='both', expand=True)

            toolbar_kwargs = {
                'canvas': canvas,
                'window': self,
                'figure': figure
            }
            
            if self.is_wordcloud:
                toolbar_kwargs['figure'] = self.wordcloud
            
            toolbar = CustomToolbar(**toolbar_kwargs)
            toolbar.update()

            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill='both', expand=True)

    def wordcloud(self, data, options, labels):
        self.is_wordcloud = True
        figure = plt.Figure(figsize=(7, 5))
        groupby_column = options['Column'].get()

        # Data manipulation
        try:
            names = data.groupby(groupby_column).count().iloc[:, 0]
            names = names[names.index.str.match(r"^[a-zA-Z ']+$")]
            names = names.to_dict()

            bg = options['BG color'].get()
            bg = 'white' if bg == '' else bg.lower()
            if bg == 'transparent':
                bg = None

            self.wordcloud = wc.WordCloud(
                background_color=bg, width=700, height=500, scale=3, mode='RGBA').generate_from_frequencies(names)
            ax = figure.add_subplot()
            ax.imshow(self.wordcloud, interpolation='bilinear')
            ax.set_axis_off()
            return figure

        except AttributeError:
            message = 'The chosen column does not consist of strings'
            messagebox.showerror(title='Column Choice', message=message)
            return None

    def barplot(self, data, options, labels):
        figure = plt.Figure(figsize=(7, 5))

        groupby_column = options['Column'].get()
        number = options['Nr. of categories'].get()
        number = int(number) if number.isdigit() else 10

        # Data Manipulation
        names = data.groupby(
            groupby_column).count().iloc[:, 0].nlargest(number)

        # Data Visualisation
        ax = figure.add_subplot()
        names.plot(kind='bar', ax=ax)

        xlab = labels['X Label'].get()
        ylab = labels['Y Label'].get()

        if xlab:
            ax.set_xlabel(xlab)
        if ylab:
            ax.set_ylabel(ylab)

        return figure

    def icicle(self, data, options, labels):
        pass

    # def save(self):

        # file_types = [('JPEG files', '.jpg'), ('PNG files', '.png')]
        # kwargs = {
        #     'filetypes': file_types,
        #     'title': 'Select File Name',
        #     'defaultextension': '.jpg',
        #     'initialdir': os.getcwd()
        # }

        # if (self.is_wordcloud or self.fig_transparent):
        #     kwargs['filetypes'] = (file_types[1], )
        #     kwargs['defaultextension'] = '.png'

        # filename = filedialog.asksaveasfilename(**kwargs)
        # if filename == '':
        #     pass
        # else:
        #     if self.wordcloud:
        #         self.wordcloud.to_file(filename)
        #     else:
        #         self.figure.savefig(filename)


class CustomToolbar(NavigationToolbar2Tk):

    def __init__(self, canvas, window, figure):
        super().__init__(canvas=canvas, window=window)
        self.figure = figure

        save_btn = ('Save', 'Save the figure', 'filesave', self.save_figure)
        toolbar_items = [t if t[0] !=
                         'Save' else save_btn for t in self.toolitems]

    def save_figure(self):
        kind = self.figure.__class__.__name__
        filetypes = [('Joint Photographic Experts Group', '.jpeg'),
                     ('Joint Photographic Experts Group', '.jpg'),
                     ('Portable Network Graphics', '.png'),
                     ('Postscript', '.ps'),
                     ('Encapsulated Postscript', '.eps'),
                     ('Portable Document Format', '.pdf'),
                     ('PGF code for LaTeX', '.pgf'),
                     ('Raw RGBA bitmap', '.raw'),
                     ('Raw RGBA bitmap', '.rgba'),
                     ('Scalable Vector Graphics', '.svg'),
                     ('Scalable Vector Graphics', '.svgz'),
                     ('Tagged Image File Format', '.tif'),
                     ('Tagged Image File Format', '.tiff')]

        if kind == 'WordCloud':
            del filetypes[0:2]

        kwargs = {
            'filetypes': filetypes,
            'title': 'Select File Name',
            'defaultextension': filetypes[0][1],
            'initialdir': os.getcwd()
        }

        filename = filedialog.asksaveasfilename(**kwargs)
        if filename:
            if kind == 'WordCloud':
                self.figure.to_file(filename)
            else:
                self.figure.savefig(filename)
        else:
            pass
        return True


class LabelFrameInput(ttk.LabelFrame):

    """
    Creates a ttk labelframe with the widgets passed through the inputs argument. 
    The primary argument is used to distinguish those instances that have a widget centered at the top (graph_options and data_entry)

    inputs argument format:
    (widget_name, {label:name, kwarg:value})

    Explanation:

    widget_name - a string representaition of the type of widget to make (according to key)

    label - The label used to explain the widget. Placed to the left of the widget
    """

    key = {
        'entry': ttk.Entry,
        'optionmenu': ttk.OptionMenu,
        'button': ttk.Button,
        'combo': ttk.Combobox,
        'checkbutton': ttk.Checkbutton
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
            frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(5,2))

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
                data_input = ttk.Button(
                    frame, text='Select data file', command=command)
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
            elif widget == 'checkbutton':
                intvar = tk.IntVar()
                widget = self.key[widget](frame, variable=intvar)
                entry_widget[label_str] = intvar
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

