
''' A L G O R I T H M   T R A D I N G   F O R   B Y B I T   E X C H A N G E '''

''' A A V E   U S D T '''
''' Aave / US Dollar Tether '''

import pandas as pd
import numpy as np

# IF A 'TIMEOUT' RESPONSE FROM THE SERVER HAPPEN, EXECUTE THE BELOW LINE IN THE TERMINAL.
# pip install --default-timeout=100 future

from pybit import HTTP
import talib as TAL
import time
from datetime import datetime
from itertools import compress 
import threading

# THIS FUNCTION AVOID THE CALL OUT FROM THE SERVER WHEN A RESPONSE TAKES MORE TIME.
import urllib3, socket
from urllib3.connection import HTTPConnection
HTTPConnection.default_socket_options = ( 
    HTTPConnection.default_socket_options + [
    (socket.SOL_SOCKET, socket.SO_SNDBUF, 1000000),
    (socket.SOL_SOCKET, socket.SO_RCVBUF, 1000000)])

''' K E Y S '''
# MAINNET
KEY, SECRET, MAINNET = "7ikvp5UbQIbdK34mej", "iVMc0BrFJLZoBYhuK3xr9Is84VJaSGSY50Nq", 'https://api.bybit.com'
# TESTNET
# KEY, SECRET, TESTNET = "ROqv1YA1fI4zvAB1kw", "2q5v9f10cSsxNrfKSPs7mWElLD7j9J4gIrIJ", 'https://api-testnet.bybit.com'

''' M A I N   S E T T I N G S '''
ENVIRONMENT = MAINNET

symbol = 'AAVEUSDT'                     # SYMBOL TO TRADE
t_frame = 5                             # MAIN TIMEFRAME TO TRADE
TP3, TP2, TP1 = 5.5, 3.4, 2.2           # DIFFERENT LEVEL FOR TAKE PROFIT / BTCUSDT
HOURLY_BODY_SIZE = 0.40                 # DEFINE SIZE HOURLY CANDLE FOR SIGNAL FUNCTION
PREV_1 = 0.5                            # PREVENT LOSE IN SL_TP FUNCTION
QTY = 3                                 # QUANTITY BUY_SELL


# HOW IT WORKS
def EXPLANATION():
    '''
    This Algorithm will trade the market as follow:
    --------------------------------------------------------------------
    FOR BUY POSITION
    Check for candlestick pattern in the 5 minute period.

    1st condition:
    If the second last 5 minute candle is a bull pattern

    2nd condition:
    If the last candle is green.

    3rd condition:
    If the high of the 3 last candles are not going down.

    4th condition:
    If the last 1 hour period candle is green.

    5th condition:
    If the body of the last 1 hour period candle is tall enough.

    6th condition:
    If the shadow of the 1 hour period candle is shorter than his body.

    FOR SHORT CONDITION THE SAME BUT UPSIDE DOWN.
    --------------------------------------------------------------------
    --------------------------------------------------------------------
    CLOSING BUY POSITION
    1st condition:
    Set as a normal Stop Loss the Lower Low of the last 2 candle of 5 minute period.

    2nd condition:
    If the current market price is now a few points above the price at the entry position.

    3rd condition:
    If the second last candle of 5 minute period is a reverse pattern, Close Position.

    4th condition:
    Condition for 1 minute period.
    If the current market price is now a few points above the entry price and
    if it turns back to the price at the entry position and
    if the current candle is bear, Close Positon.

    5th condition:
    If the atutomatic stop loss has not been set the loss reach 0.9% of the total bet, Close Position.

    FOR SHORT CONDITION THE SAME BUT UPSIDE DOWN.
    --------------------------------------------------------------------
    --------------------------------------------------------------------

    '''
    pass

# TIME FUNCTION
def TIMESTAMP():
    toda = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    dt = datetime.strptime(toda, '%Y-%m-%d %H:%M:%S')
    in_secods_now = int(dt.timestamp())

    return in_secods_now

