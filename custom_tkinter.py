import tkinter as tk
from tkinter import ttk, font, filedialog, messagebox

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import wordcloud as wc

import pandas as pd
import numpy as np
from PIL import Image

from copy import deepcopy, copy
import os
from ast import literal_eval
import re

def compress_dataframe(dataframe):
    "Compress dataframe inplace, mainly for floats, ints and categorical variables"

    def int_compress(col, float_val=False):
        if not float_val:
            for i in col:
                data = dataframe[i].values
                max_val = data.max()
                min_val = data.min()

                if (max_val<=127 and min_val>=-128):
                    dataframe[i] = data.astype("int8")
                elif (min_val>=-32768 and max_val<=32767):
                    dataframe[i] = data.astype("int16")
                elif (min_val>=-2,147,483,648 and max_val<=2,147,483,647):
                    dataframe[i] = data.astype("int32")
        else:
            for i in col:
                data = dataframe[i]
                val = data.fillna(-1).values
                max_val = val.max()
                min_val = val.min()

                if (max_val<=127 and min_val>=-128):
                    dataframe[i] = data.astype("Int8")
                elif (min_val>=-32768 and max_val<=32767):
                    dataframe[i] = data.astype("Int16")
                elif (min_val>=-2,147,483,648 and max_val<=2,147,483,647):
                    dataframe[i] = data.astype("Int32")

    def float_compress(col):
        pass

    def obj_compress(col):
        for i in col:
            unique = len(dataframe[i].unique())
            if unique <= 20:
                dataframe[i] = dataframe[i].astype("category")

    int64_col = dataframe.select_dtypes("int64").columns
    int_compress(int64_col)

    float64_col = dataframe.select_dtypes("float64").columns   
    float_to_int = [i for i in float64_col if all(np.isclose(data:=dataframe[i].fillna(-1).values, data.astype('int')))]
    # float_to_int = [i for i in float64_col if all(np.isclose(dataframe[i].fillna(-1).values, dataframe[i].fillna(-1).values.astype('int')))]
    int_compress(float_to_int, float_val=True)
    
    obj_col = dataframe.select_dtypes("object")
    obj_compress(obj_col)

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

class Scrollable(tk.Frame):
    """
       Make a frame scrollable with scrollbar on the right.
       After adding or removing widgets to the scrollable frame, 
       call the update() method to refresh the scrollable area.
    """

    def __init__(self, frame):

        self.scrollbar = tk.Scrollbar(frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=False, padx=(2,0), pady=2)

        self.canvas = tk.Canvas(frame, yscrollcommand=self.scrollbar.set, width=250, height=200)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 2), pady=2)

        self.scrollbar.config(command=self.canvas.yview)

        self.canvas.bind('<Configure>', self.__fill_canvas)

        # base class initialization
        tk.Frame.__init__(self, frame)         

        # assign this obj (the inner frame) to the windows item of the canvas
        self.windows_item = self.canvas.create_window(0,0, window=self, anchor=tk.NW)


    def __fill_canvas(self, event):
        "Enlarge the windows item to the canvas width"

        canvas_width = event.width
        self.canvas.itemconfig(self.windows_item, width = canvas_width)        

    def update(self):
        "Update the canvas and the scrollregion"

        self.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(self.windows_item))

    def destroy(self):
        self.scrollbar.destroy()
        self.canvas.destroy()
        return super().destroy()

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
        self.table = ttk.Treeview(self, columns=tuple(columns))

        scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.table.yview)
        self.table.config(yscrollcommand=scroll.set)

        self.create_entries(dataframe)

        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.table.pack(side=tk.BOTTOM, fill='both')

    def create_entries(self, dataframe, init=False):
        
        columns = dataframe.columns
        font_obj = font.Font()

        self.table.heading('#0', text='Index')

        for index, row in dataframe.iterrows():
            row = tuple(row)
            self.table.insert('', 'end', values=row, text=index)

        if not init:
            width = font_obj.measure('Index')
            self.table.column('#0', width=width, stretch=True)
            for i in columns:
                self.table.heading(i, text=i)
                longest = max(dataframe[i].values, key=len).strip()
                longest_val = font_obj.measure(text=longest)
                index_val = font_obj.measure(text=i)
                width = max(longest_val, index_val)
                self.table.column(i, width=width, stretch=True)

    def update(self, new_data):
        self.table.delete(*self.table.get_children())
        new_data = new_data.astype(str)
        self.create_entries(new_data, init=True)


