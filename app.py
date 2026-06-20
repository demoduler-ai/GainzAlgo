import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from kap_radar import get_kap_signals

from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

from datetime import datetime

st.set_page_config(
    page_title="GainzAlgo V5 Professional",
    layout="wide"
)

@st.cache_data(ttl=604800)

def get_financial_score(symbol):

    print("FINANCIAL CHECKING:", symbol)

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        print("INFO LENGTH:", len(info))
        print(symbol)
        print(info)

        if not info:
            return 50

        print(symbol)
        print("PE:", info.get("trailingPE"))
        print("PB:", info.get("priceToBook"))
        print("ROE:", info.get("returnOnEquity"))
        print("REV:", info.get("revenueGrowth"))
        print("MARGIN:", info.get("profitMargins"))
        print("DEBT:", info.get("debtToEquity"))

        pe = info.get("trailingPE")
        pb = info.get("priceToBook")
        debt = info.get("debtToEquity")

        roe = info.get("returnOnEquity")
        revenue_growth = info.get("revenueGrowth")
        profit_margin = info.get("profitMargins")
        current_ratio = info.get("currentRatio")

        score = 20

        if pe and pe < 10:
            score += 15
        elif pe and pe < 15:
            score += 10
        elif pe and pe < 20:
            score += 5

        if pb and pb < 1:
            score += 15
        elif pb and pb < 2:
            score += 10
        elif pb and pb < 3:
            score += 5

        if debt and debt < 50:
            score += 15
        elif debt and debt < 100:
            score += 10
        elif debt and debt < 150:
            score += 5

        if roe and roe > 0.20:
            score += 15
        elif roe and roe > 0.15:
            score += 10
        elif roe and roe > 0.10:
            score += 5

        if revenue_growth and revenue_growth > 0.20:
            score += 10
        elif revenue_growth and revenue_growth > 0.10:
            score += 5

        if profit_margin and profit_margin > 0.20:
            score += 10
        elif profit_margin and profit_margin > 0.10:
            score += 5

        if current_ratio and current_ratio > 2:
            score += 10
        elif current_ratio and current_ratio > 1.5:
            score += 5

        score = max(0, min(score, 100))
        
        return score

    except Exception as e:
        print("FINANCIAL ERROR:", symbol, e)
        return 0

def get_series(df, column):

    data = df[column]

    if isinstance(data, pd.DataFrame):
        data = data.iloc[:, 0]

    data = pd.to_numeric(data, errors="coerce")

    data = data.dropna()

    return data    


BIST_LIST = [
"AEFES.IS",
"AGHOL.IS",
"AKBNK.IS",
"AKFGY.IS",
"AKFYE.IS",
"AKSA.IS",
"AKSEN.IS",
"ALARK.IS",
"ALFAS.IS",
"ARCLK.IS",
"ASELS.IS",
"ASTOR.IS",
"BERA.IS",
"BIMAS.IS",
"BRSAN.IS",
"CCOLA.IS",
"CIMSA.IS",
"CWENE.IS",
"DOAS.IS","DOHOL.IS",
"ECILC.IS","ECZYT.IS","EGEEN.IS","EKGYO.IS","ENERY.IS",
"ENJSA.IS","ENKAI.IS","EREGL.IS","EUPWR.IS","FROTO.IS",
"GARAN.IS","GESAN.IS","GUBRF.IS","GWIND.IS","HALKB.IS",
"HEKTS.IS","ISCTR.IS","ISMEN.IS","KCAER.IS","KCHOL.IS",
"KLSER.IS","KONTR.IS","KOZAA.IS","KOZAL.IS","KRDMD.IS",
"MAVI.IS","MGROS.IS","MIATK.IS","ODAS.IS","OTKAR.IS",
"OYAKC.IS","PGSUS.IS","PETKM.IS","QUAGR.IS","REEDR.IS",
"SASA.IS","SAHOL.IS","SDTTR.IS","SISE.IS","SKBNK.IS",
"SMRTG.IS","SOKM.IS","TABGD.IS","TAVHL.IS","TCELL.IS",
"THYAO.IS","TKFEN.IS","TOASO.IS","TSKB.IS","TTKOM.IS",
"TTRAK.IS","TUKAS.IS","TUPRS.IS","ULKER.IS","VAKBN.IS",
"VESBE.IS","VESTL.IS","YEOTK.IS","YKBNK.IS","ZOREN.IS"
]

st.sidebar.title("GainzAlgo V5")

selected_symbol = st.sidebar.selectbox(
    "Hisse Seç",
    BIST_LIST
)

if st.sidebar.button("🔄 Verileri Güncelle"):
    st.rerun()

import json
import os

WATCHLIST_FILE = "watchlist.json"
PORTFOLIO_FILE = "portfolio.json"

