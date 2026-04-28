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
from flask import Flask, send_file, jsonify
from threading import Thread

app = Flask(__name__)
SONUC_DOSYA = "sinyaller.json"

def hisse_listesi_al():
    try:
        url = "https://bigpara.hurriyet.com.tr/api/v1/hisse/list"
        headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://bigpara.hurriyet.com.tr/"}
        r = requests.get(url, headers=headers, timeout=15)
        data = r.json()
        items = data.get("data", data) if isinstance(data, dict) else data
        semboller = [i.get("kod","") for i in items if str(i.get("kod","")).isalpha()]
        if len(semboller) > 100:
            return sorted(set(semboller))
    except: pass
        return sorted(list(set([
        "A1CAP","ACSEL","ADEL","ADESE","ADGYO","AEFES","AFYON","AGESA","AGHOL","AGROT",
        "AHGAZ","AKCNS","AKENR","AKFYE","AKGRT","AKHAN","AKSA","AKSEN","AKSUE","AKYHO",
        "ALARK","ALBRK","ALCAR","ALCTL","ALFAS","ALGYO","ALKA","ALKIM","ALKLC","ALMAD",
        "ALTNY","ALVES","ANELE","ANGEN","ANHYT","ANSGR","ARASE","ARCLK","ARDYZ","ARENA",
        "ARSAN","ARTMS","ASELS","ASLAN","ASTOR","ATAKP","ATATP","ATEKS","ATPET","AVHOL",
        "AVGYO","AVOD","AVTUR","AYCES","AYEN","AYGAZ","AZTEK","BAGFS","BAKAB","BALAT",
        "BANVT","BARMA","BASCM","BASGZ","BATRA","BFREN","BIENY","BIMAS","BIOEN","BIZIM",
        "BJKAS","BMEKS","BMSCH","BNTAS","BOBET","BOSSA","BRISA","BRKSN","BRKVY","BRMEN",
        "BRYAT","BSOKE","BTCIM","BUCIM","BURCE","BURVA","BVSAN","CANTE","CASA","CEMAS",
        "CEMTS","CIMSA","CLEBI","CMBTN","CMENT","CRFSA","CUSAN","CWENE","DAPGM","DARDL",
        "DENGE","DERHL","DERIM","DEVA","DGATE","DGKLB","DGNMO","DITAS","DMRGD","DMSAS",
        "DNISI","DOAS","DOBUR","DOCO","DOGUB","DOHOL","DRMAS","DTRND","DURAN","DYOBY",
        "DZGYO","ECILC","ECZYT","EDIP","EGEEN","EGGUB","EGPRO","EGSER","EKSUN","ELITE",
        "EMKEL","EMNIS","ENERY","ENFRA","ENGYO","ENJSA","ENKAI","ENTRA","EPLAS","ERBOS",
        "ERCB","ERDEK","EREGL","ERSU","ESCAR","ESCOM","ESEN","ETILR","ETYAT","EUHOL",
        "EUREN","EUYO","FENER","FMIZP","FORTE","FRIGO","FROTO","FZLGY","GARAN","GDKGS",
        "GEDIK","GEDZA","GENTS","GEREL","GESAN","GLBMD","GLCVY","GLRYH","GLYHO","GOLDS",
        "GOLTS","GOODY","GOZDE","GRSEL","GRTRK","GSDDE","GSDHO","GSRAY","GUBRF","GWIND",
        "GZNMI","HALKB","HATEK","HDFGS","HEDEF","HEKTS","HLGYO","HTTBT","HUBVC","HUNER",
        "HURGZ","ICBCT","IEYHO","IHLGM","IHLAS","IHEVA","IHGZT","IMASM","INDES","INFO",
        "INTEM","IPEKE","ISATR","ISCTR","ISDMR","ISFIN","ISGSY","ISGYO","ISKPL","ISLTR",
        "ISYAT","ITTFH","IZFAS","IZOCM","JANTS","KAPLM","KAREL","KARTN","KATMR","KAYSE",
        "KBORU","KCAER","KCHOL","KERVT","KFEIN","KGYO","KLGYO","KLKIM","KLMSN","KLNMA",
        "KLRHO","KLSER","KMPUR","KNFRT","KONKA","KONTR","KONYA","KOPOL","KORDS","KOZAA",
        "KOZAL","KRDMD","KRONT","KRPLS","KRSTL","KRTEK","KTLEV","KTSKR","KUTPO","KUVVA",
        "LIDER","LILAK","LINK","LKMNH","LOGO","LRSHO","LUZAM","MACKO","MAGEN","MAKIM",
        "MAKTK","MANAS","MAVI","MARTI","MEDTR","MEGAP","MEKAG","MERCN","MERIT","MERKO",
        "METRO","METUR","MGROS","MHRGY","MIPAZ","MNDRS","MNDTR","MOBTL","MOGAN","MOLPE",
        "MSGYO","MTRKS","MZHLD","NATEN","NETAS","NIBAS","NTTUR","NUGYO","NUHCM","ODAS",
        "OFSYM","ONCSM","ONRYT","ORCAY","ORGE","ORMA","OSMEN","OSTIM","OTKAR","OYAKC",
        "OYYAT","OZGYO","OZKGY","OZRDN","PAGYO","PAMEL","PAPIL","PARSN","PASEU","PATEK",
        "PCILT","PEGYO","PEKGY","PETKM","PGSUS","PINSU","PKART","PNLSN","POIPY","POLHO",
        "POLSA","POLTK","POYNT","PRZMA","PSDTC","PSGYO","RALYH","RAYSG","RBNK","RCOLS",
        "RYGYO","RHEAG","RISK","RNPOL","RODRG","SAHOL","SANFM","SANEL","SANKO","SARKY",
        "SASA","SAYAS","SDTTR","SEGMN","SEKFK","SEKUR","SELEC","SELVA","SENTE","SEYKM",
        "SILVR","SISE","SKBNK","SKTAS","SKYLP","SMART","SNKRN","SODSN","SOKM","SONME",
        "SRVGY","SUMAS","SUNTK","SUPRV","SURGY","TARKM","TATGD","TAVHL","TBORG","TCELL",
        "TDGYO","TEKTU","TETMT","TEZOL","THYAO","TKFEN","TKNSA","TLMAN","TMPOL","TOASO",
        "TRCAS","TRGYO","TRILC","TSGYO","TSKB","TSMLR","TTKOM","TTRAK","TUCLK","TUKAS",
        "TUPRS","TUREX","TURGG","TURKB","TURSG","ULUFA","ULUSE","ULUUN","UMPAS","UNLU",
        "USAK","USDTR","UTPYA","VAKBN","VAKFN","VAKKO","VBTYZ","VERUS","VESBE","VESTL",
        "VKFYO","VKGYO","VKING","VRGYO","YAPRK","YATAS","YAYLA","YBTAS","YGGYO","YKBNK",
        "YKSLN","YONGA","YUNSA","YYLGD","ZEDUR","ZOREN","ZRGYO",
    ])))



