
''' https://bybit-exchange.github.io/docs/linear/?python--pybit#t-accountdata ''' # DOCUMENTATION
''' https://github.com/bybit-exchange ''' # GITHUB EXAMPLES
''' https://api-testnetbybit.com ''' # TESTNET
''' https://api.bybit.com ''' # MAINNET


''' BOT IS SET FOR ETHEREUM (ETH) USING US DOLLAR THETER (USDT) AS A COLLATERAL ON BYBIT MAINNET EXCHANGE ONLY '''

''' L I B R A R I E S '''

import requests 
import numpy as np
import pandas as pd
import pandas_ta as ta
import copy

# from pybit.usdt_perpetual import HTTP # // Use this package if you installing pybit after 2022/05
import bybit
from pybit import HTTP

import time
from datetime import datetime



''' K E Y S '''

KEY = ""
SECRET = ""


''' M A I N   S E T T I N G S '''

symbol='ETHUSDT'
t_frame = 5
client = bybit.bybit(test=False, api_key=KEY, api_secret=SECRET) # getting data / Set to False if Mainnet
session = HTTP("https://api.bybit.com") # Mainnet
maxposition =  0.2 # volume bet
stop_percent = 0.004 # 0.01=1% stop loss
eth_proffit_array = [[0.50,1],[0.90, 1],[1.50, 2],[2, 2],[3, 2],[3.5, 2],[4, 2],[6.5, 2],[9, 0]]
proffit_array = copy.copy(eth_proffit_array)


''' GET HISTORICAL CANDLES '''

def get_futures_klines(symbol, limit=200):
    # In order to get the last historical candles from ByBit, here's the time function
    # that takes the today's time and it goes back as mach as the limit (200 candles).
    # So, 200 cnadles and each candle 5 min, will be 1000 minutes back (200 * 5)*60
    # You'll get the last 200 candles up to now.
    # --- timestamp ------------------------------------
    today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    dt = datetime.strptime(today, '%Y-%m-%d %H:%M:%S')
    in_secods_now = int(dt.timestamp())
    # --- timestamp ------------------------------------
    session = HTTP("https://api.bybit.com", api_key=KEY, api_secret=SECRET)
    historical = session.query_kline(
        symbol = symbol,
        interval = t_frame,
        limit = limit,
        from_time = (in_secods_now - (limit * t_frame)*60))

    x = historical['result']
    df = pd.DataFrame(x)
    df = df.drop(['id','symbol','period','interval','start_at','turnover'],axis=1) # cut off the useless data
    
    df = df[['open_time','open','high','low','close','volume']].astype(float)
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)

    return(df)


''' OPEN A POSITION '''

def open_position(symbol, s_l, quantity_l):
    session = HTTP("https://api.bybit.com/", api_key=KEY, api_secret=SECRET)
    print(f'Open:: {symbol} with Qty:: {str(quantity_l)}')
    sprice = get_symbol_price(symbol)

    if (s_l == 'long'):
        close_price = str(round(sprice*(1-0.01),2))
        params = session.place_active_order(
            symbol = symbol,
            side = "Buy",
            order_type = "Market",
            qty = quantity_l,
            price = close_price,
            time_in_force = "GoodTillCancel",
            reduce_only = False,
            close_on_trigger = False)

        response = (params)
        return response  
       
    if (s_l == 'short'):
        close_price = str(round(sprice*(1-0.01),2))
        params = session.place_active_order(
            symbol = symbol,
            side = "Sell",
            order_type = "Market",
            qty = quantity_l,
            price = close_price,
            time_in_force = "GoodTillCancel",
            reduce_only = False,
            close_on_trigger = False)

        response = (params)
        return response  


''' CLOSE A POSITION '''