if "portfolio" not in st.session_state:

    if os.path.exists(PORTFOLIO_FILE):

        with open(
            PORTFOLIO_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            st.session_state.portfolio = json.load(f)

    else:

        st.session_state.portfolio = []

if os.path.exists(WATCHLIST_FILE):
    with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
        st.session_state.watchlist = json.load(f)
else:
    st.session_state.watchlist = []

col1, col2 = st.sidebar.columns(2)

with col1:
    takip_ekle = st.button("⭐ Takibe Ekle")

with col2:
    satin_al = st.button(
        "💰 SATIN AL",
        key="buy_button_top"
    )

if satin_al:

    st.session_state.portfolio.append(
        {
            "symbol": selected_symbol,
            "lot": st.session_state["lot_top"],
            "alis": st.session_state["alis_top"]
        }
    )

    with open(
        PORTFOLIO_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            st.session_state.portfolio,
            f,
            ensure_ascii=False,
            indent=4
        )

    st.sidebar.success(
        f"{selected_symbol} portföye eklendi"
    )

alis = st.sidebar.number_input(
    "Alış Fiyatı",
    min_value=0.01,
    value=10.0,
    key="alis_top"
)

st.sidebar.markdown("### 💰 Portföye Al")

lot = st.sidebar.number_input(
    "Lot",
    min_value=1,
    value=100,
    key="lot_top"
)

st.sidebar.markdown("### 💰 Portföye Al")

if takip_ekle:

    if selected_symbol not in st.session_state.watchlist:

        st.session_state.watchlist.append(
            selected_symbol
        )

        with open(
            WATCHLIST_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                st.session_state.watchlist,
                f,
                ensure_ascii=False,
                indent=4
            )

        with open(
            WATCHLIST_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                st.session_state.watchlist,
                f,
                ensure_ascii=False,
                indent=4
            )

        st.sidebar.success(
            f"{selected_symbol} takip listesine eklendi"
        )

    else:

        st.sidebar.warning(
            "Bu hisse zaten takip listesinde"
        )

st.sidebar.markdown("---")
st.sidebar.subheader("📌 Takip Listem")

for hisse in st.session_state.watchlist:

    col1, col2 = st.sidebar.columns([4, 1])

    col1.write(f"✅ {hisse}")

    if col2.button(
        "❌",
        key=f"delete_{hisse}"
    ):

        st.session_state.watchlist.remove(
            hisse
        )

        with open(
            WATCHLIST_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                st.session_state.watchlist,
                f,
                ensure_ascii=False,
                indent=4
            )

        st.rerun()
st.divider()

st.header("💼 Portföyüm")

if "portfolio" not in st.session_state:

    if os.path.exists("portfolio.json"):

        with open(
            "portfolio.json",
            "r",
            encoding="utf-8"
        ) as f:

            st.session_state.portfolio = json.load(f)

    else:

        st.session_state.portfolio = []

    with open(
        "portfolio.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            st.session_state.portfolio,
            f,
            ensure_ascii=False,
            indent=4
        )

    st.sidebar.success(
        f"{selected_symbol} portföye eklendi"
    )

if len(st.session_state.portfolio) > 0:

    rows = []

    toplam_maliyet = 0
    toplam_guncel = 0

    en_iyi_hisse = ""
    en_iyi_getiri = -999999

    en_kotu_hisse = ""
    en_kotu_getiri = 999999

    kazanan_sayisi = 0
    kaybeden_sayisi = 0

    for item in st.session_state.portfolio:

        try:

            symbol = item["symbol"]

            live = yf.download(
                symbol,
                period="5d",
                progress=False
            )

            close_series = get_series(
                live,
                "Close"
            )

            if len(close_series) >= 1:

                current_price = round(
                    float(close_series.iloc[-1]),
                    2
                )

            else:

                current_price = 0

            maliyet = (
                item["lot"]
                * item["alis"]
            )

            guncel_deger = (
                item["lot"]
                * current_price
            )

            toplam_maliyet += maliyet
            toplam_guncel += guncel_deger

            kar_zarar_yuzde = round(
                (
                    (
                        current_price
                        - item["alis"]
                    )
                    / item["alis"]
                ) * 100,
                2
            )

            kar_tl = round(
                guncel_deger - maliyet,
                2
            )

            if kar_tl > 0:

                kar_tl_text = f"🟢 {kar_tl:,.2f} TL"

            else:

                kar_tl_text = f"🔴 {kar_tl:,.2f} TL"

            if kar_zarar_yuzde > en_iyi_getiri:

                en_iyi_getiri = kar_zarar_yuzde
                en_iyi_hisse = symbol

            if kar_zarar_yuzde < en_kotu_getiri:

                en_kotu_getiri = kar_zarar_yuzde
                en_kotu_hisse = symbol

            if kar_zarar_yuzde > 0:

                kazanan_sayisi += 1

            elif kar_zarar_yuzde < 0:

                kaybeden_sayisi += 1

            rows.append(
    {

        "Hisse": symbol,
        "Lot": item["lot"],
        "Alış": item["alis"],
        "Güncel": current_price,

        "K/Z %":
            f"🟢 %{kar_zarar_yuzde:.2f}"
            if kar_zarar_yuzde > 0
            else (
                f"🔴 %{kar_zarar_yuzde:.2f}"
                if kar_zarar_yuzde < 0
                else "⚪ %0.00"
            ),

        "Kâr TL": kar_tl_text,

        "Toplam": round(
            guncel_deger,
            2
        )
    }
)

        except:

            pass

        
    kar_tutar = round(
        toplam_guncel - toplam_maliyet,
        2
    )

    basari_orani = round(
        (
            kazanan_sayisi
            / len(st.session_state.portfolio)
        ) * 100,
        1
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "💰 Toplam Maliyet",
        f"{toplam_maliyet:,.2f} TL"
    )

    col2.metric(
        "📈 Güncel Değer",
        f"{toplam_guncel:,.2f} TL"
    )

    col3.metric(
        "🚀 Kâr / Zarar",
        f"{kar_tutar:,.2f} TL"
    )

    col4, col5, col6 = st.columns(3)

    col4.metric(
        "🏆 En Karlı",
        en_iyi_hisse
    )

    col5.metric(
        "📉 En Zayıf",
        en_kotu_hisse
    )

    col6.metric(
        "🎯 Başarı",
        f"%{basari_orani}"
    )

    st.info(
    f"""
    🟢 Kazanan: {kazanan_sayisi}

    🔴 Kaybeden: {kaybeden_sayisi}

    📊 Toplam Pozisyon: {len(st.session_state.portfolio)}
    """    
    )

    if len(rows) > 0:

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True
        )

st.markdown("### 🗑️ Portföyden Sil")

silinecek_hisse = st.selectbox(
    "Silinecek Hisse",
    [x["symbol"] for x in st.session_state.portfolio],
    key="delete_portfolio_stock"
)

if st.button(
    "❌ Portföyden Kaldır",
    key="delete_portfolio_button"
):

    st.session_state.portfolio = [
        x
        for x in st.session_state.portfolio
        if x["symbol"] != silinecek_hisse
    ]

    with open(
        "portfolio.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            st.session_state.portfolio,
            f,
            ensure_ascii=False,
            indent=4
        )

    st.rerun()

st.divider()

