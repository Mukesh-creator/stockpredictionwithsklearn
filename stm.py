import streamlit as st
import numpy as np
import pandas as pd
from pandas_datareader import data as pdr

import math
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from matplotlib import style
import datetime as dt
import yfinance as yf
import datetime

st.title("Stock Market Analysis and Prediction")
st.markdown("> Stock Market Analysis and Prediction is the project on technical analysis, visualization and prediction using data provided by Yahoo Finance.")
st.markdown("> It is web app which predicts the future value of company stock or other ﬁnancial instrument traded on an exchange.")

data_load_state = st.text('Loading data...')


start=dt.date(2021,6,1)
end=dt.date.today()
data=pdr.get_data_yahoo("GOOG", start, end)

data.fillna(method="ffill",inplace=True)

data_load_state.text('Loading data...done!')

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)
 
st.subheader('Detail description about Datasets:-')
descrb=data.describe()
st.write(descrb)

data["Year"]=data.index.year
data["Month"]=data.index.month
data["Weekday"]=data.index.day_name()

st.subheader('Graph of Close & Open:-')
st.line_chart(data[["Open","Close"]])

st.subheader('Graph of Adjacent Close:-')
st.line_chart(data['Adj Close'])

st.subheader('Graph of Volume:-')
st.line_chart(data['Volume'])

data['HL_PCT'] = (data['High'] - data['Low']) / data['Close'] * 100.0
data['PCT_change'] = (data['Close'] - data['Open']) / data['Open'] * 100.0
data = data[['Adj Close', 'HL_PCT', 'PCT_change', 'Volume']]

st.subheader('Newly format DataSet:-')
st.dataframe(data.tail(500))

forecast_col = 'Adj Close'
forecast_out = int(math.ceil(0.01 * len(data)))
data['label'] = data[forecast_col].shift(-forecast_out)

X = np.array(data.drop(['label'], 1))
X = preprocessing.scale(X)
X_lately = X[-forecast_out:]
X = X[:-forecast_out]
data.dropna(inplace=True)
y = np.array(data['label'])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
clf = LinearRegression(n_jobs=-1)
clf.fit(X_train, y_train)
confidence = clf.score(X_test, y_test)

st.subheader('Accuracy:')
st.write(confidence)

forecast_set = clf.predict(X_lately)
data['Forecast'] = np.nan

last_date = data.iloc[-1].name
last_unix = last_date.timestamp()
one_day = 86400
next_unix = last_unix + one_day

for i in forecast_set:
    next_date = datetime.datetime.fromtimestamp(next_unix)
    next_unix += 86400
    data.loc[next_date] = [np.nan for _ in range(len(data.columns)-1)]+[i]
    last_date = data.iloc[-1].name
    dti = pd.date_range(last_date, periods=forecast_out+1, freq='D')
    index = 1
for i in forecast_set:
    data.loc[dti[index]] = [np.nan for _ in range(len(data.columns)-1)] + [i]
    index +=1

st.subheader('Forecast value :-')
st.dataframe(data.tail(50))

st.subheader('Graph of Adj Close and Forecast :-')
st.line_chart(data[["Adj Close","Forecast"]])
