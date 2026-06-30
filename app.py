import streamlit as st
import yfinance as yf

import pandas as pd
import json
import os
import plotly.graph_objects as go
from kap_radar import get_kap_signals


from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

from datetime import datetime
from modules.ai_panel import show_ai_panel
from modules.stock_analysis import show_stock_analysis_header
from modules.ai_prefilter import passes_ai_prefilter
from modules.accuracy_update import update_accuracy_history
from modules.stock_analysis_page import show_stock_analysis_page
from modules.analysis_engine import analyze_stock
from modules.dashboard_market import show_market_panel
from modules.dashboard_data import get_dashboard_data

from modules.portfolio_page import show_portfolio_page
from modules.scanner_page import show_scanner_page
from modules.backtest_page import show_backtest_page
from modules.favorite_page import show_favorite_page
from modules.live_market_page import show_live_market_page
from modules.portfolio_page import show_portfolio_page
from modules.scanner_top10 import prepare_scanner_lists, prepare_dashboard_data
from modules.scanner_tomorrow import prepare_tomorrow_table

from modules.stock_analysis_page import show_stock_analysis_page


from modules.dashboard import (
    show_dashboard,
    show_dashboard_header,
    show_dashboard_style,
)

from modules.session import (
    get_result_df,
    has_result_df,
    set_result_df,
)

import modules.market_data as market

from modules.scoring import (
    calculate_financial_score,
    calculate_rank_score,
    calculate_trend_power,
    calculate_success_probability,
    calculate_expected_return,
    calculate_risk_adjusted_score,
)

from modules.paths import (
    PORTFOLIO_FILE,
    WATCHLIST_FILE,
    BACKTEST_FILE,
    FAVORITE_FILE,
)

from modules.utils import get_series

from modules.ai_engine import calculate_ai_engine

from modules.decision_engine import calculate_decision

from modules.ai_core import evaluate_stock

from modules.learning_engine import get_learning_bonus

from modules.constants import (
    BANKA_HISSELERI,
    ENERJI_HISSELERI,
    SAVUNMA_HISSELERI,
    SANAYI_HISSELERI,
)

from modules.portfolio import (
    load_portfolio,
    save_portfolio,
    load_watchlist,
    save_watchlist,
)

from modules.sectors import get_best_stock_from_sector

from modules.backtest import update_backtest_results

from modules.data_manager import (
    get_selected_stock_data,
)

from modules.technical import (
    get_stock_data,
    calculate_emas,
    calculate_rsi,
)

from modules.signals import (
    initialize_signals,
    calculate_trend_score,
    calculate_early_warning,
    calculate_rsi_score,
    calculate_macd_score,
    calculate_big_money_score,
    calculate_future_score,
    calculate_whale_signal,
    calculate_money_flow,
    calculate_relative_strength,
)

st.set_page_config(
    page_title="GainzAlgo V5 Professional",
    layout="wide"
)

from modules.constants import BIST_LIST

st.sidebar.title("GainzAlgo V5")

PAGE_DASHBOARD = "🏠 Dashboard"
PAGE_ANALYSIS = "📈 Hisse Analizi"
PAGE_PORTFOLIO = "⭐ AI Sepeti"
PAGE_SCANNER = "🔍 AI Tarayıcı"
PAGE_BACKTEST = "📊 Backtest Sonuçları"

page = st.sidebar.radio(
    "Menü",
    [
        PAGE_DASHBOARD,
        PAGE_ANALYSIS,
        PAGE_PORTFOLIO,
        PAGE_SCANNER,
        PAGE_BACKTEST,
    ]
)


st.sidebar.write("Toplam Hisse:", len(BIST_LIST))

selected_symbol = st.sidebar.selectbox(
    "Hisse Seç",
    BIST_LIST
)

# =====================================================
# ANA EKRAN
# =====================================================

if False:

    dashboard_data = st.session_state.get("dashboard_data", {})

    show_dashboard(
        dashboard_data=dashboard_data,
        selected_symbol=selected_symbol,
    )
        
    bist_price, bist_change = market.get_bist100()
    eur_price, eur_change = market.get_eurtry()
    gold_price, gold_change = market.get_gold()
    usd_price, usd_change = market.get_usdtry()
    btc_price, btc_change = market.get_bitcoin()

    st.write(st.session_state.get("dashboard_data"))
        
        
# =====================================================
# Dashboard Yakında Aktif Olacak Modüller
# =====================================================






# =====================================================
# PORTFOLIO
# =====================================================

if page == "⭐ AI Sepeti":
    show_portfolio_page()

# =====================================================
# 🔍 AI TARAMA MERKEZİ
# =====================================================

