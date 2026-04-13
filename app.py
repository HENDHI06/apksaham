import streamlit as st
import pandas as pd
from firebase_admin import credentials, initialize_app, db, _apps

# --- 1. CONFIG HALAMAN ---
st.set_page_config(page_title="Scanner Saham Pro", layout="wide")

# CSS Kustom untuk tampilan Card yang bersih
st.markdown("""
    <style>
    .stock-card {
        background-color: white;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 6px solid #1E3A8A;
    }
    .stock-name { color: #1E3A8A; font-size: 20px; font-weight: bold; }
    .company-desc { color: #6B7280; font-size: 13px; margin-bottom: 10px; }
    .price-tag { color: #EA580C; font-size: 24px; font-weight: bold; margin-bottom: 10px; }
    .metric-container { display: flex; justify-content: space-between; background: #F8FAFC; padding: 8px; border-radius: 8px; }
    .metric-box { text-align: center; flex: 1; }
    .metric-label { font-size: 9px; color: #9CA3AF; text-transform: uppercase; font-weight: bold; }
    .metric-value { font-size: 12px; font-weight: bold; color: #1F2937; }
    .badge { float: right; background: #E0E7FF; color: #1E3A8A; padding: 2px 10px; border-radius: 10px; font-size: 11px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. KONEKSI FIREBASE ---
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
            st.error(f"Koneksi Gagal: {e}")

init_firebase()

# --- 3. LOGIKA DATA & TAMPILAN ---
st.title("🚀 Signal Buy Saham Murah")

try:
    ref = db.reference('signals')
    data = ref.get()

    if data:
        # Konversi ke DataFrame
        if isinstance(data, list):
            data = [i for i in data if i is not None]
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame.from_dict(data, orient='index')
            if 'ticker' not in df.columns:
                df.index.name = 'ticker'
                df.reset_index(inplace=True)

        # Standarisasi nama kolom jadi kecil semua
        df.columns = [str(c).lower() for c in df.columns]

        # --- FILTER UTAMA: HANYA TAMPILKAN STATUS 'BUY' ---
        if 'signal' in df.columns:
            df = df[df['signal'].str.upper() == 'BUY']

        # Sidebar Search
        st.sidebar.header("🔍 Filter")
        search = st.sidebar.text_input("Cari Kode Saham:").upper()
        if search:
            df = df[df['ticker'].str.contains(search)]

        # Tabs kategori sesuai permintaan
        tab_titles = ["🔥 Scalping", "🌞 Day Trade", "🌊 Swing", "💎 Investasi"]
        tabs = st.tabs(tab_titles)

        # Map strategi ke Tab
        strat_map = {
            "SCALPING": tabs[0],
            "DAY TRADE": tabs[1],
            "SWING": tabs[2],
            "WATCHLIST": tabs[3]
        }

        for strat_name, tab_obj in strat_map.items():
            with tab_obj:
                # Filter per kategori
                filtered_df = df[df['strategy'].str.upper() == strat_name] if 'strategy' in df.columns else pd.DataFrame()
                
                if not filtered_df.empty:
                    # Urutkan berdasarkan harga termurah
                    filtered_df = filtered_df.sort_values('price')
                    
                    for _, row in filtered_df.iterrows():
                        st.markdown(f"""
                            <div class="stock-card">
                                <span class="badge">{strat_name}</span>
                                <div class="stock-name">{row.get('ticker', 'N/A')}</div>
                                <div class="company-desc">{row.get('nama', 'No Name')}</div>
                                <div class="price-tag">Rp {row.get('price', 0)}</div>
                                <div class="metric-container">
                                    <div class="metric-box">
                                        <div class="metric-label" style="color:#10B981">Target</div>
                                        <div class="metric-value">{row.get('tp1', '-')}</div>
                                    </div>
                                    <div class="metric-box">
                                        <div class="metric-label" style="color:#EF4444">Stop Loss</div>
                                        <div class="metric-value">{row.get('cl', '-')}</div>
                                    </div>
                                    <div class="metric-box">
                                        <div class="metric-label">PER</div>
                                        <div class="metric-value">{row.get('per', '-')}x</div>
                                    </div>
                                    <div class="metric-box">
                                        <div class="metric-label">PBV</div>
                                        <div class="metric-value">{row.get('pbv', '-')}x</div>
                                    </div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info(f"Belum ada sinyal BUY untuk kategori {strat_name}.")
    else:
        st.warning("Database kosong. Jalankan scanner di laptop dulu.")

except Exception as e:
    st.error(f"Terjadi kesalahan: {e}")

# Tombol Refresh manual
if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()
