import pandas as pd
import pandas_ta as ta
import firebase_admin
from firebase_admin import credentials, db
import yfinance as yf

# --- KONEKSI FIREBASE ---
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://scannersaham-b45ed-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

def run_scanner():
    print("🚀 Scanner Saham (< 500) & Multi-Strategi Dimulai...")
    df_excel = pd.read_excel("data_saham.xlsx")
    all_signals = []

    # Kita scan semua saham dari Excel
    for index, row in df_excel.iterrows():
        ticker_raw = str(row.get('Kode', ''))
        if not ticker_raw or ticker_raw == 'nan': continue
        
        ticker_jk = ticker_raw + ".JK"
        
        try:
            # Ambil data historis (period 1mo cukup untuk scalping/daytrade)
            stock = yf.Ticker(ticker_jk)
            hist = stock.history(period="1y", interval="1d")
            
            if len(hist) < 50: continue

            # Data Harga Terakhir
            price = hist['Close'].iloc[-1]

            # --- FILTER UTAMA: HANYA DI BAWAH 500 ---
            if price >= 500:
                continue 
            
            print(f"🔎 Analisis {ticker_raw} (Harga: {price})...")

            # --- HITUNG INDIKATOR ---
            # EMA
            hist['EMA5'] = ta.ema(hist['Close'], length=5)
            hist['EMA20'] = ta.ema(hist['Close'], length=20)
            hist['EMA50'] = ta.ema(hist['Close'], length=50)
            hist['EMA200'] = ta.ema(hist['Close'], length=200)
            
            # MACD
            macd = ta.macd(hist['Close'])
            macd_val = macd['MACD_12_26_9'].iloc[-1] if macd is not None else 0
            
            # Stochastic RSI
            stoch = ta.stochrsi(hist['Close'])
            stoch_k = stoch['STOCHRSIk_14_14_3_3'].iloc[-1] if stoch is not None else 0

            # --- LOGIKA PENENTUAN STRATEGI ---
            label = "WATCHLIST"
            
            # 1. Scalping (EMA 5 > EMA 20 & Stoch RSI < 80)
            if hist['EMA5'].iloc[-1] > hist['EMA20'].iloc[-1] and stoch_k < 80:
                label = "SCALPING"
            
            # 2. Day Trading (EMA 20 > EMA 50 & MACD Positif)
            elif hist['EMA20'].iloc[-1] > hist['EMA50'].iloc[-1] and macd_val > 0:
                label = "DAY TRADING"
            
            # 3. Swing (EMA 50 > EMA 200)
            elif hist['EMA50'].iloc[-1] > hist['EMA200'].iloc[-1]:
                label = "SWING"
            
            # 4. Investasi (Price > EMA 200 & Fundamental murah)
            elif price > hist['EMA200'].iloc[-1]:
                label = "INVESTASI"

            info = stock.info
            all_signals.append({
                'ticker': ticker_raw,
                'nama': row.get('Nama Perusahaan', 'N/A'),
                'strategy': label,
                'price': int(price),
                'tp1': int(price * 1.05),
                'cl': int(price * 0.97),
                'per': round(info.get('trailingPE', 0), 2) if info.get('trailingPE') else 0,
                'pbv': round(info.get('priceToBook', 0), 2) if info.get('priceToBook') else 0
            })
            
        except Exception as e:
            continue

    # Kirim ke Firebase
    if all_signals:
        db.reference('signals').set(all_signals)
        print(f"✅ Berhasil! {len(all_signals)} saham di bawah 500 terkirim ke Firebase.")
    else:
        print("⚠️ Tidak ada saham di bawah 500 yang memenuhi kriteria.")

if __name__ == "__main__":
    run_scanner()