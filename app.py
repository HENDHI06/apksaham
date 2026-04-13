import streamlit as st
import pandas as pd
from firebase_admin import credentials, initialize_app, db, _apps

# --- CONFIG & STYLE ---
st.set_page_config(page_title="Scanner Saham Pro", layout="wide")
st.markdown("""
    <style>
    .stock-card { background: white; border-radius: 15px; padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 8px solid #1E3A8A; }
    .stock-name { color: #1E3A8A; font-size: 22px; font-weight: bold; }
    .price-tag { color: #EA580C; font-size: 28px; font-weight: bold; margin: 10px 0; }
    .badge { float: right; background: #E0E7FF; color: #1E3A8A; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }
    .metric-container { display: flex; justify-content: space-between; background: #F3F4F6; padding: 10px; border-radius: 10px; text-align: center; }
    .label { font-size: 10px; color: #6B7280; }
    .val { font-size: 14px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def init_firebase():
    if not _apps:
        fb_dict = dict(st.secrets["firebase"])
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        initialize_app(credentials.Certificate(fb_dict), {'databaseURL': 'https://scannersaham-b45ed-default-rtdb.asia-southeast1.firebasedatabase.app'})

init_firebase()

# --- TAMPILAN ---
st.title("📈 Scanner Saham Pro")
try:
    data = db.reference('signals').get()
    if data:
        df = pd.DataFrame.from_dict(data, orient='index') if not isinstance(data, list) else pd.DataFrame([i for i in data if i is not None])
        df.columns = [str(c).lower() for c in df.columns]
        
        # TABS
        tab1, tab2, tab3, tab4 = st.tabs(["🔥 Scalping", "🌞 Day Trade", "🌊 Swing", "💎 Investasi"])
        map_tabs = {"SCALPING": tab1, "DAY TRADE": tab2, "SWING": tab3, "WATCHLIST": tab4}

        for strat, tab_obj in map_tabs.items():
            with tab_obj:
                f_df = df[df['strategy'].str.upper() == strat] if 'strategy' in df.columns else pd.DataFrame()
                if not f_df.empty:
                    for _, r in f_df.iterrows():
                        st.markdown(f"""
                        <div class="stock-card">
                            <span class="badge">{strat}</span>
                            <div class="stock-name">{r['ticker']}</div>
                            <div style="font-size:12px; color:gray;">{r['nama']}</div>
                            <div class="price-tag">Rp {r['price']}</div>
                            <div class="metric-container">
                                <div><div class="label" style="color:green">Target</div><div class="val">{r['tp1']}</div></div>
                                <div><div class="label" style="color:red">Stop Loss</div><div class="val">{r['cl']}</div></div>
                                <div><div class="label">PER</div><div class="val">{r['per']}x</div></div>
                                <div><div class="label">PBV</div><div class="val">{r['pbv']}x</div></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info(f"Belum ada sinyal {strat}")
    else:
        st.warning("Database Kosong")
except Exception as e:
    st.error(f"Error: {e}")
