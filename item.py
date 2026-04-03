#import library
from sklearn import preprocessing
from sklearn.metrics import mean_squared_error
from sklearn.metrics.pairwise import cosine_similarity
from tkinter import ttk
from PIL import Image, ImageTk

import numpy as np
import pandas as pd
import tkinter as tk

#memasukka data
rating_data = pd.read_csv('.\data\dataratingproduk.csv')
product_data = pd.read_csv('.\data\dataprodukalbis.csv', index_col=0)
user_data = pd.read_csv('.\data\datauseralbis.csv', index_col=0)


rating_matrix = rating_data.pivot_table(index='idp', columns='uid', values='rating')

clean_matrix = rating_matrix.fillna(rating_matrix.mean())

#normalisasi data
scaler = preprocessing.MinMaxScaler()
normalized_matrix = scaler.fit_transform(clean_matrix)
normalized_matrix = pd.DataFrame(normalized_matrix, columns=clean_matrix.columns, index=clean_matrix.index)

#menghitung persamaan antar item
similarity_matrix = cosine_similarity(normalized_matrix)
similarity_matrix = pd.DataFrame(similarity_matrix, columns=normalized_matrix.index, index=normalized_matrix.index)

#menghitung prediksi rating 
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

#membuat fungsi rekomendasi 
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
        
    #membuat hasil menjadi tabel
    tree = get_widget(ttk.Treeview)
        
    if tree:
        tree.destroy()
        
    tree = ttk.Treeview(root, columns=product_data.columns.tolist(), show='headings')
    tree.pack(padx=10, pady=10)
        
    for col in product_data.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)
            
    for index in predicted_ratings.index:
        row = product_data.loc[index]
        tree.insert("", "end", values=row.tolist())

def get_widget(comp):
    for widget in root.winfo_children():
        if isinstance(widget, comp):
            return widget
    return None

#membuat komponen
root = tk.Tk()
root.title('Sistem Rekomendasi UMKM ALBIS')

label_item = tk.Label(root, text="Pilih Item:")
label_item.pack(padx=5, pady=[5, 2])

combobox_item = ttk.Combobox(root, values=product_data['nama_produk'].tolist())
combobox_item.pack(padx=5, pady=1)

label_user = tk.Label(root, text="Pilih User:")
label_user.pack(padx=5, pady=[5, 2])

combobox_user = ttk.Combobox(root, values=user_data['profesi'].tolist())
combobox_user.pack(padx=5, pady=1)

rekomendasi_button = tk.Button(root, text="Rekomendasi", command=recommend_items)
rekomendasi_button.pack(padx=5, pady=10)

root.mainloop()