# GET 5min DATA
def MINUTE():
    session_5_min = HTTP(ENVIRONMENT, api_key=KEY, api_secret=SECRET)
    prices = session_5_min.query_kline(
        symbol = symbol,
        interval = t_frame,
        limit = 4,
        from_time = (TIMESTAMP() - (4 * t_frame)*60))
    df = pd.DataFrame(prices['result'])
    df = df[['open','high','low','close']].astype(float)
    FIVE_OPEN = df['open']
    FIVE_HIGH = df['high'].iloc[-2:].max()
    FIVE_LOW = df['low'].iloc[-2:].min()
    FIVE_CLOSE = df['close'].iloc[-1]

    FIVE_BULL_CANDLE = df['close'].iloc[-1] > df['open'].iloc[-1]
    FIVE_BEAR_CANDLE = df['close'].iloc[-1] < df['open'].iloc[-1]

    FIVE_HIGH_THREE = (df['high'].iloc[-3] > df['high'].iloc[-2]) and (df['high'].iloc[-2] > df['high'].iloc[-1])
    FIVE_LOW_THREE = (df['low'].iloc[-3] < df['low'].iloc[-2]) and (df['low'].iloc[-2] < df['low'].iloc[-1])

    return ([FIVE_OPEN, FIVE_HIGH, FIVE_LOW, FIVE_CLOSE, FIVE_BULL_CANDLE, FIVE_BEAR_CANDLE, FIVE_HIGH_THREE, FIVE_LOW_THREE])

# OPEN A POSITION
def open_position(symbol, SIDE, QTY):
    session = HTTP(ENVIRONMENT, api_key=KEY, api_secret=SECRET)
    sprice = MINUTE()[3]

    if (SIDE == 'long'):
        close_price = str(round(sprice*(1-0.01),2))
        params = session.place_active_order(
            symbol = symbol,
            side = "Buy",
            order_type = "Market",
            qty = QTY,
            price = close_price,
            time_in_force = "GoodTillCancel",
            reduce_only = False,
            close_on_trigger = False)

        response = (params)
        return response  
       
    if (SIDE == 'short'):
        close_price = str(round(sprice*(1-0.01),2))
        params = session.place_active_order(
            symbol = symbol,
            side = "Sell",
            order_type = "Market",
            qty = QTY,
            price = close_price,
            time_in_force = "GoodTillCancel",
            reduce_only = False,
            close_on_trigger = False)

        response = (params)
        return response  

# CLOSE A POSITION
def close_position(symbol, SIDE, QTY):
    session = HTTP(ENVIRONMENT, api_key=KEY, api_secret=SECRET)
    sprice = MINUTE()[3]

    close_price = str(round(sprice*(1+0.01),2))
    if (SIDE == 'long'):
        params = session.place_active_order(
            symbol = symbol,
            side = "Sell",
            order_type = "Market",
            qty = QTY,
            price = close_price,
            time_in_force = "GoodTillCancel",
            reduce_only = True,
            close_on_trigger = False)

        response = (params)
        return response
        
    if (SIDE == 'short'):
        close_price = str(round(sprice*(1+0.01),2))
        params = session.place_active_order(
            symbol = symbol,
            side = "Buy",
            order_type = "Market",
            qty = QTY,
            price = close_price,
            time_in_force = "GoodTillCancel",
            reduce_only = True,
            close_on_trigger = False)
        
        response = (params)
        return response

