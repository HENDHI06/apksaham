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
            
            # URL SUDAH DISESUAIKAN KE ASIA (SINGAPURA)
            initialize_app(cred, {
                'databaseURL': 'https://scannersaham-b45ed-default-rtdb.asia-southeast1.firebasedatabase.app'
            })
        except Exception as e:
            st.error(f"Koneksi Firebase Gagal: {e}")

init_firebase()

st.title("📊 Hasil Scan Saham < 500")

try:
    # Pastikan 'signals' sesuai dengan yang kamu kirim dari laptop
    ref = db.reference('signals')
    data = ref.get()

    if data:
        df = pd.DataFrame.from_dict(data, orient='index')
        df.index.name = 'Ticker'
        df.reset_index(inplace=True)

        st.success(f"Berhasil memuat {len(df)} saham dari server Asia.")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Database masih kosong di server Asia. Jalankan scanner di laptop sekali lagi!")
except Exception as e:
    st.error(f"Gagal mengambil data: {e}")

if st.button("🔄 Refresh"):
    st.rerun()
