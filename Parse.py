import pandas as pd
import time
import os

def ep_to_day(ep):
    '''Converts epoch time to day of the week.
    
    Args: 
        ep: epoch time

    Returns: 
        day of the week
    '''
    return time.strftime('%A', time.localtime(ep))


def iterate_single_file(filename, rho):
    '''Traverses the file given. Splits the file into distinct dataframes based on day and
    parses each day.
    
    Args: 
        filename: name of the csv data file
        rho: the weight of how far out of the money we go

    Returns:
        none 
    '''
    if 'DS_Store' in filename:
        return
    print(filename)

    test = pd.read_csv(filename, low_memory=False)
    days = test.groupby([' [QUOTE_DATE]'])

    # pass through file - find and store all of the fridays
    for day in days:
        day_frame = day[1]
        epoch = day_frame['[QUOTE_UNIXTIME]'].iloc[0]
        day_of_week = ep_to_day(epoch)
        if (day_of_week == 'Friday'):
            fridays_list.append(epoch)
            fridays_hash.add(epoch)



    # each iteration is sorted into a data set of each trading day
    for day in days:
        day_frame = day[1]
        underlying = day_frame[' [UNDERLYING_LAST]'].iloc[0]
        daily_underlying.append(underlying)

        
        epoch = day_frame['[QUOTE_UNIXTIME]'].iloc[0]
        day_of_week = ep_to_day(epoch)
        # only consider options if it is a friday - otherwise just track growth of underlying
        if (day_of_week == 'Friday'):
            #we want to handle puts and calls
            handle_last_week_puts(underlying)
            handle_last_week_calls(underlying)
            handle_puts(day_frame, 0.01, rho)
            handle_calls(day_frame, 0.01, rho)
            # account for price friction - difference in put and call option price
            if len(considered_puts) != 0 and len(considered_calls):
                friction = considered_puts[0][' [P_ASK]'] - considered_calls[0][' [P_ASK]']
                num_units = portfolio_value[0] / considered_puts[0][' [P_ASK]']

    print(portfolio_value[0])



def handle_last_week_puts(underlying):
    ''' Checks whether the puts from last week expired in the money or out of the money. 
    If they expired out of the money, do nothing. Otherwise, restructure part of the portfolio based 
    on the put price.
    
    Args:
        underlying: the underlying price of spx on the current friday
    
    Returns:
        none
    '''
    if len(considered_puts) == 0:
        return
    # put is in the money - expires with value - must restructure portfolio value
    if considered_puts[0][' [STRIKE]'] > underlying:
        num_units = portfolio_value[0] / underlying
        loss = num_units * (considered_puts[0][' [STRIKE]'] - underlying)
        portfolio_value[0] += (loss / 10)
    considered_puts.pop(0)
    


def handle_last_week_calls(underlying):
    ''' Checks whether the calls from last week expired in the money or out of the money. 
    If they expired out of the money, do nothing. Otherwise, restructure part of the portfolio based 
    on the call price.
    
    Args:
        underlying: the underlying price of spx on the current friday
    
    Returns:
        none
    '''
    if len(considered_calls) == 0:
        return
    # call is in the money - expires with value - must restructure portfolio value
    if considered_calls[0][' [STRIKE]'] < underlying:
        num_units = portfolio_value[0] / underlying
        gain = num_units * (underlying - considered_calls[0][' [STRIKE]'])
        portfolio_value[0] -= gain
    considered_calls.pop(0)
    