# DICTIONARY PATTERNS
candle_rankings = {
        "CDL3LINESTRIKE_Bull": 1,
        "CDL3LINESTRIKE_Bear": 2,
        "CDL3BLACKCROWS_Bull": 3,
        "CDL3BLACKCROWS_Bear": 3,
        "CDLEVENINGSTAR_Bull": 4,
        "CDLEVENINGSTAR_Bear": 4,
        "CDLTASUKIGAP_Bull": 5,
        "CDLTASUKIGAP_Bear": 5,
        "CDLINVERTEDHAMMER_Bull": 6,
        "CDLINVERTEDHAMMER_Bear": 6,
        "CDLMATCHINGLOW_Bull": 7,
        "CDLMATCHINGLOW_Bear": 7,
        "CDLABANDONEDBABY_Bull": 8,
        "CDLABANDONEDBABY_Bear": 8,
        "CDLBREAKAWAY_Bull": 10,
        "CDLBREAKAWAY_Bear": 10,
        "CDLMORNINGSTAR_Bull": 12,
        "CDLMORNINGSTAR_Bear": 12,
        "CDLPIERCING_Bull": 13,
        "CDLPIERCING_Bear": 13,
        "CDLSTICKSANDWICH_Bull": 14,
        "CDLSTICKSANDWICH_Bear": 14,
        "CDLTHRUSTING_Bull": 15,
        "CDLTHRUSTING_Bear": 15,
        "CDLINNECK_Bull": 17,
        "CDLINNECK_Bear": 17,
        "CDL3INSIDE_Bull": 20,
        "CDL3INSIDE_Bear": 56,
        "CDLHOMINGPIGEON_Bull": 21,
        "CDLHOMINGPIGEON_Bear": 21,
        "CDLDARKCLOUDCOVER_Bull": 22,
        "CDLDARKCLOUDCOVER_Bear": 22,
        "CDLIDENTICAL3CROWS_Bull": 24,
        "CDLIDENTICAL3CROWS_Bear": 24,
        "CDLMORNINGDOJISTAR_Bull": 25,
        "CDLMORNINGDOJISTAR_Bear": 25,
        "CDLXSIDEGAP3METHODS_Bull": 27,
        "CDLXSIDEGAP3METHODS_Bear": 26,
        "CDLTRISTAR_Bull": 28,
        "CDLTRISTAR_Bear": 76,
        "CDLGAPSIDESIDEWHITE_Bull": 46,
        "CDLGAPSIDESIDEWHITE_Bear": 29,
        "CDLEVENINGDOJISTAR_Bull": 30,
        "CDLEVENINGDOJISTAR_Bear": 30,
        "CDL3WHITESOLDIERS_Bull": 32,
        "CDL3WHITESOLDIERS_Bear": 32,
        "CDLONNECK_Bull": 33,
        "CDLONNECK_Bear": 33,
        "CDL3OUTSIDE_Bull": 34,
        "CDL3OUTSIDE_Bear": 39,
        "CDLRICKSHAWMAN_Bull": 35,
        "CDLRICKSHAWMAN_Bear": 35,
        "CDLSEPARATINGLINES_Bull": 36,
        "CDLSEPARATINGLINES_Bear": 40,
        "CDLLONGLEGGEDDOJI_Bull": 37,
        "CDLLONGLEGGEDDOJI_Bear": 37,
        "CDLHARAMI_Bull": 38,
        "CDLHARAMI_Bear": 72,
        "CDLLADDERBOTTOM_Bull": 41,
        "CDLLADDERBOTTOM_Bear": 41,
        "CDLCLOSINGMARUBOZU_Bull": 70,
        "CDLCLOSINGMARUBOZU_Bear": 43,
        "CDLTAKURI_Bull": 47,
        "CDLTAKURI_Bear": 47,
        "CDLDOJISTAR_Bull": 49,
        "CDLDOJISTAR_Bear": 51,
        "CDLHARAMICROSS_Bull": 50,
        "CDLHARAMICROSS_Bear": 80,
        "CDLADVANCEBLOCK_Bull": 54,
        "CDLADVANCEBLOCK_Bear": 54,
        "CDLSHOOTINGSTAR_Bull": 55,
        "CDLSHOOTINGSTAR_Bear": 55,
        "CDLMARUBOZU_Bull": 71,
        "CDLMARUBOZU_Bear": 57,
        "CDLUNIQUE3RIVER_Bull": 60,
        "CDLUNIQUE3RIVER_Bear": 60,
        "CDL2CROWS_Bull": 61,
        "CDL2CROWS_Bear": 61,
        "CDLBELTHOLD_Bull": 62,
        "CDLBELTHOLD_Bear": 63,
        "CDLHAMMER_Bull": 65,
        "CDLHAMMER_Bear": 65,
        "CDLHIGHWAVE_Bull": 67,
        "CDLHIGHWAVE_Bear": 67,
        "CDLSPINNINGTOP_Bull": 69,
        "CDLSPINNINGTOP_Bear": 73,
        "CDLUPSIDEGAP2CROWS_Bull": 74,
        "CDLUPSIDEGAP2CROWS_Bear": 74,
        "CDLGRAVESTONEDOJI_Bull": 77,
        "CDLGRAVESTONEDOJI_Bear": 77,
        "CDLHIKKAKEMOD_Bull": 82,
        "CDLHIKKAKEMOD_Bear": 81,
        "CDLHIKKAKE_Bull": 85,
        "CDLHIKKAKE_Bear": 83,
        "CDLENGULFING_Bull": 84,
        "CDLENGULFING_Bear": 91,
        "CDLMATHOLD_Bull": 86,
        "CDLMATHOLD_Bear": 86,
        "CDLHANGINGMAN_Bull": 87,
        "CDLHANGINGMAN_Bear": 87,
        "CDLRISEFALL3METHODS_Bull": 94,
        "CDLRISEFALL3METHODS_Bear": 89,
        "CDLKICKING_Bull": 96,
        "CDLKICKING_Bear": 102,
        "CDLDRAGONFLYDOJI_Bull": 98,
        "CDLDRAGONFLYDOJI_Bear": 98,
        "CDLCONCEALBABYSWALL_Bull": 101,
        "CDLCONCEALBABYSWALL_Bear": 101,
        "CDL3STARSINSOUTH_Bull": 103,
        "CDL3STARSINSOUTH_Bear": 103,
        "CDLDOJI_Bull": 104,
        "CDLDOJI_Bear": 104,
        "CDLLONGLINE_Bull": 105,
        "CDLLONGLINE_Bear": 105,
        "CDLSHORTLINE_Bull": 106,
        "CDLSHORTLINE_Bear": 106,
        "CDLSTALLEDPATTERN_Bull": 107,
        "CDLSTALLEDPATTERN_Bear": 107
    }

