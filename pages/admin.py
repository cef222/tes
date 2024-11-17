import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import pandas as pd



# Fungsi untuk hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Fungsi untuk verifikasi login
def verify_login(username, password):
    conn = sqlite3.connect('kripto.db')
    c = conn.cursor()
    # cursor() adalah metode yang digunakan untuk membuat objek cursor yang digunakan untuk mengeksekusi perintah SQL
    c.execute("SELECT password, role FROM users WHERE role='admin' AND username=?", (username,))
    # execute() adalah metode yang digunakan untuk mengeksekusi perintah SQL
    result = c.fetchone()
    # fetchone() adalah metode yang digunakan untuk mengambil satu baris hasil dari perintah SQL yang dieksekusi
    conn.close()
    # close() adalah metode yang digunakan untuk menutup koneksi ke database
    
    if result and result[0] == hash_password(password):
        return True, result[1]
    return False, None

# Fungsi untuk menambah user baru
def add_user(username, password, role):
    try:
        with sqlite3.connect('kripto.db') as conn:
            c = conn.cursor()
            
            # Cek apakah username sudah ada
            c.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
            if c.fetchone()[0] > 0:
                return False, "Username sudah digunakan"
            
            # Hash password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Insert user baru
            c.execute("""
                INSERT INTO users (username, password, role, created_at) 
                VALUES (?, ?, ?, datetime('now'))
            """, (username, hashed_password, role))
            
            conn.commit()
            return True, f"User {username} berhasil ditambahkan"

    except sqlite3.Error as e:
        return False, f"Database error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"



# Fungsi untuk mendapatkan semua user
def get_all_users():
    conn = sqlite3.connect('kripto.db')
    users = pd.read_sql_query("SELECT * FROM users", conn)
    # read_sql_query() adalah metode yang digunakan untuk membaca data dari database menggunakan query SQL
    conn.close()
    return users

def get_all_text():
    conn = sqlite3.connect('kripto.db')
    users = pd.read_sql_query("SELECT * FROM text", conn)
    return users

