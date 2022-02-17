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


#---------------------- PAGE LAYOUT ----------------------#
# must be first
st.set_page_config(layout="wide", page_icon="📈")

#---------------------- API INFO ----------------------#

# fear_greed(): does not take any arguments, returns a pandas dataframe of all time
# kucoin_price(ticker): takes the argument ticker symbol, returns a pandas dataframe of all time

#---------------------- DATA ----------------------#
strategy_list = ["Fear & Greed Index", "RSI - Relative Strength Index", "Mac D", "Candle Stick Pattern"]
fg_df = fear_greed()



# with st.expander("See explanation"):
#     st.write("""
#         The chart above shows some numbers I picked for you.
#         I rolled actual dice for these, so they're *guaranteed* to
#         be random.""")


#---------------------- SIDEBAR ----------------------#

# Sidebar Title
# st.sidebar.markdown('## Select an Asset, Timeframe, and Strategy below')

# Asset
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
st.sidebar.selectbox("Buy Strategy", strategy_list)
s1, s2 = st.sidebar.columns((1,1))
with s1:
    st.slider("Window in Days in Extreme Fear", 1, 30, value=10)
with s2:
    st.slider("% of Days in Extreme Fear", 1, 100, value=75, step=5)



# Sell Strategy
st.sidebar.selectbox("Sell Strategy", strategy_list)
s1, s2 = st.sidebar.columns((1,1))
with s1:
    st.slider("Window in Days in Extreme Greed", 1, 30, value=10)
with s2:
    st.slider("% of Days in Extreme Greed", 1, 100, value=75, step=5)



#---------------------- TITLE ----------------------#

left, center, right = st.columns((1, 3, 1))
center.title("Trading Strategy Simulator (beta)")

# Testing
# st.info("This tool allows you to test your trading strategies against historical data")
# st.success('This is a success message!')
# st.error('This is an error')
# st.warning('This is a warning')

#---------------------- BODY ----------------------#

# Columns Layout for Data
c1, c2, c3 = st.columns((3  , 1, 20))

# Results
with c1:
    st.markdown("## Results")
    st.metric(label="Buy Signal", value="35%", delta="1.2 °F")
    st.metric(label="Sell Signal", value="15%", delta="1.2 °F")
    st.metric(label="Your Return", value="25%", delta="1.2 °F")


# Fear And Greed Chart
with c3:

    # PLOTS TWO LINES
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # ADD ASSET LINE
    fig.add_trace(go.Scatter(x= df['date'], y= df[f'{asset} Price'], name=f"{asset} Price", line=dict  (color='#188FD9', width=1)), secondary_y=True)
    # ADD F&G LINE
    fig.add_trace(go.Scatter(x= df['date'], y= df['F&G index'], name='Fear & Greed Index', line=dict (color='#A8B2BF', width=1)), secondary_y=False)
    
    # ADD COLOR BAND
    # extreme fear range
    fig.add_hrect(y0=0, y1=25, line_width=0, fillcolor="#AA554E", opacity=0.1)
    # extreme greed range
    fig.add_hrect(y0=75, y1=100, line_width=0, fillcolor="#1FC0A9", opacity=0.1)
    # change grid
    fig.update_xaxes(showgrid=False, gridwidth=.1, gridcolor='#A8B2BF')
    fig.update_yaxes(showgrid=False, gridwidth=.1, gridcolor='#A8B2BF')
    fig.update_layout(yaxis2=dict(type='log'), showlegend=False)
    # Global parameters to the entire chart
    fig.update_layout(autotypenumbers='convert types', template="plotly_dark", paper_bgcolor='#0e1117', plot_bgcolor='#0e1117', title='Fear & Greed Indext (Buy / Sell Indicator)',xaxis_title='Date',yaxis_title='Fear & Greed Index', height = 700)
    
    fig.update_layout(xaxis=dict(rangeselector=dict(), rangeslider=dict(visible=True), type="date"))

    # PLOT IT!!
    st.plotly_chart(fig, use_container_width=True)


    # with c1:
#    st.markdown("## Buy Sell Strategy")
#    with st.form("my_form"):
#        buy_strategy = st.selectbox("Buys Strategy", strategy_list)
#        slider_val_1 = st.slider("Form slider")
#        sell_strategy = st.selectbox("Sell Strategy", strategy_list)
#        slider_val_2 = st.slider("Form slider 2")
#        # Every form must have a submit button.
#        submitted = st.form_submit_button("Submit")
#        if submitted:
#            slider_input = st.write("slider", slider_val_1, "another slider", slider_val_2)