# APPLY PATTERNS FOR 5min TIMEFRAME
def PATTERN_5_MIN():

    # GET DATA FROM THE EXCHANGE
    session = HTTP(ENVIRONMENT, api_key=KEY, api_secret=SECRET)
    prices = session.query_kline(
            symbol = symbol,
            interval = t_frame,
            limit = 20,
            from_time = (TIMESTAMP() - (20 * t_frame)*60))
    df = pd.DataFrame(prices['result'])
    df = df[['open','high','low','close']].astype(float)

    # GET ALL CANDLESTICK PATTERNS FROM TA-LIB
    candle_names = TAL.get_function_groups()['Pattern Recognition']
    for candle in candle_names:
        df[candle] = getattr(TAL, candle)(df.open, df.high, df.low, df.close)
    
    # CREATE 2 BLANK COLUMNS BLANK WHERE WILL BE FILLED BY PATTERNS
    df['candlestick_pattern'] = np.nan
    df['candlestick_match_count'] = np.nan

    # LOOP THROUGH, LOOK FOR PATTERN IN THE DATA
    for index, row in df.iterrows():
        # FILL THE BLANK VALUES WITH 'NO PATTERN' IF THERE'S NO PATTERN AND SET EACH WITH '0'
        if len(row[candle_names]) - sum(row[candle_names] == 0) == 0:
            df.loc[index,'candlestick_pattern'] = "NO_PATTERN"
            df.loc[index, 'candlestick_match_count'] = 0
        # SINGLE PATTERN FOUND
        elif len(row[candle_names]) - sum(row[candle_names] == 0) == 1:
            # IF FOUND A BULL PATTERN
            if any(row[candle_names].values > 0):
                # ADD 'Bull' AT THE END OF THE NAME SO WILL BE EASY TO IDENTIFY BETTER
                pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bull'
                df.loc[index, 'candlestick_pattern'] = pattern
                df.loc[index, 'candlestick_match_count'] = 1             

            # IF FOUND A BEAR PATTERN
            else:
                # ADD 'Bear' AT THE END OF THE NAME SO WILL BE EASY TO IDENTIFY BETTER
                pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bear'
                df.loc[index, 'candlestick_pattern'] = pattern
                df.loc[index, 'candlestick_match_count'] = 1            

        # IF MULTIPLE PATTERN MATCHED -- select best performance
        else:
            # FILTER OUT PATTERN NAMES
            patterns = list(compress(row[candle_names].keys(), row[candle_names].values != 0))
            container = []
            for pattern in patterns:
                if row[pattern] > 0:
                    container.append(pattern + '_Bull') 
                else:
                    container.append(pattern + '_Bear')
            
            # LOOP THOUGH THE 'container' AND CHECK IF THE NAMES IN 'cnadle_ranking' MATCH WITH NAMES IN 'container'
            rank_list = [candle_rankings[p] for p in container]
            if len(rank_list) == len(container):
                rank_index_best = rank_list.index(min(rank_list))
                df.loc[index, 'candlestick_pattern'] = container[rank_index_best]
                df.loc[index, 'candlestick_match_count'] = len(container)
    # CLEAN UP CANDLESTICK COLUMN
    df.drop(candle_names, axis = 1, inplace = True)

    return (df)

