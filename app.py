import streamlit as st
import pandas as pd
from firebase_admin import credentials, initialize_app, db, _apps

# --- 1. CONFIG HALAMAN ---
st.set_page_config(
    page_title="Scanner Saham Pro",
    page_icon="📈",
    layout="wide"
)

# --- 2. KONEKSI FIREBASE ---
def init_firebase():
    if not _apps:
        try:
            fb_conf = st.secrets["firebase"]
            fb_dict = dict(fb_conf)
            # Fix format private key
            fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            
            cred = credentials.Certificate(fb_dict)
            initialize_app(cred, {
                'databaseURL': 'https://scannersaham-b45ed-default-rtdb.asia-southeast1.firebasedatabase.app'
            })
        except Exception as e:
            st.error(f"Koneksi Firebase Gagal: {e}")

init_firebase()

# --- 3. TAMPILAN UTAMA ---
st.title("📊 Hasil Scan Saham Murah (< 500)")
st.write("Data diupdate otomatis melalui scanner laptop.")

try:
    # Ambil data dari tabel 'signals'
    ref = db.reference('signals')
    data = ref.get()

    if data:
        # Konversi data ke DataFrame
        if isinstance(data, list):
            # Jika data format List (Indeks 0, 1, 2...)
            data = [i for i in data if i is not None]
            df = pd.DataFrame(data)
        else:
            # Jika data format Dictionary (Key: Value)
            df = pd.DataFrame.from_dict(data, orient='index')
            if 'ticker' not in df.columns:
                df.index.name = 'ticker'
                df.reset_index(inplace=True)

        # --- PERAPIHAN KOLOM ---
        # 1. Pastikan nama kolom kecil semua agar konsisten
        df.columns = [str(c).lower() for c in df.columns]

        # 2. Pindahkan kolom 'ticker' ke paling depan
        if 'ticker' in df.columns:
            cols = ['ticker'] + [c for c in df.columns if c != 'ticker']
            df = df[cols]
        
        # 3. Urutkan berdasarkan ticker
        df = df.sort_values('ticker')

        # --- SIDEBAR FILTER ---
        st.sidebar.header("Pengaturan Tampilan")
        search = st.sidebar.text_input("Cari Kode Saham (Ticker):").upper()
        if search:
            df = df[df['ticker'].str.contains(search)]

        if 'strategy' in df.columns:
            strat_filter = st.sidebar.multiselect(
                "Filter Strategi:", 
                options=df['strategy'].unique(),
                default=df['strategy'].unique()
            )
            df = df[df['strategy'].isin(strat_filter)]

        # --- DISPLAY TABEL ---
        if not df.empty:
            st.success(f"Ditemukan {len(df)} saham sesuai kriteria.")
            
            # Menampilkan tabel tanpa kolom indeks angka di kiri
            st.dataframe(
                df, 
                use_container_width=True, 
                hide_index=True
            )
            
            # Keterangan tambahan
            st.info("💡 **Tips:** Klik pada judul kolom untuk mengurutkan data (Sorting).")
        else:
            st.warning("Tidak ada data yang cocok dengan filter.")
            
    else:
        st.warning("Database kosong. Pastikan script di laptop sudah selesai berjalan.")

except Exception as e:
    st.error(f"Terjadi kesalahan saat memproses data: {e}")

# Tombol Refresh
if st.button("🔄 Perbarui Data"):
    st.rerun()
