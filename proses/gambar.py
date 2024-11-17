import streamlit as st
from io import BytesIO
from PIL import Image
import numpy as np



def encyStegano(text, key, is_enc, file_data, upload_image):
    # Periksa apakah key kosong
    if not key:
        st.error("Key harus diisi sebelum menyisipkan pesan.")
        return

    # Konversi gambar menjadi array numpy
    image = Image.open(upload_image)
    image_np = np.array(image)

    # Convert message to binary
    binary_text = ''.join(format(ord(char), '08b') for char in text)
    binary_key = format(int(key), '08b')  # Kunci dalam format biner

    # Loop untuk menyisipkan pesan ke dalam bit terakhir dari setiap piksel
    data_index = 0
    for i in range(image_np.shape[0]):
        for j in range(image_np.shape[1]):
            pixel = image_np[i, j]
            for k in range(3):  # Untuk setiap kanal RGB
                if data_index < len(binary_text):
                    pixel[k] = int(bin(pixel[k])[:-1] + binary_text[data_index], 2)
                    data_index += 1
                else:
                    break
        if data_index >= len(binary_text):
            break

    # Simpan gambar hasil steganografi
    stego_image = Image.fromarray(image_np)
    stego_image.save("stego_image.png")
    st.image("stego_image.png", caption="Gambar dengan Pesan Tersimpan", use_column_width=True)
    st.download_button(
        label="💾 Unduh Gambar dengan Pesan",
        data=open("stego_image.png", "rb"),
        file_name="stego_image.png",
        mime="image/png"
    )
    st.success("Pesan berhasil disisipkan ke dalam gambar.")

# Fungsi untuk mendekripsi pesan dari gambar
def decyStegano(key, file_data, upload_image):
    if not key:
        st.error("Key harus diisi sebelum mengekstraksi pesan.")
        return

    # Konversi gambar menjadi array numpy
    image = Image.open(upload_image)
    image_np = np.array(image)

    # Ekstraksi pesan dari bit terakhir setiap piksel
    binary_text = ''
    for i in range(image_np.shape[0]):
        for j in range(image_np.shape[1]):
            pixel = image_np[i, j]
            for k in range(3):  # Untuk setiap kanal RGB
                binary_text += bin(pixel[k])[-1]  # Dapatkan bit terakhir

    # Konversi dari biner ke teks
    decoded_text = ''.join(chr(int(binary_text[i:i+8], 2)) for i in range(0, len(binary_text), 8))

    # Tampilkan hasil ekstraksi
    st.text_area("Pesan yang Diekstrak", value=decoded_text, height=100)
    st.success("Pesan berhasil diekstraksi.")
 