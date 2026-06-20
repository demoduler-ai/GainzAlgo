import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

st.set_page_config(
    page_title="GainzAlgo V5 Professional",
    layout="wide"
)

BIST_LIST = [
    "THYAO.IS",
    "ASELS.IS",
    "KCHOL.IS",
    "TUPRS.IS",
    "BIMAS.IS",
    "EREGL.IS",
    "AKBNK.IS",
    "GARAN.IS",
    "YKBNK.IS",
    "SAHOL.IS",
    "ISCTR.IS",
    "KOZAL.IS",
    "PETKM.IS",
    "SISE.IS",
    "PGSUS.IS",
    "TCELL.IS",
    "VAKBN.IS",
    "HALKB.IS",
    "ENKAI.IS",
    "ASTOR.IS"
]

st.sidebar.title("GainzAlgo V5")
selected_symbol = st.sidebar.selectbox(
    "Hisse Seç",
    BIST_LIST
)

st.title("📈 GainzAlgo V5 Professional")

results = []

progress = st.progress(0)

for i, symbol in enumerate(BIST_LIST):

    try:

        df = yf.download(
            symbol,
            period="1y",
            auto_adjust=True,
            progress=False
        )

        if len(df) < 200:
            continue

        close = df["Close"].iloc[:, 0]
        high = df["High"].iloc[:, 0]
        low = df["Low"].iloc[:, 0]
        volume = df["Volume"].iloc[:, 0]

        ema20 = EMAIndicator(close, 20).ema_indicator()
        ema50 = EMAIndicator(close, 50).ema_indicator()
        ema200 = EMAIndicator(close, 200).ema_indicator()

        rsi = RSIIndicator(close, 14).rsi()

        macd = MACD(close)

        atr = AverageTrueRange(
            high,
            low,
            close
        ).average_true_range()

        score = 0

        if ema20.iloc[-1] > ema50.iloc[-1]:
            score += 15

        if ema50.iloc[-1] > ema200.iloc[-1]:
            score += 10

        if close.iloc[-1] > ema200.iloc[-1]:
            score += 10

        rsi_now = rsi.iloc[-1]

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

        if volume.iloc[-1] > avg_volume * 1.5:
            score += 15
        elif volume.iloc[-1] > avg_volume:
            score += 8

        momentum20 = (
            (close.iloc[-1] / close.iloc[-20]) - 1
        ) * 100

        if momentum20 > 15:
            score += 10
        elif momentum20 > 7:
            score += 5

        risk_ratio = (
            atr.iloc[-1] /
            close.iloc[-1]
        ) * 100

        if risk_ratio < 3:
            score += 10
        elif risk_ratio < 5:
            score += 5

        target_price = close.iloc[-1] * (
            1 + momentum20 / 100 * 0.5
        )

        potential = (
            (target_price / close.iloc[-1]) - 1
        ) * 100

        if score >= 90:
            signal = "🚀 ELMAS"
        elif score >= 80:
            signal = "🟢 GÜÇLÜ AL"
        elif score >= 65:
            signal = "🟢 AL"
        elif score >= 50:
            signal = "🟡 NÖTR"
        elif score >= 35:
            signal = "🟠 ZAYIF"
        else:
            signal = "🔴 SAT"

        results.append({
            "Hisse": symbol,
            "AI Skor": round(score, 2),
            "Sinyal": signal,
            "RSI": round(rsi_now, 2),
            "Fiyat": round(float(close.iloc[-1]), 2),
            "Hedef": round(float(target_price), 2),
            "Potansiyel %": round(float(potential), 2),
            "Risk %": round(float(risk_ratio), 2)
        })

    except:
        pass

    progress.progress((i + 1) / len(BIST_LIST))

result_df = pd.DataFrame(results)

if len(result_df):

    result_df = result_df.sort_values(
        "AI Skor",
        ascending=False
    )

    st.subheader("🏆 Günün En Güçlü Hisseleri")

    st.dataframe(
        result_df,
        use_container_width=True
    )

    st.subheader("🔥 Top 10")

    st.table(
        result_df.head(10)
    )

st.divider()

st.subheader(f"📊 {selected_symbol} Detay Analizi")

df = yf.download(
    selected_symbol,
    period="1y",
    auto_adjust=True,
    progress=False
)

close = df["Close"].iloc[:, 0]
high = df["High"].iloc[:, 0]
low = df["Low"].iloc[:, 0]

ema20 = EMAIndicator(close, 20).ema_indicator()
ema50 = EMAIndicator(close, 50).ema_indicator()
ema200 = EMAIndicator(close, 200).ema_indicator()

rsi = RSIIndicator(close, 14).rsi()

atr = AverageTrueRange(
    high,
    low,
    close
).average_true_range()

risk_ratio = (
    atr.iloc[-1] /
    close.iloc[-1]
) * 100

momentum20 = (
    (close.iloc[-1] / close.iloc[-20]) - 1
) * 100

target_price = close.iloc[-1] * (
    1 + momentum20 / 100 * 0.5
)

potential = (
    (target_price / close.iloc[-1]) - 1
) * 100

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Fiyat",
    round(float(close.iloc[-1]), 2)
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

st.success(
    f"Risk Seviyesi: %{risk_ratio:.2f}"
)