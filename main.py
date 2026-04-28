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
SONUC = "sinyaller.json"
SAAT = "18:30"

def hisseler():
    try:
        r = requests.get("https://bigpara.hurriyet.com.tr/api/v1/hisse/list",
            headers={"User-Agent":"Mozilla/5.0"}, timeout=15)
        items = r.json().get("data", [])
        s = [i.get("kod","") for i in items if str(i.get("kod","")).isalpha()]
        if len(s) > 100: return sorted(set(s))
    except: pass
    return sorted(list(set([
        "A1CAP","ACSEL","ADEL","ADESE","ADGYO","AEFES","AFYON","AGESA","AGHOL","AGROT",
        "AHGAZ","AKCNS","AKENR","AKFYE","AKGRT","AKSA","AKSEN","AKSUE","ALARK","ALBRK",
        "ALKIM","ALGYO","ALMAD","ALTNY","ALVES","ANELE","ANHYT","ANSGR","ARCLK","ARDYZ",
        "ARSAN","ASELS","ASTOR","ATEKS","AYGAZ","AZTEK","BAGFS","BANVT","BFREN","BIMAS",
        "BIOEN","BIZIM","BJKAS","BOSSA","BRISA","BRKSN","BTCIM","BUCIM","BURCE","CEMAS",
        "CEMTS","CIMSA","CLEBI","CUSAN","CWENE","DEVA","DITAS","DMSAS","DOAS","DOGUB",
        "DOHOL","DYOBY","ECILC","ECZYT","EDIP","EGEEN","EGGUB","EKSUN","EMKEL","ENERY",
        "ENGYO","ENJSA","ENKAI","EPLAS","ERBOS","EREGL","ERSU","ESCAR","ETILR","EUHOL",
        "FENER","FRIGO","FROTO","FZLGY","GARAN","GEREL","GESAN","GLRYH","GLYHO","GOODY",
        "GOZDE","GRSEL","GSDHO","GSRAY","GUBRF","HALKB","HATEK","HEKTS","HUBVC","HURGZ",
        "IHLGM","IHLAS","INDES","INFO","ISCTR","ISDMR","ISGYO","IZOCM","JANTS","KAREL",
        "KARTN","KCHOL","KORDS","KOZAA","KOZAL","KRDMD","LOGO","MAVI","MERCN","MGROS",
        "MNDRS","NETAS","NUHCM","ODAS","OTKAR","OYAKC","PETKM","PGSUS","PINSU","POIPY",
        "POLHO","POYNT","SAHOL","SANEL","SANKO","SARKY","SASA","SISE","SKBNK","SOKM",
        "TATGD","TAVHL","TCELL","THYAO","TKFEN","TOASO","TSKB","TTKOM","TTRAK","TUPRS",
        "ULUSE","VAKBN","VESBE","VESTL","YATAS","YKBNK","YUNSA","ZOREN","ARASE","ARENA",
        "ARTMS","ATAKP","ATATP","ATPET","AVHOL","AVGYO","AVOD","AVTUR","AYCES","AYEN",
        "BAGFS","BAKAB","BALAT","BARMA","BASCM","BASGZ","BATRA","BIENY","BMEKS","BMSCH",
        "BNTAS","BOBET","BRKVY","BRMEN","BRYAT","BSOKE","BURVA","BVSAN","CANTE","CASA",
        "CMBTN","CMENT","CRFSA","CWENE","DAPGM","DARDL","DENGE","DERHL","DERIM","DGATE",
        "DGKLB","DGNMO","DMRGD","DNISI","DOBUR","DOCO","DRMAS","DTRND","DURAN","DZGYO",
        "EGPRO","EGSER","ELITE","EMNIS","ENFRA","ENTRA","ERCB","ERDEK","ESCOM","ESEN",
        "ETYAT","EUREN","EUYO","FMIZP","FORTE","GDKGS","GEDIK","GEDZA","GENTS","GLBMD",
        "GLCVY","GOLDS","GOLTS","GRTRK","GSDDE","GWIND","GZNMI","HDFGS","HEDEF","HLGYO",
        "HTTBT","HUNER","ICBCT","IEYHO","IHEVA","IHGZT","IMASM","INTEM","IPEKE","ISATR",
        "ISFIN","ISGSY","ISKPL","ISLTR","ISYAT","ITTFH","IZFAS","KAPLM","KATMR","KAYSE",
        "KBORU","KCAER","KERVT","KFEIN","KGYO","KLGYO","KLKIM","KLMSN","KLNMA","KLRHO",
        "KLSER","KMPUR","KNFRT","KONKA","KONTR","KONYA","KOPOL","KRONT","KRPLS","KRSTL",
        "KRTEK","KTLEV","KTSKR","KUTPO","KUVVA","LIDER","LILAK","LINK","LKMNH","LRSHO",
        "LUZAM","MACKO","MAGEN","MAKIM","MAKTK","MANAS","MARTI","MEDTR","MEGAP","MEKAG",
        "MERIT","MERKO","METRO","METUR","MHRGY","MIPAZ","MNDTR","MOBTL","MOGAN","MOLPE",
        "MSGYO","MTRKS","MZHLD","NATEN","NIBAS","NTTUR","NUGYO","OFSYM","ONCSM","ONRYT",
        "ORCAY","ORGE","ORMA","OSMEN","OSTIM","OYYAT","OZGYO","OZKGY","OZRDN","PAGYO",
        "PAMEL","PAPIL","PARSN","PASEU","PATEK","PCILT","PEGYO","PEKGY","PKART","PNLSN",
        "POLSA","POLTK","PRZMA","PSDTC","PSGYO","RALYH","RAYSG","RBNK","RCOLS","RYGYO",
        "RHEAG","RISK","RNPOL","RODRG","SAHOL","SANFM","SAYAS","SDTTR","SEGMN","SEKFK",
        "SEKUR","SELEC","SELVA","SENTE","SEYKM","SILVR","SKTAS","SKYLP","SMART","SNKRN",
        "SODSN","SONME","SRVGY","SUMAS","SUNTK","SUPRV","SURGY","TARKM","TBORG","TDGYO",
        "TEKTU","TETMT","TEZOL","TKNSA","TLMAN","TMPOL","TOASO","TRCAS","TRGYO","TRILC",
        "TSGYO","TSMLR","TUCLK","TUKAS","TUREX","TURGG","TURKB","TURSG","ULUFA","ULUUN",
        "UMPAS","UNLU","USAK","USDTR","UTPYA","VAKFN","VAKKO","VBTYZ","VERUS","VKFYO",
        "VKGYO","VKING","VRGYO","YAPRK","YAYLA","YBTAS","YGGYO","YKSLN","YONGA","YYLGD",
        "ZEDUR","ZRGYO",
    ])))

