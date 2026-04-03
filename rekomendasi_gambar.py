#import library
from sklearn import preprocessing
from sklearn.metrics import mean_squared_error
from sklearn.metrics.pairwise import cosine_similarity
from tkinter import ttk
from PIL import Image, ImageTk

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
    target_item_id = product_data[product_data['nama_produk'] == target_item_name].index[0]

    # Cari ID user berdasarkan profesi
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
        row = product_data.loc[index]
        img_path = row['gambar']  # Assuming the column 'gambar' contains the path to the images
        img = Image.open(img_path)
        img = img.resize((100, 100), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)
        
        img_label = tk.Label(result_frame, image=img)
        img_label.image = img  # Keep a reference to avoid garbage collection
        img_label.pack(padx=5, pady=5, side=tk.LEFT)

        info = f"{row['nama_produk']}\nHarga:{row['harga']}\nBerat:{row['berat_gram']}\nUkuran:{row['ukuran']}\nRating: {predicted_ratings[index]:.2f}"
        info_label = tk.Label(result_frame, text=info)
        info_label.pack(padx=8, pady=20, side=tk.LEFT)
        
#membuat fungsi kaetegori berdasarkan ukuran
def filter_by_size(size_category): 
    filtered_products = product_data[product_data['kategori'] == size_category]
    for widget in result_frame.winfo_children():
        widget.destroy()
        
        # Menampilkan hasil kategori dengan gambar dan informasi
    for index, row in filtered_products.iterrows():
        img_path = row['gambar']
        img = Image.open(img_path)
        img = img.resize((100, 100), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)
        
        img_label = tk.Label(result_frame, image=img)
        img_label.image = img  # Keep a reference to avoid garbage collection
        img_label.pack(padx=5, pady=5, side=tk.LEFT)

        info = f"{row['nama_produk']}\nHarga: {row['harga']}\nBerat: {row['berat_gram']} gram\nUkuran: {row['ukuran']}"
        info_label = tk.Label(result_frame, text=info)
        info_label.pack(padx=10, pady=20, side=tk.LEFT)

        
def get_widget(comp):
    for widget in root.winfo_children():
        if isinstance(widget, comp):
            return widget
    return None


# Membuat komponen button

#root tk membuat jendela utama sistem thinker
root = tk.Tk()
root.title('Sistem Rekomendasi UMKM ALBIS')

label_item = tk.Label(root, text="Cari Produk:")
label_item.pack(padx=5, pady=[5, 2])

combobox_item = ttk.Combobox(root, values=product_data['nama_produk'].tolist())
combobox_item.pack(padx=5, pady=1)

label_user = tk.Label(root, text="Pilih User:")
label_user.pack(padx=5, pady=[5, 2])

combobox_user = ttk.Combobox(root, values=user_data['profesi'].tolist())
combobox_user.pack(padx=5, pady=1)

rekomendasi_button = tk.Button(root, text="Rekomendasi Barang", command=recommend_items)
rekomendasi_button.pack(padx=5, pady=10)

result_frame = tk.Frame(root)
result_frame.pack(padx=10, pady=10)

# Title untuk filter ukuran
label_filter = tk.Label(root, text="Kategori")
label_filter.pack(padx=5, pady=[10, 5])

# Frame untuk tombol filter
filter_frame = tk.Frame(root)
filter_frame.pack(padx=10, pady=10)

kecil_button = tk.Button(filter_frame, text="Kecil", command=lambda: filter_by_size('Kecil'))
kecil_button.pack(side=tk.LEFT, padx=5, pady=5)

sedang_button = tk.Button(filter_frame, text="Sedang", command=lambda: filter_by_size('Sedang'))
sedang_button.pack(side=tk.LEFT, padx=5, pady=5)

besar_button = tk.Button(filter_frame, text="Besar", command=lambda: filter_by_size('Besar'))
besar_button.pack(side=tk.LEFT, padx=5, pady=5)

result_frame = tk.Frame(root)
result_frame.pack(padx=10, pady=1)

#menjalakan aplikasi
root.mainloop()

 