show_watchlist = st.sidebar.button(
"📊 Takip Listemi Göster"
)

st.markdown(
    "## 🌍 CANLI PİYASALAR"
)

st.caption(
    "Canlı Döviz • Emtia • Kripto Takibi"
)

from datetime import datetime

now = datetime.now()

st.info(
    f"Saat: {now.strftime('%H:%M:%S')} | "
    f"Tarih: {now.strftime('%d.%m.%Y')} | "
    f"Son Güncelleme: CANLI"
)

usd = yf.download(
    "USDTRY=X",
    period="5d",
    progress=False
)

usd_close = get_series(usd, "Close")

if len(usd_close) >= 2:

    usd_price = round(
        float(usd_close.iloc[-1]),
        2
    )

    usd_change = round(
        (
            (usd_close.iloc[-1] /
             usd_close.iloc[-2]) - 1
        ) * 100,
        2
    )

else:

    usd_price = 0

    usd_change = 0

eur = yf.download(
    "EURTRY=X",
    period="5d",
    progress=False
)

eur_close = get_series(eur, "Close")

if len(eur_close) >= 2:

    eur_price = round(
        float(eur_close.iloc[-1]),
        2
    )

    eur_change = round(
        (
            (eur_close.iloc[-1] /
             eur_close.iloc[-2]) - 1
        ) * 100,
        2
    )

else:

    eur_price = 0
    eur_change = 0
gbp = yf.download(
    "GBPTRY=X",
    period="5d",
    progress=False
)

gbp_close = get_series(gbp, "Close")

if len(gbp_close) >= 2:

    gbp_price = round(
        float(gbp_close.iloc[-1]),
        2
    )

    gbp_change = round(
        (
            (gbp_close.iloc[-1] /
             gbp_close.iloc[-2]) - 1
        ) * 100,
        2
    )

else:

    gbp_price = 0
    gbp_change = 0

gold = yf.download(
    "GC=F",
    period="5d",
    progress=False
)

gold_close = get_series(gold, "Close")

if len(gold_close) >= 2:

    gold_price = round(
        float(gold_close.iloc[-1]),
        2
    )

    gold_change = round(
        (
            (gold_close.iloc[-1] /
             gold_close.iloc[-2]) - 1
        ) * 100,
        2
    )

else:

    gold_price = 0
    gold_change = 0

silver = yf.download(
    "SI=F",
    period="5d",
    progress=False
)

silver_close = get_series(silver, "Close")

if len(silver_close) >= 2:

    silver_price = round(
        float(silver_close.iloc[-1]),
        2
    )

    silver_change = round(
        (
            (silver_close.iloc[-1] /
             silver_close.iloc[-2]) - 1
        ) * 100,
        2
    )

else:

    silver_price = 0
    silver_change = 0

btc = yf.download(
    "BTC-USD",
    period="5d",
    progress=False
)

btc_close = get_series(btc, "Close")

if len(btc_close) >= 2:

    btc_price = round(
        float(btc_close.iloc[-1]),
        0
    )

    btc_change = round(
        (
            (btc_close.iloc[-1] /
             btc_close.iloc[-2]) - 1
        ) * 100,
        2
    )

else:

    btc_price = 0
    btc_change = 0

btc_change = round(
    (
        (btc_close.iloc[-1] /
         btc_close.iloc[-2]) - 1
    ) * 100,
    2
)

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric(
    "💵 USD",
    usd_price,
    f"{usd_change}%"
)
col2.metric(
    "💶 EUR",
    eur_price,
    f"{eur_change}%"
)
col3.metric(
    "💷 GBP",
    gbp_price,
    f"{gbp_change}%"
)

col4.metric(
    "🪙 Altın",
    gold_price,
    f"{gold_change}%"
)

col5.metric(
    "🥈 Gümüş",
    silver_price,
    f"{silver_change}%"
)

col6.metric(
    "₿ Bitcoin",
    btc_price,
    f"{btc_change}%"
)

try:

    bist_live = yf.download(
        "XU100.IS",
        period="5d",
        progress=False
    )

    bist_close_live = get_series(
        bist_live,
        "Close"
    )

    bist_change = round(
        (
            (bist_close_live.iloc[-1] /
             bist_close_live.iloc[-2]) - 1
        ) * 100,
        2
    )

    if bist_change > 1:
        market_power = "🟢 GÜÇLÜ"

    elif bist_change > 0:
        market_power = "🟡 POZİTİF"

    else:
        market_power = "🔴 ZAYIF"

    st.success(
        f"📈 BIST100: %{bist_change} | {market_power}"
    )

except:
    pass

st.title("📈 GainzAlgo V5 Professional")

