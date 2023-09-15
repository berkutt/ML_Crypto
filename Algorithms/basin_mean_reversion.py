# adaptation of https://github.com/PacktPublishing/Learn-Algorithmic-Trading/blob/master/Chapter5/basic_mean_reversion.py

import pandas as pd
import matplotlib.pyplot as plt
# from datetime import date
import numpy as np
import Snippets

data = pd.read_csv("file_with_data_ADA_0522_0723.csv") 
data = data.set_index('Close Time')
data = data.iloc[:1000, :]

def get_best_param(df):
    print("Searching for best params for basin_mean_reversion")
    fast_per, slow_per, price_move, balance, trans = [], [], [], [], [] 
    for NUM_PERIODS_FAST in range(10,100,10):
        print(NUM_PERIODS_FAST%100, "%", end='\r')
        for NUM_PERIODS_SLOW in range(20,210,10):
            if NUM_PERIODS_FAST>NUM_PERIODS_SLOW: continue
            for MIN_PRICE_MOVE_FROM_LAST_TRADE in np.arange(0.90,1.0,0.015):
                df['positions'] = bmr(NUM_PERIODS_FAST, NUM_PERIODS_SLOW, MIN_PRICE_MOVE_FROM_LAST_TRADE, df)

                trans.append(np.unique(df['positions'], return_counts=True)[1][0])
                balance.append(Snippets.calculate_balance(df))
                fast_per.append(NUM_PERIODS_FAST)
                slow_per.append(NUM_PERIODS_SLOW)
                price_move.append(MIN_PRICE_MOVE_FROM_LAST_TRADE)



    final_df = pd.DataFrame(data={"fast":fast_per,"slow":slow_per,"price_move":price_move, 'balance':balance, 'transactions':trans})

    final_df = final_df[final_df['balance'] != 100] # here will be 0 transactions
    # final_df.to_csv("output.csv", index=False)

    # get best result with combination of best balance and number of tranactions
    w = 0.8
    final_df['ratio'] = w * final_df['balance'] + (1-w)*final_df['transactions']
    winner_row = final_df.sort_values("ratio").index[-1]

    print("Best params: ", final_df.iloc[winner_row, :])
    best_fast, best_slow, best_price_move = final_df.iloc[winner_row, 0], final_df.iloc[winner_row, 1], final_df.iloc[winner_row, 2]
    return best_fast, best_slow, best_price_move
 

def bmr(NUM_PERIODS_FAST, NUM_PERIODS_SLOW, MIN_PRICE_MOVE_FROM_LAST_TRADE, df):
    # print(f"{NUM_PERIODS_FAST=}, {NUM_PERIODS_SLOW=}, {MIN_PRICE_MOVE_FROM_LAST_TRADE=}")
    # Variables/constants for EMA Calculation:
    # NUM_PERIODS_FAST = 40  # Static time period parameter for the fast EMA
    K_FAST = 2 / (NUM_PERIODS_FAST + 1)  # Static smoothing factor parameter for fast EMA
    ema_fast = 0
    ema_fast_values = []  # we will hold fast EMA values for visualization purposes

    # NUM_PERIODS_SLOW = 50  # Static time period parameter for slow EMA
    K_SLOW = 2 / (NUM_PERIODS_SLOW + 1)  # Static smoothing factor parameter for slow EMA
    ema_slow = 0
    ema_slow_values = []  # we will hold slow EMA values for visualization purposes

    apo_values = []  # track computed absolute price oscillator value signals

    # Variables for Trading Strategy trade, position & pnl management:
    orders = []  # Container for tracking buy/sell order, +1 for buy order, -1 for sell order, 0 for no-action
    positions = []  # Container for tracking positions, +ve for long positions, -ve for short positions, 0 for flat/no position
    pnls = []  # Container for tracking total_pnls, this is the sum of closed_pnl i.e. pnls already locked in and open_pnl i.e. pnls for open-position marked to market price

    last_buy_price = 0  # Price at which last buy trade was made, used to prevent over-trading at/around the same price
    last_sell_price = 0  # Price at which last sell trade was made, used to prevent over-trading at/around the same price
    position = 0  # Current position of the trading strategy
    buy_sum_price_qty = 0  # Summation of products of buy_trade_price and buy_trade_qty for every buy Trade made since last time being flat
    buy_sum_qty = 0  # Summation of buy_trade_qty for every buy Trade made since last time being flat
    sell_sum_price_qty = 0  # Summation of products of sell_trade_price and sell_trade_qty for every sell Trade made since last time being flat
    sell_sum_qty = 0  # Summation of sell_trade_qty for every sell Trade made since last time being flat
    open_pnl = 0  # Open/Unrealized PnL marked to market
    closed_pnl = 0  # Closed/Realized PnL so far

    # Constants that define strategy behavior/thresholds
    APO_VALUE_FOR_BUY_ENTRY = -0.001  # APO trading signal value below which to enter buy-orders/long-position
    APO_VALUE_FOR_SELL_ENTRY = 0.001  # APO trading signal value above which to enter sell-orders/short-position
    # MIN_PRICE_MOVE_FROM_LAST_TRADE = 0.995  # Minimum price change since last trade before considering trading again, this is to prevent over-trading at/around same prices
    NUM_SHARES_PER_TRADE = 1  # Number of shares to buy/sell on every trade
    MIN_PROFIT_TO_CLOSE = 0.001  # Minimum Open/Unrealized profit at which to close positions and lock profits

    close = df['Close']
    buy_status = True
    for close_price in close:
        # This section updates fast and slow EMA and computes APO trading signal
        if (ema_fast == 0):  # first observation
            ema_fast = close_price
            ema_slow = close_price
        else:
            ema_fast = (close_price - ema_fast) * K_FAST + ema_fast
            ema_slow = (close_price - ema_slow) * K_SLOW + ema_slow

        ema_fast_values.append(ema_fast)
        ema_slow_values.append(ema_slow)

        apo = ema_fast - ema_slow
        apo_values.append(apo)

        if last_sell_price>0:
            price_dif = min(close_price ,last_sell_price)/max(close_price ,last_sell_price)
        else:
            price_dif = 0
            
        if buy_status and apo > APO_VALUE_FOR_SELL_ENTRY and price_dif < MIN_PRICE_MOVE_FROM_LAST_TRADE:
            orders.append(-1)  # mark the sell trade
            last_sell_price = close_price
            position -= NUM_SHARES_PER_TRADE  # reduce position by the size of this trade
            sell_sum_price_qty += (close_price * NUM_SHARES_PER_TRADE)  # update vwap sell-price
            sell_sum_qty += NUM_SHARES_PER_TRADE
            buy_status = False
            continue

        elif not buy_status and apo < APO_VALUE_FOR_BUY_ENTRY and price_dif < MIN_PRICE_MOVE_FROM_LAST_TRADE:
            orders.append(+1)  # mark the buy trade
            position += NUM_SHARES_PER_TRADE  # increase position by the size of this trade
            buy_sum_price_qty += (close_price * NUM_SHARES_PER_TRADE)  # update the vwap buy-price
            buy_sum_qty += NUM_SHARES_PER_TRADE
            buy_status = True
            continue

        orders.append(0)
                    
        
    
    return  orders



