import tkinter as tk
from tkinter import ttk, font, filedialog, messagebox
from pandas import read_csv
from copy import deepcopy
import os

from custom_tkinter import LabelFrameInput, CustomNotebook, NotebookTab


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
                           ('entry', {'label': 'Nr. of categories'})]
        wordcloud_widgets = [
            ('optionmenu', {'label': 'Column', 'options': ['Not available']}),
            ('optionmenu', {'label': 'BG color', 'options': ['White', 'Black', 'Transparent']})]
        graph_options = {
            'Barplot': barplot_widgets,
            'Wordcloud': wordcloud_widgets
        }
        self.graph_options = LabelFrameInput(
            self.left_frame, graph_options, text='Graph Options', primary='graph_options')

        # Plot labels
        plot_labels = [('entry', {'label': 'Title'}), ('entry', {'label': 'Subtitle'}), ('entry', {
            'label': 'Y Label'}), ('entry', {'label': 'X Label'}), ('checkbutton', {'label': 'xkcd'})]
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
                               ('entry', {'label': 'Nr. of categories'})]

            wordcloud_widgets = [
                ('optionmenu', {'label': 'Column', 'options': df_columns}),
                ('optionmenu', {'label': 'BG color', 'options': ['White', 'Black', 'Transparent']})]

            self.graph_options.inputs = {
                'Barplot': barplot_widgets,
                'Wordcloud': wordcloud_widgets
            }

            self.data_input.is_data = True
            self.graph_options.is_data = True
            self.plot_labels.is_data = True

            messagebox.showinfo(title='Data entry',
                                message='File has been read.')

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

            frame = NotebookTab(self.notebook, notebook=self.notebook,
                                data=self.data, kind=kind, options=options, labels=labels)
            if frame.is_empty:
                pass
            else:
                title = labels['Title'].get()
                title = title if title else f'graph {len(self.notebook.tabs()) + 1}'
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