# GET HOURLY CANDLE
def H():
    session_H = HTTP(ENVIRONMENT, api_key=KEY, api_secret=SECRET)
    prices_H = session_H.query_kline(
        symbol = symbol,
        interval = 60,
        limit = 1,
        from_time = (TIMESTAMP() - (1 * 60)*60))
    df_H = pd.DataFrame(prices_H['result'])
    df_H = df_H[['open','high','low','close']]
    # df_H.reset_index()

    return (df_H)
    
# GET POSITION CURRENTLY OPEN
def get_opened_positions(symbol):
    session = HTTP(ENVIRONMENT, api_key=KEY, api_secret=SECRET)
    status = session.my_position(symbol=symbol)
    positions = pd.DataFrame(status['result'])
    global profit
    a = positions[positions['symbol']==symbol]['size'].astype(float).tolist()[0:]               # GET SIZE POSITION 
    global laverage
    laverage = positions[positions['symbol']==symbol]['leverage']                               # GET CURRENT LEVERAGE
    entryprice = positions[positions['symbol']==symbol]['entry_price'].astype(float).tolist()   # GET THE PARICE AT THE ENTRY
    profit = positions['unrealised_pnl']                                                        # GET CURRENT PROFIT OR LOSS
    # Request Balance                                                                       
    request_balance = session.get_wallet_balance(coin='USDT')                                   
    balance = round(float(request_balance['result']['USDT']['wallet_balance']), 2)              # GET BALANCE
    # DEFINE IF A POSITION IS CURRENTLY OPEN OR NOT
    if a[0] > 0:
        a = a[0]
        pos = "long"
        
    elif a[1] > 0:
        a = a[1]
        pos = "short"
        
    else: 
        pos = ""
    
    return([pos,a,profit,laverage,entryprice, balance, 0])                                      # RETURN AS A LIST
 