if show_watchlist:

    st.header("📌 Takip Listem")

    watchlist_results = []

    alerts = []

    for hisse in st.session_state.watchlist:

        try:

            wdf = yf.download(
                hisse,
                period="1y",
                auto_adjust=True,
                progress=False
            )

            close = get_series(wdf, "Close")

            volume = get_series(wdf, "Volume")

            if len(close) < 20:
                continue

            
            ema20 = EMAIndicator(close, 20).ema_indicator()
            ema50 = EMAIndicator(close, 50).ema_indicator()

            rsi = RSIIndicator(close, 14).rsi()

            last_price = float(close.iloc[-1])
            daily_change = (
                (close.iloc[-1] / close.iloc[-2]) - 1
            ) * 100
            last_rsi = float(rsi.iloc[-1])

            ai_score = 0

            # Trend
            if ema20.iloc[-1] > ema50.iloc[-1]:
                ai_score += 30

            # RSI
            if 50 <= last_rsi <= 70:
                ai_score += 25

            elif last_rsi > 70:
                ai_score += 10

            elif last_rsi < 40:
                ai_score += 5

            # Hacim Patlaması
            avg_volume = volume.tail(20).mean()

            if volume.iloc[-1] > avg_volume * 1.5:
                ai_score += 25

            # Büyük Para Skoru

            big_money_score = 0

            last20_high = close.tail(20).max()
            avg_volume = volume.tail(20).mean()

            # Hacim
            if volume.iloc[-1] > avg_volume * 2:
                big_money_score += 40

            # AI Alarm Sistemi

            if ai_score >= 80:

                alerts.append(
                f"🚨 {hisse} güçlü alım bölgesinde (AI: {ai_score})"
                )

            if volume.iloc[-1] > avg_volume * 2:

                alerts.append(
                f"💰 {hisse} büyük para girişi tespit edildi"
                )

            if last_rsi < 35:

                alerts.append(
                f"⚠️ {hisse} aşırı satım bölgesinde (RSI: {round(last_rsi,2)})"
                )

            elif volume.iloc[-1] > avg_volume * 1.5:
                big_money_score += 25

            # Trend
            if ema20.iloc[-1] > ema50.iloc[-1]:
                big_money_score += 20

            # RSI
            if 50 <= last_rsi <= 70:
                big_money_score += 20

            # Kırılım
            if last_price >= last20_high:
                big_money_score += 20

            # AI kırılım puanı
            if last_price >= last20_high:
                ai_score += 45

            ai_score = min(ai_score, 100)

            if last_rsi < 30:
                alerts.append(
                    f"🔵 {hisse} → RSI {round(last_rsi,1)} (Dip Bölgesi)"
                )

            if last_rsi > 70:
                alerts.append(
                    f"🟠 {hisse} → RSI {round(last_rsi,1)} (Kar Riski)"
                )

            if ai_score <= 40:
                alerts.append(
                    f"🔴 {hisse} → Zayıf Görünüm"
                )

            if volume.iloc[-1] > avg_volume * 2.5:
                alerts.append(
                f"🔥 {hisse} → Çok Güçlü Para Girişi"
                )

            elif volume.iloc[-1] > avg_volume * 1.5:
                alerts.append(
                    f"💰 {hisse} → Güçlü Para Girişi"
                )

            if ai_score >= 90:
                alerts.append(
                    f"🟢 {hisse} → AI Skor {ai_score}"
                )

            elif ai_score >= 80:
                alerts.append(
                    f"🟡 {hisse} → Güçlü Takip"
                )

            if ai_score >= 80:
                signal = "🟢 AL"

            elif ai_score >= 60:
                signal = "🟡 TAKİP"

            else:
                signal = "🔴 SAT"

            # Son 50 günlük tepe
            target_price = round(
                close.tail(50).max(),
                2
            )

            # Eğer hedef mevcut fiyatın altındaysa
            if target_price <= last_price:
                target_price = round(
                    last_price * 1.08,
                    2
                )

            potential = round(
                (
                    (target_price - last_price)
                    / last_price
                ) * 100,
                2
            )

            watchlist_results.append(
    {
        "Hisse": hisse,
        "Fiyat": round(last_price, 2),
        "Günlük %": round(daily_change, 2),
        "RSI": round(last_rsi, 2),

        "AI_SAYI": ai_score,

        "AI Skor":
            f"🟢 {ai_score}"
            if ai_score >= 80
            else (
                f"🟡 {ai_score}"
                if ai_score >= 60
                else f"🔴 {ai_score}"
            ),

        "Sinyal": signal,

        "Para Skoru":
            f"🔥 {big_money_score}"
            if big_money_score >= 80
            else (
                f"💰 {big_money_score}"
                if big_money_score >= 50
                else f"➖ {big_money_score}"
            ),

        "Büyük Para":
            "🔥 ÇOK GÜÇLÜ"
            if volume.iloc[-1] > avg_volume * 2.5
            else (
                "💰 GÜÇLÜ"
                if volume.iloc[-1] > avg_volume * 1.5
                else "➖ NORMAL"
            ),

        "Yarın AL":
            "🟢 YAKIN"
            if ai_score >= 80
            else (
                "👀 TAKİP"
                if ai_score >= 60
                else "🔴 UZAK"
            ),

        "Hedef": target_price,

        "Potansiyel %":
            f"🚀 {potential}%"
            if potential >= 20
            else (
                f"🟢 {potential}%"
                if potential >= 10
                else f"🟡 {potential}%"
            )
    }
)

        except Exception as e:
            st.error(f"HATA: {e}")

    if len(alerts) > 0:

        st.error("🚨 BUGÜN DİKKAT")

        for a in alerts:
            st.write(a)

        st.divider()

    if len(watchlist_results) > 0:

        watch_df = pd.DataFrame(
            watchlist_results
        )

        watch_df = watch_df.sort_values(
            by="AI_SAYI",
            ascending=False
        )

        favorite = watch_df.iloc[0]

        st.success("Günün Favorisi Hazır")

        watch_df = watch_df[
            [
                "Hisse",
                "Fiyat",
                "Günlük %",
                "RSI",
                "AI Skor",
                "Para Skoru",
                "Sinyal",
                "Büyük Para",
                "Yarın AL",
                "Hedef",
                "Potansiyel %"
            ]
        ]

        st.dataframe(
            watch_df,
            use_container_width=True
        )

    else:

        st.warning(
            "Takip listesinde analiz edilecek hisse bulunamadı."
        )

    st.divider()

st.divider()

# BIST100

bist_df = yf.download(
    "XU100.IS",
    period="1y",
    auto_adjust=False,
    progress=False
)

bist_close = get_series(bist_df, "Close")

results = []

progress = st.progress(0)

all_data = yf.download(
    BIST_LIST,
    period="1y",
    auto_adjust=False,
    group_by="ticker",
    progress=False,
    threads=True
)

