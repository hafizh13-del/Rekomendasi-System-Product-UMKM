import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import pandas as pd
from sklearn import preprocessing
from sklearn.metrics import mean_squared_error, root_mean_squared_error
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image

# 2. Membuat Matriks Rating Item Pengguna
rating_data = pd.read_csv('./data/dataratingproduk-2.csv')
rating_matrix = rating_data.pivot_table(index='idp', columns='uid', values='rating')

user_data = pd.read_csv('./data/datauseralbis.csv', index_col=0)

# 3. Membersihkan Data yang Hilang
# rating_matrix.isnull().sum(axis=1)
clean_matrix = rating_matrix.fillna(rating_matrix.mean())

# 4. Normalisasi Data
scaler = preprocessing.MinMaxScaler()
normalized_matrix = scaler.fit_transform(clean_matrix)
normalized_matrix = pd.DataFrame(normalized_matrix, columns=clean_matrix.columns, index=clean_matrix.index)

# 5. Menghitung Kesamaan Antar Item
similarity_matrix = cosine_similarity(normalized_matrix)
similarity_matrix = pd.DataFrame(similarity_matrix, columns=normalized_matrix.index, index=normalized_matrix.index)

# 6. Merekomendasikan Beberapa Item Berdasarkan Item yang Dipilih
summary_data = rating_data.groupby('idp').agg({'rating': 'mean', 'uid':'count'}).rename(columns={'uid':'reviewers'})
item_data = pd.read_csv('./data/dataprodukalbis.csv', index_col=0)
item_data = pd.merge(item_data, summary_data, left_on="idp", right_index=True, how="left", sort=False)

root = tk.Tk()
root.title('Load Product Data from CSV')

combobox = ttk.Combobox(root, values=rating_matrix.index.tolist())
combobox.pack(pady=5)

# 7. Memprediksi Rating Berdasarkan Rating Item Pengguna
def predict_ratings(user_ratings, similarity_matrix):
    predicted_ratings = user_ratings.copy()

    for idp in similarity_matrix.index:
        similar_items = similarity_matrix.loc[idp, :]
        similar_items = similar_items.drop(idp)

        weighted_sum = (similar_items * user_ratings[similar_items.index]).sum()
        total_weight = similar_items.sum()

        if total_weight > 0:
            predicted_rating = weighted_sum / total_weight
        else:
            predicted_rating = user_ratings.mean()

        predicted_ratings.loc[idp] = predicted_rating

    return predicted_ratings

def recomend_items():
    target_idp = combobox.get()
    user_ratings = clean_matrix[target_idp]
    predicted_ratings = predict_ratings(user_ratings, similarity_matrix)

    mse = mean_squared_error(user_ratings, predicted_ratings)
    rmse = root_mean_squared_error(user_ratings, predicted_ratings)

    # 8. Merekomendasikan Beberapa Item Berdasarkan Prediksi Rating Item Pengguna dan Item yang Dipilih
    predicted_ratings = predicted_ratings[predicted_ratings.index!=target_idp]
    predicted_ratings = predicted_ratings.sort_values(ascending=False)

    # 9. Menampilkan Item yang Direkomendasikan ke Sistem
    recommended_items = item_data.loc[predicted_ratings.index]

#button rekomendasi
rekomendasi_button = tk.Button(root, text="Rekomendasi", command=recomend_items)
rekomendasi_button.pack(pady=10)

# Menjalankan aplikasi
root.mainloop()