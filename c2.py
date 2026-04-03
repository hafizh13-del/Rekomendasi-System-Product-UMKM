import pandas as pd
import tkinter as tk
from tkinter import ttk

item_data = pd.read_csv('./data/dataprodukalbis.csv', index_col=0)

root = tk.Tk()

def format_func(event):
    selected_id = combobox.get()
    if selected_id:
        label_selected.config(text=f"Selected: {item_data['nama_produk'].loc[int(selected_id)]}")
        
combobox = ttk.Combobox(root, values=item_data.index.tolist())
combobox.pack()
combobox.bind("<<ComboboxSelected>>", format_func)

label_selected = tk.Label(root, text="Selected: ")
label_selected.pack()

root.mainloop()