for i, symbol in enumerate(BIST_LIST):

    try:

        if symbol not in all_data.columns.get_level_values(0):
            continue

        df = all_data[symbol].copy()
        
        if df.empty:
            continue

        close = get_series(df, "Close")

        high = get_series(df, "High")
        low = get_series(df, "Low")
        volume = get_series(df, "Volume")

        if len(close) < 200:
            continue

        ema20 = EMAIndicator(close, 20).ema_indicator()
        ema50 = EMAIndicator(close, 50).ema_indicator()
        ema200 = EMAIndicator(close, 200).ema_indicator()

        if (
            len(close) < 220
            or len(ema20.dropna()) == 0
            or len(ema50.dropna()) == 0
            or len(ema200.dropna()) == 0
        ):
            continue

        rsi = RSIIndicator(close, 14).rsi()

        macd = MACD(close)

        common_index = close.index.intersection(high.index)
        common_index = common_index.intersection(low.index)

        close = close.loc[common_index]
        high  = high.loc[common_index]
        low   = low.loc[common_index]

        atr = AverageTrueRange(
            high,
            low,
            close
        ).average_true_range()
        
        
        score = 0

        big_money_score = 0

        early_warning = "—"
        tomorrow_signal = "—"
        future_score = 0
       
        if ema20.iloc[-1] > ema50.iloc[-1]:
            score += 15
               
        if ema50.iloc[-1] > ema200.iloc[-1]:
            score += 10

        if close.iloc[-1] > ema200.iloc[-1]:
            score += 10

        rsi_now = rsi.iloc[-1]

        dip_radar = "—"

        if (
            rsi_now > 45 and
            rsi_now < 60 and
            close.iloc[-1] > ema20.iloc[-1] and
            ema20.iloc[-1] > ema50.iloc[-1]
        ):
            dip_radar = "🚀 YAKIN AL"

        elif (
            rsi_now > 45 and
            rsi_now < 55 and
            close.iloc[-1] > ema20.iloc[-1]
):
            dip_radar = "👀 İZLE"

        # Erken Uyarı Sistemi

        if rsi_now > 60 and rsi.iloc[-2] < 55:
            early_warning = "🚀 Yeni Yükseliş"

        elif rsi_now < 45 and rsi.iloc[-2] > 50:
            early_warning = "⚠️ Güç Kaybı"

        if 55 <= rsi_now <= 70:
            score += 15
        elif 50 <= rsi_now < 55:
            score += 10
        elif 40 <= rsi_now < 50:
            score += 5

        macd_diff = macd.macd_diff().iloc[-1]
        macd_prev = macd.macd_diff().iloc[-2]

        if macd_diff > 0:
            score += 10

        if macd_diff > macd_prev:
            score += 5
        avg_volume = volume.tail(20).mean()

        volume_ratio = volume.tail(5).mean() / avg_volume
               
        volume_ratio = volume.tail(5).mean() / avg_volume

        # Büyük Para Skoru

        avg_volume = volume.tail(20).mean()

        if volume.iloc[-1] > avg_volume * 2:
            big_money_score += 40

        elif volume.iloc[-1] > avg_volume * 1.5:
            big_money_score += 25

        if ema20.iloc[-1] > ema50.iloc[-1]:
            big_money_score += 20

        if 50 <= rsi_now <= 70:
            big_money_score += 20

        if close.iloc[-1] >= close.tail(20).max():
            big_money_score += 20

        # Yarın AL Skoru

        future_score = 0

        rsi_now = float(rsi.iloc[-1])

        if rsi_now > rsi.iloc[-2]:
            future_score += 25

        if macd_diff > macd_prev:
            future_score += 25

        distance_ema20 = (
            abs(close.iloc[-1] - ema20.iloc[-1])
            / ema20.iloc[-1]
        ) * 100

        if distance_ema20 < 2:
            future_score += 20

        if volume_ratio > 1:
            future_score += 15

        if ema20.iloc[-1] > ema50.iloc[-1]:
            future_score += 15

        # Ana trend filtresi

        if score < 50:
            future_score -= 20

        if score < 35:
            future_score -= 20

        future_score = min(future_score, score + 10)

        future_score = max(0, future_score)

        # Yarın AL Sinyali

        if (
            future_score >= 80 and
            volume_ratio > 1.3 and
            ema20.iloc[-1] > ema50.iloc[-1]
        ):
            tomorrow_signal = "🚀 YARIN AL"

        elif future_score >= 60:
            tomorrow_signal = "🟢 YAKIN"

        elif future_score >= 40:
            tomorrow_signal = "👀 TAKİP"

        else:
            tomorrow_signal = "—"
          

        if volume_ratio > 2:
            whale_signal = "🐋 GÜÇLÜ KURUMSAL ALIM"

        elif volume_ratio > 1.3:
            whale_signal = "🟢 KURUMSAL İLGİ"

        elif volume_ratio < 0.6:
            whale_signal = "🔴 KURUMSAL SATIŞ"

        else:
            whale_signal = "⚪ NORMAL"

        if volume.iloc[-1] > avg_volume * 2:
            money_flow = "🔥 GÜÇLÜ"

        elif volume.iloc[-1] > avg_volume * 1.3:
            money_flow = "🟢 VAR"

        elif volume.iloc[-1] > avg_volume:
            money_flow = "🟡 ZAYIF"

        else:
            money_flow = "⚪ YOK"

        if volume.iloc[-1] > avg_volume * 1.5:
            score += 15
        elif volume.iloc[-1] > avg_volume:
            score += 8

        momentum20 = (
            (close.iloc[-1] / close.iloc[-20]) - 1
        ) * 100

        bist_momentum20 = (
            (bist_close.iloc[-1] / bist_close.iloc[-20]) - 1
        ) * 100

        relative_strength = (
            momentum20 - bist_momentum20
        )

        if relative_strength > 20:
            rs_text = "🔥 ÇOK GÜÇLÜ"

        elif relative_strength > 10:
            rs_text = "🚀 GÜÇLÜ"

        elif relative_strength > 0:
            rs_text = "🟢 POZİTİF"

        elif relative_strength > -10:
            rs_text = "🟡 ZAYIF"

        else:
            rs_text = "🔴 ÇOK ZAYIF"

        # RS Bonus

        if relative_strength > 20:
            score += 15

        elif relative_strength > 10:
            score += 10

        elif relative_strength > 5:
            score += 5

        elif relative_strength < -10:
            score -= 10

        # Relative Strength

        

        if momentum20 > 15:
            score += 10
        elif momentum20 > 7:
            score += 5

        last_close = float(close.dropna().iloc[-1])
        last_atr = float(atr.dropna().iloc[-1])

        risk_ratio = (last_atr / last_close) * 100

        if risk_ratio < 3:
            score += 10
        elif risk_ratio < 5:
            score += 5

        score = min(score, 100)

        # ATR Bazlı Hedef Hesabı

        target_price = last_close + (last_atr * 4)

        # Çok güçlü hisselerde ekstra hedef

        if score >= 85:
            target_price += last_atr * 2

        elif score >= 75:
            target_price += last_atr * 1

        potential = (
        (target_price / last_close) - 1
        ) * 100

        # Negatif potansiyel cezası

        if potential < 0:
            future_score -= 30

        future_score = max(0, future_score)

        # Çok küçük negatif sapmaları yok say

        if 0 < potential < 2:
            potential = 2.01

        # Nihai Sinyal

        if potential < 0 and score < 50:

            signal = "🔴 SAT"
            action = "SAT"

        elif potential < 0:

            signal = "🟡 DÜZELTMEDE"
            action = "BEKLE"

        elif potential < 2:

            signal = "🟡 GETİRİ DÜŞÜK"
            action = "BEKLE"

        else:

            if score >= 85:
                signal = "🚀 GÜÇLÜ AL"
                action = "AL"

            elif score >= 65:
                signal = "🟢 AL"
                action = "AL"

            elif score >= 50:
                signal = "🟡 BEKLE"
                action = "BEKLE"

            elif score >= 35:
                signal = "🟠 KAR AL"
                action = "KAR AL"

            elif score >= 20:
                signal = "🔴 SAT"
                action = "SAT"

            else:
                signal = "⛔ UZAK DUR"
                action = "UZAK DUR"

        financial_score = get_financial_score(symbol)

        print("FINANCIAL SCORE:", symbol, financial_score)

        # Sıralama Skoru

        rank_score = (
            score * 0.20 +
            future_score * 0.15 +
            financial_score * 0.75 +
            relative_strength * 0.10 +
            big_money_score * 0.10
        )

        # Risk cezası

        rank_score -= risk_ratio * 1.2

        # Büyük para bonusu

        if big_money_score >= 80:
            rank_score += 10

        elif big_money_score >= 60:
            rank_score += 5

        # Kurumsal alım bonusu

        if whale_signal == "🟢 KURUMSAL İLGİ":
            rank_score += 5

        elif whale_signal == "🐋 GÜÇLÜ KURUMSAL ALIM":
            rank_score += 10

        # Para girişi bonusu

        if money_flow == "🔥 GÜÇLÜ":
            rank_score += 5

        elif money_flow == "🟢 VAR":
            rank_score += 2

        # Potansiyel ödülü

        if potential > 20:
            rank_score += 10

        elif potential > 15:
            rank_score += 7

        elif potential > 10:
            rank_score += 4

        elif potential > 7:
            rank_score += 2

        # Negatif potansiyel cezası

        if potential < 0:
            rank_score -= 15

        # Dip Radarı bonusu

        if dip_radar == "🚀 YAKIN AL":
            rank_score += 5

        elif dip_radar == "👀 İZLE":
            rank_score += 2

        trend_power = 0

        # Trend

        if close.iloc[-1] > ema20.iloc[-1]:
            trend_power += 20

        if ema20.iloc[-1] > ema50.iloc[-1]:
            trend_power += 20

        # RSI

        if rsi_now > 70:
            trend_power += 20

        elif rsi_now > 60:
            trend_power += 12

        elif rsi_now > 50:
            trend_power += 6

        # Relative Strength

        if relative_strength > 20:
            trend_power += 35

        elif relative_strength > 10:
            trend_power += 25

        elif relative_strength > 0:
            trend_power += 15

        elif relative_strength > -10:
            trend_power += 5

        trend_power = min(trend_power, 100)

        print(symbol, financial_score)

        results.append({
            "Hisse": symbol,
            "Finansal Skor": financial_score,
            "Dip Radarı": dip_radar,
            "🐋 Büyük Para": whale_signal,
            "Erken Uyarı": early_warning,
            "Para Girişi": money_flow,
            "Karar": action,
            "AI Skor": round(score, 2),
            "Sinyal": signal,
            "RSI": round(rsi_now, 2),
            "Fiyat": round(last_close, 2),
            "Hedef": round(float(target_price), 2),
            "Potansiyel %": round(float(potential), 2),
            "Yarın AL": tomorrow_signal,
            "RS Skor": round(relative_strength, 2),
            "RS Güç": rs_text,
            "Trend Gücü": trend_power,
            "Yarın Skor": future_score,
            "Risk %": round(float(risk_ratio), 2),

        "Fırsat": (
            "🔥 KAÇIRMA" if rank_score >= 60 else
            "🚀 GÜÇLÜ" if rank_score >= 55 else
            "🟢 İYİ" if rank_score >= 45 else
            "👀 TAKİP"
        ),
            "Rank Skor": round(rank_score, 2),
            })

    except Exception as e:
        import traceback

        st.error(f"{symbol} hata: {e}")

        st.code(traceback.format_exc())

        

    progress.progress((i + 1) / len(BIST_LIST))

