"""
Railway'de çalışan BIST Tarama Botu
Her gün 18:30'da tüm BIST'i tarar
Sonuçları GitHub'daki sinyaller.json'a yazar
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json
import time
import requests
import schedule
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from github import Github

# ── AYARLAR (Railway'den gelecek) ──
GITHUB_TOKEN  = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO   = os.environ.get("GITHUB_REPO", "")   # kullaniciadi/bist-miniapp
TARAMA_SAATI  = os.environ.get("TARAMA_SAATI", "18:30")

# ── HİSSE LİSTESİ ──
def hisse_listesi_al():
    try:
        url = "https://bigpara.hurriyet.com.tr/api/v1/hisse/list"
        headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://bigpara.hurriyet.com.tr/"}
        r = requests.get(url, headers=headers, timeout=15)
        data = r.json()
        items = data.get("data", data) if isinstance(data, dict) else data
        semboller = [i.get("kod","") for i in items if i.get("kod","").isalpha()]
        if len(semboller) > 100:
            print(f"✅ {len(semboller)} hisse çekildi")
            return sorted(set(semboller))
    except Exception as e:
        print(f"BigPara hatası: {e}")

    # Fallback liste
    return [
        "AKBNK","AKSEN","ALARK","ARCLK","ASELS","BIMAS","DOHOL","EKGYO","ENKAI","EREGL",
        "FROTO","GARAN","GUBRF","HALKB","ISCTR","KCHOL","KOZAA","KOZAL","KRDMD","LOGO",
        "MGROS","OTKAR","OYAKC","PETKM","PGSUS","SAHOL","SISE","SKBNK","SOKM","TAVHL",
        "TCELL","THYAO","TKFEN","TSKB","TTKOM","TUPRS","VAKBN","VESBE","VESTL","YKBNK",
        "ZOREN","AEFES","AFYON","AGESA","AGHOL","AGROT","AHGAZ","AKGRT","AKSA","AKCNS",
        "AKENR","AKFYE","ALBRK","ALKIM","ANELE","ANHYT","ANSGR","ARSAN","ATEKS","AYGAZ",
        "BAGFS","BAKAB","BANVT","BFREN","BIZIM","BJKAS","BOSSA","BRISA","BRKSN","BTCIM",
        "BUCIM","BURCE","CEMAS","CEMTS","CIMSA","CLEBI","CUSAN","DEVA","DITAS","DMSAS",
        "DOAS","DOGUB","DYOBY","ECILC","ECZYT","EDIP","EGEEN","EGGUB","EKSUN","EMKEL",
        "ENERY","ENGYO","ENJSA","EPLAS","ERBOS","EREGL","ERSU","ESCAR","ETILR","EUHOL",
        "FENER","FRIGO","FZLGY","GDKGS","GEREL","GESAN","GLRYH","GLYHO","GOODY","GOZDE",
        "GRSEL","GSDHO","GSRAY","GUBRF","HATEK","HEKTS","HUBVC","HURGZ","ICBCT","IHLGM",
        "IHLAS","INDES","INFO","ISCTR","ISDMR","ISGYO","IZOCM","JANTS","KAREL","KARTN",
        "KCHOL","KORDS","KOZAA","KOZAL","KRDMD","LOGO","MAVI","MERCN","MGROS","MNDRS",
        "NETAS","NUHCM","ODAS","OTKAR","OYAKC","OZGYO","PETKM","PGSUS","PINSU","POLHO",
        "POYNT","SAHOL","SANEL","SANKO","SARKY","SASA","SISE","SKBNK","SOKM","SUMAS",
        "TATGD","TAVHL","TCELL","THYAO","TKFEN","TOASO","TSKB","TTKOM","TTRAK","TUPRS",
        "ULUSE","VAKBN","VESBE","VESTL","YATAS","YKBNK","YUNSA","ZOREN",
    ]

# ── İNDİKATÖRLER ──
def calc_sma(c, p): return c.rolling(p).mean()
def calc_ema(c, p): return c.ewm(span=p, adjust=False).mean()

def calc_rsi(c, p=14):
    d = c.diff()
    g = d.clip(lower=0).rolling(p).mean()
    l = (-d.clip(upper=0)).rolling(p).mean()
    return 100 - (100 / (1 + g / l.replace(0, np.nan)))

def calc_bollinger(c, p=20):
    sma = calc_sma(c, p)
    std = c.rolling(p).std()
    return sma+2*std, sma-2*std, (4*std)/sma*100

def calc_vwap(h, l, c, v, p=10):
    tp = (h+l+c)/3
    return (tp*v).rolling(p).sum() / v.rolling(p).sum().replace(0, np.nan)

# ── 13 STRATEJİ ──
def strateji_tara(sembol, df):
    if len(df) < 210: return []
    try:
        c  = df["Close"].squeeze()
        h  = df["High"].squeeze()
        l  = df["Low"].squeeze()
        o  = df["Open"].squeeze()
        v  = df["Volume"].squeeze()

        rsi   = calc_rsi(c)
        s50   = calc_sma(c, 50)
        s200  = calc_sma(c, 200)
        e20   = calc_ema(c, 20)
        e50   = calc_ema(c, 50)
        e200  = calc_ema(c, 200)
        vwap  = calc_vwap(h, l, c, v)
        ub,lb,bw = calc_bollinger(c)
        avgv  = v.rolling(20).mean()

        def f(s): return float(s.iloc[-1])
        def f2(s): return float(s.iloc[-2])

        cv    = f(c); cv2 = f2(c)
        chg   = (cv-cv2)/cv2*100 if cv2 else 0
        vol   = f(v); av = f(avgv)
        rv    = vol/av if av else 0
        ri    = f(rsi)
        gap   = (f(o)-cv2)/cv2*100 if cv2 else 0
        p1m   = float(c.iloc[-21]) if len(c)>21 else cv
        drop  = (p1m-cv)/p1m*100 if p1m else 0
        tarih = str(df.index[-1].date())

        out = []
        def s(kod, emoji, aciklama, guven):
            out.append({
                "sembol": sembol, "tarih": tarih,
                "strateji_kodu": kod, "emoji": emoji,
                "aciklama": aciklama, "guven": guven,
                "fiyat": round(cv,2), "rsi": round(ri,1),
                "degisim_pct": round(chg,2), "rel_hacim": round(rv,2),
            })

        if cv>f(e20) and 40<=ri<=89 and f(e20)>f(e50) and vol>av:
            s("MOMENTUM_ALFA","🚀",f"Fiyat EMA20 üzerinde, RSI={ri:.1f}","ORTA")
        if f(e20)>f(e50)>f(e200) and 40<=ri<=65:
            s("ALTIN_TARAMA","⭐","EMA20>EMA50>EMA200 sıralı dizilim","YÜKSEK")
        if 25<=ri<=40 and cv>f(s200) and drop>5:
            s("DIP_AVCISI","🌊",f"1 aylık düşüş %{drop:.1f}, SMA200 üstü","YÜKSEK")
        if f(bw)<10 and f(e50)>f(e200) and 40<=ri<=60:
            s("PATLAMA_ONCESI","💣",f"Bollinger %{f(bw):.1f} sıkışma!","YÜKSEK")
        if cv>f(ub) and ri>60 and vol>av*1.5:
            s("ROKET_RAMPA","🚀","Bollinger üst bant kırışı + yüksek hacim","ORTA")
        if rv>2 and chg>2 and cv>f(e20) and vol>500000:
            s("AKILLI_PARA","💼",f"Relatif Hacim {rv:.1f}x kurumsal ilgi","YÜKSEK")
        if f(e20)>f(e50) and 50<=ri<=70 and vol>1000000:
            s("TREND_SORFCUSU","🏄","Güçlü trende biniş fırsatı","ORTA")
        if f2(s50)<=f2(s200) and f(s50)>f(s200) and cv>f(s200):
            s("GOLDEN_CROSS","✨","SMA50, SMA200'ü yukarı kesti!","ÇOK YÜKSEK")
        if f2(s50)>=f2(s200) and f(s50)<f(s200) and cv<f(s200):
            s("DEATH_CROSS","☠️","SMA50, SMA200'ü aşağı kesti!","ÇOK YÜKSEK")
        if gap>2 and chg>1 and rv>1.5 and vol>500000:
            s("SABAH_AVCISI","🌅",f"%{gap:.2f} GAP açılışı + hacim","ORTA")
        if chg>3 and rv>2 and 55<=ri<=75 and cv>f(vwap):
            s("MOMENTUM_BOMBASI","💥","Hacimli yükseliş + VWAP üstü","YÜKSEK")
        if cv>f(vwap) and chg>0 and 50<=ri<=70 and vol>500000:
            s("VWAP_SAVASCISI","⚔️",f"Fiyat VWAP üzerinde tutuyor","ORTA")
        if chg<-2 and ri<35 and cv>f(s200) and vol>500000:
            s("AS_FIRSATI","🌗","Gün içi sert düşüş, toparlanma emaresi","YÜKSEK")
        return out
    except:
        return []

# ── VERİ ÇEK ──
def hisse_isle(sembol):
    try:
        df = yf.download(f"{sembol}.IS", period="2y", interval="1d",
                         progress=False, auto_adjust=True)
        if df.empty or len(df)<210: return []
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return strateji_tara(sembol, df)
    except:
        return []

# ── GITHUB'A YÜKLE ──
def github_guncelle(sinyaller):
    if not GITHUB_TOKEN or not GITHUB_REPO:
        print("⚠️ GitHub token veya repo ayarlanmamış!")
        return
    try:
        g    = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)
        ozet = {}
        for s in sinyaller:
            ozet[s["strateji_kodu"]] = ozet.get(s["strateji_kodu"],0)+1

        icerik = json.dumps({
            "tarama_tarihi": datetime.now().isoformat(),
            "taranan_hisse_sayisi": len(hisse_listesi_al()),
            "toplam_sinyal": len(sinyaller),
            "strateji_ozeti": ozet,
            "sinyaller": sinyaller,
        }, ensure_ascii=False, indent=2)

        try:
            dosya = repo.get_contents("sinyaller.json")
            repo.update_file("sinyaller.json", "Bot güncelledi", icerik, dosya.sha)
        except:
            repo.create_file("sinyaller.json", "Bot oluşturdu", icerik)

        print(f"✅ GitHub güncellendi: {len(sinyaller)} sinyal")
    except Exception as e:
        print(f"❌ GitHub hatası: {e}")

# ── ANA TARAMA ──
def tara():
    print(f"\n🔍 Tarama başladı: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    hisseler = hisse_listesi_al()
    print(f"📊 {len(hisseler)} hisse taranacak")

    sinyaller = []
    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = {ex.submit(hisse_isle, s): s for s in hisseler}
        for i, fut in enumerate(as_completed(futures), 1):
            sonuc = fut.result()
            if sonuc:
                sinyaller.extend(sonuc)
                for s in sonuc:
                    print(f"  {s['emoji']} {s['sembol']} → {s['strateji_kodu']}")
            if i % 50 == 0:
                print(f"  ▓ {i}/{len(hisseler)} tamamlandı...")

    print(f"\n✅ Bitti! {len(sinyaller)} sinyal bulundu")
    github_guncelle(sinyaller)

# ── BAŞLAT ──
if __name__ == "__main__":
    print(f"🤖 BIST Bot başladı — Her gün {TARAMA_SAATI}'de çalışacak")
    tara()  # İlk çalışmada hemen tara
    schedule.every().day.at(TARAMA_SAATI).do(tara)
    while True:
        schedule.run_pending()
        time.sleep(60)
