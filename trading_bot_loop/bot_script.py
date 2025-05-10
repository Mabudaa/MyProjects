#######################################################################@ Working System @###############################################################################
import pandas as pd
import numpy as np
import pandas_ta as ta
import MetaTrader5 as mt5
import time
import datetime
import uuid
import ntplib

#######################################################################@ Indicators Section @##############################################################################
def calculate_cci(df, period=10):
    typical_price = (df['high'] + df['low'] + df['close']*2) / 4
    mean_deviation = typical_price.rolling(window=period).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
    cci = round((typical_price - typical_price.rolling(window=period).mean()) / (0.015 * mean_deviation),2)
    return cci

def lope(df,period = 10):
    weights = np.arange(1, period+1)
    envelope = df['cci'].rolling(window = period).apply(lambda x: np.dot(x, weights)/ weights.sum(), raw = True)
    return envelope

def calculate_atr(df, period=14):
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    return round(atr,2)

def generate_data(df):
    df['cci'] = calculate_cci(df)
    df['prev_cci'] = df['cci'].shift(1)
    df['atr'] = calculate_atr(df)
    df['envelope'] = lope(df)
    df['date'] = pd.to_datetime(df['time'], unit = 's')
    df = df.dropna()
    return df

######################################################################@ Checking Section @###################################################################################

def check_open_signal(symbol, dfs, open_signals):
    cci = dfs[symbol]['cci'].iat[-1]
    envelope = dfs[symbol]['envelope'].iat[-1]
    prev = dfs[symbol]['prev_cci'].iat[-1]
    if ((cci > envelope) and (prev < envelope)):
        if open_signals[symbol][-1] == "None" or open_signals[symbol][-1] == "sell":    
            open_signals[symbol].append("buy")
            return "buy"
        else:
            pass
    elif ((cci < envelope) and (prev > envelope)):
        if open_signals[symbol][-1] == "None" or open_signals[symbol][-1] == "buy":    
            open_signals[symbol].append("sell")
            return "sell"
        else:
            pass
    else:
        open_signals[symbol].append("None")
        return "None" 

def space_for_normal(symbol):
    positions = mt5.positions_get(symbol=symbol)
    if positions:
        buys = [trade for trade in positions if  trade.type == 0 and trade.comment == "normal"]
        sells = [trade for trade in positions if trade.type == 1 and trade.comment == "normal" ]
        if len(buys) == 0 and len(sells) == 0:
            return "no_normal_positions"
        elif len(buys) > 0 and len(sells) == 0:
            return "open_for_normal_short"
        elif len(sells) > 0 and len(buys) == 0:
            return "open_for_normal_long"
        else:
            return "None"
    return "no_normal_positions"

def check_level(symbol, dfs, current_close):
    points = assemble_highs_lows_by_date(dfs, symbol)
    filtered = filter_turning_points(points)
    labelled_highs_lows = label_highs_lows(filtered)
    if len(labelled_highs_lows) < 2:
        print(f"Not enough data in labelled_highs_lows for {symbol}")
        return "not_enough_data"
    
    # Fetch the latest label and second latest label's value
    latest_label = labelled_highs_lows[-1][1]
    close = current_close
    second_latest_label_value = labelled_highs_lows[-2][0][1]
    print(f"Lastest in check level: {latest_label}" )

    # Logic based on the label (hl or lh)
    if latest_label == "hl":
        if close > second_latest_label_value:
            return "level_passed"
        else:
            return "level_not_passed"
    elif latest_label == "lh":
        if close < second_latest_label_value:
            return "level_passed"
        else:
            return "level_not_passed"
    else:
        return "unknown_label"



############################################################################@ Trend Section @######################################################################################################

