import pandas as pd
import numpy as np
import Snippets
from ML_finance import Indicators
import warnings

warnings.filterwarnings('ignore')

def double_moving_average(financial_data, short_window, long_window):
  """
  This function calculates the double moving average of a financial data set.

  Args:
    financial_data: A pandas DataFrame containing the financial data.
    short_window: The number of periods for the short moving average.
    long_window: The number of periods for the long moving average.

  Returns:
    A pandas DataFrame containing the double moving average signals.
  """

  # Create a new DataFrame to store the signals.
  signals = pd.DataFrame(index=financial_data.index)
  signals['signal'] = 0.0

  # Calculate the short and long moving averages.
  signals['short_mavg'] = Indicators.SMA(np.array(financial_data['Close']), short_window)
  signals['long_mavg'] = Indicators.SMA(financial_data['Close'], long_window)

  # Create the trading signals.
  # If the short moving average is greater than the long moving average,
  # then a buy signal is generated.
  # Otherwise, a sell signal is generated.
  if short_window >= long_window:
    signals['signal'][long_window:] = \
        np.where(signals['short_mavg'][long_window:]
                     > signals['long_mavg'][long_window:], 1.0, 0.0)
  else:
    signals['signal'][short_window:] = \
        np.where(signals['short_mavg'][short_window:]
                     > signals['long_mavg'][short_window:], 1.0, 0.0)

  # Calculate the positions.
  # The positions column indicates whether we should buy (1) or sell(-1) or do nothing(0)
  signals = signals['signal'].diff()

  # # Add the closing price and close time columns.
  # signals['Close'] = financial_data['Close']
  # signals['Close Time'] = financial_data['Close Time']

  return signals

def check_all_variants(data_signal):
  
  """
  This function checks all possible combinations of short and long moving average windows
  and returns the ones that resulted in the highest balance.

  Args:
    data_signal: A pandas DataFrame containing the financial data and the trading signals.

  Returns:
    short_window, long_window: integers
  """
  print("Searching for best params for double_average")
  # Initialize the balance array.
  balance_ar = []

  # Initialize the short window array.
  sw_ar = []

  # Initialize the long window array.
  lw_ar = []

  # Initialize the long window array.
  trades_count = []

  # Iterate over all possible combinations of short and long moving average windows.
  for sw in range(5, 100, 3):
    print(sw%100, "%", end='\r')
    for lw in range(5, 100, 3):
      # Skip if the short window is equal to the long window.
      if sw == lw:
        continue

      # Skip if the data is not long enough.
      if len(data_signal) < sw or len(data_signal) < lw:
        continue
      # Calculate the double moving average signals.
      signals = double_moving_average(data_signal, sw, lw)

      # Calculate the balance.
      data_signal["positions"] = signals
      balance = Snippets.calculate_balance(data_signal)

      # If the balance is positive, then add it to the balance array.
      if balance - 100 > 0:
        balance_ar.append(balance - 100)
        sw_ar.append(sw)
        lw_ar.append(lw)
        trades_count.append(np.unique(data_signal["positions"], return_counts=True)[1][0])
  # Create a dictionary to store the results.
  data = {'balance': balance_ar, 'short': sw_ar, 'long': lw_ar, 'transactions':trades_count}

  # Create a DataFrame from the dictionary.
  df = pd.DataFrame(data)

  # get best result with combination of best balance and number of tranactions
  w = 0.8
  df['ratio'] = w * df['balance'] + (1-w)*df['transactions']
  winner_row = df.sort_values("ratio").index[-1]
  print('Best combo \n',  df.iloc[winner_row,:])
  short_window, long_window = df.iloc[winner_row,1], df.iloc[winner_row, 2]


  # Return the DataFrame.
  return short_window, long_window


def get_lw_sw(start_point, end_point, ada, bnb):
    ada = ada.iloc[start_point:end_point, :]
    ada_var = check_all_variants(ada)

    ada_var['Key'] = ada_var['short'].astype(str) + ada_var['long'].astype(str)

    bnb = bnb.iloc[start_point:end_point, :]
    bnb_var = check_all_variants(bnb)

    bnb_var['Key'] = bnb_var['short'].astype(str) + bnb_var['long'].astype(str)

    data = pd.merge(ada_var, bnb_var, on='Key')
    data["Sum_Bal"] = data['Balance_x'] + data['Balance_y']  # + data['Balance']
    if len(data) > 0:
        sw = data.sort_values("Sum_Bal").iloc[-1, 1]
        lw = data.sort_values("Sum_Bal").iloc[-1, 2]
        return sw, lw
    return 0, 0

def get_results(sw, lw, start_poimt, end_point, ada, bnb):
    ada = ada.iloc[start_poimt:end_point, :]

    data_signal = double_moving_average(ada, sw, lw)

    startdate_arr.append(ada['Close Time'].iloc[0])

    close_arr.append(ada['Close'].iloc[0])
    balance_arr.append(100 - Snippets.calculate_balance(data_signal))
    sw_arr.append(sw)
    lw_arr.append(lw)
#    past_arr.append(past_interval/96)
    ticker_arr.append('SOL')

    bnb = bnb.iloc[start_poimt:end_point, :]

    data_signal = double_moving_average(bnb, sw, lw)

    startdate_arr.append(bnb['Close Time'].iloc[0])
    close_arr.append(bnb['Close'].iloc[0])
    balance_arr.append(100 - Snippets.calculate_balance(data_signal))
    sw_arr.append(sw)
    lw_arr.append(lw)
    #past_arr.append(past_interval/96)
    ticker_arr.append('ETC')

# ada = pd.read_csv("C:\\Users\\Vlad\\Desktop\\Finance\\SOL 15 min.csv")
# bnb = pd.read_csv("C:\\Users\\Vlad\\Desktop\\Finance\\ETC 15 min.csv")

#eth = pd.read_csv("C:\\Users\\Vlad\\Desktop\\Finance\\ETH 15 min.csv")
#eth = eth.iloc[:len(ada), :]
close_arr = []
startdate_arr = []
enddate_arr = []
balance_arr = []
sw_arr = []
lw_arr = []
ticker_arr = []
past_arr = []

# train_data = bnb.iloc[:round(len(bnb)*0.8), :]
# test_data = bnb.iloc[round(len(bnb)*0.8):, :]
#
# ada_var = check_all_variants(train_data)
#

def check_many_steps():
    future_interval = 5 * 96
    past_interval = 96
    #for past_interval in range(0, 1152, 96):
    #print(past_interval / 1152 * 100)
    for start_range in range(0, len(ada)-300, future_interval):
        print(start_range/ len(ada)*100)
        try:
            sw, lw = get_lw_sw(start_range, start_range + past_interval, ada, bnb)
            if sw != 0:
                get_results(sw, lw, past_interval + start_range, past_interval + start_range + future_interval, ada, bnb)
        except:
            continue

    final_data = {'StartDate': startdate_arr,  'Balance': balance_arr,
                  'SW': sw_arr, 'LW': lw_arr, 'Ticker': ticker_arr, 'Close': close_arr}

    final_df = pd.DataFrame(final_data)
    print(final_df.groupby(['Ticker']).sum())

    final_df.to_csv("C:\\Users\\Vlad\\Desktop\\Finance\\ADAd" + str(future_interval / 96) + " days.csv")


# if __name__ == '__main__':
#    check_all_variants() 

