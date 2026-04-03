#import library
from sklearn import preprocessing
from sklearn.metrics import mean_squared_error
from sklearn.metrics.pairwise import cosine_similarity
from tkinter import ttk
from PIL import Image, ImageTk
import tkinter.messagebox as messagebox

import numpy as np
import pandas as pd
import tkinter as tk

# Memasukkan data
rating_data = pd.read_csv('./data/dataratingproduk.csv')
product_data = pd.read_csv('./data/dataprodukalbis.csv', index_col=0)
user_data = pd.read_csv('./data/datauseralbis.csv', index_col=0)

#mengklasiikasikan ukuran produk berdasarkan data produk
def map_size_to_category(size):
    if 'kecil' in size.lower():
        return 'Kecil'
    elif 'sedang' in size.lower():
        return 'Sedang'
    elif 'besar' in size.lower():
        return 'Besar'
    else:
        return 'Tidak Diketahui'

#mengaplikasikan map size kedalam data produk
product_data['kategori'] = product_data['ukuran'].apply(map_size_to_category)

# Fungsi untuk filter produk berdasarkan ukuran
# def size adalah fungsi dari thinker untuk mengatur ukuran
def filter_by_size(size):
    filtered_data = product_data[product_data['kategori'] == size]

    # Membersihkan frame hasil
    for widget in result_frame.winfo_children():
        widget.destroy()

    # Menampilkan hasil filter dengan gambar dan informasi
    for index, row in filtered_data.iterrows():
        img_path = row['gambar']  # Assuming the column 'gambar' contains the path to the images
        img = Image.open(img_path)
        img = img.resize((100, 100), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)

        img_label = tk.Label(result_frame, image=img, bg="lightblue")
        img_label.image = img  # Keep a reference to avoid garbage collection
        img_label.pack(padx=5, pady=5, side=tk.LEFT)

        info = f"{row['nama_produk']}\nHarga: {row['harga']}\nBerat: {row['berat_gram']} gram\nUkuran: {row['ukuran']}"
        info_label = tk.Label(result_frame, text=info, bg="lightblue", fg="black")
        info_label.pack(padx=10, pady=20, side=tk.LEFT)

#membuat data menjadi tabel pivot
rating_matrix = rating_data.pivot_table(index='idp', columns='uid', values='rating')

#membersihkan data yang hilang
clean_matrix = rating_matrix.fillna(rating_matrix.mean())

# Normalisasi data
scaler = preprocessing.MinMaxScaler()
normalized_matrix = scaler.fit_transform(clean_matrix)
normalized_matrix = pd.DataFrame(normalized_matrix, columns=clean_matrix.columns, index=clean_matrix.index)

# Menghitung kemiripan antar item
similarity_matrix = cosine_similarity(normalized_matrix)
similarity_matrix = pd.DataFrame(similarity_matrix, columns=normalized_matrix.index, index=normalized_matrix.index)

# Menghitung prediksi rating 
def predict_ratings(user_ratings, similarity_matrix):
    predicted_ratings = user_ratings.copy()

    for item_id in similarity_matrix.index:
        similar_items = similarity_matrix.loc[item_id, :]
        similar_items = similar_items.drop(item_id)

        weighted_sum = (similar_items * user_ratings[similar_items.index]).sum()
        total_weight = similar_items.sum()

        if total_weight > 0:
            predicted_rating = weighted_sum / total_weight
        else:
            predicted_rating = user_ratings.mean()

        predicted_ratings.loc[item_id] = predicted_rating

    return predicted_ratings

