import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st
from datetime import datetime, timedelta

# ---------------------------
# Streamlit App
# ---------------------------
st.set_page_config(layout="wide")
st.title("📈 LRS Signal for Next Trading Day")
st.write(
    "This app determines whether to hold a leveraged position for the next trading day based on the Leverage Rotation Strategy."
)

# Sidebar for user inputs
st.sidebar.header("Strategy Parameters")
ma_period = st.sidebar.selectbox("Select Moving Average Period:", [10, 20, 50, 100, 200], index=4)

# --- Data Fetching ---
@st.cache_data
def load_data(period_years=5):
    """Fetches the last N years of SPY data."""
    end_date = datetime.today()
    start_date = end_date - timedelta(days=period_years * 365)
    spy = yf.Ticker("SPY")
    data = spy.history(start=start_date, end=end_date)
    return data[['Close']]

data = load_data(5)

# --- Signal Calculation ---
if not data.empty and len(data) >= ma_period:
    # Calculate the simple moving average
    data['SMA'] = data['Close'].rolling(window=ma_period).mean()

    # Get the latest data points
    latest_close = data['Close'].iloc[-1]
    latest_sma = data['SMA'].iloc[-1]
    latest_date = data.index[-1].strftime('%Y-%m-%d')

    # Determine the signal
    if latest_close > latest_sma:
        signal = "LEVERAGE ✅"
        signal_color = "green"
        explanation = f"The closing price is **above** the {ma_period}-day SMA, suggesting an uptrend. The strategy indicates holding a leveraged position."
    else:
        signal = "CASH / DELEVERAGE 現金"
        signal_color = "red"
        explanation = f"The closing price is **below** the {ma_period}-day SMA, suggesting a downtrend or higher volatility. The strategy indicates moving to a risk-off position (cash)."

    # --- Display the Signal ---
    st.header(f"Signal for the Next Trading Day (based on {latest_date} close)")

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label=f"Last SPY Close ({latest_date})", value=f"${latest_close:,.2f}")
    with col2:
        st.metric(label=f"{ma_period}-Day SMA", value=f"${latest_sma:,.2f}")

    st.markdown("---")

    # Display the final, clear signal
    st.markdown(f"""
    <div style="
        border: 2px solid {signal_color};
        border-radius: 10px;
        padding: 25px;
        text-align: center;
        background-color: {'#e8f5e9' if signal_color == 'green' else '#ffebee'};">
        <h2 style="color: {signal_color}; margin:0;">{signal}</h2>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<div style='padding-top: 15px;'>{explanation}</div>", unsafe_allow_html=True)


    # --- Chart Visualization ---
    st.subheader("Price vs. Moving Average Chart")
    st.line_chart(data[['Close', 'SMA']])

    st.info("Disclaimer: This is not financial advice. This tool is for educational purposes only, based on the rules of a specific trading strategy. Past performance is not indicative of future results.")

else:
    st.error(f"Could not fetch sufficient data to calculate a {ma_period}-day moving average. Please ensure you have an internet connection and the 'yfinance' library is working correctly.")
