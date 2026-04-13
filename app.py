import streamlit as st
import pandas as pd
from firebase_admin import credentials, initialize_app, db, _apps

# Konfigurasi Tampilan
st.set_page_config(page_title="IHSG Scanner", layout="wide")

st.title("📊 Scanner Saham < 500")

# Fungsi koneksi ke Firebase via Secrets
def init_firebase():
    if not _apps:
        # Mengambil data dari menu "Manage app" -> "Secrets"
        try:
            fb_conf = st.secrets["firebase"]
            fb_dict = {
                "type": fb_conf["type"],
                "project_id": fb_conf["project_id"],
                "private_key_id": fb_conf["private_key_id"],
                "private_key": fb_conf["private_key"].replace('\\n', '\n'),
                "client_email": fb_conf["client_email"],
                "client_id": fb_conf["client_id"],
                "auth_uri": fb_conf["auth_uri"],
                "token_uri": fb_conf["token_uri"],
                "auth_provider_x509_cert_url": fb_conf["auth_provider_x509_cert_url"],
                "client_x509_cert_url": fb_conf["client_x509_cert_url"]
            }
            cred = credentials.Certificate(fb_dict)
            initialize_app(cred, {
                'databaseURL': 'MASUKKAN_URL_FIREBASE_KAMU_DISINI'
            })
        except Exception as e:
            st.error(f"Gagal koneksi Secrets: {e}")

init_firebase()

# Fungsi ambil data
def load_data():
    try:
        ref = db.reference('saham_low_price')
        data = ref.get()
        if data:
            # Mengubah hasil scan ke DataFrame
            df = pd.DataFrame.from_dict(data, orient='index')
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Gagal ambil data dari Database: {e}")
        return pd.DataFrame()

# Tampilan Utama
df = load_data()

if not df.empty:
    st.write(f"Ditemukan **{len(df)}** saham sesuai kriteria.")
    
    # Percantik Tabel
    st.dataframe(
        df.style.highlight_max(axis=0, subset=['Signal']), 
        use_container_width=True
    )
    
    if st.button('🔄 Refresh Data'):
        st.rerun()
else:
    st.warning("Belum ada data di database. Jalankan 'scanner_saham.py' di laptop kamu dulu.")
