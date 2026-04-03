import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd

# Fungsi untuk memuat file CSV
# def load_csv():
#     file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
#     if file_path:
#         try:
#             df = pd.read_csv('./data/dataprodukalbis.csv', index_col=0)
#             if 'nama_produk' in df.columns and 'idp' in df.columns:
#                 global item_data
#                 item_data = df.set_index('idp')  # Menggunakan kolom 'idp' sebagai index
#                 combobox['values'] = item_data.index.tolist()
#             else:
#                 messagebox.showerror("Error", "Kolom 'idp' atau 'nama_produk' tidak ditemukan di file CSV.")
#         except Exception as e:
#             messagebox.showerror("Error", f"Gagal membaca file CSV: {e}")

item_data = pd.read_csv('./data/dataprodukalbis.csv', index_col=0)

# Fungsi untuk memformat dan menampilkan pilihan yang dipilih
# def format_func(event):
#     selected_idp = combobox.get()
#     if selected_idp:
#         label_selected.config(text=f"Selected: {item_data['nama_produk'].loc[int(selected_idp)]}")

# Membuat jendela utama
root = tk.Tk()
root.title('Load Product Data from CSV')

# Membuat tombol untuk memuat file CSV
# load_button = tk.Button(root, text="Load CSV", command=load_csv)
# load_button.pack(pady=10)

# Membuat label untuk Combobox
label_combobox = tk.Label(root, text="Pilih Item:")
label_combobox.pack(pady=5)

# Membuat dan mengkonfigurasi Combobox
combobox = ttk.Combobox(root, values=item_data['nama_produk'])
combobox.pack()
# combobox.bind("<<ComboboxSelected>>", format_func)

# Membuat label untuk menampilkan pilihan yang dipilih
# label_selected = tk.Label(root, text="Selected: ")
# label_selected.pack(pady=10)

# Menjalankan aplikasi
root.mainloop()
