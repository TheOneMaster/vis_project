import tkinter as tk
from tkinter import ttk, font, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from copy import deepcopy, copy
import os
import wordcloud as wc
import pandas as pd
from ast import literal_eval
import re

# Classes that are basically done

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


class CustomToolbar(NavigationToolbar2Tk):

    """
    Custom  matplotlib Navigation Toolbar for Tkinter. Changes the save functionality.

    TODO: Change the x, y coordinate output to rounded 2d vectors [x,y] instead of x=x, y=y

    """

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


class DataTable(ttk.Frame):
    "Creates table representation of dataframe"
    def __init__(self, master, dataframe, options, **kw):
        super().__init__(master=master, **kw)
        dataframe = dataframe.astype(str)
        columns = dataframe.columns
        self.table = ttk.Treeview(self, columns=tuple(columns[1:]), height=8)

        scroll = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.table.xview)
        self.table.config(xscrollcommand=scroll.set)

        self.create_entries(dataframe)

        scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.table.pack(side=tk.BOTTOM, fill='both')

    def create_entries(self, dataframe):
        
        columns = dataframe.columns
        font_obj = font.Font()

        width = font_obj.measure(columns[0])
        self.table.heading('#0', text=columns[0])
        self.table.column('#0', width=width)

        for index, row in dataframe.iterrows():
            row = tuple(row)
            self.table.insert('', 'end', values=row[1:], text=row[0])

        for i in columns[1:]:
            self.table.heading(i, text=i)
            longest = max(dataframe[i].values, key=len).strip()
            longest_val = font_obj.measure(text=longest)
            index_val = font_obj.measure(text=i)
            width = max(longest_val, index_val)
            self.table.column(i, width=width)

    def update(self, new_data):
        self.table.delete(*self.table.get_children())
        self.create_entries(new_data)

# Classes that are still being worked on 

class NotebookTab(ttk.Frame):
    "A ttk Frame with the frame layout and figure for the notebook"

    def __init__(self, master, notebook, data, kind, options, labels, *args, **kwargs):
        super().__init__(master=master, **kwargs)

        self.hover = False
        self.is_empty = True
        self.is_wordcloud = False

        plot_types = {
            'Barplot': self.barplot,
            'Wordcloud': self.wordcloud,
            'Icicle': self.icicle,
            'Line': self.line
        }

        if labels['xkcd'].get():
            with plt.xkcd():
                figure = plot_types[kind](
                    data=data, options=options, labels=labels)
        else:
            figure = plot_types[kind](
                data=data, options=options, labels=labels)

        if figure is None:
            pass
        elif isinstance(figure, tk.Canvas):
            self.is_empty = False
            title = labels['title'].get().strip()
            title = title if title else None

            if title is not None:
                figure.canvas.create_text(0, 0, text=title)
            canvas = figure.canvas
        else:
            self.is_empty = False
            title = labels['title'].get()
            title = title if title != '' else None

            if title is not None:
                figure.suptitle(title)

            figure.set_tight_layout(True)

            self.canvas = FigureCanvasTkAgg(figure, master=self)

            if self.hover is not None:
                self.canvas.mpl_connect('motion_notify_event', lambda event: self.hover(event))

            toolbar_kwargs = {
                'canvas': self.canvas,
                'window': self,
                'figure': figure
            }

            if self.is_wordcloud:
                toolbar_kwargs['figure'] = self.wordcloud

            toolbar = CustomToolbar(**toolbar_kwargs)
            toolbar.update()

            self.canvas.draw()
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill='both', expand=True)

    def wordcloud(self, data, options, labels):
        self.is_wordcloud = True
        figure = plt.Figure(figsize=(7, 5))
        groupby_column = options['column'].get()

        # Data manipulation
        try:
            names = data.groupby(groupby_column).count().iloc[:, 0]
            names = names[names.index.str.match(r"^[a-zA-Z ']+$")]
            
            filt = options['filter'].get().strip()
            if filt:
                names = names[~(names.index.str.match(filt))]
            
            names = names.to_dict()

            bg = options['bg'].get()
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

        groupby_column = options['column'].get()
        number = options['categories'].get().strip()
        number = int(number) if number.isdigit() else 10

        # Data Manipulation
        names = data.groupby(
            groupby_column).count().iloc[:, 0].nlargest(number)

        # Data Visualisation
        ax = figure.add_subplot()
        names.plot(kind='bar', ax=ax)

        xlab = labels['xlab'].get()
        ylab = labels['ylab'].get()

        if xlab:
            ax.set_xlabel(xlab)
        if ylab:
            ax.set_ylabel(ylab)

        return figure

    def icicle(self, data, options, labels):
        return IciclePlot(self, data, options)

    def line(self, data, options, labels):

        # Data manipulation
        figure = plt.Figure(figsize=(7, 5))
        ax = figure.add_subplot()
        options = "Year"
        names = data.groupby([options]).count().iloc[:,0]
        line, = ax.plot(names.index, names.values, marker='o', color='green', mfc='red')

        annot = ax.annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)

        def update_annot(ind):
            x,y = line.get_data()
            ind = ind['ind'][0]
            annot.xy = (x[ind], y[ind])
            text = f"{options}-{names.index[ind]}, People-{names.values[ind]}"
            annot.set_text(text)
            annot.get_bbox_patch().set_alpha(0.4)


        def hover(event):
            vis = annot.get_visible()
            if event.inaxes == ax:
                cont, ind = line.contains(event)
                if cont:
                    update_annot(ind)
                    annot.set_visible(True)
                    self.canvas.draw_idle()
                else:
                    if vis:
                        annot.set_visible(False)
                        self.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    self.canvas.draw_idle()

        self.hover = hover                
        return figure