def calc_sma(c, p): return c.rolling(p).mean()
def calc_ema(c, p): return c.ewm(span=p, adjust=False).mean()
def calc_rsi(c, p=14):
    d=c.diff(); g=d.clip(lower=0).rolling(p).mean(); l=(-d.clip(upper=0)).rolling(p).mean()
    return 100-(100/(1+g/l.replace(0,np.nan)))
def calc_bollinger(c, p=20):
    sma=calc_sma(c,p); std=c.rolling(p).std()
    return sma+2*std, sma-2*std, (4*std)/sma*100
def calc_vwap(h,l,c,v,p=10):
    tp=(h+l+c)/3; return (tp*v).rolling(p).sum()/v.rolling(p).sum().replace(0,np.nan)

def strateji_tara(sembol, df):
    if len(df)<210: return []
    try:
        c=df["Close"].squeeze(); h=df["High"].squeeze()
        l=df["Low"].squeeze(); o=df["Open"].squeeze(); v=df["Volume"].squeeze()
        rsi=calc_rsi(c); s50=calc_sma(c,50); s200=calc_sma(c,200)
        e20=calc_ema(c,20); e50=calc_ema(c,50); e200=calc_ema(c,200)
        vwap=calc_vwap(h,l,c,v); ub,lb,bw=calc_bollinger(c); avgv=v.rolling(20).mean()
        def f(s): return float(s.iloc[-1])
        def f2(s): return float(s.iloc[-2])
        cv=f(c); cv2=f2(c); chg=(cv-cv2)/cv2*100 if cv2 else 0
        vol=f(v); av=f(avgv); rv=vol/av if av else 0
        ri=f(rsi); gap=(f(o)-cv2)/cv2*100 if cv2 else 0
        p1m=float(c.iloc[-21]) if len(c)>21 else cv
        drop=(p1m-cv)/p1m*100 if p1m else 0
        tarih=str(df.index[-1].date())
        out=[]
        def s(kod,emoji,aciklama,guven):
            out.append({"sembol":sembol,"tarih":tarih,"strateji_kodu":kod,
                "emoji":emoji,"aciklama":aciklama,"guven":guven,
                "fiyat":round(cv,2),"rsi":round(ri,1),
                "degisim_pct":round(chg,2),"rel_hacim":round(rv,2)})
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
            s("VWAP_SAVASCISI","⚔️","Fiyat VWAP üzerinde tutuyor","ORTA")
        if chg<-2 and ri<35 and cv>f(s200) and vol>500000:
            s("AS_FIRSATI","🌗","Gün içi sert düşüş, toparlanma emaresi","YÜKSEK")
        return out
    except: return []