def close_position(symbol,s_l,quantity_l):
    session = HTTP("https://api.bybit.com/", api_key=KEY, api_secret=SECRET)
    print(f'Close:: {symbol} with Qty:: {str(quantity_l)}')
    sprice = get_symbol_price(symbol)
    close_price = str(round(sprice*(1+0.01),2))
    if (s_l == 'long'):
        params = session.place_active_order(
            symbol = symbol,
            side = "Sell",
            order_type = "Market",
            qty = quantity_l,
            price = close_price,
            time_in_force = "GoodTillCancel",
            reduce_only = True,
            close_on_trigger = False)

        response = (params)
        return response
        
    if (s_l == 'short'):
        close_price = str(round(sprice*(1+0.01),2))
        params = session.place_active_order(
            symbol = symbol,
            side = "Buy",
            order_type = "Market",
            qty = quantity_l,
            price = close_price,
            time_in_force = "GoodTillCancel",
            reduce_only = True,
            close_on_trigger = False)
        
        response = (params)
        return response


''' GET ALL OPENED POSITIONS '''

def get_opened_positions_long(symbol):
    session = HTTP("https://api.bybit.com", api_key=KEY, api_secret=SECRET)
    status = session.my_position(symbol=symbol)
    positions = pd.DataFrame(status['result'])
    global profit
    a = positions[positions['symbol']==symbol]['size'].astype(float).tolist()[0:]
    global laverage
    laverage = positions[positions['symbol']==symbol]['leverage']
    entryprice = positions[positions['symbol']==symbol]['entry_price']
    profit = positions['unrealised_pnl']
    # Request Balance
    request_balance = session.get_wallet_balance(coin='USDT')
    balance = round(float(request_balance['result']['USDT']['wallet_balance']), 2)
        
    if a[0] > 0:
        a = a[0]
        pos = "long"
        
    else: 
        pos = ""
    return([pos,a,profit,laverage,balance,entryprice,0])

def get_opened_positions_short(symbol):
    session = HTTP("https://api.bybit.com", api_key=KEY, api_secret=SECRET)
    status = session.my_position(symbol=symbol)
    positions = pd.DataFrame(status['result'])
    global profit
    a = positions[positions['symbol']==symbol]['size'].astype(float).tolist()[0:]
    global laverage
    laverage = positions[positions['symbol']==symbol]['leverage']
    entryprice = positions[positions['symbol']==symbol]['entry_price']
    profit = positions['unrealised_pnl']
    # Request Balance
    request_balance = session.get_wallet_balance(coin='USDT')
    balance = round(float(request_balance['result']['USDT']['wallet_balance']), 2)
        
    if a[1] > 0:
        a = a[1]
        pos = "short"
        
    else: 
        pos = ""
    return([pos,a,profit,laverage,balance,entryprice,0])


''' GET SYMBOL PRICES '''

def get_symbol_price(symbol):
    # --- timestamp ------------------------------------
    today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    dt = datetime.strptime(today, '%Y-%m-%d %H:%M:%S')
    in_secods_now = int(dt.timestamp())
    # --- timestamp ------------------------------------
    session = HTTP("https://api.bybit.com", api_key=KEY, api_secret=SECRET)
    prices = session.query_kline(
        symbol = symbol,
        interval = t_frame,
        limit = 200,
        from_time = (in_secods_now - (200 * t_frame)*60))
    df = pd.DataFrame(prices['result'])

    return(df['close'])


''' GET SYMBOL LAST PRICE '''

def get_symbol_price_last(symbol):
    # --- timestamp ------------------------------------
    today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    dt = datetime.strptime(today, '%Y-%m-%d %H:%M:%S')
    in_secods_now = int(dt.timestamp())
    # --- timestamp ------------------------------------
    session = HTTP("https://api.bybit.com", api_key=KEY, api_secret=SECRET)
    prices = session.query_kline(
        symbol = symbol,
        interval = t_frame,
        limit = 200,
        from_time = (in_secods_now - (200 * t_frame)*60))
    df = pd.DataFrame(prices['result'])
    df = df['close'].iloc[-1]

    return (df)


''' I N D I C A T O R S '''

''' This is the space for any indicator or strategy you want to build.
    Make sure to return your strategy with the keyword "signal" 
    that will be used below to process the orders. '''