result_df = pd.DataFrame(results)

top5_df = (
    result_df
    .sort_values(
        by="Rank Skor",
        ascending=False
    )
    .head(5)
)

if result_df.empty:
    st.error("Hiç hisse analiz edilemedi.")
    

result_df = result_df.sort_values(
        "Rank Skor",
        ascending=False
    )

favorite = result_df.iloc[0]

st.success(
    f"""
🏆 GÜNÜN FAVORUMUZ

📌 Hisse: {favorite['Hisse']}

🤖 AI Skoru: {favorite['AI Skor']}
📈 Rank Skoru: {favorite['Rank Skor']}
💰 Finansal Skor: {favorite['Finansal Skor']}
🚀 Yarın Skor: {favorite['Yarın Skor']}

🎯 Potansiyel: %{favorite['Potansiyel %']}
⚠️ Risk: %{favorite['Risk %']}

📊 Karar: {favorite['Karar']}
🔥 Fırsat: {favorite['Fırsat']}
"""
)

if not result_df.empty:

    st.header("🏆 BUGÜNÜN EN GÜÇLÜ 10 HİSSESİ")

    top10 = (
        result_df
        .sort_values(
            by="Rank Skor",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        top10[
            [
                "Hisse",
                "AI Skor",
                "Rank Skor",
                "Karar",
                "Fırsat",
                "Potansiyel %"
            ]
        ],
        use_container_width=True
    )

    st.divider()

st.header("🏆 Yarının En Güçlü 5 Hissesi")

top5_show = top5_df[
    [
        "Hisse",
        "Karar",
        "Rank Skor",
        "Yarın AL",
        "Hedef",
        "Potansiyel %",
        "Risk %"
    ]
]

st.dataframe(
    top5_show,
    use_container_width=True
)

st.divider()

st.subheader("🏅 Günün En Güçlü Hisseleri")

st.dataframe(
    result_df,
    use_container_width=True
)

st.subheader("🚨 Yaklaşan AL Sinyalleri")

dip_df = result_df[
    result_df["Dip Radarı"] == "🚀 YAKIN AL"
]

if len(dip_df) > 0:

    st.success("🚀 Dipten Toplama Adayları")

    st.dataframe(
        dip_df,
        use_container_width=True
    )

else:

    st.info(
        "Şu an güçlü dip adayı bulunamadı."
    )

early_df = result_df[
    result_df["Erken Uyarı"] == "🚀 Yeni Yükseliş"
]

if len(early_df) > 0:

    st.dataframe(
        early_df,
        use_container_width=True
    )

else:

    st.info(
        "Şu anda yaklaşan güçlü AL sinyali yok."
    )

st.subheader("🔮 Yarın AL Verebilecek Hisseler")

future_df = result_df[
    (
        result_df["Yarın AL"].isin(
            ["🚀 YARIN AL", "🟢 YAKIN"]
        )
    )
    &
    (
        result_df["Karar"].isin(
            ["AL"]
        )
    )
]

if len(future_df) > 0:

    st.dataframe(
        future_df.sort_values(
            "Yarın Skor",
            ascending=False
        ),
        use_container_width=True
    )

else:

    st.info(
        "Şu an güçlü aday bulunamadı."
    )

st.subheader("📢 KAP Radar")

kap_df = get_kap_signals()

st.dataframe(
    kap_df,
    use_container_width=True
)

st.subheader("🔥 Top 10")

st.table(
    result_df.head(10)
)

st.divider()

st.markdown("---")

st.divider()

st.subheader("📊 SEÇİLEN HİSSE ANALİZİ")

st.markdown(
    f"## 🏦 {selected_symbol}"
)
   
df = yf.download(
    selected_symbol,
    period="1y",
    auto_adjust=True,
    progress=False
)

close = get_series(df, "Close")
high = get_series(df, "High")
low = get_series(df, "Low")

ema20 = EMAIndicator(close, 20).ema_indicator()
ema50 = EMAIndicator(close, 50).ema_indicator()
ema200 = EMAIndicator(close, 200).ema_indicator()

if (
    len(close) < 220
    or len(ema20.dropna()) == 0
    or len(ema50.dropna()) == 0
    or len(ema200.dropna()) == 0
):
    st.error("Yeterli veri yok.")
    

rsi = RSIIndicator(close, 14).rsi()

atr = AverageTrueRange(
    high,
    low,
    close
).average_true_range()

last_close = float(close.dropna().iloc[-1])

risk_ratio = (
    float(atr.dropna().iloc[-1]) /
    last_close
) * 100

last_atr = float(atr.dropna().iloc[-1])

entry_price = last_close

stop_price = last_close - (2 * last_atr)

target1 = last_close + (2 * last_atr)

target2 = last_close + (4 * last_atr)

target3 = last_close + (6 * last_atr)

risk_reward = (
    (target3 - entry_price)
    /
    (entry_price - stop_price)
)

if len(close.dropna()) > 20:
    momentum20 = (
        (close.iloc[-1] / close.iloc[-20]) - 1
    ) * 100
else:
    momentum20 = 0

target_price = last_close + (last_atr * 4)

potential = (
    (target_price / close.iloc[-1]) - 1
) * 100

if potential < 0:
    future_score = 0
    tomorrow_signal = "—"

# Nihai Sinyal

if potential < 0:

    signal = "🔴 HEDEF AŞAĞIDA"
    action = "SAT"

elif potential < 2:

    signal = "🟡 GETİRİ DÜŞÜK"
    action = "BEKLE"

# Negatif potansiyel cezası


detail_score = 0

detail_score = 0

if ema20.iloc[-1] > ema50.iloc[-1]:
    detail_score += 15

if ema50.iloc[-1] > ema200.iloc[-1]:
    detail_score += 10

if last_close > ema200.iloc[-1]:
    detail_score += 10

rsi_now = float(rsi.iloc[-1])

if 55 <= rsi_now <= 70:
    detail_score += 15

elif 50 <= rsi_now < 55:
    detail_score += 10

elif 40 <= rsi_now < 50:
    detail_score += 5

if detail_score >= 85:
    detail_signal = "🚀 GÜÇLÜ AL"
    trend_text = "Güçlü Yükseliş"

elif detail_score >= 70:
    detail_signal = "🟢 AL"
    trend_text = "Yükseliş"

elif detail_score >= 55:
    detail_signal = "🟡 BEKLE"
    trend_text = "Yatay"

elif detail_score >= 40:
    detail_signal = "🟠 KAR AL"
    trend_text = "Zayıflıyor"

else:
    detail_signal = "🔴 SAT"
    trend_text = "Düşüş"

st.subheader("🎯 İşlem Planı")

reward_ratio = (
    target3 - last_close
) / (
    last_close - stop_price
)


if reward_ratio >= 3:
    st.success("🟢 ALIM İÇİN UYGUN")

elif reward_ratio >= 2:
    st.warning("🟡 TAKİP ET")

else:
    st.error("🔴 UZAK DUR")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Giriş",
    round(entry_price, 2)
)

