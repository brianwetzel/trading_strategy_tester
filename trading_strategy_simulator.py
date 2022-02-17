import streamlit as st
import pandas as pd
from functions import fear_greed, kucoin_price
from plotly.subplots import make_subplots
import plotly.graph_objects as go

#---------------------- API NOTES ----------------------#

# fear_greed(): does not take any arguments.  It returns a pandas dataframe for all time available.
# kucoin_price(ticker): takes the argument ticker symbol.  It returns a pandas dataframe of all time available.

#---------------------- PAGE CONFIG ----------------------#
# must be first
st.set_page_config(layout="wide", page_icon="📈")

#---------------------- TITLE & DESCRIPTION ----------------------#

st.markdown("## Trading Strategy Simulator (beta)")
st.write("""Use this app to explore various combinations of indicators and their parameters to find a profitable trading strategy.  Then compare your result to a simply buy & hold strategy.  We'll start you off with $100,000.  Try not to blow it! 💰 """)

#---------------------- DATA ----------------------#

strategy_list = ["- Pick a strategy -", "Fear & Greed Index", "RSI - Relative Strength Index", "Mac D", "Candle Stick Pattern"]
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
st.sidebar.write("________")

# st.sidebar.select_slider("test a different type", options=[start_date, end_date])


start_date = str(start_date) # convert dates to from datetime to strings
end_date = str(end_date) # convert dates to from datetime to strings
df = df.loc[(df['date'] >= start_date) & (df['date'] <= end_date)] # Our dataframe gets updated based on the start_date and end_date selected



# BUY STRATEGY
buy_strategy = st.sidebar.selectbox("Buy Strategy", strategy_list, index = 0)
if buy_strategy == "- Pick a strategy -":
    st.sidebar.write('')
elif buy_strategy == "Fear & Greed Index":
    c1, c2, c3 = st.sidebar.columns((1,1,1))
    with c1:
        st.slider("F&G Index: Threshold to Buy ", 0, 40, value=10)
    with c2:
        st.slider("Window of days below threshold", 1, 90, value=20)
    with c3:
        st.slider("% days of window below Threshold", 1, 100, value=75, step=5)
else:
    st.sidebar.write('This strategy is not setup yet')

# buy_overlay = st.sidebar.checkbox("View Buy Strategy on Chart", value=False)

st.sidebar.write("________")




# Sell Strategy
sell_strategy = st.sidebar.selectbox("Sell Strategy", strategy_list, index=0)
if sell_strategy == "- Pick a strategy -":
    st.sidebar.write('')
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

overlay_options = ["None", "Buy Strategy", "Sell Strategy"]
overlay = st.sidebar.selectbox("Chart Overlay", overlay_options, index=0)


# Testing
# st.info("This tool allows you to test your trading strategies against historical data")
# st.success('This is a success message!')
# st.error('This is an error')
# st.warning('This is a warning')

#---------------------- CALCULATIONS ----------------------#




#---------------------- BODY ----------------------#


# Results

st.markdown("_______")

h1, s1, c1, s2, c2, = st.columns((4,1,3,1,3))

with h1:
    st.markdown("### Your Strategy")
    st.write("this whole results section is a placeholder")

with c1:
    st.metric(label="Account Balance", value="$125,000", delta="$25,000") # Your Strategy
with c2:
    st.metric(label="Return (%)", value="25%", delta="Gain")  # Your Strategy


st.markdown("_______")

h1, s1, c1, s2, c2 = st.columns((4,1,3,1,3))

with h1:
    st.markdown("### Buy & Hold")
with c1:
    st.metric(label="Account Balance", value="$99,000", delta="-$1,000") # Your Strategy
with c2:
    st.metric(label="Return (%)", value="-1%", delta="-Loss")  # Your Strategy


st.markdown("_______")

# CHART
# st.markdown(f"### {asset} Chart")

# PLOTS TWO LINES
fig = make_subplots(specs=[[{"secondary_y": True}]])

# ADD ASSET LINE
fig.add_trace(go.Scatter(x= df['date'], y= df[f'{asset} Price'], name=f"{asset} Price", line=dict  (color='#188FD9', width=1)), secondary_y=False)
# change grid
fig.update_xaxes(showgrid=True, gridwidth=.1, gridcolor='#252526')
fig.update_yaxes(showgrid=True, gridwidth=.1, gridcolor='#252526')
fig.update_layout(yaxis1=dict(type='log'), yaxis1_title = f"{asset} Price (log)", showlegend=False)

# ADD F&G LINE
if buy_strategy == "Fear & Greed Index" or sell_strategy == "Fear & Greed Index":
    # F&G Line
    fig.add_trace(go.Scatter(x= df['date'], y= df['F&G index'], name='Fear & Greed Index', line=dict (color='#A8B2BF', width=1)), secondary_y=True)
    # F&G Bands (extreme fear, extreme greed)
    fig.add_hrect(y0=0, y1=25, line_width=0, fillcolor="#0072c4", opacity=0.1, secondary_y=True)
    fig.add_hrect(y0=75, y1=100, line_width=0, fillcolor="#49068f", opacity=0.1, secondary_y=True)
    fig.update_layout(yaxis2=dict(type="linear"), yaxis2_title = f"Fear & Greed Index", showlegend=False)

# Global parameters to the entire chart
fig.update_layout(autotypenumbers='convert types', template="plotly_dark", paper_bgcolor='#0e1117', plot_bgcolor='#181a1b', xaxis_title='Date')  # yaxis_title=f'{asset} Price (log)', height = 700
fig.update_layout(title=f'{asset} Price Chart • Buy & Sell Strategies Overlay')
fig.update_layout(xaxis=dict(rangeselector=dict(), rangeslider=dict(visible=True), type="date"))

# PLOT IT!!
st.plotly_chart(fig, use_container_width=True)

st.markdown("_______")

st.write("View the code on [GitHub](https://github.com/brianwetzel/trading_strategy_tester)")  # Text with a url embedded



# DATAFRAME

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