def check_lows(dfs, symbol):
    lows = []
    i = 1 
    while i < len(dfs[symbol]) - 1:
        next_close = dfs[symbol]['close'].iat[i + 1]
        next_open = dfs[symbol]['open'].iat[i + 1]
        prev_close = dfs[symbol]['close'].iat[i - 1]
        prev_open = dfs[symbol]['open'].iat[i - 1]
        current_down_close = dfs[symbol]['close'].iat[i]
        #print(f"Iteration {dfs[symbol]['date'].iat[i]}:")
    #   print(f"  Prev close: {prev_close}, Prev open: {prev_open}")
    #   print(f"  Current close: {current_down_close}")
    #   print(f"  Next close: {next_close}, Next open: {next_open}")
        
        if ((prev_close >= current_down_close) and (prev_open > current_down_close) and (current_down_close < next_close)):
            if next_open <= current_down_close:
                potential_peak = next_open
            else:
                potential_peak = current_down_close
    #       print(f"  Potential peak: {potential_peak}")
            
            potential_peak_index = dfs[symbol].index[i]
            down_atr = dfs[symbol].loc[potential_peak_index, 'atr']
            sliced_df = dfs[symbol].loc[potential_peak_index:]
    #       print(f"  ATR at potential peak index {potential_peak_index}: {down_atr}")
            
            for index, row in sliced_df.iterrows():
                if (row['close'] - potential_peak) > down_atr:
    #               print(f"  Low found at index {index}: {row['close']}")
                    lows.append((potential_peak_index, potential_peak))
                    break
                elif potential_peak > row['close']:
    #               print(f"  Breaking, peak is greater than row close: {row['close']}")
                    break
        i += 1
    return lows

def check_highs(dfs, symbol):
    highs = []
    i = 1 
    while i < len(dfs[symbol]) - 1:
        next_close = dfs[symbol]['close'].iat[i + 1]
        next_open = dfs[symbol]['open'].iat[i + 1]
        prev_close = dfs[symbol]['close'].iat[i - 1]
        prev_open = dfs[symbol]['open'].iat[i - 1]
        current_up_close = dfs[symbol]['close'].iat[i]
    #   print(f"Iteration {dfs[symbol]['date'].iat[i]}:")
    #   print(f"  Prev close: {prev_close}, Prev open: {prev_open}")
    #   print(f"  Current close: {current_up_close}")
    #   print(f"  Next close: {next_close}, Next open: {next_open}")
        
        if ((prev_close <= current_up_close) and (prev_open < current_up_close) and (current_up_close > next_close)):
            if next_open > current_up_close:
                potential_trough = next_open
            else:
                potential_trough = current_up_close
    #       print(f"  Potential trough: {potential_trough}")
            
            potential_trough_index = dfs[symbol].index[i]
            up_atr = dfs[symbol].loc[potential_trough_index, 'atr']
            sliced_df = dfs[symbol].loc[potential_trough_index:]
    #       print(f"  ATR at potential trough index {potential_trough_index}: {up_atr}")
            
            for index, row in sliced_df.iterrows():
                # Debugging line to print current comparison
    #           print(f"  Current row close: {row['close']}, Potential trough: {potential_trough}, Difference: {potential_trough - row['close']}, ATR: {up_atr}")
                
                if (potential_trough - row['close']) > up_atr:
    #               print(f"  High found at index {index}: {row['close']}")
                    highs.append((potential_trough_index, potential_trough))
                    break
                elif potential_trough < row['close']:
    #               print(f"  Breaking, trough is less than row close: {row['close']}")
                    break
        i += 1
    return highs

def assemble_highs_lows_by_date(dfs, symbol):
    combined = []
    lows = check_lows(dfs, symbol)
    highs = check_highs(dfs, symbol)

    
    for low_index, low_value in lows:
        low_date = dfs[symbol].loc[low_index, 'time']
        combined.append((low_date, low_value, 'low'))
        
    for high_index, high_value in highs:
        high_date = dfs[symbol].loc[high_index, 'time']
        combined.append((high_date, high_value, 'high'))
        
    combined.sort(key=lambda x: x[0])
    return combined

def filter_turning_points(turning_points):
    filtered_turning_points = [turning_points[0]]
    i = 0 
    while i < len(turning_points) - 1:  
        curr = turning_points[i][2]
        nex = turning_points[i+1][2]
        if (curr == 'low' and nex == 'high') or (curr == 'high' and nex == 'low'):
            if filtered_turning_points[-1][2] != nex:
                filtered_turning_points.append(turning_points[i+1])
            else: 
                continue
        i += 1 
    return filtered_turning_points

def label_highs_lows(highs_lows):
    if highs_lows[0][2] == 'low':
        start_index = 3
    else:
        start_index = 4
    labelled_highs_lows = []
    for i in range(start_index, len(highs_lows), 2):
        if highs_lows[i][1] < highs_lows[i-2][1]:
            labelled_highs_lows.append((highs_lows[i], "lh"))
        elif highs_lows[i][1] > highs_lows[i-2][1]:
            labelled_highs_lows.append((highs_lows[i], "hh"))
            
    for k in range(start_index + 1, len(highs_lows), 2):
        if highs_lows[k][1] < highs_lows[k-2][1]:
            labelled_highs_lows.append((highs_lows[k], "ll"))
        elif highs_lows[k][1] > highs_lows[k-2][1]:
            labelled_highs_lows.append((highs_lows[k], "hl"))

    labelled_highs_lows.sort(key=lambda x: x[0][0])
    return labelled_highs_lows
                  
