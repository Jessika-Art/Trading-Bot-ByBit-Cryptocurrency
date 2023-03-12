# Trading Bot on ByBit crypto-currency exchange.

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