class LabelFrameInput(ttk.LabelFrame):

    """
    Creates a ttk labelframe with the widgets passed through the inputs argument.
    The primary argument is used to distinguish those instances that have a widget centered at the top (graph_options and data_entry)

    inputs argument format:
    {kind: type, id: code reference ,label:name,  kwarg:value})

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
        alt_command = kwargs.pop('alt_command') if 'alt_command' in kwargs else None

        super().__init__(master, **kwargs)
        self.is_data = False
        self.inputs = inputs

        if primary == 'graph_options':

            self.frames = {}
            self.values = {}

            frame = ttk.Frame(self)
            graph_options_lab = ttk.Label(frame, text='Graph Type', width=15)
            options = ['Barplot', 'Wordcloud', 'Line', 'Icicle']
            self.graph_type = tk.StringVar()
            graph_options_opt = ttk.OptionMenu(
                frame, self.graph_type, options[0], *options, command=self.update)
            graph_options_lab.pack(side=tk.LEFT)
            graph_options_opt.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(5, 2))

            for i in options:
                if i in inputs:
                    data = self.create_frame(inputs[i])
                    self.frames[i] = data[0]
                    self.values[i] = data[1]

            self.current = self.frames['Barplot']
            self.current.pack(side=tk.TOP, fill=tk.X, padx=5)

        else:

            if primary == 'data_input':
                top_frame = ttk.Frame(self)
                str_var = tk.StringVar(value='No file selected')
                filename = ttk.Label(top_frame, textvariable=str_var)
                data_input = ttk.Button(
                    top_frame, text='Select data file', command=lambda: str_var.set(command()))
                filename.pack(side=tk.BOTTOM, expand=True)
                data_input.pack(fill='both')

                bottom_frame = ttk.Frame(self)
                filter_apply = ttk.Button(bottom_frame, text='Filter', command=alt_command[0])
                filter_remove = ttk.Button(bottom_frame, text='Clear', command=alt_command[1])

                filter_apply.pack(side=tk.LEFT, expand=True, padx=(5,2.5))
                filter_remove.pack(side=tk.RIGHT, expand=True, padx=(2.5,5))

                top_frame.pack(side=tk.TOP, fill=tk.X, pady=5, padx=5)
                bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)


            self.frames, self.values = self.create_frame(inputs)
            self.frames.pack(side=tk.TOP, fill=tk.X, padx=5)

    def create_frame(self, entries):

        frame_master = ttk.Frame(self)
        inputs = deepcopy(entries)
        entry_widget = {}

        for kwargs in inputs:
            widget = kwargs.pop('kind')
            identity = kwargs.pop('id')
            frame = ttk.Frame(frame_master)
            label_str = kwargs.pop('label')
            label = ttk.Label(frame, text=label_str, width=15, anchor='sw')

            if widget == 'optionmenu':
                stringvar = tk.StringVar()
                options = kwargs.pop('options')
                widget = self.key[widget](
                    frame, stringvar, options[0], *options, **kwargs)
                entry_widget[identity] = stringvar

            elif widget == 'combo':
                stringvar = tk.StringVar()
                options = kwargs.pop('options')
                widget = self.key[widget](frame, textvariable=stringvar, values=list(options[0:10]), **kwargs)
                widget.bind('<KeyRelease>', lambda event: self.get_names(stringvar, widget, options.copy()))
                entry_widget[identity] = stringvar

            elif widget == 'checkbutton':
                intvar = tk.IntVar()
                widget = self.key[widget](frame, variable=intvar)
                entry_widget[identity] = intvar

            else:
                widget = self.key[widget](frame, **kwargs)
                entry_widget[identity] = widget

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

    def get_names(self, stringvar, combo, names):
        val = stringvar.get().strip()
        
        if not val:
            combo['values'] = names[0:10]
        else:
            val = val.lower()
            regex = re.compile(f'{val}')
            values = [index for index, name in enumerate(names) if regex.match(name.lower())]

            if len(values) >= 10:
                values = values[0:10]
                     
            elif len(values) == 0:
                regex = re.compile(f'[{val}]')
                values = [index for index, name in enumerate(names) if regex.match(name.lower())]
                if len(values)>10:
                    values = values[0:10]

            values = [names[i] for i in values] if len(values)>0 else names[0:10]
            combo['values'] = values


class IciclePlot(tk.Canvas):

    def __init__(self, master, data, inputs):
        super().__init__(master=master)

        # retype strings to integers and tuples:
        options = inputs.copy()
        Column = options['column'].get()
        try:
            cutoff = options.pop('cutoff').get().strip()
            Height = options['height'].get().strip()
            Width = options['width'].get().strip()
            min_char_width = options['min_char_width'].get()
            cutoff = int(cutoff) if cutoff.isdigit() else 1
            Height = int(Height) if Height.isdigit() else 700
            Width = int(Width) if Width.isdigit() else 700
            min_char_width = int(
                min_char_width) if min_char_width.isdigit() else 1
        except ValueError:
            title = 'Incorrect Input'
            message = 'cutoff, Height, Width or min_char_width was not coercable to int'
            messagebox.showerror(title=title, message=message)
        # decode strings representing tuples:
        bool_clrs_str = options['colours'].get().strip()
        bool_clrs = literal_eval(f'[{bool_clrs_str}]')
        options['bool_clrs'] = bool_clrs
        
        # decode strings representing names
        bool_val_str = options['values'].get().strip()
        bool_vals = bool_val_str.split(',')
        
        options['bool_vals'] = bool_vals
        options['bool_clmn'] = options['bool_column'].get()

        x = 0
        y = 0
        """
        Does all the work for the name icicle plot except the recursion:
        Sorts the names, determines how high 1 name is and how wide 1 character is,
        creates a canvas

        Arguments:
        self: parent Window1 object
        data: a list of names or pandas DataFrame.
            If a DataFrame is given, name_clmn is used to decide what column to use for names.
        width: width of desired canvas
        height: height of desired canvas
        x,y: coordinates of starting position. Useful for recursion and to make labels on the side
        cutoff: determines the minimum number of names required to get a rect to actually display, minimum 1
        min_char_width: determines a minimum width per character on the final graph, for if some names are extremely long
        Column selects the column to use for plotting if the data is a DataFrame, can be int or string

        Output:
        memorydict: a dictionary containing the location and selectedness of all rectangles
            example entry: 'Menno' : [(200,250,300,350), False, (255,0,255), 'no']
            representing the square representing the names starting with Menno,
            which spans from (200,250) to (300,350), which is not selected
            All rectangles start out not selected
            3rd entry is the colour of the rectangle
            4th entry is the text in this rectangle
        """

        # get the name column from the dataframe if needed, sort stuff
        if type(data) == pd.core.frame.DataFrame:
            mask = [isinstance(value, str) for value in data[Column]]
            self.data = data.loc[mask]
            self.data.sort_values(by=Column, inplace=True)
            self.name_list = self.data.loc[:, Column].astype(str)
        else:
            self.name_list = data
            self.name_list.sort()

        # sorting names and cleaning input
        names = [name for name in self.name_list if name != "-1"]

        # creating canvas
        self.canvas = tk.Canvas(master, width=Width, height=Height)
        self.canvas.bind("<ButtonPress-1>", self.Select)
        Width = Width
        Height = Height

        # create an appropriate colour function:
        self.clr_func = self.clr_func_definer(
            data, 'b', mode='bool_blend', **options)

        def black_or_white(clr):
            """takes an input hexcode, returns the hex code for what will be more visible: black or white"""
            nrs = "0123456789abcdef"
            r = nrs.index(clr[1])*16+nrs.index(clr[2])
            g = nrs.index(clr[3])*16+nrs.index(clr[4])
            b = nrs.index(clr[5])*16+nrs.index(clr[6])

            if r+g+b < 381:  # average value under 127
                return("#ffffff")
            else:
                return("#000000")

        self.text_clr_func = black_or_white

        # determine height and width
        height_per_name = Height/len(names)
        width_per_char = max(Width/max([len(name)
                             for name in names]), min_char_width)

        self.memorydict = self.NameIciclePlot(
            names, width_per_char, height_per_name, x, y, Width, cutoff, self.data, **options)
        self.canvas.pack(fill='both', expand=True)

    def NameIciclePlot(self, names, width_per_char, height_per_name, x, y,
                       outline, cutoff, data: list, topname="", recursioncounter=0, *args, **kwargs):
        """Plots the icicle graphs by recursive function
        topname is a variable storing the bit of each name cut off at the front, for later printing
        recursioncounter is for testing purposes
        outline is the width + 100, the point where names must have ended"""
        memorydict = {}
        last_name = names[0]
        overlap = len(names[0])
        nrnames = -1
        for i in range(0, len(names)):
            name = names[i]
            nrnames += 1

            new_overlap = 0
            flag = False
            for j in range(0, min(len(name), len(last_name))):
                # this for loop finds the overlap this word has with the last word
                if flag == False and name[j] == last_name[j]:
                    new_overlap += 1
                else:
                    flag = True
            # print(f"line 49, recursion: {recursioncounter}, data: {(names, overlap, new_overlap)}")
            if new_overlap == 0:
                # if there is no overlap, we will plot a rectangle representing the last group of words
                end_x = x+(width_per_char*overlap)
                end_y = y+(nrnames*height_per_name)
                if nrnames >= cutoff:
                    # any displaying will only happen if the cutoff is reached
                    new_data = data[i-nrnames:i]
                    rect_clr = self.clr_func(data=new_data, **kwargs)
                    text_clr = self.text_clr_func(rect_clr)
                    self.canvas.create_rectangle(
                        x+1, y+1, end_x-1, end_y-1, fill=rect_clr)
                    display_text = names[i-1][:overlap]
                    self.canvas.create_text(x + 5, (y + end_y)/2,
                                            text=display_text, anchor=tk.W, fill=text_clr)
                    new_topname = topname + display_text
                    memorydict[new_topname] = [
                        (x+1, y+1, end_x-1, end_y-1), False, rect_clr, display_text]

                    # then there is a recursion case: if the overlap wasn't total, recurse on the remaining characters
                    newnames = names[i-nrnames:i]
                    full_overlap = [
                        name for name in newnames if len(name) == overlap]
                        # required for displaying certain names on right side
                    # print(f"line 59, recursion: {recursioncounter}, data: {(newnames, overlap)}")
                    newnames = [name[overlap:] for name in newnames]
                    # print(newnames)
                    newnames = [name for name in newnames if len(name) > 0]
                    # print(newnames)
                    if len(newnames) > 0:
                        new_memorydict = self.NameIciclePlot(newnames, width_per_char, height_per_name, end_x, y,
                                            outline, cutoff, new_data, new_topname, recursioncounter + 1, **kwargs)
                        memorydict.update(new_memorydict)
                    # displaying name that was fully overlapped:
                    if len(full_overlap) >= cutoff:
                        mid_y = y + len(newnames)*height_per_name
                        disp_text = topname + \
                            full_overlap[0] + ' : ' + str(nrnames)
                        self.canvas.create_text(
                            outline, (mid_y + end_y)/2, text=disp_text, anchor=tk.E)
                # reseting values
                nrnames = 0
                overlap = len(name)
                new_overlap = overlap
                y = end_y
            # end of iteration updates
            overlap = min(overlap, new_overlap)
            last_name = name
        # draw a rect for the final stuff:
        nrnames += 1
        end_x = x+(width_per_char*overlap)
        end_y = y+(nrnames*height_per_name)
        if nrnames >= cutoff:
            new_data = data[len(names)-nrnames:len(names)]
            rect_clr = self.clr_func(data=new_data, **kwargs)
            text_clr = self.text_clr_func(rect_clr)
            self.canvas.create_rectangle(
                x+1, y+1, end_x-1, end_y-1, fill=rect_clr)
            display_text = names[-1][:overlap]
            self.canvas.create_text(
                x + 5, (y + end_y)/2, text=display_text, anchor=tk.W, fill=text_clr)
            new_topname = topname + display_text
            memorydict[new_topname] = [
                (x+1, y+1, end_x-1, end_y-1), False, rect_clr, display_text]

            # recursion if needed
            newnames = names[len(names)-nrnames:len(names)]

            full_overlap = [name for name in newnames if len(name) == overlap]
            # print(f"line 87, recursion: {recursioncounter}, data: {(newnames, overlap)}")
            newnames = [name[overlap:] for name in newnames]
            # print(newnames)
            newnames = [name for name in newnames if len(name) > 0]
            # print(newnames)
            if len(newnames) > 0:
                new_topname = topname + names[i-1][:overlap]
                new_memorydict = self.NameIciclePlot(newnames, width_per_char, height_per_name, end_x, y,
                                    outline, cutoff, new_data, new_topname, recursioncounter + 1, **kwargs)
                memorydict.update(new_memorydict)
            # displaying name that was fully overlapped:
            if len(full_overlap) >= cutoff:
                mid_y = y + len(newnames)*height_per_name
                disp_text = topname+full_overlap[0] + ' : ' + str(nrnames)
                self.canvas.create_text(
                    outline, (mid_y + end_y)/2, text=disp_text, anchor=tk.E)
        return(memorydict)

    def Select(self, event):
        """Selects the square which is clicked"""
        for rect_key in self.memorydict.keys():
            rect = self.memorydict[rect_key]
            loc_tup = rect[0]
            if event.x > loc_tup[0] and event.x < loc_tup[2] and event.y > loc_tup[1] and event.y < loc_tup[3]:
                if rect[1] == False:
                    clr = rect[2].lower()
                    nrs = "0123456789abcdef"
                    r = (nrs.index(clr[1])*16+nrs.index(clr[2])+50) % 255
                    g = (nrs.index(clr[3])*16+nrs.index(clr[4])+50) % 255
                    b = (nrs.index(clr[5])*16+nrs.index(clr[6])+50) % 255
                    new_clr = self._from_rgb((r, g, b))
                    self.canvas.create_rectangle(
                        loc_tup[0], loc_tup[1], loc_tup[2], loc_tup[3], fill=new_clr)
                    text_clr = self.text_clr_func(new_clr)
                    self.canvas.create_text(loc_tup[0]+5, (loc_tup[1]+loc_tup[3])/2,
                                            text=rect[3], anchor=tk.W, fill=text_clr)
                    rect[1] = True

                elif rect[1] == True:
                    self.canvas.create_rectangle(
                        loc_tup[0], loc_tup[1], loc_tup[2], loc_tup[3], fill=rect[2])
                    text_clr = self.text_clr_func(rect[2])
                    self.canvas.create_text(loc_tup[0]+5, (loc_tup[1]+loc_tup[3])/2,
                                            text=rect[3], anchor=tk.W, fill=text_clr)
                    rect[1] = False
        # todo: make it work on children of selected node
 
    def clr_func_definer(self, dat, main_clr : str, mode : str, 
                     bool_clrs : list = None, bool_clmn : str = None, bool_vals : list = None, **kwargs):
      """Returns a colour function used to colour in a graph

      Arguments:
      dat: the dataframe that will be used for the graph
      main_clr: the main colour used. 'r' for red, 'g' for green or 'b' for blue.
      mode: what mode is used to turn the data into a colour. 
          Supported modes: 
          bool: a set of values and colorrs is given. 
              For each rect, the colour is that of the value that occurs most in this rect
          bool_blend: a set of values and colours is given
              For each rect, the colour is the weighted average of colours given, weights being how often each name occurs
      bool_clrs: a list of rgb tuples for colours for each value, only required in bool mode
      bool_clmn: the column in the dataframe containing the values worked on, only required in bool mode
      bool_vals: the values to check for, only required in bool mode
      """

      convert_main_clr_dict = {'r' : 0, 'g': 1,'b' : 2}
      main_index = convert_main_clr_dict[main_clr]

      if mode == 'bool' or mode == 'bool_blend': #creates a bool or bool_blend mode function
          # catching invalid input for bool or bool_blend modes:
          for item in [bool_clrs, bool_clmn, bool_vals]:
              if item == None:
                  raise TypeError('bool_clrs, bool_clmn or bool_vals missing while in bool mode')
          if len(bool_clrs) != len(bool_vals):
              raise Exception("""bool_clrs and bool_vals were not of equal length. 
                              clr_func_definer requires an identical number of colours and values in bool mode.""")

          if mode == 'bool':
              # actual defining of bool function:
              def clr_func(data, none_clr = (127,127,127), **kwargs):
                  f"""Colour function finding the most common value of {bool_vals} in the input dataframe in column {bool_clmn}
                  and returning the value in {bool_clrs} of the same index.
                  Arguments:
                  data: input dataframe containing a column named {bool_clmn}
                  except_clr: the colour to be output when none of the values in {bool_vals} are encountered"""
                  # counting occurences of each value:
                  # print(data.loc[:,['firstname', 'gender']])
                  nr_counts = {"" : 0}
                  for val in bool_vals:
                      nr_counts[val] = 0
                  for item in data[bool_clmn]:
                      try:
                          nr_counts[item] += 1
                      except:
                          pass
                  # determining the most common occurence, prefering values given later by dict.keys:
                  largest = max(nr_counts, key = nr_counts.get) 
                  if largest == "":
                      return(self._from_rgb(none_clr))
                  # finds correct colour tuple:
                  clr = bool_clrs[bool_vals.index(largest)]
                  # print(clr)
                  return(self._from_rgb(clr))
          elif mode == 'bool_blend':
              # actual definition of bool_blend function:
              def clr_func(data, none_clr = (127,127,127), **kwargs):
                  f"""
                  Colour function giving a weighted average of the colours in {bool_clrs}, 
                  the weights being the number of occurences of {bool_vals} with the same index in {bool_clmn}
                  Arguments:
                  data: input dataframe containing a column named {bool_clmn}
                  except_clr: the colour to be output when none of the values in {bool_vals} are encountered
                  """
                  nr_counts = {}
                  # counting occurences of each value:
                  # print(data.loc[:,['firstname', 'gender']])
                  for val in bool_vals:
                      nr_counts[val] = 0
                  for item in data[bool_clmn]:
                      try:
                          nr_counts[item] += 1
                      except:
                          pass
                  # making a weighted average:
                  r,g,b = 0,0,0
                  counter = 0
                  for val in bool_vals:
                      # for each value, add the nr of occurences * colour strength to the total colour, 
                      # and add nr of occurences to the counter
                      r += bool_clrs[bool_vals.index(val)][0]*nr_counts[val]
                      g += bool_clrs[bool_vals.index(val)][1]*nr_counts[val]
                      b += bool_clrs[bool_vals.index(val)][2]*nr_counts[val]
                      counter += nr_counts[val]
                      # print(r,g,b,counter)
                  if counter > 0:
                      # zeroDivision failsafe: if no values encountered, return none_clr
                      r = int(r/counter)
                      g = int(g/counter)
                      b = int(b/counter)
                      return(self._from_rgb((r,g,b)))
                  else:
                      return(self._from_rgb(none_clr))
                  # print(r,g,b)
                  # print(nr_counts)

              return(clr_func)


      # default colour function only giving 255 for main_clr
      def clr_func(**kwargs):
          clr = [0,0,0]
          clr[main_index] = 255
          # print(clr)
          clr = tuple(clr)
          return(self._from_rgb(clr))
      return(clr_func)

    def _from_rgb(self, rgb):
        """translates an rgb tuple of int to a tkinter friendly color code
        """
        return "#%02x%02x%02x" % rgb