def check_trend(symbol, dfs):
    points = assemble_highs_lows_by_date(dfs, symbol)
    filtered = filter_turning_points(points)
    labelled_highs_lows = label_highs_lows(filtered)
    if len(labelled_highs_lows) < 3:
        return "trend_not_clear"

    print(labelled_highs_lows)
    
    latest_label = labelled_highs_lows[-1][1]
    second_latest_label = labelled_highs_lows[-2][1]
    third_latest_label = labelled_highs_lows[-3][1]
    second_latest_label_value = labelled_highs_lows[-2][0][1]
    latest_label_date = labelled_highs_lows[-1][0][0]
    second_latest_label_date = labelled_highs_lows[-2][0][0]
    third_latest_label_date = labelled_highs_lows[-3][0][0]
    latest_readable_date = dfs[symbol].loc[dfs[symbol]['time'] == latest_label_date, 'date']
    second_latest_readable_date = dfs[symbol].loc[dfs[symbol]['time'] == second_latest_label_date, 'date']
    third_latest_readable_date = dfs[symbol].loc[dfs[symbol]['time'] == third_latest_label_date, 'date']
    close = dfs[symbol]['close'].iat[-1]
    index1 = dfs[symbol].index[dfs[symbol]['date'] == second_latest_label_date ]
    sliced_df = dfs[symbol].loc[index1[0]:]
    #print(f"Close in trend: {close}")
    #print(f"Third:{third_latest_label} {third_latest_readable_date} Second:{second_latest_label} {second_latest_readable_date} Lastest:{latest_label} {latest_readable_date}")
    
    def check_down_movement(sliced_df, second_latest_label_value):
        #print(f"[DEBUG] Checking down movement against label value: {second_latest_label_value}")
        for index, row in sliced_df.iterrows():
        #   print(f"[DEBUG] Row index: {index}, Close price: {row['close']}")
            if row['close'] < second_latest_label_value:
        #       print("[DEBUG] Found a close price lower than the label value. Returning False.")
                return False
        #print("[DEBUG] All close prices are above the label value. Returning True.")
        return True

    def check_up_movement(sliced_df, second_latest_label_value):
        #print(f"[DEBUG] Checking up movement against label value: {second_latest_label_value}")
        for index, row in sliced_df.iterrows():
            #print(f"[DEBUG] Row index: {index}, Close price: {row['close']}")
            if row['close'] > second_latest_label_value:
                #print("[DEBUG] Found a close price higher than the label value. Returning False.")
                return False
        #print("[DEBUG] All close prices are below the label value. Returning True.")
        return True
                       
    up_direction = check_down_movement(sliced_df, second_latest_label_value)
    down_direction = check_up_movement(sliced_df, second_latest_label_value)

    if (third_latest_label == 'hh' and second_latest_label == 'hl' and latest_label == 'hh') and (close < labelled_highs_lows[-2][0][1]):
        return "potential_down"
    elif (third_latest_label == 'lh' and second_latest_label == 'hl' and latest_label == 'hh') and (close < labelled_highs_lows[-2][0][1]):
        return "potential_down"
    elif (third_latest_label == 'lh' and second_latest_label == 'hl' and latest_label == 'lh') and (close< labelled_highs_lows[-2][0][1]):
        return "potential_down"
    elif (third_latest_label == 'll' and second_latest_label == 'lh' and latest_label == 'll') and (close> labelled_highs_lows[-2][0][1]):
        return "potential_up"
    elif (third_latest_label == 'hl' and second_latest_label == 'lh' and latest_label == 'll') and (close > labelled_highs_lows[-2][0][1]):
        return "potential_up"
    elif (third_latest_label == 'hl' and second_latest_label == 'lh' and latest_label == 'hl') and (close > labelled_highs_lows[-2][0][1]):
        return "potential_up"
    
    elif third_latest_label == 'hh' and second_latest_label == 'll' and latest_label == 'lh':
        return "down_trend"
    elif third_latest_label == 'll' and second_latest_label == 'hh' and latest_label == 'hl':
        return "up_trend"
    elif third_latest_label == 'lh' and second_latest_label == 'll' and latest_label == 'lh':
        return "down_trend"
    elif third_latest_label == 'hl' and second_latest_label == 'hh' and latest_label == 'hl':
        return "up_trend"

    elif third_latest_label == 'hh' and second_latest_label == 'hl' and latest_label == 'hh':
        if up_direction:
            return "up_trend"
        else:
            return "potential_down"
    elif third_latest_label == 'lh' and second_latest_label == 'hl' and latest_label == 'hh':
        if up_direction:
            return "up_trend"
        else:
            return "potential_down"   
    elif third_latest_label == 'hh' and second_latest_label == 'll' and latest_label == 'hh':
        if up_direction:
            return "up_trend"
        else:
            return "potential_down"
    elif third_latest_label == 'lh' and second_latest_label == 'll' and latest_label == 'hh':
        if up_direction:
            return "potential_up"
        else:
            return "potential_down"
    elif third_latest_label == 'hl' and second_latest_label == 'lh' and latest_label == 'll':
        if down_direction:
            return "down_trend"
        else:
            return "potential_up"
    elif third_latest_label == 'll' and second_latest_label == 'hh' and latest_label == 'll':
        if down_direction:
            return "down_trend"
        else:
            return "potential_up"
    elif third_latest_label == 'hl' and second_latest_label == 'hh' and latest_label == 'll':
        if down_direction:
            return "potential_down"
        else:
            return "potential_up"
    elif third_latest_label == 'll' and second_latest_label == 'lh' and latest_label == 'll':
        if down_direction:
            return "down_trend"
        else:
            return "potential_up"
    else:
        return "trend_not_clear"