# CHECK SIGNAL TO OPEN POSITION
def check_signal(symbol):

    SIGNAL = ''

    # DISPLAY LAST VALID PATTERN
    PATTERN = PATTERN_5_MIN()['candlestick_pattern'].iloc[-2]
    # print(PATTERN) 

    # CHECK IF LAST PATTERN (5min) IS BULLISH
    BULL = PATTERN_5_MIN()['candlestick_pattern'].str.contains('Bull')

    # CHECK IF LAST PATTERN (5min) IS BEARISH
    BEAR = PATTERN_5_MIN()['candlestick_pattern'].str.contains('Bear')

    # CHECK IF CURRENT CANDLE IS A BULL
    FIVE_BULL_CANDLE = MINUTE()[4]

    # CHECK IF CURRENT CANDLE IS A BEAR
    FIVE_BEAR_CANDLE = MINUTE()[5]

    # CHECK LAST THREE HIGH ARE DESCENDENT
    FIVE_HIGH_THREE = MINUTE()[6]

    # CHECK LAST THREE HIGH ARE ACENDENT
    FIVE_LOW_THREE = MINUTE()[7]

    # LOOP THROUGH HOURLY CANDLE
    for index, row in H().iterrows():
        BULLISH_CANDLE = row['close'] > row['open']                 # BULLISH HOURLY TREND
        BEARISH_CANDLE = row['close'] < row['open']                 # BEARISH HOURLY TREND     

        RED_BODY = row['open'] - row['close']                       # BEAR BODY SIZE
        GREEN_BODY = row['close'] - row['open']                     # BULL BODY SIZE
        BULL_SHADOWS = row['high'] - row['close']                   # HIGH SHADOW SIZE
        BEAR_SHADOWS = row['close'] - row['low']                    # LOW SHADOW SIZE

    # L O N G
    if BULLISH_CANDLE == True:                                      # IF IS UP-TREND
        print('BULL Trend')
        if GREEN_BODY > HOURLY_BODY_SIZE:                           # IF THE BODY IS GREATER ENAUGH
            print('Body is grater enaugh')
            if round(GREEN_BODY, 3) > round(BULL_SHADOWS, 3):       # IF THE BODY IS LONGER THAN THE HIGH
                print('Body is Longer than its HIGH')
                if FIVE_HIGH_THREE == False:                        # IF IS NOT GOES DOWN
                    print(PATTERN)                                  # DISPLAY PATTERN NAME
                    if BULL.iloc[-2] == True:                       # IF A VALID PATTERN HAS BEEN FOUND
                        if FIVE_BULL_CANDLE == True or BULL.iloc[-1] == True:
                            SIGNAL = 'long'
                            print(f'LONG SIGNAL CATCHED for {symbol}')


    # S H O R T
    if BEARISH_CANDLE == True:                                      # IF IS DOWN-TREND
        print('BEAR Trend')
        if RED_BODY > HOURLY_BODY_SIZE:                             # IF THE BODY IS GREATER ENAUGH
            print('Body is grater enaugh')
            if round(RED_BODY, 3) > round(BEAR_SHADOWS, 3):         # IF THE BODY IS LONGER THAN THE LOW
                print('Body is Longer than its LOW')
                if FIVE_LOW_THREE == False:                         # IF IS NOT GOES UP
                    print(PATTERN)                                  # DISPLAY PATTERN NAME
                    if BEAR.iloc[-2] == True:                       # IF A VALID PATTERN HAS BEEN FOUND
                        if FIVE_BEAR_CANDLE == True or BEAR.iloc[-1] == True:
                            SIGNAL = 'short'
                            print(f'SHORT SIGNAL CATHED for {symbol}')
    
    return SIGNAL

# BUY or SELL
def main(step):

    POSITIONS = get_opened_positions(symbol)
    open_sl = POSITIONS[0]                                      # GET THE SIDE BUY OR SELL
    HH = MINUTE()[1]                                            # GET THE HIGHER HIGH   
    LL = MINUTE()[2]                                            # GET THE LOWER LOW
    OPENED = False                                              # NEEDED IN ORDER TO OPEN ONE POSITION AT TIME
        
    # LOOKING FOR PATTERN
    if open_sl == "" and OPENED == False:

        try:
            signal = check_signal(symbol)                       # TO GET THE SIGNALS FOR BUY AND SELL

            # O P E N   P O S I T I O N   L O N G   S I D E
            if signal == 'long':                      
                open_position(symbol, 'long', QTY)              
                print('Long Opened')
                session_SLL = HTTP(ENVIRONMENT, api_key=KEY, api_secret=SECRET)
                session_SLL.set_trading_stop(
                symbol=symbol,
                side="Buy",
                stop_loss=LL)                             

                OPENED = True
                        

            # O P E N   P O S I T I O N   S H O R T   S I D E
            elif signal == 'short':
                open_position(symbol, 'short', QTY)
                print('Short Opened')
                session_SLL = HTTP(ENVIRONMENT, api_key=KEY, api_secret=SECRET)
                session_SLL.set_trading_stop(
                symbol=symbol,
                side="Sell",
                stop_loss=HH)  

            
            # I F   N O   P A T T E R N,   D O   N O T H I N G
            else:
                None
        except:
            print(f'Could NOT open a new position {symbol}')
        
