import streamlit as st
import pandas as pd
from firebase_admin import credentials, initialize_app, db, _apps

# --- CONFIG ---
st.set_page_config(page_title="Scanner Saham Pro", layout="wide")

def init_firebase():
    if not _apps:
        try:
            # Ambil data dari Secrets
            fb_conf = st.secrets["firebase"]
            fb_dict = dict(fb_conf)
            
            # Memperbaiki format private_key agar terbaca sistem
            fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            
            cred = credentials.Certificate(fb_dict)
            initialize_app(cred, {
                'databaseURL': 'https://scannersaham-b45ed-default-rtdb.firebaseio.com/'
            })
        except Exception as e:
            st.error(f"Koneksi Firebase Gagal: {e}")

init_firebase()

st.title("📊 Hasil Scan Saham < 500")

# Ambil data dari tabel 'signals' (sesuai log laptop kamu tadi)
try:
    ref = db.reference('signals')
    data = ref.get()

    if data:
        # Ubah ke DataFrame
        df = pd.DataFrame.from_dict(data, orient='index')
        df.index.name = 'Ticker'
        df.reset_index(inplace=True)

        # Styling
        st.success(f"Berhasil memuat {len(df)} saham.")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Database kosong. Jalankan scanner di laptop dulu!")
except Exception as e:
    st.error(f"Gagal mengambil data: {e}")

if st.button("🔄 Refresh"):
    st.rerun()
