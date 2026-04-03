#Membuat GUI 

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo

window = tk.Tk()

#membuat background
window.configure(bg="white")

#metode
window.geometry("300x400")

#ukuran jendela
window.resizable(False,False)

window.title("Prototype")

#frame input
input_frame = ttk.Frame(window)
#penempatan Grid, Pack, Place
input_frame.pack(padx=10,pady=10, fill="x", expand=True)

#komponen-komponen
# 1. nama depan label
nama_depan_label = ttk.Label(window, text="Nama Depan")
nama_depan_label.pack(fill="x", expand=True) 

# 2.entry nama depan
NAMA_DEPAN = tk.StringVar()
nama_depan_entry = ttk.Entry(input_frame, textvariable=NAMA_DEPAN)
nama_depan_entry.pack(fill="x", expand=True) 

# 1. nama belakang label
nama_belakang_label = ttk.Label(window, text="Nama belakang")
nama_belakang_label.pack(fill="x", expand=True) 

# 2.entry nama belakang
NAMA_BELAKANG = tk.StringVar()
nama_belakang_entry = ttk.Entry(input_frame, textvariable=NAMA_BELAKANG)
nama_belakang_entry.pack(fill="x", expand=True) 

#tombol
def tombol_click():
    '''fungsi ini akan dipanggil oleh tombol'''
    pesan= f"haalo {NAMA_DEPAN.get()} {NAMA_BELAKANG.get()}, Ganteng"
    showinfo(title='Whazzup', message=pesan)

tombol_sapa = ttk.Button(input_frame, text="sapa", command=tombol_click)
tombol_sapa.pack(fill="x", expand=True, padx='10', pady=10)

#menampilkan output frame
#membuat jendela window
window.mainloop()