c2.metric(
    "Stop",
    round(stop_price, 2)
)

c3.metric(
    "Hedef 1",
    round(target1, 2)
)

c4.metric(
    "Hedef 2",
    round(target2, 2)
)

c5.metric(
    "Hedef 3",
    round(target3, 2)
)

st.info(
    f"Risk / Getiri Oranı : 1 : {risk_reward:.2f}"
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Fiyat",
    round(last_close, 2)
)

col2.metric(
    "RSI",
    round(float(rsi.iloc[-1]), 2)
)

col3.metric(
    "Hedef",
    round(float(target_price), 2)
)

col4.metric(
    "Potansiyel %",
    round(float(potential), 2)
)

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df.index,
        y=close,
        name="Fiyat"
    )
)

fig.add_trace(
    go.Scatter(
        x=df.index,
        y=ema20,
        name="EMA20"
    )
)

fig.add_trace(
    go.Scatter(
        x=df.index,
        y=ema50,
        name="EMA50"
    )
)

fig.add_trace(
    go.Scatter(
        x=df.index,
        y=ema200,
        name="EMA200"
    )
)

fig.update_layout(
    height=650
)

st.plotly_chart(
    fig,
    use_container_width=True
)

detail_volume = get_series(df, "Volume")

avg_volume_detail = detail_volume.tail(20).mean()