class CheckCombo(ttk.Combobox):

    def __init__(self, master, **kw):
        self.stringvar = tk.StringVar()
        self.options = kw.pop('values')
        super().__init__(master=master, textvariable=self.stringvar, values=list(self.options[0:10]), **kw)
        self.bind('<KeyRelease>', self.get_val)

    def get_val(self, event):
        val = self.stringvar.get().strip()
        if val:
            options = [str(x) for x in self.options]
            val = val.lower()
            regex = re.compile(f'{val}')
            values = [index for index, value in enumerate(options) if regex.match(value.lower())]
            n = len(values)

            if n >= 10:
                values = values[0:10]
            else:
                regex = re.compile(f'[{val}]')
                values = [index for index, value in enumerate(options) if regex.match(value.lower())]
                new = len(values)
                if new >= 10:
                    values = values[0:10]
                
            self['values'] = [self.options[i] for i in values] if len(values)>0 else self.options[0:10]
        else:
            self['values'] = self.options[0:10]
 

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
            'Line': self.line,
            'Test': self.test
        }

        if labels['xkcd'].get():
            with plt.xkcd():
                figure = plot_types[kind](data=data, options=options, labels=labels)
        else:
            figure = plot_types[kind](data=data, options=options, labels=labels)

        # figure = plot_types[kind](data=data, options=options, labels=labels)

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
            else:
                figure.set_tight_layout(True)

            self.canvas = FigureCanvasTkAgg(figure, master=self)

            if self.hover is not False:
                self.canvas.mpl_connect('motion_notify_event', lambda event: self.hover(event))

            toolbar_kwargs = {
                'canvas': self.canvas,
                'window': self,
                'figure': figure
            }

            if self.is_wordcloud:
                toolbar_kwargs['figure'] = self.wc

            toolbar = CustomToolbar(**toolbar_kwargs)
            toolbar.update()

            self.canvas.draw()
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill='both', expand=True)

    def wordcloud(self, data, options, labels):
        self.is_wordcloud = True
        figure = plt.Figure(figsize=(7, 5))
        ax = figure.add_subplot()
        groupby_column = options['column'].get()

        def transform_format(val):
            if val == 0:
                return 255
            else:
                return val
        # Data manipulation
        try:
            names = data[groupby_column].value_counts()
            names = names.sort_index(ascending=True)
            names = names[names.index.str.match(r"^[a-zA-Z ']+$", na=False)]
            
            filt = options['filter'].get().strip()
            if filt:
                names = names[~(names.index.str.match(filt))]
            
            names = names.to_dict()

            bg = options['bg'].get()
            bg = 'white' if bg == '' else bg.lower()
            if bg == 'transparent':
                bg = None

            mask = options['file_mask'].get()
            
            if mask:
                mask = np.array(Image.open(mask))
                mask[mask==0] = 255
                
                self.wc = wc.WordCloud(background_color=bg, scale=3, mask=mask,
                                              max_words=500, max_font_size=50,
                                              mode='RGBA').generate_from_frequencies(names)
                colors = wc.ImageColorGenerator(mask)
                
                ax.imshow(self.wc.recolor(color_func=colors), interpolation='bilinear')
            else:
                self.wc = wc.WordCloud(
                    background_color=bg, width=700, height=500, scale=3, mode='RGBA').generate_from_frequencies(names)
                ax.imshow(self.wc, interpolation='bilinear')

            ax.set_axis_off()
            return figure

        except AttributeError:
            message = 'The chosen column does not consist of strings.'
            messagebox.showerror(title='Column Choice', message=message)
            return None
        except ValueError:
            message = 'The chosen column does not consist of words.'
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

        y_ax = options['y'].get()
        groupby = options['groupby'].get()
        # Data manipulation
        figure, ax = plt.subplots()
        lines = []
        self.location = [0,0]

        if groupby == 'None':
            used_data = data[y_ax].value_counts()
            used_data = used_data.sort_index(ascending=True)
            lines, = ax.plot(used_data.index, used_data.values, marker='o')
            annot = ax.annotate("", xy=(0,0), xytext=(-30,20),textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"), clip_on=True)
            annot.set_visible(False)
        
        else:
            for label, df in data.groupby(groupby):
                used_data = df[y_ax].value_counts()
                used_data = used_data.sort_index(ascending=True)

                picker = (used_data.max()-used_data.min())/(len(used_data.index)*100)


                line, = ax.plot(used_data.index, used_data.values, label=label, marker='o', picker=1)
                lines.append([line, label])
                
                annot = ax.annotate("", xy=(0,0), xytext=(-30,20),textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"), clip_on=True)
                annot.set_visible(False)

            plt.legend()

        def update_annot(ind, event=None, index=None):
            if isinstance(lines, list):
                x,y = lines[index][0].get_data()
                label = lines[index][1]
                ind = ind['ind'][0]

                location = self.location
                if (x[ind]==location[0]) and (y[ind]==location[1]):
                    return
                
                if abs(x[ind]-event.xdata) < abs(location[0]-event.xdata):
                    x = x[ind]
                    self.location[0] = x
                if abs(y[ind]-event.ydata) < abs(location[1]-event.ydata):
                    y = y[ind]
                    self.location[1] = y

                annot.xy = (self.location[0], self.location[1])

                annot_text = annot.get_text()
                text = f'{label}\n{y_ax}-{self.location[0]}, People-{self.location[1]}'
                if text in annot_text:
                    return
                else:
                    if annot_text:
                        annot_text = f'{annot_text}\n\n{text}'
                    else:
                        annot_text = text
                annot.set_text(annot_text)
                annot.get_bbox_patch().set_alpha(1)
            else:
                x, y = lines.get_data()
                ind = ind['ind'][0]
                annot.xy = (x[ind], y[ind])
                text = f'{y_ax}-{x[ind]} People-{y[ind]}'

                annot.set_text(text)
                annot.get_bbox_patch().set_alpha(1)

        def hover(event):
            vis = annot.get_visible()
            if isinstance(lines, list):
                x = 0
                length = len(lines)
                if event.inaxes == ax:
                    for index, line in enumerate(lines):
                        line = line[0]
                        cont, ind = line.contains(event)
                        if cont:
                            update_annot(ind, event, index)                        
                        else:
                            x += 1
                
                    if (x==length):
                        annot.set_text('')
                        annot.set_visible(False)
                        self.canvas.draw_idle()
                    else:
                        annot.set_visible(True)
                        self.canvas.draw_idle()
            else:
                if event.inaxes == ax:
                    cont, ind = lines.contains(event)
                    if cont:
                        update_annot(ind)
                        annot.set_visible(True)
                        self.canvas.draw_idle()
                    else:
                        if vis:
                            annot.set_visible(False)
                            self.canvas.draw_idle()
                            
        self.hover = hover                
        return figure

    def test(self, data, options, labels):
        a = TestPlot(data, options)
        if a.empty:
            return None
        else:
            return a

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
        'combo': CheckCombo,
        'checkbutton': ttk.Checkbutton
    }

    def __init__(self, master, inputs, primary=None, **kwargs):

        command = kwargs.pop('command') if 'command' in kwargs else None
        alt_command = kwargs.pop('alt_command') if 'alt_command' in kwargs else None

        super().__init__(master, **kwargs)
        self.is_data = False
        self.inputs = inputs
        self.frames = None
        self.scroll = False

        if primary == 'graph_options':

            self.frames = {}
            self.values = {}

            frame = ttk.Frame(self)
            graph_options_lab = ttk.Label(frame, text='Graph Type', width=15)
            options = list(self.inputs)
            self.graph_type = tk.StringVar()
            graph_options_opt = ttk.OptionMenu(
                frame, self.graph_type, options[0], *options, command=self.update)
            graph_options_lab.pack(side=tk.LEFT)
            graph_options_opt.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(5, 2))

            for i in options:
                if i in inputs:
                    if inputs[i] is None:
                        continue
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
                filename.pack(side=tk.BOTTOM, expand=True, anchor=tk.CENTER)
                data_input.pack(fill='both')

                bottom_frame = ttk.Frame(self)
                filter_apply = ttk.Button(bottom_frame, text='Filter', command=alt_command[0])
                filter_remove = ttk.Button(bottom_frame, text='Clear', command=alt_command[1])

                filter_apply.pack(side=tk.LEFT, expand=True, padx=(5,2.5))
                filter_remove.pack(side=tk.RIGHT, expand=True, padx=(2.5,5))

                top_frame.pack(side=tk.TOP, fill=tk.X, pady=5, padx=5)
                bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

            if inputs is not None:
                self.frames, self.values = self.create_frame(inputs)
                self.frames.pack(side=tk.TOP, fill=tk.X, padx=5)
            else:
                pass

    def create_frame(self, entries):
        
        if self.scroll:
            frame_top = ttk.LabelFrame(self, text='Filters')
            frame_1 = ttk.Frame(frame_top)
            frame_1.pack(fill='both', expand=True)
            frame_master = Scrollable(frame_1)
        else:
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

            elif widget == 'checkbutton':
                intvar = tk.IntVar()
                widget = self.key[widget](frame, variable=intvar)
                entry_widget[identity] = intvar

            elif widget == 'button':
                command = kwargs.pop('command')
                stringvar = tk.StringVar(value='')
                
                widget = self.key[widget](frame, command=lambda: stringvar.set(self.get_file()), **kwargs)
                entry_widget[identity] = stringvar
                

            else:
                if widget == 'entry' and 'validate' in kwargs:
                    reg = frame.register(self.int_validate)
                    kwargs['validatecommand'] = (reg, '%P')
                    kwargs['validate'] = 'key'
                
                widget = self.key[widget](frame, **kwargs)
                entry_widget[identity] = widget


            if not self.is_data:
                widget.config(state='disabled')

            label.pack(side=tk.LEFT)
            widget.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            frame.pack(fill=tk.X, pady=5)

        if self.scroll:
            frame_master.update()
            return frame_top, entry_widget
        else:
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
                try:
                    self.frames.destroy()
                    self.frames, self.values = self.create_frame(self.inputs)
                    # if self.scroll:
                    #     return True
                    self.frames.pack(side=tk.TOP, fill=tk.X, padx=5)
                except AttributeError:
                    self.frames, self.values = self.create_frame(self.inputs)
                    # if self.scroll:
                    #     return True
                    self.frames.pack(side=tk.TOP, fill=tk.X, padx=5)

        else:
            self.current.pack_forget()

            if name in self.frames:
                self.current = self.frames[name]
                self.current.pack(side=tk.TOP, fill=tk.X, padx=5)

    def get_names(self, stringvar, combo, names):
        val = stringvar.get().strip()
        print(val)
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

    def int_validate(self, inp):
        if inp.isdigit():
            return True
        elif not inp:
            return True
        else:
            return False

    def get_file(self):

        try:
            filename = filedialog.askopenfilename(filetypes=[('PNG files', '.png')])
            return filename

        except FileNotFoundError:
            message = f"No file found."
            messagebox.showerror(title='File not found', message=message)
            return ""