def sma(c,p): return c.rolling(p).mean()
def ema(c,p): return c.ewm(span=p,adjust=False).mean()
def rsi(c,p=14):
    d=c.diff(); g=d.clip(lower=0).rolling(p).mean()
    l=(-d.clip(upper=0)).rolling(p).mean()
    return 100-(100/(1+g/l.replace(0,np.nan)))
def boll(c,p=20):
    m=sma(c,p); s=c.rolling(p).std()
    return m+2*s, m-2*s, (4*s)/m*100
def vwap(h,l,c,v,p=10):
    tp=(h+l+c)/3
    return (tp*v).rolling(p).sum()/v.rolling(p).sum().replace(0,np.nan)

def tara_hisse(sym):
    try:
        df=yf.download(f"{sym}.IS",period="2y",interval="1d",progress=False,auto_adjust=True)
        if df.empty or len(df)<210: return []
        if isinstance(df.columns,pd.MultiIndex): df.columns=df.columns.get_level_values(0)
        c=df["Close"].squeeze(); h=df["High"].squeeze()
        l=df["Low"].squeeze(); o=df["Open"].squeeze(); v=df["Volume"].squeeze()
        ri=rsi(c); s50=sma(c,50); s200=sma(c,200)
        e20=ema(c,20); e50=ema(c,50); e200=ema(c,200)
        vw=vwap(h,l,c,v); ub,lb,bw=boll(c); av=v.rolling(20).mean()
        def f(s): return float(s.iloc[-1])
        def f2(s): return float(s.iloc[-2])
        cv=f(c); pv=f2(c); chg=(cv-pv)/pv*100 if pv else 0
        vol=f(v); avg=f(av); rv=vol/avg if avg else 0
        r=f(ri); gap=(f(o)-pv)/pv*100 if pv else 0
        p1m=float(c.iloc[-21]) if len(c)>21 else cv
        drop=(p1m-cv)/p1m*100 if p1m else 0
        tarih=str(df.index[-1].date())
        out=[]
        def s(kod,em,ac,gv):
            out.append({"sembol":sym,"tarih":tarih,"strateji_kodu":kod,
                "emoji":em,"aciklama":ac,"guven":gv,"fiyat":round(cv,2),
                "rsi":round(r,1),"degisim_pct":round(chg,2),"rel_hacim":round(rv,2)})
        if cv>f(e20) and 40<=r<=89 and f(e20)>f(e50) and vol>avg:
            s("MOMENTUM_ALFA","🚀",f"Fiyat EMA20 üzerinde RSI={r:.1f}","ORTA")
        if f(e20)>f(e50)>f(e200) and 40<=r<=65:
            s("ALTIN_TARAMA","⭐","EMA20>EMA50>EMA200 dizilim","YÜKSEK")
        if 25<=r<=40 and cv>f(s200) and drop>5:
            s("DIP_AVCISI","🌊",f"1 aylık düşüş %{drop:.1f} SMA200 üstü","YÜKSEK")
        if f(bw)<10 and f(e50)>f(e200) and 40<=r<=60:
            s("PATLAMA_ONCESI","💣",f"Bollinger %{f(bw):.1f} sıkışma","YÜKSEK")
        if cv>f(ub) and r>60 and vol>avg*1.5:
            s("ROKET_RAMPA","🚀","Bollinger üst bant kırışı + hacim","ORTA")
        if rv>2 and chg>2 and cv>f(e20) and vol>500000:
            s("AKILLI_PARA","💼",f"Relatif Hacim {rv:.1f}x kurumsal ilgi","YÜKSEK")
        if f(e20)>f(e50) and 50<=r<=70 and vol>1000000:
            s("TREND_SORFCUSU","🏄","Güçlü trende biniş fırsatı","ORTA")
        if f2(s50)<=f2(s200) and f(s50)>f(s200) and cv>f(s200):
            s("GOLDEN_CROSS","✨","SMA50 SMA200'ü yukarı kesti","ÇOK YÜKSEK")
        if f2(s50)>=f2(s200) and f(s50)<f(s200) and cv<f(s200):
            s("DEATH_CROSS","☠️","SMA50 SMA200'ü aşağı kesti","ÇOK YÜKSEK")
        if gap>2 and chg>1 and rv>1.5 and vol>500000:
            s("SABAH_AVCISI","🌅",f"%{gap:.2f} GAP açılışı","ORTA")
        if chg>3 and rv>2 and 55<=r<=75 and cv>f(vw):
            s("MOMENTUM_BOMBASI","💥","Hacimli yükseliş VWAP üstü","YÜKSEK")
        if cv>f(vw) and chg>0 and 50<=r<=70 and vol>500000:
            s("VWAP_SAVASCISI","⚔️","Fiyat VWAP üzerinde","ORTA")
        if chg<-2 and r<35 and cv>f(s200) and vol>500000:
            s("AS_FIRSATI","🌗","Sert düşüş toparlanma emaresi","YÜKSEK")
        return out
    except: return []

