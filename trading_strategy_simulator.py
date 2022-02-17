import streamlit as st
from PIL import Image
import requests
import pandas as pd
import numpy as np
from functions import fear_greed, kucoin_price
# import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import datetime, timedelta


#---------------------- API NOTES ----------------------#

# fear_greed(): does not take any arguments.  It returns a pandas dataframe for all time available.
# kucoin_price(ticker): takes the argument ticker symbol.  It returns a pandas dataframe of all time available.

#---------------------- PAGE CONFIG ----------------------#
# must be first
st.set_page_config(layout="wide", page_icon="📈")

#---------------------- TITLE & DESCRIPTION ----------------------#

st.title("Trading Strategy Simulator (beta)")
st.write('Use this app to explore various combinations of indicators and their parameters to find a profitable trading strategy.')
# st.write("You'll start with $100,000.")

#---------------------- DATA ----------------------#

strategy_list = ["-", "Fear & Greed Index", "RSI - Relative Strength Index (not setup)", "Mac D", "Candle Stick Pattern"]
fg_df = fear_greed()

#---------------------- SIDEBAR ----------------------#

# ASSET
asset_list = ["btc", "eth", "avax", "sol", "shib", "ftm", "near"]
asset = st.sidebar.selectbox("Asset", asset_list).upper()

# FETCH DATA, CREATE DF
df = pd.concat([kucoin_price(f"{asset}"),fear_greed()], axis = 1).dropna().reset_index()
df.rename(columns={'index':'date'}, inplace=True)
df['extreme fear'] = 25
df['extreme greed'] = 75

# TIMEFRAME
s1, s2 = st.sidebar.columns((1,1))
with s1:
    start_date = st.date_input("Start Date", value = df.at[0, 'date'], min_value = df.at[0, 'date'], max_value = df.at[(df.date.count()-1), 'date'])
with s2:
    end_date = st.date_input("End Date", value = df.at[(df.date.count()-1), 'date'], min_value = df.at[0, 'date'], max_value = df.at[(df.date.count()-1), 'date'])

# convert dates to from datetime to strings
start_date = str(start_date)
end_date = str(end_date)
# new df for charting that displays based on the start date and end date selected
df = df.loc[(df['date'] >= start_date) & (df['date'] <= end_date)]



# BUY STRATEGY
buy_strategy = st.sidebar.selectbox("Buy Strategy", strategy_list, index = 0)
if buy_strategy == "-":
    st.sidebar.write('Pick a strategy')
elif buy_strategy == "Fear & Greed Index":
    s1, s2, s3 = st.sidebar.columns((1,1,1))
    with s1:
        st.slider("F&G Index: Threshold to Buy ", 0, 40, value=10)
    with s2:
        st.slider("Window of days below threshold", 1, 90, value=20)
    with s3:
        st.slider("% days of window below Threshold", 1, 100, value=75, step=5)
else:
    st.sidebar.write('This strategy is not setup yet')
st.sidebar.write("________")




# Sell Strategy
sell_strategy = st.sidebar.selectbox("Sell Strategy", strategy_list, index=0)
if sell_strategy == "-":
    st.sidebar.write('Pick a strategy')
elif sell_strategy == "Fear & Greed Index":
    s1, s2, s3 = st.sidebar.columns((1,1,1))
    with s1:
        st.slider("F&G Index: Threshold to Sell ", 0, 100, value=10)
    with s2:
        st.slider("Window of days above threshold", 1, 90, value=20)
    with s3:
        st.slider("% days of window above Threshold", 1, 100, value=75, step=5)
else:
    st.sidebar.write('This strategy is not setup yet')
st.sidebar.write("________")

# Testing
# st.info("This tool allows you to test your trading strategies against historical data")
# st.success('This is a success message!')
# st.error('This is an error')
# st.warning('This is a warning')

#---------------------- BODY ----------------------#

# CHART

# PLOTS TWO LINES
fig = make_subplots(specs=[[{"secondary_y": True}]])

# ADD ASSET LINE
fig.add_trace(go.Scatter(x= df['date'], y= df[f'{asset} Price'], name=f"{asset} Price", line=dict  (color='#188FD9', width=1)), secondary_y=False)
# change grid
fig.update_xaxes(showgrid=True, gridwidth=.1, gridcolor='#252526')
fig.update_yaxes(showgrid=True, gridwidth=.1, gridcolor='#252526')
fig.update_layout(yaxis1=dict(type='log'), yaxis1_title = f"{asset} Price (log)", showlegend=False)
# fig.update_layout(yaxis2=dict, yaxis2_title = "Fear & Greed Index")

# ADD F&G LINE
if buy_strategy == "Fear & Greed Index":
    # F&G Line
    fig.add_trace(go.Scatter(x= df['date'], y= df['F&G index'], name='Fear & Greed Index', line=dict (color='#A8B2BF', width=1)), secondary_y=True)
    # F&G Bands (extreme fear, extreme greed)
    fig.add_hrect(y0=0, y1=25, line_width=0, fillcolor="#0072c4", opacity=0.1, secondary_y=True)
    fig.add_hrect(y0=75, y1=100, line_width=0, fillcolor="#49068f", opacity=0.1, secondary_y=True)

# Global parameters to the entire chart
fig.update_layout(autotypenumbers='convert types', template="plotly_dark", paper_bgcolor='#0e1117', plot_bgcolor='#181a1b', xaxis_title='Date',)  # yaxis_title=f'{asset} Price (log)', height = 700
# fig.update_layout(title='Fear & Greed Indext (Buy / Sell Indicator)')
fig.update_layout(xaxis=dict(rangeselector=dict(), rangeslider=dict(visible=True), type="date"))

# PLOT IT!!
st.plotly_chart(fig, use_container_width=True)


# Results
c1, c2, c3, c4, c5 = st.columns((2,1,2,1,2))
with c1:
    st.markdown("### Your Results")
with c2:
    st.markdown("### -")
with c3:
    st.markdown("### Buy & Hold")
with c4:
    st.markdown("### = ")
with c5:
    st.markdown("### Winner")


with c1:
    st.metric(label="Account Balance", value="$125,000", delta="$25,000")
    st.metric(label="Return (%)", value="25%", delta="Gain")
    st.metric(label="Sharpe Ratio", value=".6", delta="Not bad")
with c3:
    st.metric(label="Account Balance", value="$115,000", delta="$15,000")
    st.metric(label="Return (%)", value="15%", delta="Gain")
    st.metric(label="Sharpe Ratio", value="1.1", delta="Risky Business")
with c5:
    st.metric(label="Your Return vs Buy & Hold", value="$10,000", delta="$25,000")
    st.metric(label="You Won", value="10%", delta="Gain")
    st.metric(label="Sharpe Ratio", value="Risky", delta="Risky Business")





# FORM (TEST)
# with c1:
#     st.markdown("## Buy Sell Strategy")
#     with st.form("my_form"):
#         buy_strategy = st.selectbox("Buys Strategy", strategy_list)
#         slider_val_1 = st.slider("Form slider")
#         sell_strategy = st.selectbox("Sell Strategy", strategy_list)
#         slider_val_2 = st.slider("Form slider 2")
#         # Every form must have a submit button.
#         submitted = st.form_submit_button("Submit")
#         if submitted:
#             slider_input = st.write("slider", slider_val_1, "another slider", slider_val_2)