def handle_puts(day_frame, bid_ask_spread, rho):
    '''Finds the put that passes the liquidity threshold and is closest to our rho value while still passing the rho value.
    
    Args:
        day_frame: the column set of all of the options on the given friday
        bid_ask_spread: difference between the bid and ask on an option
        rho: the weight of how far out of the money we go
        
    Return:
        none
    '''
    for index, row in day_frame.iterrows():
        # only consider out-of-money-puts by a certain ratio
        if rho <= ((row[' [UNDERLYING_LAST]'] - row[' [STRIKE]']) / row[' [UNDERLYING_LAST]']):
            # only consider those which expire next friday
            if row[' [EXPIRE_UNIX]'] in fridays_hash and fridays_list.index(row[' [EXPIRE_UNIX]']) == fridays_list.index(row['[QUOTE_UNIXTIME]']) + 1:
                needed_volume = portfolio_value[0] / float(row[' [P_ASK]'])
                # meet the volume threshold
                if row[' [P_VOLUME]'] != ' ' and (needed_volume / 1000) <= float(row[' [P_VOLUME]']):
                    spread_rate = (float(row[' [P_ASK]']) - float(row[' [P_BID]'])) / row[' [STRIKE]']
                    # meet the spread threshold
                    
                    if spread_rate <= bid_ask_spread:
                        # find the option that is the closest to the rho
                        considered_puts.append(row)
                        if len(considered_puts) == 2:
                            rho_1 = (considered_puts[0][' [UNDERLYING_LAST]'] - considered_puts[0][' [STRIKE]']) / considered_puts[0][' [UNDERLYING_LAST]']
                            rho_2 = (considered_puts[1][' [UNDERLYING_LAST]'] - considered_puts[1][' [STRIKE]']) / considered_puts[1][' [UNDERLYING_LAST]']
                            # we choose the option that is closest to our rho value
                            if rho_1 <= rho_2:
                                considered_puts.pop(1)
                            else:
                                considered_puts.pop(0)






def handle_calls(day_frame, bid_ask_spread, rho):
    '''Finds the call that passes the liquidity threshold and is closest to our rho value while still passing the rho value.
    
    Args:
        day_frame: the column set of all of the options on the given friday
        bid_ask_spread: difference between the bid and ask on an option
        rho: the weight of how far out of the money we go
        
    Return:
        none
    '''
    for index, row in day_frame.iterrows():
        # only consider out-of-money-puts by a certain ratio
        if rho <= ((row[' [STRIKE]'] - row[' [UNDERLYING_LAST]']) / row[' [UNDERLYING_LAST]']):
            # only consider those which expire next friday
            if row[' [EXPIRE_UNIX]'] in fridays_hash and fridays_list.index(row[' [EXPIRE_UNIX]']) == fridays_list.index(row['[QUOTE_UNIXTIME]']) + 1:
                needed_volume = portfolio_value[0] / float(row[' [C_ASK]'])
                # meet the volume threshold
                if row[' [C_VOLUME]'] != ' ' and needed_volume <= float(row[' [C_VOLUME]']):
                    spread_rate = (float(row[' [C_ASK]']) - float(row[' [C_BID]'])) / row[' [STRIKE]']
                    # meet the spread threshold
                    if spread_rate <= bid_ask_spread:
                        # find the option that is the closest to the rho
                        considered_calls.append(row)
                        if len(considered_puts) == 2:
                            rho_1 = (considered_calls[0][' [UNDERLYING_LAST]'] - considered_calls[0][' [STRIKE]']) / considered_calls[0][' [UNDERLYING_LAST]']
                            rho_2 = (considered_calls[1][' [UNDERLYING_LAST]'] - considered_calls[1][' [STRIKE]']) / considered_calls[1][' [UNDERLYING_LAST]']
                            if rho_1 <= rho_2:
                                considered_calls.pop(1)
                            else:
                                considered_calls.pop(0)
    
def calculate_daily_growth():
    '''Calculates the daily growth of the strategy.
    
    Args:
        none
        
    Return:
        none
    '''
    for i in range (len(daily_underlying)):
        if (i != 0):
            daily_growth.append(daily_underlying[i] / daily_underlying[i - 1])
    return daily_growth

def calculate_portfolio_value():
    '''Calculates the final portfolio value over the alotted time.
    
    Args:
        none
    
    Return:
        none
        
    '''
    for i in range(len(daily_growth)):
        portfolio_value[0] *= daily_growth[i]
    

def iterate_over_files(directory, rho):
    '''Traverses all of the files in the directory.
    
    Args:
        directory: name of the directory with the csv data files
        rho: the weight of how far out of the money we go
        
    Return:
        none
    '''
    file_list = sorted(os.listdir(directory))
    for filename in file_list:
        if os.path.isdir(filename):
            iterate_over_files(filename)
        else :
            iterate_single_file(os.path.join(directory, filename), rho)
            




if __name__ == '__main__':
    for i in range(1, 10):
        rho = i / 100
        rho = 0.01
        daily_growth =[]
        daily_growth.append(1)
        daily_underlying = []

        portfolio_value = []
        portfolio_value.append(1_000_000)

        considered_puts = []
        considered_calls = []

        fridays_list = []
        fridays_hash = set()
        iterate_over_files("OptionsData", rho)
        calculate_daily_growth()
        calculate_portfolio_value()
        print(rho)
        print(portfolio_value[0])
        print()