def tara():
    print(f"🔍 Tarama: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    liste=hisseler(); sonuc=[]
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs={ex.submit(tara_hisse,s):s for s in liste}
        for i,fut in enumerate(as_completed(futs),1):
            r=fut.result()
            if r: sonuc.extend(r)
            if i%50==0: print(f"  {i}/{len(liste)}")
    ozet={}
    for s in sonuc: ozet[s["strateji_kodu"]]=ozet.get(s["strateji_kodu"],0)+1
    with open(SONUC,"w",encoding="utf-8") as f:
        json.dump({"tarama_tarihi":datetime.now().isoformat(),
            "taranan_hisse_sayisi":len(liste),"toplam_sinyal":len(sonuc),
            "strateji_ozeti":ozet,"sinyaller":sonuc},f,ensure_ascii=False)
    print(f"✅ {len(sonuc)} sinyal kaydedildi")

@app.route("/")
def index(): return send_file("index.html")

@app.route("/sinyaller.json")
def get_sinyaller():
    if os.path.exists(SONUC):
        return send_file(SONUC, mimetype="application/json")
    return jsonify({"sinyaller":[],"tarama_tarihi":datetime.now().isoformat(),
        "toplam_sinyal":0,"taranan_hisse_sayisi":0})

def bot():
    tara()
    schedule.every().day.at(SAAT).do(tara)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__=="__main__":
    Thread(target=bot,daemon=True).start()
    port=int(os.environ.get("PORT",8080))
    app.run(host="0.0.0.0",port=port)