''' T A K E   P R O F I T   /   S T O P   L O S S '''

def main_long(step):
    global proffit_array
    time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    try:
        getTPSLfrom_telegram()
        position = get_opened_positions_long(symbol)
        open_sl = position[0]
        if open_sl == "":
            signal = check_if_signal(symbol)
            proffit_array = copy.copy(eth_proffit_array)
            
            if signal == 'long':
                open_position(symbol,'long',maxposition)
                print(f'Getting Open a New Position:: LONG \nAT:: {time_now}')
            
        else: # check, keep or close the positions
            entry_price = position[5] # enter price
            current_price = get_symbol_price_last(symbol)
            quantity = position[1]
            balance = get_opened_positions_long(symbol)
            print(f'Position:: [{open_sl}] is Active')
            
            if open_sl == 'long':
                stop_price = entry_price[0]*(1-stop_percent)
                
                if current_price < stop_price:
                    # stop loss activated
                    close_position(symbol, 'long', abs(quantity))
                    proffit_array = copy.copy(eth_proffit_array)
                    print(f'Closing a Position:: LONG')
                else:
                    temp_arr = copy.copy(eth_proffit_array)
                    for j in range(0,len(temp_arr)-1):
                        delta = temp_arr[j][0]
                        contracts = temp_arr[j][1]

                        if (current_price > (entry_price[0]+delta)):
                        # take profit activated
                            close_position(symbol,'long',abs(round(maxposition*(contracts/20),3)))
                            del temp_arr[0]
      
    except :
        print(f'\n\n{symbol} Something went wrong. Continuing...')


def main_short(step):
    global proffit_array
    time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    try:
        getTPSLfrom_telegram()
        position = get_opened_positions_short(symbol)
        open_sl = position[0]
        if open_sl == "": # no position
            signal = check_if_signal(symbol)
            proffit_array = copy.copy(eth_proffit_array)
            
            if signal == 'short':
                open_position(symbol,'short',maxposition)
                print(f'Getting Open a New Position:: SHORT \nAT:: {time_now}')
        else: # check, keep or close the positions
            entry_price = position[5] # enter price
            current_price = get_symbol_price_last(symbol)
            quantity = position[1]
            balance = get_opened_positions_short(symbol)
            print(f'Position:: [{open_sl}] is Active')
           
            if open_sl == 'short': 
                stop_price = entry_price[1]*(1+stop_percent)
                
                if current_price > stop_price: 
                    # stop loss activated
                    close_position(symbol, 'short', abs(quantity))
                    proffit_array = copy.copy(eth_proffit_array)
                    print(f'Closing a Position:: SHORT')
                else:
                    temp_arr = copy.copy(eth_proffit_array)
                    for j in range(0,len(temp_arr)-1):
                        delta = temp_arr[j][0]
                        contracts = temp_arr[j][1]

                        if (current_price < (entry_price[1]-delta)):
                        # take profit activated
                            close_position(symbol,'short',abs(round(maxposition*(contracts/20),3)))
                            del temp_arr[0]
      
    except :
        print(f'\n\n{symbol} Something went wrong. Continuing...')


''' E X E C U T I O N '''

starttime = time.time()
timeout = time.time() + 60*60*48  # 60 seconds times 60 meaning the script will run for 24 hr
counterr = 1
began = print(f'{symbol} GETTING STARTED'), print('GETTING STARTED')
while time.time() <= timeout:
    try:
        main_long(counterr), main_short(counterr)
        counterr = counterr+1
        if counterr > 5:
            counterr = 1
        time.sleep(50 - ((time.time() - starttime) % 50.0)) # 2 minutes (120sec) interval between each new execution
        
    except KeyboardInterrupt:
        print('\n\KeyboardInterrupt. Stopping.')
        exit()

if time.time() >= timeout:
    print(f'*** T I M E O U T *** \nBOT SUSPENDED')


''' E N D '''


'''
     \                |         \ 
   _  \       |\__/|  |       _  \ 
__/  __\    __|    |__|    __/  __\ 

'''


