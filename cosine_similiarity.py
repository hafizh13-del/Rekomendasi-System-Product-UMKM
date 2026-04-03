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
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# Fungsi untuk filter produk berdasarkan ukuran
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
    
def search_product():
    keyword = search_product.get().strip().lower()
    
    # Cari produk berdasarkan nama_produk yang mengandung kata kunci
    search_results = product_data[product_data['nama_produk'].str.lower().str.contains(keyword)]
    
    if len(search_results) == 0:
        tk.messagebox.showinfo("Info", f"Tidak ditemukan produk dengan kata kunci '{keyword}'")
    else:
        # Tampilkan produk yang ditemukan dalam combobox_item
        combobox_item['values'] = search_results['nama_produk'].tolist()
        combobox_item.current(0)  # Set default value to the first item found
        recommend_items()  # Panggil fungsi rekomendasi setelah pencarian

# Membuat komponen
root = tk.Tk()
root.title('Sistem Rekomendasi UMKM ALBIS')


# Frame utama dengan latar belakang transparan
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

def show_cosine_similarity():
    selected_product = combobox_item.get()
    selected_product_id = product_data[product_data['nama_produk'] == selected_product].index[0]

    # Ambil cosine similarity dari produk yang dipilih dengan produk lainnya
    similarities = similarity_matrix.loc[selected_product_id, :].sort_values(ascending=False)
    
    # Membersihkan frame hasil
    for widget in result_frame.winfo_children():
        widget.destroy()
    
    # Menampilkan hasil cosine similarity dengan gambar dan informasi
    for idx, (index, similarity_score) in enumerate(similarities.items()):
        if index != selected_product_id:  # Jangan tampilkan produk yang dipilih
            row = product_data.loc[index]
            img_path = row['gambar']  # Assuming the column 'gambar' contains the path to the images
            img = Image.open(img_path)
            img = img.resize((100, 100), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)

            img_label = tk.Label(result_frame, image=img, bg="lightblue")
            img_label.image = img  # Keep a reference to avoid garbage collection
            img_label.pack(padx=5, pady=5, side=tk.LEFT)

            info = f"{row['nama_produk']}\nSimilarity: {similarity_score:.2f}"
            info_label = tk.Label(result_frame, text=info, bg="lightblue", fg="black")
            info_label.pack(padx=10, pady=20, side=tk.LEFT)

# Tambahkan tombol untuk menampilkan hasil cosine similarity
show_similarity_button = tk.Button(main_frame, text="Tampilkan Cosine Similarity", command=show_cosine_similarity, bg="purple", fg="white", font=('Helvetica', 12, 'bold'))
show_similarity_button.pack(padx=5, pady=10)

# Menampilkan aplikasi
root.mainloop()
def get_widget(comp):
    for widget in root.winfo_children():
        if isinstance(widget, comp):
            return widget
    return None

#menjalakan aplikasi
root.mainloop()

 