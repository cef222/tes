import streamlit as st
import hashlib
from proses.utliss import is_encrypted
from proses.gambar import encyStegano, decyStegano
from proses.file import encyFile, decyFile
import proses.text as te
import sqlite3
import pandas as pd
import base64
from io import BytesIO 
from PIL import Image

conn = sqlite3.connect('kripto.db')
# Fungsi untuk mengenkripsi password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Fungsi untuk inisialisasi database
def init_db():
    conn = sqlite3.connect('kripto.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         username TEXT UNIQUE NOT NULL,
         password TEXT NOT NULL,
         role TEXT NOT NULL,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS text
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         enkripsi TEXT NOT NULL,
         key TEXT NOT NULL,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         user_id INTEGER NOT NULL,
         FOREIGN KEY(user_id) REFERENCES users(id))
    ''')
    
    # Cek apakah admin default sudah ada
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        # Tambahkan admin default
        admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
        # hashlib adalah modul yang menyediakan fungsi hash yang aman dan cepat
        # sha256() adalah fungsi yang digunakan untuk membuat objek hash SHA-256
        # encode() adalah metode yang digunakan untuk mengonversi string menjadi byte
        # hexdigest() adalah metode yang digunakan untuk mengembalikan representasi string dari data yang di-hash
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                 ('admin', admin_password, 'admin'))
    
    conn.commit()
    # commit() adalah metode yang digunakan untuk menyimpan perubahan yang dilakukan ke database
    conn.close()

def create_login_ui():
    # Custom CSS for login page
    st.markdown("""
        <style>
        /* Main container styling */
        .main-container {
            max-width: 800px;
            margin: auto;
            padding: 20px;
        }
        
        /* Card styling */
        .login-card {
            background-color: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-top: 2rem;
        }
        
        /* Login form styling */
        .login-form {
            padding: 20px;
        }
        
        /* Header styling */
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        /* Input field styling */
        .stTextInput>div>div>input {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ced4da;
        }
        
        /* Button styling */
        .stButton>button {
            width: 100%;
            padding: 10px;
            border: 1px solid #ced4da;
            border-radius: 5px;
            background-color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .stButton>button:hover {
            background-color: #0056b3;
        }
        
        /* Error message styling */
        .stAlert {
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 5px;
        }
        
        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .viewerBadge_container__1QSob {display: none;}
        
        /* Divider styling */
        .divider {
            display: flex;
            align-items: center;
            text-align: center;
            margin: 1rem 0;
        }
        
        .divider::before,
        .divider::after {
            content: '';
            flex: 1;
            border-bottom: 1px solid #ced4da;
        }
        
        .divider span {
            padding: 0 10px;
            color: #6c757d;
            font-size: 0.9rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Page layout
    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        # Login card container
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        # Header
        st.markdown("""
            <div class="login-header">
                <h1>🔒 Login User</h1>
                <p style="color: #6c757d;">Selamat datang di Aplikasi Kriptografi</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Login form
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Masukkan username Anda")
            password = st.text_input("Password", type="password", placeholder="Masukkan password Anda")
            
            
            submit = st.form_submit_button("Login")
            
            if submit:
                conn = sqlite3.connect('kripto.db')
                verify_credentials = conn.execute(
                    f"SELECT * FROM users WHERE username = '{username}' AND password = '{hash_password(password)}'"
                ).fetchone()
                
                if verify_credentials:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.id = verify_credentials[0]
                    st.session_state.role = verify_credentials[3]
                    
                    # Success message with animation
                    success_html = """
                        <div style="display: flex; justify-content: center; margin: 1rem;">
                            <div style="
                                background-color: #d4edda;
                                color: #155724;
                                padding: 1rem;
                                border-radius: 5px;
                                text-align: center;
                                animation: fadeIn 0.5s ease-in;
                            ">
                                ✅ Login berhasil! Mengalihkan...
                            </div>
                        </div>
                    """
                    st.markdown(success_html, unsafe_allow_html=True)
                    st.rerun()
                else:
                    # Error message with animation
                    error_html = """
                        <div style="display: flex; justify-content: center; margin: 1rem;">
                            <div style="
                                background-color: #f8d7da;
                                color: #721c24;
                                padding: 1rem;
                                border-radius: 5px;
                                text-align: center;
                                animation: shake 0.5s ease-in-out;
                            ">
                                ❌ Username atau password salah!
                            </div>
                        </div>
                    """
                    st.markdown(error_html, unsafe_allow_html=True)

# Function to encode the message into the image
def encode_message(message, image):
    encoded_image = image.copy()

    # Encoding the message into the image
    encoded_image.putdata(encode_data(image, message))

    # Save the encoded image
    encoded_image_path = "encoded.png"
    encoded_image.save(encoded_image_path)

    st.success("Image encoded successfully.")
    show_encoded_image(encoded_image_path)


# Function to decode the hidden message from the image
def decode_message(image, key):
    # Decode the hidden message from the image
    decoded_message = decode_data(image)
    decripted_message = te.rail_fence_decrypt(decoded_message, key)
    # show_decoded_image(image)  # Call the function to display the decoded image
    return decripted_message


# Function to display the decoded image in the UI
# def show_decoded_image(decoded_image):
#     st.image(decoded_image, caption="Decoded Image", use_column_width=True)


# Function to encode the data (message) into the image
def encode_data(image, data):
    data = data + "$"  # Adding a delimiter to identify the end of the message
    data_bin = ''.join(format(ord(char), '08b') for char in data)

    pixels = list(image.getdata())
    encoded_pixels = []

    index = 0
    for pixel in pixels:
        if index < len(data_bin):
            red_pixel = pixel[0]
            new_pixel = (red_pixel & 254) | int(data_bin[index])
            encoded_pixels.append((new_pixel, pixel[1], pixel[2]))
            index += 1
        else:
            encoded_pixels.append(pixel)

    return encoded_pixels


# Function to decode the data (message) from the image
def decode_data(image):
    pixels = list(image.getdata())

    data_bin = ""
    for pixel in pixels:
        # Extracting the least significant bit of the red channel
        data_bin += bin(pixel[0])[-1]

    data = ""
    for i in range(0, len(data_bin), 8):
        byte = data_bin[i:i + 8]
        data += chr(int(byte, 2))
        if data[-1] == "$":
            break

    return data[:-1]  # Removing the delimiter


# Function to display the encoded image in the UI and add a download button
def show_encoded_image(image_path):
    encoded_image = Image.open(image_path)

    st.image(encoded_image, caption="Encoded Image", use_column_width=True)

    buffered = BytesIO()
    encoded_image.save(buffered, format="PNG")

    img_str = base64.b64encode(buffered.getvalue()).decode()

    href = ('<a href="data:file/png;base64,' + img_str + '" '
            'download="' + image_path + '">Download Encoded Image</a>')

    st.markdown(href, unsafe_allow_html=True)


#  Fungsi untuk menampilkan aplikasi utama
def main_app():
    # ============= KONFIGURASI APLIKASI =============
    st.title("🔒 Aplikasi Kriptografi")
    st.markdown("Aplikasi yang dapat menyembunyikan dan memecahkan rahasia text, gambar, dan file")
    tab1, tab2, tab3 = st.tabs(["📝 Enkripsi Text", "📁 Enkripsi File", "📸 Steganografi Gambar"])

    # ============= TAB 1: TEXT =============
    with tab1:
        st.header("Super Encryption Text dengan Rail Fence, dan RC4")
        
        with st.expander("ℹ️ Informasi Metode Enkripsi"):
            st.markdown("""
            - **Rail Fence**: Menggunakan kata kunci angka
            - **RC4**: Stream cipher dengan key string
            - **Super Encryption**: Kombinasi Rail Fence  + RC4
            """)
        left_col, right_col = st.columns(2)
        
        with left_col:
            st.subheader("🔒 Enkripsi")
            input_text_encrypt = st.text_area("Masukkan Text untuk Enkripsi", height=100, key="encrypt_input")
            keyRail = st.text_input("Masukkan Key Rail", type="password")
            keyRC4 = st.text_input("Masukkan Key RC4", type="password")
            
            if st.button("🔒 Enkripsi", key="encrypt_button"):
                try:
                    if input_text_encrypt:
                        result = te.super_encrypt(input_text_encrypt, keyRail, keyRC4)
                        st.text_area("Hasil Enkripsi", result, height=100)
                        if result:
                            conn = sqlite3.connect('kripto.db')
                            c = conn.cursor()
                            if 'id' in st.session_state:
                                c.execute("INSERT INTO text (user_id, enkripsi, key) VALUES (?, ?, ?)", 
                                        (st.session_state.id, result, str(keyRail)+"|"+str(keyRC4)))
                            else:
                                st.error("Login Dulu")
                            conn.commit()
                            conn.close()
                            st.success("Data berhasil disimpan.")
                    else:
                        st.error("Masukkan text yang akan dienkripsi")
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {str(e)}")

        with right_col:
            st.subheader("🔓 Dekripsi")
            input_text_decrypt = st.text_area("Masukkan Text untuk Dekripsi", height=100, key="decrypt_input")
            keyRail_decrypt = st.text_input("Masukkan Key Rail untuk Dekripsi", type="password")
            keyRC4_decrypt = st.text_input("Masukkan Key RC4 untuk Dekripsi", type="password")
            
            if st.button("🔓 Dekripsi", key="decrypt_button"):
                try:
                    if input_text_decrypt:
                        result = te.super_decrypt(input_text_decrypt, keyRail_decrypt, keyRC4_decrypt)
                        st.text_area("Hasil Dekripsi", result, height=100)
                        if result:
                            st.success("Data berhasil didekripsi.")
                    else:
                        st.error("Masukkan text yang akan didekripsi")
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {str(e)}")


    # ============= TAB 2: ENKRIPSI FILE =============
    with tab2:
        st.header("Enkripsi File dengan Fernet")
        mode = st.radio("Pilih Mode:", ("🔒 Enkripsi", "🔓 Dekripsi"))
        
        if mode == "🔒 Enkripsi":
            encyFile()
        else:
            decyFile()

    # ============= TAB 3: STEGANOGRAFI GAMBAR =============
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.header("Encode")
            pesan = st.text_input("Masukkan Pesan Rahasia")
            key: int = st.text_input("Masukkan Kunci", type="password", key='encode')
            message = te.rail_fence_encrypt(pesan, key)
            # password = col1.text_input("Enter Password", type="password")
            image_file = st.file_uploader("Pilih Gambar", type=["png", "jpg", "jpeg"])
        with col2:
            st.header("Encoded Image")
            if message and image_file:
                image = Image.open(image_file)
                encode_message(message, image)

        st.markdown("---")

        col3, col4 = st.columns(2)
        with col3:
            st.header("Decode")
            keyDecy = st.text_input("Masukkan Kunci", type="password", key='decode')
        with col4:
            st.header("Pesan Rahasia")

        # decode_password = col3.text_input("Enter Password for Decoding", type="password")
        decode_image_file = col3.file_uploader(
            "Pilih Gambar yang Ingin diketahui pesannya", type=["png", "jpg", "jpeg"]
        )

        if decode_image_file:
            decode_image = Image.open(decode_image_file)
            col4.write("Pesan Rahasia: " + decode_message(decode_image, keyDecy))
        

def display_main_application():
    # Sidebar Navigation
    with st.sidebar:
        st.title("Menu Users")
        show_data = st.button("Data Text")
        logout = st.button("Logout")
    
    # Main Content Area
    if show_data:
        # Tampilkan hanya data pengguna
        handle_data()
    elif logout:
        # Tangani logout
        handle_logout()
    else:
        # Jika tidak memilih "Data Text", tampilkan aplikasi utama
        main_app()

def handle_data():
    st.header("Data Text")
    conn = sqlite3.connect('kripto.db')
    user_id = st.session_state.get('id', None)
    
    if user_id is not None:
        query = "SELECT * FROM text WHERE user_id = ?"
        data = pd.read_sql_query(query, conn, params=(user_id,))
        if not data.empty:
            st.dataframe(data)
        else:
            st.info("Belum ada data yang disimpan.")
    else:
        st.error("Terjadi kesalahan: Anda belum login.")
    
    conn.close()


def handle_logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.current_page = 'main'
    st.rerun()

def main():
    # Page config
    st.set_page_config(
        page_title="Login - Aplikasi Kriptografi",
        page_icon="🔒",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        create_login_ui()
    else:
        display_main_application()

if __name__ == "__main__":
    init_db()
    main()