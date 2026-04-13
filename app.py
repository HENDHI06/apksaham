import streamlit as st
import pandas as pd
from firebase_admin import credentials, initialize_app, db, _apps

# --- 1. CONFIG HALAMAN ---
st.set_page_config(page_title="Scanner Saham Pro", layout="wide")

# CSS Kustom untuk membuat tampilan Card
st.markdown("""
    <style>
    .stock-card {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 10px solid #1E3A8A;
    }
    .stock-name { color: #1E3A8A; font-size: 24px; font-weight: bold; margin-bottom: 5px; }
    .company-desc { color: #6B7280; font-size: 14px; margin-bottom: 15px; }
    .price-tag { color: #EA580C; font-size: 32px; font-weight: bold; margin-bottom: 15px; }
    .metric-container { display: flex; justify-content: space-between; background: #F3F4F6; padding: 10px; border-radius: 10px; }
    .metric-box { text-align: center; flex: 1; }
    .metric-label { font-size: 10px; color: #9CA3AF; text-transform: uppercase; }
    .metric-value { font-size: 14px; font-weight: bold; color: #1F2937; }
    .badge { float: right; background: #1E3A8A; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; }
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

# --- 3. LOGIKA APLIKASI ---
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

        df.columns = [str(c).lower() for c in df.columns]

        # Membuat Tabs sesuai gambar
        tab_titles = ["🔥 Scalping", "🌞 Day Trade", "🌊 Swing", "💎 Investasi"]
        tabs = st.tabs(tab_titles)

        # Mapping strategi ke Tab (Sesuaikan dengan isi kolom 'strategy' di Excel kamu)
        strat_map = {
            "SCALPING": tabs[0],
            "DAY TRADE": tabs[1],
            "SWING": tabs[2],
            "WATCHLIST": tabs[3] # Sesuai data kamu, WATCHLIST masuk ke Investasi
        }

        for strat_name, tab_obj in strat_map.items():
            with tab_obj:
                # Filter data berdasarkan strategi
                filtered_df = df[df['strategy'].str.upper() == strat_name] if 'strategy' in df.columns else pd.DataFrame()
                
                if not filtered_df.empty:
                    # Tampilkan dalam bentuk Card
                    for _, row in filtered_df.iterrows():
                        ticker = row.get('ticker', 'N/A')
                        nama = row.get('nama', 'Unknown Company')
                        price = row.get('price', 0)
                        target = row.get('tp1', '-')
                        stoploss = row.get('cl', '-')
                        per = row.get('per', '-')
                        pbv = row.get('pbv', '-')

                        st.markdown(f"""
                            <div class="stock-card">
                                <span class="badge">{strat_name}</span>
                                <div class="stock-name">{ticker}</div>
                                <div class="company-desc">{nama}</div>
                                <div class="price-tag">Rp {price}</div>
                                <div class="metric-container">
                                    <div class="metric-box">
                                        <div class="metric-label" style="color:green">Target</div>
                                        <div class="metric-value">{target}</div>
                                    </div>
                                    <div class="metric-box">
                                        <div class="metric-label" style="color:red">Stop Loss</div>
                                        <div class="metric-value">{stoploss}</div>
                                    </div>
                                    <div class="metric-box">
                                        <div class="metric-label">PER</div>
                                        <div class="metric-value">{per}x</div>
                                    </div>
                                    <div class="metric-box">
                                        <div class="metric-label">PBV</div>
                                        <div class="metric-value">{pbv}x</div>
                                    </div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.write("Belum ada saham untuk kategori ini.")
    else:
        st.warning("Data belum ada. Jalankan scanner di laptop.")

except Exception as e:
    st.error(f"Error: {e}")
