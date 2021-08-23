import numpy as np
import pandas as pd
import pandas_datareader.data as pdr
import matplotlib.pyplot as plt
from scipy.stats import norm
import yfinance as yf
yf.pdr_override()

def import_stock_data(tickers, start):
    data = pd.DataFrame()
    if len([tickers]) ==1:
        data[tickers] = pdr.get_data_yahoo(tickers, data_source='yahoo', start=start)['Adj Close']
        data = pd.DataFrame(data)
    else:
        for t in tickers:
            data[t] = pdr.get_data_yahoo(t, data_source='yahoo', start=start)['Adj Close']
    return(data)

def log_returns(data):
    return (np.log(1+data.pct_change()))

# Generating Drifts for values
def drift_calc(data):
    lr = log_returns(data)
    u = lr.mean()
    var = lr.var()
    drift = u-(0.5*var)
    try:
        return drift.values
    except:
        return drift

def daily_returns(data, days, iterations):
    ft = drift_calc(data)
    try:
        stv = log_returns(data).std().values
    except:
        stv = log_returns(data).std()
    dr = np.exp(ft + stv * norm.ppf(np.random.rand(days, iterations)))
    return dr

def probs_find(predicted, higherthan, on = 'value'):
    if on == 'return':
        predicted0 = predicted.iloc[0,0]
        predicted = predicted.iloc[-1]
        predList = list(predicted)
        over = [(i*100)/predicted0 for i in predList if ((i-predicted0)*100)/predicted0 >= higherthan]
        less = [(i*100)/predicted0 for i in predList if ((i-predicted0)*100)/predicted0 < higherthan]
    elif on == 'value':
        predicted = predicted.iloc[-1]
        predList = list(predicted)
        over = [i for i in predList if i >= higherthan]
        less = [i for i in predList if i < higherthan]
    else:
        print("'on' must be either value or return")
    return (len(over)/(len(over)+len(less)))


def simulate_mc(params, graph):
    print("[INFO] Simulation Started.")
    # converting data in required data type
    # params is the dictionary which contains the data required for simulation
    ticker = str(params['ticker'])
    ticker = ticker.rstrip()
    ticker = ticker.upper()
    start = params['s_Date']
    days = int(params['days'])
    iterations = int(params['iterations'])
    # importing and saving data in variable data
    data = import_stock_data(ticker, start)
    # Generate daily returns
    returns = daily_returns(data, days, iterations)
    # Create empty matrix
    price_list = np.zeros_like(returns)
    # Put the last actual price in the first row of matrix.
    price_list[0] = data.iloc[-1]
    # Calculate the price of each day
    for t in range(1, days):
        price_list[t] = price_list[t - 1] * returns[t]

    #Current Market Price
    Cmp = str(data.tail(1).iloc[0])
    Cmp_list = Cmp.split()
    Cmp_price = Cmp_list[1]

    # Plotting Graphs
    plt.figure(figsize=(10, 6))
    plt.plot(price_list)
    plt.show()



    # Printing information about stock
    try:
        [print(nam) for nam in data.columns]
    except:
        print(data.name)
    print(f"Days: {days}")
    Cmp_price = float(Cmp_price)
    Cmp_price = round(Cmp_price,2)
    curr_unit = "$"
    if ticker[len(ticker)-3:] == '.NS':
        curr_unit = "₹"
    print(f"Current Market Price: {curr_unit} {Cmp_price}")
    print(f"Expected Value: {curr_unit} {round(pd.DataFrame(price_list).iloc[-1].mean(), 2)}")
    print(
        f"Return: {round(100 * (pd.DataFrame(price_list).iloc[-1].mean() - price_list[0, 1]) / pd.DataFrame(price_list).iloc[-1].mean(), 2)}%")
    print(f"Probability of Breakeven: {probs_find(pd.DataFrame(price_list), 0, on='return')}")

    # return pd.DataFrame(price_list)
    graph[0] = price_list


# print("starting")
# simulate_mc('TSLA','2020-01-01',250,1000)