# EXECUTE MAIN - BUY or SELL
def execution_main():
    counterr = 1
    print(f'{symbol} Looking for pattern...')
    while True:
        try:
            
            main(counterr)
            counterr = counterr + 1
            if counterr > 5:
                counterr = 1
            time.sleep(44)
            
        except KeyboardInterrupt:
            print('\n\KeyboardInterrupt. Stopping.')
            exit()

# EXECUTION CLOSE - TAKE PROFIT and STOP LOSS
def execution_tp_sl():
    
    while True:

        # try:
        
        # S E T T I N G S

        # CHECK IF LAST PATTERN (5min) IS BULLISH
        BULL = PATTERN_5_MIN()['candlestick_pattern'].str.contains('Bull')

        # CHECK IF LAST PATTERN (5min) IS BEARISH
        BEAR = PATTERN_5_MIN()['candlestick_pattern'].str.contains('Bear')

        POSITIONS = get_opened_positions(symbol)                            # STORE FUNCTION IN A VAR IN ORDER TO USE IT EASLY
        open_sl = POSITIONS[0]                                              # GET THE 'long', 'short' POSITIONS
        MAX_QTY = POSITIONS[1]                                              # THE CURRENT QUANTITY IN A OPEN POSITION
        entry_price_long_day_minor = POSITIONS[4][0] + TP1                  # GET THE PRICE AT THE ENTRY POSITION + A FEW POINTS TO USE AS A TP / 0.340
        entry_price_short_day_minor = POSITIONS[4][1] - TP1                 # GET THE PRICE AT THE ENTRY POSITION - A FEW POINTS TO USE AS A TP
        prevent_lose_long = POSITIONS[4][0] + PREV_1                        # GET THE PRICE AT THE ENTRY POSITION + A FEW POINTS TO USE AS A TP / 0.340
        prevent_lose_short = POSITIONS[4][1] - PREV_1                       # GET THE PRICE AT THE ENTRY POSITION - A FEW POINTS TO USE AS A TP

        # REQUEST DATA FOR 1min TIMEFRAME
        session_one_min = HTTP(ENVIRONMENT, api_key=KEY, api_secret=SECRET)
        prices = session_one_min.query_kline(
            symbol = symbol,
            interval = 1,
            limit = 4,
            from_time = (TIMESTAMP() - (4 * 1)*60))
        df = pd.DataFrame(prices['result'])
        df = df[['open','high','low','close']].astype(float)
        CURRENT_BULL = df['close'].iloc[-1] > df['open'].iloc[-1]           # IF CURRENT CANDLE IS BULL
        CURRENT_BEAR = df['close'].iloc[-1] < df['open'].iloc[-1]           # IF CURRENT CANDLE IS BEAR
        ONE_HIGH = df['high'].iloc[-3]
        ONE_LOW = df['low'].iloc[-3]
        ONE_CLOSE_2RD = df['close'].iloc[-2]
        ONE_OPEN_2ND = df['open'].iloc[-3]
        ONE_CLOSE = df['close'].iloc[-1]                                    # GET THE CURRENT PRICE

        # FORCE STOP LOSS
        ENTRY_LONG = POSITIONS[4][0]                                        # GET THE PARICE AT THE ENTRY FOR BUY    
        ENTRY_SHORT = POSITIONS[4][1]                                       # GET THE PARICE AT THE ENTRY FOR SELL 
        STOP_PERCENTAGE = 0.009                                             # 0.01 == 1%
        STOP_LOSS_LONG = ENTRY_LONG * (1-STOP_PERCENTAGE)                   # STOP LOSS FOR BUY POSITION
        STOP_LOSS_SHORT = ENTRY_SHORT * (1+STOP_PERCENTAGE)                 # STOP LOSS FOR SELL POSITION

        LMT = []

        # S T A R T   C L O S I N G   T H E   L O N G   S I D E   P O S I T I O N
        if open_sl == 'long':                                               
                        
            # if NO Bullish day
            # if NO 4h pattern
            # if the price has reached the 1st price
            if ONE_CLOSE > entry_price_long_day_minor: 
                # if a Bear pattern is met, TP     
                if BEAR.iloc[-2] == True:                      
                    close_position(symbol, 'long', MAX_QTY)                 
                    print('Take Profit - Inverse Pattern Met')
                # if the price meet the high of the 3rd candle, TP
                elif ONE_CLOSE < ONE_HIGH and CURRENT_BEAR:           
                    close_position(symbol, 'long', MAX_QTY)                
                    print('Progressive Take Profit Activated for Long Position')
            
            # PREVENT LOSS
            # else the price has NOT reached any main deal
            elif ONE_CLOSE > prevent_lose_long:
                LMT.append(ONE_OPEN_2ND)
                if len(LMT) == 2:
                    del LMT[-1]
                elif ONE_CLOSE < LMT[0]:
                    close_position(symbol, 'long', MAX_QTY)
                    del LMT[::]
                    print('Prevent Loses Activated, closing position_3 LONG')
                else:
                    None

            # else FORCE STOP LOSS
            else:
                if STOP_LOSS_LONG == True:                        
                    close_position(symbol, 'long', MAX_QTY)
                    print('STOP LOSS ACTIVATED')


        # S T A R T   C L O S I N G   T H E   S H O R T   S I D E   P O S I T I O N
        if open_sl == 'short':                                               
   
            # if NO Bearish day
            # if NO 4h pattern
            # if the price has reached the 1st price
            if ONE_CLOSE < entry_price_short_day_minor: 
                # if a Bull pattern is met, TP     
                if BULL.iloc[-2] == True:                      
                    close_position(symbol, 'short', MAX_QTY)                 
                    print('Take Profit - Inverse Pattern Met')
                # if the price meet the low of the 3rd candle, TP
                elif ONE_CLOSE > ONE_LOW and CURRENT_BULL:           
                    close_position(symbol, 'short', MAX_QTY)                
                    print('Progressive Take Profit Activated for Short Position')
            
            # PREVENT LOSS
            # else the price has NOT reached any main deal
            elif ONE_CLOSE < prevent_lose_short:
                LMT.append(ONE_OPEN_2ND)
                if len(LMT) == 2:
                    del LMT[-1]
                elif ONE_CLOSE > LMT[0]:
                    close_position(symbol, 'short', MAX_QTY)
                    del LMT[::]
                    print('Prevent Loses Activated, closing position_3 SHORT')
                else:
                    None

            # else FORCE STOP LOSS
            else:
                if STOP_LOSS_SHORT == True:                        
                    close_position(symbol, 'short', MAX_QTY)
                    print('STOP LOSS ACTIVATED')

        time.sleep(16)
        

''' EXECUTE WHILE LOOP SIMULTANEOUSY '''

# CHECK FOR SIGNAL AND OPENA A POSITION
thread_AAVE_buy_sell = threading.Thread(target = execution_main)
thread_AAVE_buy_sell.start()
# STOP LOSS AND TAKE PROFIT
thread_AAVE_tp_sl = threading.Thread(target = execution_tp_sl)
thread_AAVE_tp_sl.start()