def hisse_isle(sembol):
    try:
        df=yf.download(f"{sembol}.IS",period="2y",interval="1d",progress=False,auto_adjust=True)
        if df.empty or len(df)<210: return []
        if isinstance(df.columns,pd.MultiIndex): df.columns=df.columns.get_level_values(0)
        return strateji_tara(sembol,df)
    except: return []

def tara():
    print(f"\n🔍 Tarama: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    hisseler=hisse_listesi_al()
    sinyaller=[]
    with ThreadPoolExecutor(max_workers=10) as ex:
        futures={ex.submit(hisse_isle,s):s for s in hisseler}
        for i,fut in enumerate(as_completed(futures),1):
            sonuc=fut.result()
            if sonuc: sinyaller.extend(sonuc)
            if i%50==0: print(f"  ▓ {i}/{len(hisseler)}")
    ozet={}
    for s in sinyaller: ozet[s["strateji_kodu"]]=ozet.get(s["strateji_kodu"],0)+1
    with open(SONUC_DOSYA,"w",encoding="utf-8") as f:
        json.dump({"tarama_tarihi":datetime.now().isoformat(),
            "taranan_hisse_sayisi":len(hisseler),
            "toplam_sinyal":len(sinyaller),
            "strateji_ozeti":ozet,"sinyaller":sinyaller},f,ensure_ascii=False)
    print(f"✅ {len(sinyaller)} sinyal kaydedildi")

@app.route("/")
def index(): return send_file("index.html")

@app.route("/sinyaller.json")
def sinyaller():
    if os.path.exists(SONUC_DOSYA):
        return send_file(SONUC_DOSYA, mimetype="application/json")
    return jsonify({"sinyaller":[],"tarama_tarihi":datetime.now().isoformat()})

def bot_thread():
    tara()
    schedule.every().day.at("18:30").do(tara)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__=="__main__":
    Thread(target=bot_thread, daemon=True).start()
    port=int(os.environ.get("PORT",8080))
    app.run(host="0.0.0.0",port=port)