# Fungsi untuk menghapus user
def delete_user(user_id):
    conn = sqlite3.connect('kripto.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=? AND username!='admin'", (user_id,))
    conn.commit()
    conn.close()

def main():
    # Page config
    st.set_page_config(
        page_title="Login - Aplikasi Kriptografi",
        page_icon="🔒",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    
    if not st.session_state.logged_in:
        create_login_ui()
    else:
        display_main_application()

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
                <h1>🔒 Login Admin</h1>
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

def display_main_application():
    

    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'
    
    with st.sidebar:
        st.markdown('<div class="sidebar-title">Menu Admin</div>', unsafe_allow_html=True)
        
        # Menu items list
        menu_items = [
            {"id": "dashboard", "icon": "🏠", "text": "Dashboard"},
            {"id": "users", "icon": "👥", "text": "Data User"},
            {"id": "texts", "icon": "📝", "text": "Data Text"},
            {"id": "add_user", "icon": "➕", "text": "Tambah User"},
            {"id": "logout", "icon": "🚪", "text": "Logout"}
        ]
        
        # Display menu items with navigation
        for item in menu_items:
            is_active = st.session_state.current_page == item["id"]
            active_class = "active" if is_active else ""
            
            if st.button(f"{item['icon']} {item['text']}", key=f"btn-{item['id']}"):
                st.session_state.current_page = item["id"]

        # Handle page navigation
    if st.session_state.current_page == 'dashboard':
        display_dashboard()
    elif st.session_state.current_page == 'users':
        display_user_data()
    elif st.session_state.current_page == 'texts':
        display_text_data()
    elif st.session_state.current_page == 'add_user':
        display_add_user_form()
    elif st.session_state.current_page == 'logout':
        handle_logout()

def display_dashboard():
    st.title("🏠 Dashboard Admin")
    st.write(f"Selamat datang, {st.session_state.username}!")
    if st.session_state.role != 'admin':
        st.error("Maaf, Anda tidak memiliki akses ke halaman ini!")
        return
    
    # Add dashboard content here
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Users", len(get_all_users()))
    with col2:
        st.metric("Total Text Entries", len(get_all_text()))

def display_user_data():
    st.title("👥 Data User")
    
    # Hanya admin yang dapat mengakses halaman ini
    if st.session_state.role != 'admin':
        st.error("Maaf, Anda tidak memiliki akses ke halaman ini!")
        return
    
    # Ambil data semua pengguna
    users_df = get_all_users()
    if users_df.empty:
        st.info("Belum ada pengguna.")
        return
    
    # Tampilkan data pengguna
    st.dataframe(
        users_df,
        column_config={
            "username": "Username",
            "role": "Role",
            "created_at": "Tanggal Dibuat"
        },
        hide_index=True
    )
    
    st.write("### Aksi")
    for index, row in users_df.iterrows():
        if row['id'] == st.session_state.id:
            # Jangan tampilkan tombol hapus untuk admin yang sedang login
            continue
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{row['username']}** (Role: {row['role']})")
        
        with col2:
            if st.button(f"Hapus {row['username']}", key=f"delete_{row['id']}"):
                result = delete_user(row['id'], st.session_state.id)
                st.success(result)
                st.rerun()  # Reload halaman untuk memperbarui daftar


def delete_user(user_id, current_admin_id):
    conn = sqlite3.connect('kripto.db')
    c = conn.cursor()
    
    # Ambil informasi pengguna yang akan dihapus
    c.execute("SELECT id, role FROM users WHERE id = ?", (user_id,))
    user_to_delete = c.fetchone()
    
    if not user_to_delete:
        conn.close()
        return "Pengguna tidak ditemukan."
    
    # Validasi penghapusan
    user_role = user_to_delete[1]
    if user_role == 'admin' and current_admin_id <= user_id:
        # Admin dapat menghapus admin lain jika ID admin yang menghapus lebih kecil
        c.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return "Admin berhasil dihapus."
    elif user_role == 'admin' and current_admin_id > user_id:
        conn.close()
        return "Anda tidak dapat menghapus admin dengan ID yang lebih kecil atau sama."
    else:
        # Hapus pengguna non-admin
        c.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return "Pengguna berhasil dihapus."


def display_text_data():
    st.title("📝 Data Text")
    if st.session_state.role != 'admin':
        st.error("Maaf, Anda tidak memiliki akses ke halaman ini!")
        return
    
    text_df = get_all_text()
    st.dataframe(
        text_df,
        column_config={
            "enkripsi": "Text Terenkripsi",
            "created_at": "Tanggal Dibuat",
            "user_id": "ID User"
        },
        hide_index=True
    )

# Function called when the form is submitted
def on_button_click_add_user(username, password, role):
    add_user(username, password, role)

def display_add_user_form():
    st.title("➕ Tambah User Baru")
    
    # Cek akses admin
    if st.session_state.role != 'admin':
        st.error("Maaf, Anda tidak memiliki akses ke halaman ini!")
        return
    
    with st.form("add_user_form"):
        st.markdown("### Form Tambah User")
        
        # Input untuk username, password, dan role
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        new_role = st.selectbox("Role", ["user", "admin"])

        # Cek jika form disubmit
        if st.form_submit_button("Submit User"):
            # Error handling: jika username atau password kosong
            if not new_username.strip():
                st.error("Username tidak boleh kosong!")
            elif not new_password.strip():
                st.error("Password tidak boleh kosong!")
            else:
                # Jika input valid, coba tambahkan user
                success, message = add_user(new_username, new_password, new_role)
                
                if success:
                    st.success(message)  # Tampilkan pesan sukses jika berhasil
                    st.rerun()  # Reload halaman untuk memperbarui daftar
                else:
                    st.error(message)  # Tampilkan pesan error jika gagal
            
        
def handle_logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.current_page = 'main'
    st.rerun()

if __name__ == "__main__":
    main()