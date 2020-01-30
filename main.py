# Tkinter libraries
import tkinter as tk
from tkinter import ttk, font, filedialog, messagebox
from custom_tkinter import LabelFrameInput, CustomNotebook, NotebookTab, DataTable, compress_dataframe

# Other libraries
from pandas import read_csv
import os
import numpy as np
import gc

class MainWindow(ttk.Frame):

    def __init__(self, master, **kw):
        """ Creates the frame for the main window of the application. It consists of 3 subframes: 
        The left frame(input), midframe(plots), and the right frame(output)
        """
        super().__init__(master, **kw)

        self.left_frame = ttk.Frame(self)
        self.mid_frame = ttk.Frame(self)
        self.bottom_frame = ttk.Frame(self, height=205)
        self.base = None
        self.data = None

        """
        Left frame widgets
        """
        # Data entry

        self.data_input = LabelFrameInput(self.left_frame, None, 'data_input',
                                          command=self.get_data, alt_command=[self.filter_data, self.clear_filter],
                                          text='Data entry and preprocessing')

        # Graph Options
        barplot_widgets = [
            {'kind': 'optionmenu', 'label': 'Column',
                'options': ['Not available'], 'id': 'column'},
            {'kind': 'entry', 'label': 'Nr. of categories', 'id': 'categories', 'validate':'int'}
        ]

        wordcloud_widgets = [
            {'kind': 'optionmenu', 'label': 'Column',
                'options': ['Not available'], 'id': 'column'},
            {'kind': 'optionmenu', 'label': 'BG color', 'options': [
                'White', 'Black', 'Transparent'], 'id': 'bg'},
            {'kind': 'entry', 'label': 'Filter', 'id': 'filter'},
            {'kind': 'button', 'label': 'Image Mask', 'command': 'file', 'id': 'file_mask', 'text': 'Select File'}
        ]

        icicle_widgets = [
            {'kind': 'optionmenu', 'label': 'Column',
                'options': ['Not Available'], 'id': 'column'},
            {'kind': 'entry', 'label': 'Cutoff', 'id': 'cutoff'},
            {'kind': 'entry', 'label': 'Width', 'id': 'width'},
            {'kind': 'entry', 'label': 'Height', 'id': 'height'},
            {'kind': 'entry', 'label': 'Min Char Width', 'id': 'min_char_width'},
            {'kind': 'entry', 'label': 'Colours', 'id': 'colours'},
            {'kind': 'entry', 'label': 'Values', 'id': 'values'},
            {'kind': 'optionmenu', 'label': 'Bool column',
                'options': ['Not Available'], 'id': 'bool_column'}
        ]

        line_widgets = [
            {'kind': 'optionmenu', 'label': 'Y Axis',
                'options': ['Not Available'], 'id': 'y'},
            {'kind': 'optionmenu', 'label': 'Group By',
                'options': ['Not Available'], 'id': 'groupby'}
        ]
        
        test_widgets = [
            {'kind': 'optionmenu', 'label': 'Level 1', 'options': ['Not Available'], 'id': 'lv_1'},
            {'kind': 'optionmenu', 'label': 'Level 2', 'options': ['Not Available'], 'id': 'lv_2'},
            {'kind': 'optionmenu', 'label': 'Level 3', 'options': ['Not Available'], 'id': 'lv_3'},
            {'kind': 'optionmenu', 'label': 'Level 4', 'options': ['Not Available'], 'id': 'lv_4'},
            {'kind': 'optionmenu', 'label': 'Level 5', 'options': ['Not Available'], 'id': 'lv_5'}
        ]
        
        graph_options = {
            'Barplot': barplot_widgets,
            'Wordcloud': wordcloud_widgets,
            'Line': line_widgets,
            'Icicle': icicle_widgets,
            # 'Test': test_widgets
        }
        

        self.graph_options = LabelFrameInput(self.left_frame, graph_options, text='Graph Options', primary='graph_options')

        # Plot labels
        plot_labels = [
            {'kind': 'entry', 'label': 'Title', 'id': 'title'},
            {'kind': 'entry', 'label': 'Subtitle', 'id': 'subtitle'},
            {'kind': 'entry', 'label': 'Y Label', 'id': 'ylab'},
            {'kind': 'entry', 'label': 'X Label', 'id': 'xlab'},
            {'kind': 'checkbutton', 'label': 'xkcd', 'id': 'xkcd'}
        ]
        self.plot_labels = LabelFrameInput(self.left_frame, plot_labels, text='Graph Labels')

        plot_btn = ttk.Button(self.left_frame, text='Plot', command=self.plot)
        plot_btn.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.data_input.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.plot_labels.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        self.graph_options.pack(side=tk.TOP, fill='both',
                                expand=True, padx=5, pady=5)

        """
        Middle frame widgets
        """
        # Notebook
        self.notebook = CustomNotebook(self.mid_frame)
        self.notebook.pack(fill='both', expand=True)

        """
        Bottom frame widgets
        """

        # Pack the frames
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.mid_frame.pack(side=tk.LEFT, fill='both', expand=True)

    def get_data(self):
        "Allows user input CSV and then adjusts the various widgets accordingly"
        try:
            file_types = [('CSV files', '.csv')]
            filename = filedialog.askopenfilename(filetypes=file_types)

            with open(filename, 'r', encoding='utf-8') as data_file:
                self.base = None
                self.data = None
                gc.collect()   # Try to reduce the memory footprint of the loaded data as much as possible
                data = read_csv(data_file)
                compress_dataframe(data)
                self.base = data
                self.data = self.base.copy(deep=True)

            try:
                self.table.destroy()
                self.table = DataTable(self.bottom_frame, data.head(50).copy(), None)
                self.table.pack(fill='both', expand=True)
            except:
                self.table = DataTable(self.bottom_frame, data.head(50).copy(), None)
                self.table.pack(fill='both')

            "Add column values to the various dropdown menus"
            df_columns = list(data.columns)
            for widget in self.graph_options.inputs.values():
                try:
                    for dictionary in widget:
                        if dictionary['id'] in {'column', 'bool_column', 'y', 'groupby'}:
                            if dictionary['id'] == 'groupby':
                                copy = df_columns.copy()
                                copy.insert(0, 'None')
                                dictionary['options'] = copy
                            else:
                                dictionary['options'] = df_columns
                except TypeError:
                    pass

            "Add filter columns (only categorical or object columns)"
            temp_list = [dict(kind='combo', label=i, id=i, values=data[i].value_counts(ascending=False).index)
                         for i in data.select_dtypes(['object', 'category']).columns]
            temp_list.append(dict(kind='entry', label='Nr. of Rows', id='rows', validate='int'))


            self.data_input.inputs = temp_list

            # Scrollable Frames
            # self.data_input.scroll = True
            # self.graph_options.scroll = True

            # Enable widgets
            self.data_input.is_data = True
            self.graph_options.is_data = True
            self.plot_labels.is_data = True

            self.data_input.update()
            self.graph_options.update()
            self.plot_labels.update()

            messagebox.showinfo(title='Data entry',
                                message=f'{os.path.basename(filename)} has been read.')

            return os.path.basename(filename)

        except FileNotFoundError:
            title = 'Data entry'
            message = 'File was not selected properly. Please select file properly.'
            messagebox.showerror(title=title, message=message)

    def plot(self):

        if self.data is None:
            title = 'No Data'
            message = 'There is no data provided to the application.'
            messagebox.showerror(title=title, message=message)

        else:
            kind = self.graph_options.graph_type.get()
            options = self.graph_options.values[kind] if kind in self.graph_options.values else None
            labels = self.plot_labels.values

            frame = NotebookTab(self.notebook, notebook=self.notebook,
                                data=self.data, kind=kind, options=options, labels=labels)
            if frame.is_empty:
                pass
            else:
                title = labels['title'].get()
                title = title.strip()
                title = title if title else f'graph {len(self.notebook.tabs()) + 1}'
                title = f'{kind} - {title}'
                self.notebook.add(frame, text=title)
                self.notebook.select(frame)

    def filter_data(self):
        options = self.data_input.values

        for key, val in options.items():
            text = val.get().strip()
            
            if text:
                try: 
                    self.data = self.data[~(self.data[key].astype(str)==text)].reset_index(drop=True)
                except:
                    rows = val.get()
                    length = len(self.data.index)
                    rows = int(rows) if rows.isdigit() else length
                    rows = min(rows, length)
                    self.data = self.data.head(rows)
                                
                try:
                    val.set("")
                except AttributeError:
                    val.delete(0, 'end')
        
        self.table.update(self.data.head(50))
        
    def clear_filter(self):
        self.data = self.base.copy(deep=True)
        self.table.update(self.data.head(50).copy())


def main():
    root = tk.Tk()
    root.title('GUI Implementation')
    root.state('zoomed')

    window_1 = MainWindow(root)
    window_1.pack(expand=True, fill='both')

    root.mainloop()


if __name__ == "__main__":
    main()