######################################################################################################@ Trades Section @#########################################################################################
######################################################################################################@ Important Trades @############################################################################################
def normal_long(symbol, risk, dfs, stoploss_distances):
    price = mt5.symbol_info_tick(symbol).ask
    atr_value = dfs[symbol]['atr'].iat[-1]
    spread = dfs[symbol]['spread'].iat[-1]
    volume = risk
    sl = price - stoploss_distances[symbol]
    if atr_value<1:
        tp = price+(atr_value)
        volume = risk*2
    else:
        tp = price + (atr_value)
        volume = risk
    request6 = { 
        "action": mt5.TRADE_ACTION_DEAL, 
        "symbol": symbol,
        "volume": volume,
        "price": price,
        "sl": sl,
        "tp": tp,
        "comment":"normal",
        "type": mt5.ORDER_TYPE_BUY,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    mt5.order_send(request6)

def normal_short(symbol, risk, dfs, stoploss_distances):
    price = mt5.symbol_info_tick(symbol).bid
    spread = dfs[symbol]['spread'].iat[-1]
    atr_value = dfs[symbol]['atr'].iat[-1]
    sl = price + stoploss_distances[symbol]
    if atr_value<1:
        tp = price-(atr_value)
        volume = risk*2
    else:
        tp = price - (atr_value)
        volume = risk
    request1 = { 
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "price": price,
        "sl": sl,
        "tp": tp,
        "comment":"normal",
        "type": mt5.ORDER_TYPE_SELL,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    mt5.order_send(request1)

   
####################################################################################################@ Unimportant Trades @#########################################################################################

def mitigation_short(symbol,mitigation_price, mitigation_atr, risk, dfs, stoploss_distances, the_id):
    price = mt5.symbol_info_tick(symbol).ask
    atr_value = mitigation_atr
    spread = dfs[symbol]['spread'].iat[-1]
    sl = price + stoploss_distances[symbol]
    if atr_value<1:
        tp = price-(atr_value)
        volume = risk*6
    else:
        tp = price - atr_value
        volume = risk*3
    request7 = { 
        "action": mt5.TRADE_ACTION_DEAL, 
        "symbol": symbol,
        "volume": volume,
        "price": price,
        "sl": sl,
        "tp": tp,
        "comment":'mitigation,'+ the_id,
        "type": mt5.ORDER_TYPE_SELL,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
   
    def add_on_long(symbol,mitigation_price, mitigation_atr, risk, dfs, stoploss_distances, the_id):
        price = mitigation_price
        atr_value = mitigation_atr
        volume = risk*4
        if symbol == 'XAUUSD':
            sl = price - atr_value*2
        else:
            sl =  price - atr_value
        tp = price + atr_value
        request8 = { 
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": volume,
            "price": price,
            "sl": sl,
            "tp": tp,
            "comment":'add_on,'+ the_id,
            "type": mt5.ORDER_TYPE_BUY_STOP,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        mt5.order_send(request8)

    def re_add_on_long(symbol,mitigation_price, mitigation_atr, risk, dfs, stoploss_distances, the_id):
        atr_value = mitigation_atr
        price = mitigation_price + atr_value
        volume = risk*4 
        sl = price - atr_value*2
        tp = price + atr_value/2
        request9 = { 
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": volume,
            "price": price,
            "sl": sl,
            "tp": tp,
            "comment":'re_add_on,'+the_id,
            "type": mt5.ORDER_TYPE_BUY_STOP,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        mt5.order_send(request9)
    mt5.order_send(request7)
    add_on_long(symbol,mitigation_price, mitigation_atr, risk, dfs, stoploss_distances, the_id)
    re_add_on_long(symbol,mitigation_price, mitigation_atr, risk, dfs, stoploss_distances, the_id)

def re_mitigation_short(symbol,mitigation_price, mitigation_atr, risk, dfs, stoploss_distances, the_id):
    atr_value = mitigation_atr
    price = mitigation_price - (atr_value*2)
    sl = price + atr_value*2
    if atr_value<1:
        tp = price-(atr_value)
        volume = risk*6
    else:
        tp = price - atr_value
        volume = risk*3
    request10 = { 
        "action": mt5.TRADE_ACTION_PENDING, 
        "symbol": symbol,
        "volume": volume,
        "price": price,
        "sl": sl,
        "tp": tp,
        "comment":'re_mitigation,'+ the_id,
        "type": mt5.ORDER_TYPE_SELL_STOP,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    mt5.order_send(request10)


def mitigation_long(symbol,mitigation_price, mitigation_atr, risk, dfs, stoploss_distances, the_id):
    price = mt5.symbol_info_tick(symbol).ask
    atr_value = mitigation_atr
    sl = price - stoploss_distances[symbol]
    if atr_value<1:
        tp = price+(atr_value*1.5)
        volume = risk*6
    else:
        tp = price + atr_value
        volume = risk*3
    request2 = { 
        "action": mt5.TRADE_ACTION_DEAL, 
        "symbol": symbol,
        "volume": volume,
        "price": price,
        "sl": sl,
        "tp": tp,
        "comment":'mitigation,'+ the_id,
        "type": mt5.ORDER_TYPE_BUY,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    def add_on_short(symbol,mitigation_price, mitigation_atr, risk, dfs, stoploss_distances, the_id):
        price = mitigation_price
        atr_value = mitigation_atr
        volume = risk*4  #round((risk/2), 2)
        if symbol == 'XAUUSD':
            sl = price + atr_value*2
        else:
            sl =  price + atr_value*2
        tp = price - -atr_value
        request3 = { 
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": volume,
            "price": price,
            "sl": sl,
            "tp": tp,
            "comment":'add_on,'+ the_id,
            "type": mt5.ORDER_TYPE_SELL_STOP,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        mt5.order_send(request3)
    def re_add_on_short(symbol,mitigation_price, mitigation_atr, risk, dfs, stoploss_distances, the_id):
        atr_value = mitigation_atr
        price = mitigation_price - atr_value
        volume = risk*3  
        sl = price + atr_value*2
        tp = price - atr_value/2
        request4 = { 
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": volume,
            "price": price,
            "sl": sl,
            "tp": tp,
            "comment":'re_add_on,'+ the_id,
            "type": mt5.ORDER_TYPE_SELL_STOP,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        mt5.order_send(request4)
    mt5.order_send(request2)
    add_on_short(symbol,mitigation_price, mitigation_atr, risk, dfs, stoploss_distances, the_id)
    re_add_on_short(symbol,mitigation_price, mitigation_atr, risk, dfs, stoploss_distances, the_id)

def re_mitigation_long(symbol,mitigation_price, mitigation_atr, risk, dfs, stoploss_distances, the_id):
    atr_value = mitigation_atr
    price = mitigation_price + (atr_value*2)
    sl = price - atr_value*2
    if atr_value<1:
        tp = price+(atr_value*1.5)
        volume = risk*6
    else:
        tp = price + atr_value
        volume = risk*3
    request5 = { 
        "action": mt5.TRADE_ACTION_PENDING, 
        "symbol": symbol,
        "volume": volume,
        "price": price,
        "sl": sl,
        "tp": tp,
        "comment":'re_mitigation,'+ the_id,
        "type": mt5.ORDER_TYPE_BUY_STOP,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
        }
    mt5.order_send(request5)

#############################################################################################@ Mitigaation Opener @####################################################################################

def mitigation_opener(symbol, dfs, stoploss_distances, digits, long_mitigations, short_mitigations):
    current_close = dfs[symbol]['close'].iat[-1]
    if long_mitigations[symbol]:
        for mitigation in long_mitigations[symbol]:
            mitigation_id = mitigation[0]
            mitigation_price = mitigation[1]
            mitigation_risk = mitigation[2]
            mitigation_atr = mitigation[3]
            if current_close > mitigation_price:
                mitigation_long(symbol,mitigation_price, mitigation_atr, risk=mitigation_risk, dfs=dfs, stoploss_distances=stoploss_distances, the_id=mitigation_id)
                element_to_remove = mitigation_id
                for sublist in long_mitigations[symbol][:]:
                    if sublist[0] == element_to_remove:
                        long_mitigations[symbol].remove(sublist)
            else:
                pass
    else:
        pass
    if short_mitigations[symbol]:
        for mitigation in short_mitigations[symbol]:
            mitigation_id = mitigation[0]
            mitigation_price = mitigation[1]
            mitigation_risk = mitigation[2]
            mitigation_atr = mitigation[3]
            if current_close < mitigation_price:
                mitigation_short(symbol,mitigation_price, mitigation_atr, risk=mitigation_risk, dfs=dfs, stoploss_distances=stoploss_distances, the_id=mitigation_id)
                element_to_remove = mitigation_id
                for sublist in short_mitigations[symbol][:]:
                    if sublist[0] == element_to_remove:
                        short_mitigations[symbol].remove(sublist)
            else:
                pass
    else:
        pass

def re_mitigation_opener(symbols, dfs, stoploss_distances, digits, long_re_mitigations, short_re_mitigations):
    for symbol in symbols:
        positions = mt5.positions_get(symbol = symbol)
        if positions:
            buys = [trade for trade in positions if trade.type == 0]
            sells = [trade for trade in positions if trade.type == 1]
            if long_re_mitigations[symbol]:
                for mitigation in long_re_mitigations[symbol]:
                    mitigation_id = mitigation[0]
                    mitigation_price = mitigation[1]
                    mitigation_risk = mitigation[2]
                    mitigation_atr = mitigation[3]
                    active_add_on_short = [trade for trade in sells if split_and_add_to_list(trade.comment)[0] == 'add_on' and split_and_add_to_list(trade.comment)[1] == mitigation_id]
                    if len(active_add_on_short) == 1:
                        re_mitigation_long(symbol,mitigation_price, mitigation_atr, risk, dfs, stoploss_distances, the_id)
                        element_to_remove = mitigation_id
                        for sublist in long_re_mitigations[symbol][:]:
                            if sublist[0] == element_to_remove:
                                long_re_mitigations[symbol].remove(sublist)
                    else:
                        pass

            else:
                pass
            if short_re_mitigations[symbol]:
                for mitigation in short_re_mitigations[symbol]:
                    mitigation_id = mitigation[0]
                    mitigation_price = mitigation[1]
                    mitigation_risk = mitigation[2]
                    mitigation_atr = mitigation[3]
                    active_add_on_long = [trade for trade in buys if split_and_add_to_list(trade.comment)[0] == 'add_on' and split_and_add_to_list(trade.comment)[1] == mitigation_id]
                    if len(active_add_on_short) == 1:
                        re_mitigation_short(symbol,mitigation_price, mitigation_atr, risk, dfs, stoploss_distances, the_id)
                        element_to_remove = mitigation_id
                        for sublist in short_re_mitigations[symbol][:]:
                            if sublist[0] == element_to_remove:
                                short_re_mitigations[symbol].remove(sublist)
                    else:
                        pass
            else:
                pass
        else:
            continue

#############################################################################################@ News Handling Area @####################################################################################

def check_risk_period(timestamp, time_ranges):
    timestamp = datetime.datetime.fromtimestamp(timestamp)
    
    current_time = timestamp.time()

    for start, end in time_ranges:
        start_time = datetime.datetime.strptime(start, '%I:%M%p').time()
        end_time = datetime.datetime.strptime(end, '%I:%M%p').time()
        if start_time <= current_time <= end_time:
            return "risky area"
    
    return "safe"

#############################################################################################@ Data Handling Section @#################################################################################

def download_initial_data(symbols, dfs=None):
    if dfs is None:
        dfs = {}

    for symbol in symbols:
        #print(f"Fetching initial data for symbol: {symbol}")
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 110)
        if rates is None or len(rates) == 0:
            print(f"Error: No rates returned for symbol {symbol}")
            continue
        #print(f"Fetched {len(rates)} rates for {symbol}")
        df = pd.DataFrame(rates)
        #print(f"Initial data for {symbol}:\n{df.head()}")
        df = generate_data(df)
        #print(f"Data after applying generate_data for {symbol}:\n{df.head()}")
        dfs[symbol] = df
        

    # Return the dfs dictionary containing data for all symbols
    return dfs

def update_data(symbols, dfs):
    for symbol in symbols:
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 1, 110)
        if rates is None or len(rates) == 0:
            print(f"Error: No rates returned for symbol {symbol}")
            continue
        #print(f"Fetched {len(rates)} rates for {symbol}")
        df = pd.DataFrame(rates)
        #print(f"Initial data for {symbol}:\n{df.head()}")
        df = generate_data(df)
        df = df.sort_values(by='time', ascending=True)
        #print(f"Data after generate_data for {symbol}:\n{df.head()}")
        if not dfs[symbol].empty:
            #print(f"Previous data exists for {symbol}, concatenating new data.")
            dfs[symbol] = pd.concat([dfs[symbol], df]).drop_duplicates().reset_index(drop=True)
            #print(f"Data after concatenation for {symbol}:\n{dfs[symbol].tail(5)}")
        else:
            #print(f"No previous data for {symbol}, initializing new data.")
            dfs[symbol] = df
    
        dfs[symbol] = dfs[symbol].sort_values(by='time', ascending=True)

        dfs[symbol] = dfs[symbol].tail(75).reset_index(drop=True)
        #print(f"{dfs[symbol].tail(20)}")
    
        #print(f"Final data for {symbol} after tailing and resetting index:\n{dfs[symbol].tail()}"

def split_and_add_to_list(statement, existing_list=None):
    words = statement.split(',')
    if existing_list is None:
        existing_list = []
    existing_list.extend(words)
    
    return existing_list

def generate_unique_trade_id2(generated_ids):
    new_id = uuid.uuid4().hex[:10]  
    while new_id in generated_ids:
        new_id = uuid.uuid4().hex[:10]  
    generated_ids.append(new_id)
    return new_id
###############################################################################@ Time Handling Section @###################################################################################
NTP_SERVERS = ['time.google.com', 'pool.ntp.org','time.windows.com' ]

def fetch_ntp_time():
    ntp_client = ntplib.NTPClient()
    for server in NTP_SERVERS:
        try:
            response = ntp_client.request(server, version=3)
            print(f"Time fetched successfully from {server}")
            return  response.tx_time
        except Exception as e:
            print(f"Failed to fetch time from {server}: {e}")
    return None  

def calculate_offset(ntp_time):
    system_time = time.time()
    offset = ntp_time - system_time
    return offset

def get_synced_time(offset):
    synced_time = time.time() + offset
    return datetime.datetime.fromtimestamp(synced_time)

def predictor(symbol, sc, NN, dfs):
    atr_value = dfs[symbol]['atr'].iat[-1]
    scaled_atr = sc.transform([[atr_value]])
    prediction0 = NN.predict(scaled_atr)
    prediction = prediction0.item()
    if prediction == None or prediction == 'None':
        return 0
    else:
        return round(prediction)

#############################################################################@ Main Section @##############################################################################################

def bot():
    with app.app_context():
        enabled_symbols = Symbol.query.filter_by(enabled=True).all()
        if not enabled_symbols:
            print("No enabled symbols found.")
            return

        symbols = [s.name for s in enabled_symbols]
        digits = {s.name: s.digits for s in enabled_symbols}
    
    dfs = download_initial_data(symbols)
    ntp_time = fetch_ntp_time()
    open_signals = {symbol: ["None"] for symbol in symbols}
    generated_ids = []
    stoploss_distances = {'XAUUSD': 7.5, 'USA30': 60}  # You can also fetch from DB if stored
    lots = {'XAUUSD': 0.08, 'USA30': 0.8}  # Same here
    threshold = {'XAUUSD': 3.4, 'USA30': 28}
    time_ranges = [['12:00pm', '5:00pm'], ['7:00pm', '11:00pm'], ['8:00am', '11:00am'], ['2:00am', '5:00am']]
    already_synced = False
    sc, NN = joblib.load(r'../mlpclassifier.pkl')   
    
    if ntp_time:
        offset = calculate_offset(ntp_time)
        print(f"Time offset calculated: {offset:.6f} seconds")
    else:
        print("Warning: Could not sync with any NTP server, using system time.")
        offset = 0

    while True:
        current_time = get_synced_time(offset)
        #re_mitigation_opener(symbols, dfs, stoploss_distances, digits, long_re_mitigations, short_re_mitigations)
        if current_time.second == 2 and current_time.minute % 5 == 0:
            print(f"[DEBUG] Current Time: {current_time}") 
            update_data(symbols, dfs)
            
            for symbol in symbols:
                print(f"[DEBUG] Processing symbol: {symbol}")
                print(f"Head.\n{dfs[symbol].head(20)}")
                print(f"Tail.\n{dfs[symbol].tail(20)}")
                current_trend = check_trend(symbol, dfs)
                current_close = dfs[symbol]['close'].iat[-1]
                current_atr = dfs[symbol]['atr'].iat[-1]
                current_open = dfs[symbol]['open'].iat[-1]
                current_time1 = dfs[symbol]['time'].iat[-1]
                signal = check_open_signal(symbol, dfs, open_signals)
                space_normal = space_for_normal(symbol)
                level = check_level(symbol, dfs, current_close)
                prediction = predictor(symbol, sc, NN, dfs)
                news_status = check_risk_period(current_time1, time_ranges)
                print(f"Latest close for {symbol}: {dfs[symbol]['close'].iat[-1]}, ATR: {current_atr}")
                print(f"[DEBUG] Current Trend for {symbol}: {current_trend}, Signal: {signal}, Space: {space_normal}")

                if current_trend == "down_trend":
                    if signal == "sell":
                        if (space_normal == "open_for_normal_short") or (space_normal == "no_normal_positions"):
                            if current_atr<threshold[symbol]:
                                if news_status == 'safe':
                                    if level == "level_not_passed":
                                        if prediction == 1:
                                            risk = lots[symbol]
                                            normal_short(symbol, risk, dfs, stoploss_distances)
                                        else:
                                            risk = lots[symbol]/2
                                            normal_short(symbol, risk, dfs, stoploss_distances)
                                    
                                else:
                                    if level == "level_not_passed":
                                        if prediction == 1:
                                            risk = lots[symbol]/2
                                            normal_short(symbol, risk, dfs, stoploss_distances)
                                        else:
                                            risk = lots[symbol]/4
                                            normal_short(symbol, risk, dfs, stoploss_distances)
                                        
                        else:
                            pass
                    
                    else:
                        pass

                elif current_trend == "up_trend":
                    if signal == "buy":
                        if (space_normal == "open_for_normal_long") or (space_normal == "no_normal_positions"):
                            if current_atr<threshold[symbol]:
                                if news_status == 'safe':
                                    if level == "level_not_passed":
                                        if prediction == 1:
                                            risk = lots[symbol]
                                            normal_long(symbol, risk, dfs, stoploss_distances)
                                        else:
                                            risk = lots[symbol]/2
                                            normal_long(symbol, risk, dfs, stoploss_distances)
                                else:
                                    if level == "level_not_passed":
                                        if prediction == 1:
                                            risk = lots[symbol]/2
                                            normal_long(symbol, risk, dfs, stoploss_distances)
                                        else:
                                            risk = lots[symbol]/4
                                            normal_long(symbol, risk, dfs, stoploss_distances)
                        else:
                            pass
                        #else:
                            #pass
                    else:
                        pass
                else:
                    continue
                
        if current_time.minute == 0 and not already_synced:
            ntp_time = fetch_ntp_time()  # Function to fetch NTP time
            if ntp_time:
                offset = calculate_offset(ntp_time)  # Function to calculate the offset
                print(f"Time re-synced. New offset: {offset:.6f} seconds")
            
            # Set the flag to indicate that sync has occurred
            already_synced = True
        elif current_time.minute != 0:
            # Reset the flag when it's no longer the 0th minute
            already_synced = False

        time.sleep(1)

if __name__ == "__main__":
    main()
