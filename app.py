import streamlit as st
import pandas as pd
from firebase_admin import credentials, initialize_app, db, _apps

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Scanner Saham Low Price",
    page_icon="📈",
    layout="wide"
)

# --- FUNGSI INISIALISASI FIREBASE ---
def init_firebase():
    if not _apps:
        try:
            # Mengambil data dari menu "Manage app" -> "Settings" -> "Secrets"
            fb_conf = st.secrets["firebase"]
            
            # Konversi Secret menjadi dictionary yang dikenali Firebase
            # Kita gunakan dict(fb_conf) agar format private_key otomatis tertangani
            fb_dict = dict(fb_conf)
            
            # Inisialisasi kredensial
            cred = credentials.Certificate(fb_dict)
            
            # Masukkan URL Realtime Database kamu di sini
            initialize_app(cred, {
                'databaseURL': 'SILAKAN_GANTI_DENGAN_URL_FIREBASE_KAMU'
            })
        except Exception as e:
            st.error(f"❌ Gagal koneksi ke Firebase: {e}")
            st.info("Pastikan menu 'Secrets' di Streamlit Cloud sudah diisi dengan benar.")

init_firebase()

# --- FUNGSI AMBIL DATA ---
def load_data():
    try:
        ref = db.reference('saham_low_price')
        data = ref.get()
        if data:
            # Mengubah hasil dari Firebase ke DataFrame Pandas
            df = pd.DataFrame.from_dict(data, orient='index')
            # Merapikan tampilan kolom
            df.index.name = 'Ticker'
            df.reset_index(inplace=True)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"⚠️ Error saat mengambil data: {e}")
        return pd.DataFrame()

# --- TAMPILAN UTAMA ---
st.title("🚀 Scanner Saham di Bawah 500")
st.markdown("Aplikasi ini menampilkan hasil scan teknikal (EMA20 & Stoch RSI) untuk saham-saham murah.")

df = load_data()

if not df.empty:
    st.success(f"Ditemukan **{len(df)}** saham dalam pantauan.")
    
    # Menambahkan filter sederhana di sidebar
    st.sidebar.header("Filter")
    pilihan_signal = st.sidebar.multiselect("Pilih Signal:", options=df['Signal'].unique(), default=df['Signal'].unique())
    
    # Filter data berdasarkan pilihan
    df_filtered = df[df['Signal'].isin(pilihan_signal)]
    
    # Menampilkan tabel
    st.dataframe(
        df_filtered.style.apply(lambda x: ['background-color: #004d00' if v == 'BUY' else '' for v in x], subset=['Signal']),
        use_container_width=True
    )
    
    if st.button('🔄 Perbarui Tampilan'):
        st.rerun()
else:
    st.warning("⚠️ Belum ada data di database.")
    st.info("Silakan jalankan file 'scanner_saham.py' di laptop kamu terlebih dahulu untuk mengirim data ke Firebase.")

# --- FOOTER ---
st.markdown("---")
st.caption("Data diperbarui berdasarkan scan terakhir dari laptop.")
