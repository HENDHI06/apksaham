import streamlit as st
from firebase_admin import db, credentials, initialize_app, _apps

# --- SETUP HALAMAN ---
st.set_page_config(page_title="Scanner Saham Pro", layout="centered")

if not _apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    initialize_app(cred, {'databaseURL': 'https://scannersaham-b45ed-default-rtdb.asia-southeast1.firebasedatabase.app/'})

# --- CSS: WARNA KONTRAS TINGGI AGAR NYAMAN DI MATA ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .card { 
        background: white; 
        padding: 18px; 
        border-radius: 15px; 
        border-left: 10px solid #1e3d59; /* Garis tebal di kiri agar elegan */
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
        margin-bottom: 20px; 
    }
    .ticker-header { 
        display: flex; 
        justify-content: space-between; 
        align-items: flex-start; 
        margin-bottom: 5px;
    }
    .t-code { 
        font-size: 26px; 
        font-weight: 900; 
        color: #000000; /* Hitam pekat agar terbaca jelas */
        letter-spacing: 1px;
    }
    .t-name { 
        font-size: 14px; 
        font-weight: 600; 
        color: #444444; /* Abu gelap pekat */
        margin-top: -5px;
        margin-bottom: 10px;
    }
    .strategy-badge { 
        background: #1e3d59; 
        color: #ffffff; 
        padding: 5px 12px; 
        border-radius: 8px; 
        font-size: 11px; 
        font-weight: bold;
        text-transform: uppercase;
    }
    .t-price { 
        font-size: 32px; 
        font-weight: bold; 
        color: #d35400; /* Oranye gelap agar kontras dengan putih */
        margin: 10px 0;
    }
    .info-grid { 
        display: flex; 
        justify-content: space-between; 
        background: #f8f9fa; 
        padding: 10px; 
        border-radius: 10px;
        margin-top: 10px;
    }
    .info-box { text-align: center; flex: 1; }
    .info-label { font-size: 10px; color: #777; font-weight: bold; text-transform: uppercase; }
    .info-val { font-size: 15px; font-weight: bold; color: #1e3d59; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Market Scanner < 500")

# SEARCH & TABS
query = st.text_input("🔍 Cari Kode Saham...", "").upper()
tab1, tab2, tab3, tab4 = st.tabs(["🔥 Scalping", "☀️ Day Trade", "🌊 Swing", "💎 Investasi"])

try:
    data = db.reference('signals').get()
    if data:
        items = [i for i in data if i is not None]
        if query: items = [i for i in items if query in i['ticker']]

        def render_section(cat):
            filtered = [s for s in items if s['strategy'] == cat]
            if not filtered:
                st.info(f"Belum ada saham untuk kategori {cat}")
            for s in filtered:
                st.markdown(f"""
                <div class="card">
                    <div class="ticker-header">
                        <div>
                            <div class="t-code">{s['ticker']}</div>
                            <div class="t-name">{s['nama']}</div>
                        </div>
                        <span class="strategy-badge">{s['strategy']}</span>
                    </div>
                    <div class="t-price">Rp {s['price']:,}</div>
                    <div class="info-grid">
                        <div class="info-box">
                            <div class="info-label" style="color:green;">Target</div>
                            <div class="info-val">{s['tp1']:,}</div>
                        </div>
                        <div class="info-box">
                            <div class="info-label" style="color:red;">Stop Loss</div>
                            <div class="info-val">{s['cl']:,}</div>
                        </div>
                        <div class="info-box">
                            <div class="info-label">PER</div>
                            <div class="info-val">{s['per']}x</div>
                        </div>
                        <div class="info-box">
                            <div class="info-label">PBV</div>
                            <div class="info-val">{s['pbv']}x</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with tab1: render_section("SCALPING")
        with tab2: render_section("DAY TRADING")
        with tab3: render_section("SWING")
        with tab4: render_section("INVESTASI")

except Exception as e:
    st.error(f"Gagal memuat data: {e}")

if st.button("🔄 Refresh Data Real-time", use_container_width=True):
    st.rerun()