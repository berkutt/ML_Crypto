# ML_Crypto

Logic of the project:

Get the data from Binance through API (binance.client)
Add financial indicators (SMA, EMA, ROC etc.) to the dataset.
Check how each model perform on the data based on one ticker
Pick model and apply it to all others tickers.
Important note: I am ignoring model accuracy. Model selected based on revenue and nr of deals made.


Here is a summary of my algorith

market_trend - how did each ticker changed from '2022-03-20' until '2022-06-30', in %
my_trend - how much each ticker performed on my account, in %
transaction - how many times deal was closed
position - just comparing if i did better than market
ticker - ticker

![image](https://user-images.githubusercontent.com/35238615/199279070-568aea6f-69b9-4cfa-8ba1-1095c6b4b282.png)
