import requests, pandas as pd, time
from datetime import datetime

TOKEN = "8500797990:AAGpnn06DGu1-ojJpjIIww96GX1GFU_wzEA"
CHAT  = "655166781"

def send(t):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT, "text": t}, timeout=10)
    except: pass

send(f"BHAI BOT RESTART HO GAYA - AB ADX>25 COMPULSORY HAI\n{datetime.now().strftime('%d %b %Y - %I:%M %p')}")

# DMI/ADX function
def dmi_adx(df):
    h,l,c = df["h"],df["l"],df["c"]
    tr = pd.concat([h-l, abs(h-c.shift()), abs(l-c.shift())], axis=1).max(axis=1)
    plus = h.diff().clip(lower=0)
    minus = (-l.diff()).clip(lower=0)
    atr = tr.ewm(alpha=1/14,adjust=False).mean()
    pdi = 100*plus.ewm(alpha=1/14,adjust=False).mean()/atr
    mdi = 100*minus.ewm(alpha=1/14,adjust=False).mean()/atr
    adx = 100*abs(pdi-mdi)/(pdi+mdi)
    adx = adx.ewm(alpha=1/14,adjust=False).mean()
    return pdi.iloc[-1], mdi.iloc[-1], adx.iloc[-1], pdi.iloc[-2], mdi.iloc[-2]

last_btc = ""
last_nifty = ""

while True:
    try:
        # BTC
        df = requests.get("https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=50", timeout=10).json()
        df = pd.DataFrame(df, columns=["ot","o","h","l","c","v","ct","q","t","tb","tq","i"])
        df["c"]=df["c"].astype(float); df["h"]=df["h"].astype(float); df["l"]=df["l"].astype(float)
        p1,m1,a1,p2,m2 = dmi_adx(df)
        price = df["c"].iloc[-1]
        t = datetime.now().strftime("%d %b %I:%M %p")
        if last_btc != t:
            if p2 <= m2 and p1 > m1 and a1 > 25:           # ← ADX > 25 compulsory
                send(f"BTC LONG\n{t}\nEntry ${price:.0f}\nTP ${price+200}\nSL ${price-100}\nADX: {a1:.1f}")
                last_btc = t
            elif m2 <= p2 and m1 > p1 and a1 > 25:         # ← ADX > 25 compulsory
                send(f"BTC SHORT\n{t}\nEntry ${price:.0f}\nTP ${price-200}\nSL ${price+100}\nADX: {a1:.1f}")
                last_btc = t

        # NIFTY
        df = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI?interval=5m&range=1d", headers={"User-Agent":"Mozilla/5.0"}, timeout=10).json()
        q = df["chart"]["result"][0]["indicators"]["quote"][0]
        df = pd.DataFrame({"h":q["high"],"l":q["low"],"c":q["close"]}).dropna().astype(float)
        if len(df)>30:
            p1,m1,a1,p2,m2 = dmi_adx(df)
            price = df["c"].iloc[-1]
            t = datetime.now().strftime("%d %b %I:%M %p")
            if last_nifty != t:
                if p2 <= m2 and p1 > m1 and a1 > 25:
                    send(f"NIFTY LONG\n{t}\nEntry {price:.0f}\nTP {price+100}\nSL {price-50}\nADX: {a1:.1f}")
                    last_nifty = t
                elif m2 <= p2 and m1 > p1 and a1 > 25:
                    send(f"NIFTY SHORT\n{t}\nEntry {price:.0f}\nTP {price-100}\nSL {price+50}\nADX: {a1:.1f}")
                    last_nifty = t

        time.sleep(60)
    except:
        time.sleep(60)