# Membuat fungsi rekomendasi 
def recommend_items():
    target_item_name = combobox_item.get()
    target_user_profession = combobox_user.get()

    # Cari ID item berdasarkan nama produk
    if target_item_name not in product_data['nama_produk'].values:
        messagebox.showerror("Error", "Produk tidak ditemukan!")
        return

    target_item_id = product_data[product_data['nama_produk'] == target_item_name].index[0]

    # Cari ID user berdasarkan profesi
    if target_user_profession not in user_data['profesi'].values:
        messagebox.showerror("Error", "User tidak ditemukan!")
        return

    target_user_id = user_data[user_data['profesi'] == target_user_profession].index[0]

    similar_items = similarity_matrix[target_item_id]
    similar_items = similar_items[similar_items.index != target_item_id]
    similar_items = similar_items.sort_values(ascending=False)

    user_ratings = clean_matrix[target_user_id]
    predicted_ratings = predict_ratings(user_ratings, similarity_matrix)

    predicted_ratings = predicted_ratings[predicted_ratings.index != target_item_id]
    predicted_ratings = predicted_ratings.sort_values(ascending=False)

    # Membersihkan frame hasil
    for widget in result_frame.winfo_children():
        widget.destroy()
    
    # Menampilkan hasil rekomendasi dengan gambar dan informasi
    for index in predicted_ratings.index:
        #row = baris
        row = product_data.loc[index]
        
        #memasukkan source gambar ke dalam baris di data produk
        img_path = row['gambar']  # Assuming the column 'gambar' contains the path to the images
        img = Image.open(img_path)
        
        #mengatur ukuran gambar
        img = img.resize((100, 100), Image.LANCZOS)
        
        #thinker membaca gambar yang diberikan
        img = ImageTk.PhotoImage(img)
        
        #menampilkan gambar
        img_label = tk.Label(result_frame, image=img)
        img_label.image = img  # Keep a reference to avoid garbage collection
        img_label.pack(padx=5, pady=5, side=tk.LEFT)
        
        #memasukkan data nama produk, harga, berat, ukuran, dan rating pada hasil rekomendasi
        #\n (new line) membuat baris baru
        info = f"{row['nama_produk']}\nHarga:{row['harga']}\nBerat:{row['berat_gram']}\nUkuran:{row['ukuran']}\nRating: {predicted_ratings[index]:.2f}"
        info_label = tk.Label(result_frame, text=info)
        info_label.pack(padx=8, pady=20, side=tk.LEFT)
        
#membuat fungsi kategori berdasarkan ukuran
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk



# Membuat komponen
root = tk.Tk()
root.title('Sistem Rekomendasi UMKM ALBIS')


# Frame utama dengan latar belakang transparan
# fungsi pack digunakan untuk menampilkan komponen
main_frame = tk.Frame(root, bg='lightblue')
main_frame.pack(padx=20, pady=20, fill='both', expand=True)

label_item = tk.Label(main_frame, text="Pilih Item:", bg="lightblue", fg="black", font=('Helvetica', 12, 'bold'))
label_item.pack(padx=5, pady=[5, 2])

combobox_item = ttk.Combobox(main_frame, values=product_data['nama_produk'].tolist())
combobox_item.pack(padx=5, pady=1)

label_user = tk.Label(main_frame, text="Pilih User:", bg="lightblue", fg="black", font=('Helvetica', 12, 'bold'))
label_user.pack(padx=5, pady=[5, 2])

combobox_user = ttk.Combobox(main_frame, values=user_data['profesi'].tolist())
combobox_user.pack(padx=5, pady=1)

rekomendasi_button = tk.Button(main_frame, text="Rekomendasi", command=recommend_items, bg="darkblue", fg="white", font=('Helvetica', 12, 'bold'))
rekomendasi_button.pack(padx=5, pady=10)

# Title untuk filter ukuran
label_filter = tk.Label(main_frame, text="KATEGORI", bg="lightblue", fg="black", font=('Helvetica', 12, 'bold'))
label_filter.pack(padx=5, pady=[10, 5])

# Frame untuk tombol filter
filter_frame = tk.Frame(main_frame, bg="lightblue")
filter_frame.pack(padx=10, pady=10)

kecil_button = tk.Button(filter_frame, text="Kecil", command=lambda: filter_by_size('Kecil'), bg="green", fg="white", font=('Helvetica', 10, 'bold'))
kecil_button.pack(side=tk.LEFT, padx=5, pady=5)

sedang_button = tk.Button(filter_frame, text="Sedang", command=lambda: filter_by_size('Sedang'), bg="orange", fg="white", font=('Helvetica', 10, 'bold'))
sedang_button.pack(side=tk.LEFT, padx=5, pady=5)

besar_button = tk.Button(filter_frame, text="Besar", command=lambda: filter_by_size('Besar'), bg="red", fg="white", font=('Helvetica', 10, 'bold'))
besar_button.pack(side=tk.LEFT, padx=5, pady=5)

result_frame = tk.Frame(main_frame, bg="lightblue")
result_frame.pack(padx=10, pady=10)
        
def get_widget(comp):
    for widget in root.winfo_children():
        if isinstance(widget, comp):
            return widget
    return None


# Membuat Canvas dan Scrollbar untuk result_frame
canvas = tk.Canvas(main_frame, bg="lightblue")
result_frame = tk.Frame(canvas, bg="lightblue")
h_scrollbar = tk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=canvas.xview)
canvas.configure(xscrollcommand=h_scrollbar.set)

# Mengatur posisi canvas dan scrollbar
canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

# Menempatkan frame di dalam canvas
canvas.create_window((0, 0), window=result_frame, anchor='nw')

# Memastikan frame bisa di-scroll
result_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Fungsi untuk menambahkan widget di dalam result_frame
def add_widget_to_result_frame(widget):
    widget.pack(padx=10, pady=10)

#menjalakan aplikasi
root.mainloop()

 