class IciclePlot(tk.Canvas):

    def __init__(self, master, data, inputs):
        super().__init__(master=master)
        # retype strings to integers and tuples:
        options = inputs.copy()
        Column = options['column'].get()
        try:
            
            Height = options['height'].get().strip()
            Width = options['width'].get().strip()
            Height = int(Height) if Height.isdigit() else 700
            Width = int(Width) if Width.isdigit() else 700

            cutoff = options.pop('cutoff').get().strip()
            min_char_width = options['min_char_width'].get()
            cutoff = int(cutoff) if cutoff.isdigit() else 1
            min_char_width = int(min_char_width) if min_char_width.isdigit() else 1
        
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
            mask = data[Column].notnull().values
            self.data = data.loc[mask]
            self.data.sort_values(by=Column, inplace=True)
            self.name_list = [str(x) for x in self.data[Column].values]
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
        width_per_char = max(Width/max(len(name)
                             for name in names), min_char_width)

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


######### IGNORE ###########


class TestPlot(plt.Figure):

    color_lvl = {
        0: 'white',
        1: 'royalblue',
        2: 'fuchsia',
        3: 'olivedrab',
        4: 'coral'
    }

    def __init__(self, data, options):
        super().__init__()
        colors = False
        ax = self.add_subplot(projection='polar')

        lv_list = [options[f'lv_{i}'].get() for i in range(1,6) if options[f'lv_{i}'].get() != 'Not Available']
        
        if len(lv_list) == 0:
            messagebox.showerror('Column Selection', 'No columns selected for visualisation')
            self.empty = True
        else:
            tree = self.get_list(data, lv_list)
            self.sunburst(tree, ax=ax, colors=colors)
        

    def sunburst(self, nodes, total=np.pi * 2, offset=0, level=0, colors=False, ax=None):

        if level == 0 and len(nodes) == 1:
            if colors:
                label, value, color, subnodes = nodes[0]
            else:
                label, value, subnodes = nodes[0]
                color = self.__class__.color_lvl[level]
            
            ax.bar([0], [0.5], [np.pi * 2], color=color)
            ax.text(0, 0, label, ha='center', va='center')
            if colors:
                self.sunburst(subnodes, total=value, level=level + 1, ax=ax, colors=True)
            else:
                self.sunburst(subnodes, total=value, level=level + 1, ax=ax)
        elif nodes:
            d = np.pi * 2 / total
            labels = []
            widths = []
            local_offset = offset
            if colors is True:
                color_list = []
                for label, value, color, subnodes in nodes:
                    labels.append(label)
                    widths.append(value * d)
                    color_list.append(color)
                    self.sunburst(subnodes, total=total, offset=local_offset,
                            level=level + 1, ax=ax, colors=True)
                    local_offset += value
                values = np.cumsum([offset * d] + widths[:-1])
                heights = [1] * len(nodes)
                bottoms = np.zeros(len(nodes)) + level - 0.5

                rects = ax.bar(values, heights, widths, bottoms, linewidth=1,
                        edgecolor='white', align='edge', color=color_list)

            else:
                for label, value, subnodes in nodes:
                    labels.append(label)
                    widths.append(value * d)
                    self.sunburst(subnodes, total=total, offset=local_offset,
                            level=level + 1, ax=ax)
                    local_offset += value
                values = np.cumsum([offset * d] + widths[:-1])
                heights = [1] * len(nodes)
                bottoms = np.zeros(len(nodes)) + level - 0.5

                rects = ax.bar(values, heights, widths, bottoms, linewidth=1,
                        edgecolor='white', align='edge', color=self.__class__.color_lvl[level%5])
            
            for rect, label in zip(rects, labels):
                x = rect.get_x() + rect.get_width() / 2
                y = rect.get_y() + rect.get_height() / 2
                rotation = (90 + (360 - np.degrees(x) % 180)) % 360
                ax.text(x, y, label, rotation=rotation, ha='center', va='center') 

        if level == 0:
            ax.set_theta_direction(-1)
            ax.set_theta_zero_location('N')
            ax.set_axis_off()

    def convert_to_percent(self, arr_main, parent):

        try:
            for arr in arr_main:
                arr[1] = (arr[1]/parent)*100
                self.convert_to_percent(arr[3], parent=arr[1])
        except:
            print(arr)

    def remove_colors(self, arr):

        for i in arr:
            del i[2]
            self.remove_colors(i[2])

    def get_list(self, df, lv):
        try:
            unique = df[lv[0]].value_counts()
            return_list = []
            for i in unique.index:
                tmp = self.get_list(df[df[lv[0]]==i], lv[1:])
                return_list.append([i, unique[i], tmp])
            return return_list
        except:
            return []