last_volume = detail_volume.iloc[-1]

if last_volume > avg_volume_detail * 2:
    money_flow_detail = "🔥 GÜÇLÜ PARA GİRİŞİ"

elif last_volume > avg_volume_detail * 1.3:
    money_flow_detail = "🟢 PARA GİRİŞİ VAR"

elif last_volume > avg_volume_detail:
    money_flow_detail = "🟡 HAFİF PARA GİRİŞİ"

else:
    money_flow_detail = "⚪ PARA GİRİŞİ YOK"

st.info(
    f"Para Akışı: {money_flow_detail}"
)

st.success(
    f"Risk Seviyesi: %{risk_ratio:.2f}"
)

st.divider()

st.subheader("🎯 Dip Radarı")

if (
    rsi.iloc[-1] > 45 and
    rsi.iloc[-1] < 60 and
    last_close > ema20.iloc[-1] and
    ema20.iloc[-1] > ema50.iloc[-1]
):

    st.success(
        "🚀 Dipten çıkış başladı"
    )

elif (
    rsi.iloc[-1] > 40 and
    last_close > ema20.iloc[-1]
):

    st.warning(
        "👀 Yakından takip edilmeli"
    )

else:

    st.info(
        "Şu an dip formasyonu yok"
    )


st.subheader("📡 Erken Uyarı Sistemi")

if rsi.iloc[-1] > 60 and rsi.iloc[-2] < 55:
    st.success("🚀 Yeni Yükseliş Başlıyor")

elif rsi.iloc[-1] < 45 and rsi.iloc[-2] > 50:
    st.error("⚠️ Güç Kaybı Başladı")

else:
    st.info("ℹ️ Şu an kritik sinyal yok")

st.subheader("🤖 GainzAlgo AI Yorumu")

# Trend

if ema20.iloc[-1] > ema50.iloc[-1] > ema200.iloc[-1]:
    trend = "📈 Güçlü Yükseliş"

elif ema20.iloc[-1] > ema50.iloc[-1]:
    trend = "🟢 Yükseliş"

elif ema20.iloc[-1] < ema50.iloc[-1] < ema200.iloc[-1]:
    trend = "📉 Güçlü Düşüş"

else:
    trend = "🟡 Kararsız"

# Momentum

if rsi.iloc[-1] > 60:
    momentum = "🚀 Güçlü"

elif rsi.iloc[-1] > 50:
    momentum = "🟢 Pozitif"

elif rsi.iloc[-1] > 40:
    momentum = "🟡 Nötr"

else:
    momentum = "🔴 Zayıf"

# Risk

if risk_ratio < 3:
    risk_text = "🟢 Düşük"

elif risk_ratio < 5:
    risk_text = "🟡 Orta"

else:
    risk_text = "🔴 Yüksek"

# Nihai Karar

if reward_ratio >= 3 and rsi.iloc[-1] > 55:
    final_decision = "🟢 AL"

elif reward_ratio >= 2:
    final_decision = "🟡 TAKİP ET"

else:
    final_decision = "🔴 UZAK DUR"

# Güven Skoru

confidence = 50

# Trend
if ema20.iloc[-1] > ema50.iloc[-1]:
    confidence += 10

if ema50.iloc[-1] > ema200.iloc[-1]:
    confidence += 10

# RSI
if rsi.iloc[-1] > 60:
    confidence += 10

elif rsi.iloc[-1] > 50:
    confidence += 5

# Risk
if risk_ratio < 3:
    confidence += 10

elif risk_ratio < 5:
    confidence += 5

# Risk/Getiri
if reward_ratio >= 3:
    confidence += 10

elif reward_ratio >= 2:
    confidence += 5

confidence = min(confidence, 90)

if confidence > 95:
    confidence = 95

st.write(f"Trend: {trend}")
st.write(f"Momentum: {momentum}")
st.write(f"Risk: {risk_text}")

st.divider()

st.success(f"Karar: {final_decision}")


trend_power = 0

if close.iloc[-1] > ema20.iloc[-1]:
    trend_power += 25

if ema20.iloc[-1] > ema50.iloc[-1]:
    trend_power += 25

if ema50.iloc[-1] > ema200.iloc[-1]:
    trend_power += 20

if rsi_now > 60:
    trend_power += 15
elif rsi_now > 50:
    trend_power += 10

if relative_strength > 20:
    trend_power += 15
elif relative_strength > 10:
    trend_power += 10
elif relative_strength > 0:
    trend_power += 5

trend_power = min(trend_power, 100)

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Güven Skoru",
        f"%{confidence}"
    )

with col2:
    st.metric(
        "Trend Gücü",
        f"%{trend_power}"
    )