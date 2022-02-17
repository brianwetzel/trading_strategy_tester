import streamlit as st
from PIL import Image
import requests
import pandas as pd
import numpy as np

#---------------------- FUNCTIONS ----------------------#

def fear_greed():
    # fetch data from api
    fear_greed_data = requests.get(f"https://api.alternative.me/fng/?limit=2000").json()
    # covert api dictionary to pandas dataframe
    fear_greed_df = pd.DataFrame.from_dict(fear_greed_data['data'])
    # drop column time_unitl_update
    fear_greed_df.drop(columns=['time_until_update', 'value_classification'], inplace = True)
    # convert epcoh timestamp column to normral date
    fear_greed_df['timestamp'] = pd.to_datetime(fear_greed_df['timestamp'],unit='s')
    # convert date column again to match the same type as our other data frame for easy concat
    fear_greed_df['timestamp'] = pd.to_datetime(fear_greed_df['timestamp']).dt.date
    # rename timestamp column to date
    fear_greed_df.rename(columns={'timestamp':'date', 'value':'F&G index', 'value_classification':'classification'}, inplace=True)
    # set date to index
    fear_greed_df.set_index("date", inplace = True)
    # sort datafram oldest to newest
    fear_greed_df.sort_index(ascending=True, inplace=True)
    # fear_greed_df.reset_index(inplace=True)

    return fear_greed_df


def kucoin_price(asset_ticker):
    
    # make asset ticker uppercase to be compatible with api
    asset_ticker = asset_ticker.upper()
    
    # Request data from api
    price_data = requests.get(f'https://api.kucoin.com/api/v1/market/candles?type=1day&symbol={asset_ticker}-USDT').json()

    # Create pandas df from json file    
    price_data_df = pd.DataFrame(price_data['data'])

    # Rename columns appropriately for later mplfinance processing
    price_data_df.rename(columns={0:'Dates',1:'Open',2:f'{asset_ticker} Price',3:'High',4:'Low',6:'Volume'}, inplace=True)

    # Drop excess data
    price_data_df.drop(columns=['Open', 'High', 'Low', 'Volume'],inplace=True)

    # Create dataframe with converted datetime for column 'Dates'
    price_data_df_dates = pd.to_datetime(price_data_df['Dates'], unit='s')

    # Ensure data in OHLCV columns are floats
    price_data_df = price_data_df[f'{asset_ticker} Price'].astype(float)

    # Concatenate 'Date' dataframe with 'OHLCV' dataframe
    price_data_df = pd.concat([price_data_df_dates,price_data_df], axis = 1, join = 'inner')

    #Set index to 'Dates'
    price_data_df.set_index('Dates',inplace=True)
    
    # reverse order of dataframe so dates go old to new
    price_data_df = price_data_df.iloc[::-1]

    return price_data_df