if page == "🔍 AI Tarayıcı":

    st.title("🔍 AI Tarama Merkezi")

    st.markdown("### 📊 AI Tarama Listeleri")

    # =====================================================
    # Bugünün En Güçlü 10 Hissesi
    # =====================================================

    with st.expander("🏆 Bugünün En Güçlü 10 Hissesi", expanded=True):

        if "top10_df" in st.session_state:

            st.dataframe(
                st.session_state["top10_df"],
                use_container_width=True
            )

    # =====================================================
    # 🔮 Yarının En Güçlü 5 Hissesi
    # =====================================================

    with st.expander("🔮 Yarının En Güçlü 5 Hissesi"):

        if "tomorrow_df" in st.session_state:

            st.dataframe(
                st.session_state["tomorrow_df"][
                    [
                        "Hisse",
                        "Karar",
                        "AI Puanı",
                        "AI Güven",
                        "Trend Gücü",
                        "Yarın AL",
                        "Dip Radarı",
                        "🐋 Büyük Para",
                        "Hedef",
                        "Potansiyel %",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

    # =====================================================
    # Yaklaşan AL Sinyalleri
    # =====================================================

    with st.expander("🚨 Yaklaşan AL Sinyalleri"):

        if "result_df" in st.session_state:

            st.write(
                st.session_state["result_df"][["Hisse", "Yarın AL"]]
            )

    # =====================================================
    # Dip Radarı
    # =====================================================

    with st.expander("🎯 Dip Radarı"):

        if "result_df" in st.session_state:

            dip_df = (
                st.session_state["result_df"]
                .loc[
                    st.session_state["result_df"]["Dip Radarı"] == "🚀 YAKIN AL"
                ]
            )

            if dip_df.empty:
                st.info("Dip Radarı adayı bulunamadı.")
            else:
                st.dataframe(
                    dip_df,
                    use_container_width=True
                )

    # =====================================================
    # KAP Radar
    # =====================================================

    with st.expander("📢 KAP Radar"):

        kap_df = get_kap_signals()

        if kap_df.empty:
            st.info("Bugün önemli KAP bildirimi bulunamadı.")
        else:
            st.dataframe(
                kap_df,
                use_container_width=True
            )

    # =====================================================
    # Tüm Hisseler
    # =====================================================

    with st.expander("📊 Tüm Hisseler"):

        if "result_df" in st.session_state:

            st.dataframe(
                st.session_state["result_df"],
                use_container_width=True
            )

if st.sidebar.button("🔄 Verileri Güncelle"):
    st.rerun()

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

st.session_state.watchlist = load_watchlist()

yatirim_tutari = st.sidebar.number_input(
    "Yatırım Tutarı (TL)",
    min_value=100,
    value=20000,
    step=1000
)

try:
    fiyat_df = yf.download(
        selected_symbol,
        period="5d",
        auto_adjust=False,
        progress=False
    )

    # st.dataframe(fiyat_df.tail())

    close_series = (
        fiyat_df["Close"]
        .squeeze()
    )

    open_series = (
        fiyat_df["Open"]
        .squeeze()
    )

    if pd.notna(close_series.iloc[-1]):
        alis = round(
            float(close_series.iloc[-1]),
            2
        )
    else:
        alis = round(
            float(open_series.iloc[-1]),
            2
        )

except Exception as e:
    st.sidebar.error(str(e))
    alis = 10.0

st.sidebar.metric(
    "Güncel Fiyat",
    f"{alis} TL"
)

lot = int(yatirim_tutari / alis)

st.sidebar.info(
    f"📦 Otomatik Lot: {lot:,}"
)

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
            "lot": lot,
            "alis": alis
        }
    )

    save_portfolio(st.session_state.portfolio)

    st.sidebar.success(
        f"{selected_symbol} portföye eklendi"
    )

if takip_ekle:

    if selected_symbol not in st.session_state.watchlist:

        st.session_state.watchlist.append(
            selected_symbol
        )

        save_watchlist(st.session_state.watchlist)

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

        # -------------------------
        # Data Manager Test
        # -------------------------

        result_df = st.session_state.get("result_df")

        selected_stock = get_selected_stock_data(
            result_df,
            selected_symbol
        )

        if selected_stock is not None:

            st.write(selected_stock.index.tolist())

            st.sidebar.info(
                f"AI Skor: {selected_stock['AI Skor']}"
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

            save_watchlist(st.session_state.watchlist)

            st.rerun()

        del st.session_state.watchlist[i]

        save_watchlist(st.session_state.watchlist)

        st.rerun()

st.divider()

st.header("💼 Portföyüm")

rows = []

if "portfolio" not in st.session_state:
    st.session_state.portfolio = load_portfolio()

if len(st.session_state.portfolio) == 0:

    st.info("""
📭 Sepetinizde alınmış hisse bulunmuyor.

Portföye hisse eklediğinizde burada görüntülenecek.
""")

else:

    rows = []

    alerts = []

    kar_al_listesi = []
    stop_listesi = []
    kar_al_yaklasiyor_listesi = []

    watchlist_results = []

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
                period="1y",
                auto_adjust=False,
                progress=False
            )

            close_series = get_series(
                live,
                "Close"
            )

            if len(close_series) >= 1:

                son_fiyat = close_series.iloc[-1]

                if hasattr(son_fiyat, "iloc"):
                    son_fiyat = son_fiyat.iloc[0]

                current_price = round(
                    float(son_fiyat),
                    2
                )

                ai_score = 50

                volume = get_series(
                    live,
                    "Volume"
                )

                ema20 = EMAIndicator(
                    close_series,
                    20
                ).ema_indicator()

                ema50 = EMAIndicator(
                    close_series,
                    50
                ).ema_indicator()

                rsi = RSIIndicator(
                    close_series,
                    14
                ).rsi()

                last_rsi = float(
                    rsi.iloc[-1]
                )

                if ema20.iloc[-1] > ema50.iloc[-1]:
                    ai_score += 20

                if 50 <= last_rsi <= 70:
                    ai_score += 15

                elif last_rsi > 70:
                    ai_score += 5

                elif last_rsi < 40:
                    ai_score -= 10

                avg_volume = volume.tail(20).mean()

                if volume.iloc[-1] > avg_volume * 1.5:
                    ai_score += 15

                ai_score = max(
                    0,
                    min(ai_score, 100)
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

            # Alarm Sistemi

            if kar_zarar_yuzde >= 15:

                alarm = "🎯 KAR AL"

                # kar_al_listesi.append(
                #    f"{symbol} (%{kar_zarar_yuzde:.2f})"
                # )

            elif kar_zarar_yuzde <= -7:

                alarm = "🛑 STOP"

                # stop_listesi.append(
                #    f"{symbol} (%{kar_zarar_yuzde:.2f})"
                # )

            else:

                alarm = "🟢 TUT"


            # Satış Karar Motoru V1

            satis_puani = 50

            # AI Bonus

            if ai_score >= 90:
                satis_puani += 20

            elif ai_score >= 80:
                satis_puani += 10

            elif ai_score < 50:
                satis_puani -= 10

            ai_bonus = 0

            if kar_zarar_yuzde > 0:
                satis_puani += 10

            if kar_zarar_yuzde > 1:
                satis_puani += 5

            if kar_zarar_yuzde > 2:
                satis_puani += 5

            if kar_zarar_yuzde > 3:
                satis_puani += 10

            if kar_zarar_yuzde < -1:
                satis_puani -= 10

            if kar_zarar_yuzde < -2:
                satis_puani -= 20

            kalan_potansiyel = round(
                (
                    (current_price * 1.15 - current_price)
                    / current_price
                ) * 100,
                2
            )

            # if kalan_potansiyel >= 15:
            #    satis_puani += 15
            # 
            # elif kalan_potansiyel >= 10:
            #    satis_puani += 10
            # 
            # elif kalan_potansiyel >= 5:
            #    satis_puani += 5
          
            if satis_puani >= 80:

                satis_onerisi = "💰 KAR AL"

            elif satis_puani >= 60:

                satis_onerisi = "🟡 KAR AL YAKLAŞIYOR"

            elif satis_puani <= 30:

                satis_onerisi = "🔴 STOP"

            else:

                satis_onerisi = "🟢 TUT"

           
            if satis_onerisi == "💰 KAR AL":

                kar_al_listesi.append(
                    f"{symbol} | %{kar_zarar_yuzde:.2f}"
                )

            elif satis_onerisi == "🟡 KAR AL YAKLAŞIYOR":

                kar_al_yaklasiyor_listesi.append(
                    f"{symbol} | %{kar_zarar_yuzde:.2f}"
                )

            elif satis_onerisi == "🔴 STOP":

                stop_listesi.append(
                    f"{symbol} | %{kar_zarar_yuzde:.2f}"
                )


            rows.append(
                {
                    "Hisse": symbol,
                    "Lot": item["lot"],
                    "Alış": item["alis"],
                    "Güncel": current_price,

                    "🚨 Alarm": alarm,

                    "K/Z %":
                        f"🟢 %{kar_zarar_yuzde:.2f}"
                        if kar_zarar_yuzde > 0
                        else (
                            f"🔴 %{kar_zarar_yuzde:.2f}"
                            if kar_zarar_yuzde < 0
                            else "⚪ %0.00"
                        ),

                    "Kâr TL": kar_tl_text,

                    "Hedef Fiyat": round(
                        current_price * 1.15,
                        2
                    ),

                    "Kalan Potansiyel %": round(
                        (
                            (current_price * 1.15 - current_price)
                            / current_price
                        ) * 100,
                        2
                    ),

                    "🎯 Satış Önerisi": satis_onerisi,

                    "🧠 AI": ai_score,

                    "🧠 Satış Puanı": satis_puani,

                    "Toplam": round(
                        guncel_deger,
                        2
                    )
                }
            )

        except Exception as e:

            st.error(
                f"{symbol} HATA: {e}"
            )
        
    kar_tutar = round(
        toplam_guncel - toplam_maliyet,
        2
    )

    portfoy_getiri = round(
        (kar_tutar / toplam_maliyet) * 100,
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

    if kar_tutar >= 0:
        col3.metric(
            "🟢 Kâr",
            f"{kar_tutar:,.2f} TL",
            f"%{portfoy_getiri}"
        )
    else:
        col3.metric(
            "🔴 Zarar",
            f"{kar_tutar:,.2f} TL",
            f"%{portfoy_getiri}"
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

st.subheader("🚨 Satış Merkezi")

kar_al_listesi = []
kar_al_yaklasiyor_listesi = []
stop_listesi = []

col1, col2, col3 = st.columns(3)

with col1:

    st.warning("🎯 Kar Al Adayları")

    if len(kar_al_listesi) > 0:

        for hisse in kar_al_listesi:
            st.write(hisse)

    else:

        st.write("Şu an kar al seviyesine ulaşan hisse yok")

with col3:

    st.info("⚠️ Kar Al Yaklaşıyor")

    if len(kar_al_yaklasiyor_listesi) > 0:

        for hisse in kar_al_yaklasiyor_listesi:
            st.write(hisse)

    else:

        st.write("Yaklaşan satış adayı yok")

with col2:

    st.error("🛑 Stop Adayları")

    if len(stop_listesi) > 0:

        for hisse in stop_listesi:
            st.write(hisse)

    else:

        st.write("Şu an stop seviyesine ulaşan hisse yok")

if len(st.session_state.portfolio) > 0 and len(rows) > 0:

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

    st.rerun()

st.divider()

show_watchlist = st.sidebar.button(
"📊 Takip Listemi Göster"
)

show_glossary = st.sidebar.button(
    "ℹ️ Skor Sözlüğü"
)

show_backtest = st.sidebar.button(
    "📊 Geri Test Sonuçları"
)

if show_glossary:

    st.title("ℹ️ GainzAlgo Skor Sözlüğü")

    st.markdown("""
    ## 🎯 Rank Skor
    Tüm göstergelerin birleşiminden oluşan ana sıralama puanıdır.
    Yüksek olması hissenin genel görünümünün güçlü olduğunu gösterir.

    ## 🤖 AI Skor
    Yapay zekâ modelinin teknik görünümden ürettiği puandır.
    100'e yaklaştıkça olumlu görünüm artar.

    ## 📊 Finansal Skor
    Şirketin bilanço, kârlılık, büyüme ve borçluluk verilerinden hesaplanır.

    ## 🚀 Yarın Skor
    Hissenin kısa vadede yükselme ihtimalini gösteren momentum puanıdır.

    ## 💰 Potansiyel %
    Algoritmanın hesapladığı teorik yükseliş potansiyelidir.

    ### Genel Yorum

    - 80+ = Çok Güçlü
    - 70-80 = Güçlü
    - 60-70 = İzlenebilir
    - 50-60 = Nötr
    - 50 Altı = Zayıf
    """)

if show_backtest:

    st.title("📊 Geri Test Sonuçları")

    try:

        df_backtest = pd.read_csv(
            BACKTEST_FILE
        )

        st.metric(
            "Toplam Kayıt",
            len(df_backtest)
        )

        st.dataframe(
            df_backtest,
            use_container_width=True
        )

    except Exception as e:

        st.error(
            f"Geri test dosyası okunamadı: {e}"
        )

    st.stop()
 
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

    # -------------------------
    # Market Regime (AI)
    # -------------------------

    if bist_change >= 2:
        market_regime = "STRONG_BULL"

    elif bist_change >= 0.75:
        market_regime = "BULL"

    elif bist_change > -0.75:
        market_regime = "NEUTRAL"

    elif bist_change > -2:
        market_regime = "BEAR"

    else:
        market_regime = "STRONG_BEAR"

    st.success(
        f"📈 BIST100: %{bist_change} | {market_power}"
    )

except:
    pass

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
            
            open_price = get_series(wdf, "Open")

            volume = get_series(wdf, "Volume")

            if len(close) < 20:
                continue
            
            ema20 = EMAIndicator(close, 20).ema_indicator()
            ema50 = EMAIndicator(close, 50).ema_indicator()

            rsi = RSIIndicator(close, 14).rsi()

            if pd.isna(wdf["Close"].iloc[-1].squeeze()):
                last_price = float(wdf["Open"].iloc[-1].squeeze())
            else:
                last_price = float(close.iloc[-1])

            print(hisse, "LAST PRICE =", last_price)
            
            daily_change = (
                (close.iloc[-1] / close.iloc[-2]) - 1
            ) * 100

            last_rsi = float(rsi.iloc[-1])

            # Relative Strength (BIST Karşılaştırması)

            rs_score = daily_change - bist_change

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

            # Relative Strength Bonus

            if rs_score > 8:
                ai_score += 30

            elif rs_score > 5:
                ai_score += 20

            elif rs_score > 2:
                ai_score += 10

            elif rs_score < -2:
                ai_score -= 15

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

            # Hedefe Ulaşma Olasılığı

            olasilik = 40

            # AI Etkisi
            olasilik += (ai_score - 50) * 0.40

            # Para Etkisi
            olasilik += (big_money_score - 40) * 0.20

            # RS Etkisi
            olasilik += rs_score * 2

            olasilik = max(
                5,
                min(round(olasilik, 1), 95)
            )

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
              
            favori_skoru = round(
                (
                    ai_score * 0.5
                )
                +
                (
                    big_money_score * 0.3
                )
                +
                (
                    rs_score * 5
                ),
                1
            )

            watchlist_results.append(
    {
        "Hisse": hisse,
        "Fiyat": round(last_price, 2),
        "Günlük %": round(daily_change, 2),
        "RSI": round(last_rsi, 2),

        "RS": round(rs_score, 2),

        "AI_SAYI": ai_score,

        "PARA_SAYI": big_money_score,

        "OLASILIK": olasilik,

        "FAVORI_SKORU": favori_skoru,

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
                "RS",
                "AI_SAYI",
                "PARA_SAYI",
                "OLASILIK",
                "FAVORI_SKORU",
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

        st.subheader("🚀 Yarının Favorileri")

        favoriler = watch_df[
            (watch_df["AI_SAYI"] >= 80)
            &
            (watch_df["RS"] >= 2)
            &
            (watch_df["PARA_SAYI"] >= 60)
            
        ]

        favoriler = favoriler.sort_values(
            "FAVORI_SKORU",
            ascending=False
        )

        if len(favoriler) > 0:
        
            st.dataframe(
                favoriler[
                    [
                        "Hisse",
                        "AI_SAYI",
                        "PARA_SAYI",
                        "RS",
                        "OLASILIK",
                        "FAVORI_SKORU",
                        "AI Skor",
                        "Sinyal"
                    ]
                ],
                use_container_width=True
            )

        else:

            st.info(
                "Bugün güçlü favori bulunamadı."
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
                      
        if symbol == "EUPWR.IS":
            st.write("RAW DF SON 5")
            st.dataframe(df.tail())

            st.write("CLOSE SON 5")
            st.write(get_series(df, "Close").tail())
        
        if df.empty:
            continue

        close = get_series(df, "Close")

        high = get_series(df, "High")
        low = get_series(df, "Low")
        volume = get_series(df, "Volume")

        if len(close) < 200:
            continue

        ema20, ema50, ema200 = calculate_emas(close)

        rsi = calculate_rsi(close)

        macd = MACD(close)

        common_index = close.index.intersection(high.index)
        common_index = common_index.intersection(low.index)

        close = close.loc[common_index]
        high = high.loc[common_index]
        low = low.loc[common_index]

        atr = AverageTrueRange(
            high,
            low,
            close
        ).average_true_range()
        
        
        (
            score,
            big_money_score,
            early_warning,
            tomorrow_signal,
            future_score,
            dip_radar,
        ) = initialize_signals()
       
        score = calculate_trend_score(
            ema20,
            ema50,
            ema200,
            close,
        )

        rsi_now = rsi.iloc[-1]

        
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

        early_warning = calculate_early_warning(rsi)

        score += calculate_rsi_score(rsi_now)

        macd_diff = macd.macd_diff().iloc[-1]
        macd_prev = macd.macd_diff().iloc[-2]

        score += calculate_macd_score(
            macd_diff,
            macd_prev,
        )

        avg_volume = volume.tail(20).mean()

        volume_ratio = volume.tail(5).mean() / avg_volume
               
        
        # Büyük Para Skoru

        big_money_score = calculate_big_money_score(
            volume,
            ema20,
            ema50,
            rsi_now,
            close,
        )

        future_score = calculate_future_score(
            rsi_now,
            rsi,
            macd_diff,
            macd_prev,
            close,
            ema20,
            ema50,
            volume_ratio,
)

        (
            momentum20,
            bist_momentum20,
            relative_strength,
            rs_text,
        ) = calculate_relative_strength(
            close,
            bist_close,
        )

        if momentum20 > 10:
            future_score += 10

        elif momentum20 > 5:
            future_score += 5

        # Yarın AL Sinyali

        if (
            future_score >= 75 and
            volume_ratio > 1.3 and
            ema20.iloc[-1] > ema50.iloc[-1]
            and relative_strength > 0
        ):
            tomorrow_signal = "🚀 YARIN AL"

        elif future_score >= 55:
            tomorrow_signal = "🟢 YAKIN"

        elif future_score >= 35:
            tomorrow_signal = "👀 TAKİP"

        else:
            tomorrow_signal = "—"

        whale_signal = calculate_whale_signal(
            volume_ratio,
        )          
        
        money_flow = calculate_money_flow(
            volume,
            avg_volume,
        )

        if volume.iloc[-1] > avg_volume * 1.5:
            score += 15
        elif volume.iloc[-1] > avg_volume:
            score += 8        
        
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

        # Güncel fiyat seçimi

        today_open = float(df["Open"].iloc[-1])

        if pd.isna(df["Close"].iloc[-1]):
            last_close = today_open
        else:
            last_close = float(df["Close"].iloc[-1])

        last_atr = float(atr.dropna().iloc[-1])

        if last_close <= 0:
            continue

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

        financial_score = calculate_financial_score(symbol)

        print("FINANCIAL SCORE:", symbol, financial_score)

        rank_score = calculate_rank_score(
            score=score,
            future_score=future_score,
            financial_score=financial_score,
            relative_strength=relative_strength,
            big_money_score=big_money_score,
            risk_ratio=risk_ratio,
            whale_signal=whale_signal,
            money_flow=money_flow,
            potential=potential,
            dip_radar=dip_radar,
        )

        trend_power = calculate_trend_power(
            close=close,
            ema20=ema20,
            ema50=ema50,
            rsi_now=rsi_now,
            relative_strength=relative_strength,
        )

        # Hedefe Ulaşma Olasılığı

        success_probability = calculate_success_probability(
            score=score,
            future_score=future_score,
            financial_score=financial_score,
            big_money_score=big_money_score,
            relative_strength=relative_strength,
            trend_power=trend_power,
            risk_ratio=risk_ratio,
            potential=potential,
        )

        expected_return = calculate_expected_return(
            potential=potential,
            success_probability=success_probability,
        )

        risk_adjusted_score = calculate_risk_adjusted_score(
            future_score=future_score,
            big_money_score=big_money_score,
            relative_strength=relative_strength,
            risk_ratio=risk_ratio,
        )

        prefilter_pass = passes_ai_prefilter(
            financial_score=financial_score,
            trend_power=trend_power,
            relative_strength=relative_strength,
        )

        learning_bonus = get_learning_bonus(symbol)

        score += learning_bonus

        decision = calculate_decision(
            ai_score=score,
            big_money_score=big_money_score,
            probability=success_probability,
            signal="NÖTR",
            alerts=[],
            target_price=target_price,

            rank_score=score,
            trend_power=trend_power,
            success_probability=success_probability,
            expected_return=expected_return,
            risk_adjusted_score=risk_adjusted_score,
            opportunity="NORMAL",
            confidence="ORTA",
        )

        # =====================================================
        # Dashboard Veri Paketi
        # =====================================================

        analysis_data = {
            "symbol": symbol,
            "decision": decision,
            "score": score,
            "future_score": future_score,
            "financial_score": financial_score,
            "big_money_score": big_money_score,
            "trend_power": trend_power,
            "success_probability": success_probability,
            "expected_return": expected_return,
            "risk_adjusted_score": risk_adjusted_score,
            "target_price": target_price,
        }

        print(symbol, financial_score)

        # -------------------------
        # AI Context
        # -------------------------

        ai_context = {

            "symbol": symbol,

            "ai_score": round(score, 2),

            "financial_score": financial_score,

            "trend_power": trend_power,

            "learning_bonus": learning_bonus,

        }
        
        ai_core = evaluate_stock(ai_context)

        print("AI CORE:", ai_core)

        # -------------------------
        # AI Context Database
        # -------------------------

        if "ai_contexts" not in st.session_state:
            st.session_state["ai_contexts"] = {}

        st.session_state["ai_context"] = ai_context

        results.append({
            "Hisse": symbol,
            "Finansal Skor": financial_score,
            "Dip Radarı": dip_radar,
            "🐋 Büyük Para": whale_signal,
            "Erken Uyarı": early_warning,
            "Para Girişi": money_flow,
            "Karar": action,
            "AI Güven": ai_core.confidence,
            "AI PreFilter": "✅ PASS" if prefilter_pass else "❌ FAIL",
            "AI Puanı": ai_core.score,
            "AI Gerekçesi": " • ".join(ai_core.reasons),
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
            "Patlama Skoru": min(
                100,
                round(
                    (
                        future_score * 0.45 +
                        big_money_score * 0.35 +
                        relative_strength * 0.20
                    ),
                    2
                )
            ),

            "Hedefe Ulaşma Olasılığı (%)": success_probability,

            "Beklenen Kazanç (%)": expected_return,

            "Risk Ayarlı Skor": calculate_risk_adjusted_score(
                future_score=future_score,
                big_money_score=big_money_score,
                relative_strength=relative_strength,
                risk_ratio=risk_ratio,
            ),

            "Risk %": round(float(risk_ratio), 2),

        "Fırsat": (
            "🔥 KAÇIRMA" if rank_score >= 60 else
            "🚀 GÜÇLÜ" if rank_score >= 55 else
            "🟢 İYİ" if rank_score >= 45 else
            "👀 TAKİP"
        ),

        "Güven Notu": (
            "A+" if rank_score >= 110 else
            "A" if rank_score >= 95 else
            "B+" if rank_score >= 90 else
            "B" if rank_score >= 80 else
            "C"
        ),
            "Sıra Skoru": round(rank_score, 2),
            })
            
    except Exception as e:
        import traceback

        st.error(f"{symbol} hata: {e}")

        st.code(traceback.format_exc())

        

    progress.progress((i + 1) / len(BIST_LIST))

result_df = pd.DataFrame(results)

# -------------------------
# Global Analysis Data
# -------------------------

set_result_df(result_df)

(
    top10_df,
    tomorrow_df,
    near_buy_df,
    dip_df,
) = prepare_scanner_lists(result_df)

dashboard_data = prepare_dashboard_data(result_df)

st.session_state["top10_df"] = top10_df
st.session_state["tomorrow_df"] = tomorrow_df
st.session_state["near_buy_df"] = near_buy_df
st.session_state["dip_df"] = dip_df

dashboard_data = prepare_dashboard_data(result_df)

# =====================================================
# Dashboard
# =====================================================

if page == "🏠 Dashboard":

    show_dashboard(
        dashboard_data=dashboard_data,
        selected_symbol=selected_symbol,
    )

# =====================================================
# HİSSE ANALİZİ
# =====================================================

if page == "📈 Hisse Analizi":
    
    show_stock_analysis_page(
        selected_symbol,
        result_df,
    )

    
# =====================================================
# BACKTEST
# =====================================================

if page == PAGE_BACKTEST:

    
    show_backtest_page()


top5_df = (
    result_df
    .sort_values(
        by="Sıra Skoru",
        ascending=False
    )
    .head(5)
    .reset_index(drop=True)
)

if result_df.empty:
    st.error("Hiç hisse analiz edilemedi.")
    

result_df_favorite = result_df.sort_values(
    "Beklenen Kazanç (%)",
    ascending=False
)

favorite = result_df_favorite.iloc[0]

today = pd.Timestamp.today().strftime("%Y-%m-%d")

if not os.path.exists(FAVORITE_FILE):
    pd.DataFrame(columns=[
        "Tarih",
        "Hisse",
        "Fiyat",
        "Beklenen Kazanç (%)",
        "Hedefe Ulaşma Olasılığı (%)",
        "AI Skor",
        "Yarın Skor",
        "Decision Score",
        "Confidence",
        "Trend Power",
        "AI PreFilter",
        "Market Regime",
        "Ertesi Gün Fiyat",
        "Gerçek Getiri (%)",
        "Başarılı"
    ]).to_csv(
        FAVORITE_FILE,
        index=False
    )

history_df = pd.read_csv(FAVORITE_FILE)

history_df["Başarılı"] = history_df["Başarılı"].astype("object")

for idx, row in history_df.iterrows():

    if pd.isna(row["Ertesi Gün Fiyat"]):

        try:

            hisse = row["Hisse"]

            data = yf.download(
                hisse,
                period="5d",
                progress=False,
                auto_adjust=False
            )

            if len(data) >= 2:

                close_series = get_series(
                    data,
                    "Close"
                ).dropna()

                if len(close_series) > 0:

                    ertesi_fiyat = float(
                        close_series.iloc[-1]
                    )

                    history_df.loc[
                        idx,
                        "Ertesi Gün Fiyat"
                    ] = round(
                        ertesi_fiyat,
                        2
                    )

        except Exception as e:
            st.error(f"HATA: {e}")

history_df.to_csv(
    FAVORITE_FILE,
    index=False,
    encoding="utf-8-sig"
)

# Geçmiş favorileri güncelle

for idx, row in history_df.iterrows():

    if pd.isna(row["Gerçek Getiri (%)"]):

        try:

            data = yf.download(
                row["Hisse"],
                period="5d",
                progress=False
            )

            if len(data) >= 2:

                close_series = get_series(
                    data,
                    "Close"
                ).dropna()

                if len(close_series) > 0:

                    next_price = float(
                        close_series.iloc[-1]
                    )

                    entry_price = float(
                        row["Fiyat"]
                    )

                    real_return = round(
                        (
                            (next_price - entry_price)
                            / entry_price
                        ) * 100,
                        2
                    )

                    history_df.at[
                        idx,
                        "Ertesi Gün Fiyat"
                    ] = next_price

                    history_df.at[
                        idx,
                        "Gerçek Getiri (%)"
                    ] = real_return

                    history_df.at[
                        idx,
                        "Başarılı"
                    ] = (
                        1
                        if real_return > 0
                        else 0
                    )

        except Exception as e:
            import traceback
            st.text(traceback.format_exc())
            st.error(f"GETIRI HATASI: {e}")                          

                
history_df.to_csv(
    FAVORITE_FILE,
    index=False,
    encoding="utf-8-sig"
)

if (
    history_df.empty
    or today not in history_df["Tarih"].astype(str).values
):

    new_row = pd.DataFrame([{
        "Tarih": today,
        "Hisse": favorite["Hisse"],
        "Fiyat": favorite["Fiyat"],
        "Beklenen Kazanç (%)":
            favorite["Beklenen Kazanç (%)"],
        "Hedefe Ulaşma Olasılığı (%)":
            favorite["Hedefe Ulaşma Olasılığı (%)"],
        "AI Skor":
            favorite["AI Skor"],
        "Yarın Skor":
            favorite["Yarın Skor"],

        "Decision Score":
            favorite["AI Puanı"],

        "Confidence":
            favorite["AI Güven"],

        "Trend Power":
            favorite["Trend Gücü"],

        "AI PreFilter":
            favorite["AI PreFilter"],

        "Market Regime":
            market_regime,

        "Ertesi Gün Fiyat": None,
        "Gerçek Getiri (%)": None,
        "Başarılı": None
    }])

    history_df = pd.concat(
        [history_df, new_row],
        ignore_index=True
    )

    history_df.to_csv(
        FAVORITE_FILE,
        index=False,
        encoding="utf-8-sig"
    )

st.success(
    f"""
🏆 GÜNÜN FAVORUMUZ

📌 Hisse: {favorite['Hisse']}

🤖 AI Skoru: {favorite['AI Skor']}
📈 Sıra Skoru: {favorite['Sıra Skoru']}
🚀 Patlama Skoru: {favorite['Patlama Skoru']}
🛡️ Güven Notu: {favorite['Güven Notu']}
💰 Finansal Skor: {favorite['Finansal Skor']}
🚀 Yarın Skor: {favorite['Yarın Skor']}
📈 RS Gücü: {favorite['RS Güç']}
🐋 Büyük Para: {favorite['🐋 Büyük Para']}

💰 Beklenen Kazanç: %{favorite['Beklenen Kazanç (%)']}
🎯 Hedefe Ulaşma: %{favorite['Hedefe Ulaşma Olasılığı (%)']}
🎯 Potansiyel: %{favorite['Potansiyel %']}
⚠️ Risk: %{favorite['Risk %']}

📊 Karar: {favorite['Karar']}
🔥 Fırsat: {favorite['Fırsat']}
"""
)

st.subheader("📊 Favori Performans Takibi")

history_df = pd.read_csv(FAVORITE_FILE)

history_df = update_accuracy_history(history_df)

# ---------------------------------
# Güncellenmesi gereken kayıtlar
# ---------------------------------

pending_rows = history_df[
    history_df["Ertesi Gün Fiyat"].isna()
]

for index, row in pending_rows.iterrows():

    symbol = row["Hisse"]

    try:

        df = yf.download(
            symbol,
            period="5d",
            progress=False,
            auto_adjust=True,
        )

        if df.empty:
            continue

        print(symbol, "fiyat alındı")

        next_price = float(df["Close"].iloc[-1])

        history_df.loc[
            index,
            "Ertesi Gün Fiyat"
        ] = next_price

        print("Son Fiyat:", next_price)

    except Exception:
        continue

# ---------------------------------
# Bekleyen kayıt sayısı
# ---------------------------------

pending_count = len(pending_rows)

# ---------------------------------
# AI Accuracy
# ---------------------------------

completed_predictions = history_df[
    history_df["Başarılı"].notna()
]

total_predictions = len(completed_predictions)

successful_predictions = (
    completed_predictions["Başarılı"] == 1
).sum()

if total_predictions > 0:
    accuracy = round(
        successful_predictions /
        total_predictions * 100,
        2
    )
else:
    accuracy = 0

history_df = history_df.fillna("-")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📌 Toplam Favori",
        len(history_df)
    )

with col2:
    st.metric(
        "🎯 AI Accuracy",
        f"%{accuracy:.2f}"
    )

with col3:
    st.metric(
        "🏆 En Yüksek Beklenen Kazanç",
        f"%{history_df['Beklenen Kazanç (%)'].max():.2f}"
    )

with col4:
    st.metric(
        "⏳ Bekleyen Güncelleme",
        pending_count
    )

basarili_sayisi = (
    pd.to_numeric(
        history_df["Başarılı"],
        errors="coerce"
    )
    .fillna(0)
    .sum()
)

basarisiz_sayisi = (
    len(history_df)
    - basarili_sayisi
)

toplam_sonuc = (
    basarili_sayisi +
    basarisiz_sayisi
)

if toplam_sonuc > 0:

    basari_orani = round(
        basarili_sayisi
        / toplam_sonuc
        * 100,
        1
    )

else:

    basari_orani = 0

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "✅ Başarılı",
        basarili_sayisi
    )

with col2:
    st.metric(
        "❌ Başarısız",
        basarisiz_sayisi
    )

with col3:
    st.metric(
        "🎯 Başarı Oranı",
        f"%{basari_orani}"
    )
        
    ortalama_getiri = pd.to_numeric(
        history_df["Gerçek Getiri (%)"],
        errors="coerce"
    ).mean()

    if pd.isna(ortalama_getiri):

        ortalama_getiri = 0

    ortalama_getiri = round(
        ortalama_getiri,
        2
)

st.metric(
    "📈 Ort. Gerçek Getiri",
    f"%{ortalama_getiri}"
)

st.write("### Son Favoriler")

st.dataframe(
    history_df.tail(10),
    use_container_width=True
)

best_banka = get_best_stock_from_sector(
result_df,
BANKA_HISSELERI
)

best_enerji = get_best_stock_from_sector(
result_df,
ENERJI_HISSELERI
)

best_savunma = get_best_stock_from_sector(
result_df,
SAVUNMA_HISSELERI
)

best_sanayi = get_best_stock_from_sector(
result_df,
SANAYI_HISSELERI
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if best_banka is not None:
        st.metric(
            "🏦 En Güçlü Banka",
            best_banka["Hisse"],
            round(best_banka["Sıra Skoru"], 2)
        )

with col2:
    if best_enerji is not None:
        st.metric(
            "⚡ En Güçlü Enerji",
            best_enerji["Hisse"],
            round(best_enerji["Sıra Skoru"], 2)
        )

with col3:
    if best_savunma is not None:
        st.metric(
            "🛡️ En Güçlü Savunma",
            best_savunma["Hisse"],
            round(best_savunma["Sıra Skoru"], 2)
        )

with col4:
    if best_sanayi is not None:
        st.metric(
            "🏭 En Güçlü Sanayi",
            best_sanayi["Hisse"],
            round(best_sanayi["Sıra Skoru"], 2)
        )

st.divider()

if page == "🔍 AI Tarayıcı":
        
    if not result_df.empty:

        st.subheader("🔍 AI Tarama Sonuçları")
        st.divider()

        st.subheader("🏆 Bugünün En Güçlü 10 Hissesi")

    top10 = (
        result_df
        .sort_values(
            by="Sıra Skoru",
            ascending=False
        )
        .head(10)
        .reset_index(drop=True)
    )

    # BACKTEST KAYIT

    try:

        backtest_file = BACKTEST_FILE

        save_df = top10.copy()
        
        save_df.columns = save_df.columns.str.strip()

        today = datetime.now().strftime("%Y-%m-%d")

        save_df["Tarih"] = today

        save_df["Gerçek Fiyat"] = None
        save_df["Gerçek Getiri %"] = None
        save_df["Başarılı"] = None

        save_df = save_df.reindex(columns=[
                "Tarih",
                "Hisse",
                "Fiyat",
                "Sıra Skoru",
                "AI Skor",
                "Finansal Skor",
                "Yarın Skor",
                "Potansiyel %",
                "Gerçek Fiyat",
                "Gerçek Getiri %",
                "Başarılı"
        ])
        
        save_today = True

        if os.path.exists(backtest_file):

            old_df = pd.read_csv(backtest_file)

            if (
                "Tarih" in old_df.columns
                and today in old_df["Tarih"].astype(str).values
            ):
                save_today = False


        if save_today:

            if os.path.exists(backtest_file):

                save_df.to_csv(
                    backtest_file,
                    mode="a",
                    header=False,
                    index=False
                )

            else:

                save_df.to_csv(
                    backtest_file,
                    index=False
                )

    except Exception as e:

        st.warning(
            f"Backtest kayıt hatası: {e}"
        )

    st.dataframe(
        top10[
            [
                "Hisse",
                "AI Skor",
                "Karar",
                "Potansiyel %",
                "Risk %",
                "Güven Notu",
                "Sıra Skoru",
            ]
        ],
        use_container_width=True,
    )

    st.subheader("🔮 Yarının En Güçlü 5 Hissesi")

    st.divider()

    top5_show = prepare_tomorrow_table(top5_df)

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

    st.divider()

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

st.divider()
st.subheader("🔮 Yarın AL Verebilecek Hisseler")

future_df = result_df[
    result_df["Yarın AL"].isin(
        ["🚀 YARIN AL", "🟢 YAKIN"]
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
# =========================
# BACKTEST PERFORMANSI
# =========================

st.subheader("📊 Sistem Performansı")

try:

    bt = pd.read_csv(
        BACKTEST_FILE
    )

    bt["Gerçek Getiri %"] = pd.to_numeric(
        bt["Gerçek Getiri %"],
        errors="coerce"
    )

    bt = bt.dropna(
        subset=["Gerçek Getiri %"]
    )

    toplam = len(
        bt[
            bt["Gerçek Getiri %"].notna()
        ]
    )

    st.write(
        bt[
            ["Hisse", "Gerçek Getiri %"]
        ].tail(20)
    )

    kazanan = len(
        bt[
            bt["Gerçek Getiri %"] > 0
        ]
    )

    kaybeden = len(
        bt[
            bt["Gerçek Getiri %"] < 0
        ]
    )

    basari = round(
        (kazanan / toplam) * 100,
        1
    ) if toplam > 0 else 0

    ortalama_getiri = round(
        bt["Gerçek Getiri %"].mean(),
        2
    ) if toplam > 0 else 0

    en_iyi_getiri = round(
        bt["Gerçek Getiri %"].max(),
        2
    ) if toplam > 0 else 0

    en_kotu_getiri = round(
        bt["Gerçek Getiri %"].min(),
        2
    ) if toplam > 0 else 0

    kumulatif_getiri = round(
        bt["Gerçek Getiri %"].sum(),
        2
    ) if toplam > 0 else 0

    c1, c2, c3 = st.columns(3)
    c4, c5, c6 = st.columns(3)

    c1.metric(
        "Toplam Sinyal",
        toplam
    )

    c2.metric(
        "Kazanan",
        kazanan
    )

    c3.metric(
        "Başarı %",
        basari
    )

    c4.metric(
        "Ort. Getiri %",
        ortalama_getiri
    )

    c5.metric(
        "🏆 En İyi İşlem",
        f"%{en_iyi_getiri}"
    )

    c6.metric(
        "📉 En Kötü İşlem",
        f"%{en_kotu_getiri}"
    )

    st.metric(
        "💰 Kümülatif Getiri",
        f"%{kumulatif_getiri}"
    )

except Exception as e:

    st.warning(
        f"Backtest verisi okunamadı: {e}"
    )

st.divider()

st.subheader("📢 KAP Radar")

kap_df = get_kap_signals()

st.dataframe(
    kap_df,
    use_container_width=True
)

st.subheader("🚀 Bugünün En Güçlü 5 Adayı")

top5_df = result_df.sort_values(
    "Risk Ayarlı Skor",
    ascending=False
)

st.dataframe(
    top5_df[
        [
            "Hisse",
            "Beklenen Kazanç (%)",
            "Hedefe Ulaşma Olasılığı (%)",
            "Risk Ayarlı Skor",
            "Patlama Skoru",
            "AI Skor",
            "Yarın Skor",
            "Karar",
            "Potansiyel %",
            "Risk %"
        ]
    ].head(5),
    use_container_width=True
)

st.divider()

st.subheader("🔥 Top 10")

st.table(
    result_df.head(10)
)

st.stop()

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

ticker = yf.Ticker(selected_symbol)

try:
    st.write("ANLIK FİYAT")
    st.write(ticker.fast_info["lastPrice"])
except:
    pass

close = get_series(df, "Close")

st.write("ANALIZ CLOSE SON DEĞER")
st.write(close.tail())

st.write("DF SON TARİH")
st.write(df.index[-1])

st.write("TOPLAM SATIR")
st.write(len(df))

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

last_close = alis

st.write("ANALIZ FIYATI =", last_close)

st.write("LAST_CLOSE =", last_close)

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

left_col, right_col = st.columns([3, 1])

with left_col:

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with right_col:

    show_ai_panel(
        st.session_state["dashboard_data"]
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