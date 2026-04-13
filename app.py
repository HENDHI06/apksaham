import streamlit as st
import pandas as pd
from firebase_admin import credentials, initialize_app, db, _apps

# --- CONFIG ---
st.set_page_config(page_title="Scanner Saham Pro", layout="wide")

def init_firebase():
    if not _apps:
        try:
            fb_conf = st.secrets["firebase"]
            fb_dict = dict(fb_conf)
            fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            
            cred = credentials.Certificate(fb_dict)
            initialize_app(cred, {
                'databaseURL': 'https://scannersaham-b45ed-default-rtdb.asia-southeast1.firebasedatabase.app'
            })
        except Exception as e:
            st.error(f"Koneksi Firebase Gagal: {e}")

init_firebase()

st.title("📊 Hasil Scan Saham < 500")

try:
    ref = db.reference('signals')
    data = ref.get()

    if data:
        # SOLUSI ERROR 'LIST' OBJECT:
        # Jika data berbentuk List (karena indeks angka), kita ubah ke DataFrame langsung
        if isinstance(data, list):
            # Bersihkan data None jika ada (Firebase sering selipkan None di index 0)
            data = [i for i in data if i is not None]
            df = pd.DataFrame(data)
        else:
            # Jika data berbentuk Dictionary (seperti yang kita mau)
            df = pd.DataFrame.from_dict(data, orient='index')
            df.index.name = 'Ticker'
            df.reset_index(inplace=True)

        if not df.empty:
            st.success(f"Berhasil memuat {len(df)} saham.")
            
            # Tambahkan kolom sinyal warna untuk estetika
            def color_signal(val):
                color = '#00ff00' if val == 'BUY' else '#ffffff'
                return f'color: {color}'

            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Data kosong.")
    else:
        st.warning("Database masih kosong. Jalankan scanner di laptop!")

except Exception as e:
    st.error(f"Gagal mengambil data: {e}")

if st.button("🔄 Refresh Data"):
    st.rerun()
