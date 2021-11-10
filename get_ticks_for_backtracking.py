import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
from dateutil import parser  # 解析器：把字符串解析为datetime格式
import os

bar_path = '/Users/superblackwoo/Desktop/Master1/Project1/data/history_A_stock_k_data.csv'
ticks_path = '/Users/superblackwoo/Desktop/Master1/Project1/data/history_A_stock_k_data_ticks.csv'

if __name__ == '__main__':
    # if os.path.exists(ticks_path):
    #     ticks = pd.read_csv(ticks_path, parse_dates=['datetime'], index_col=['datetime'])
    #     # ticks_df = pd.read_csv(ticks_path)
    #     tick_list = []
    #     for index, row in ticks.iterrows():
    #         tick_list.append((index, row[0]))
    #     ticks = np.array(tick_list)
    #
    #     print('wuhu')
    # else:
    #     bar_5m_df = pd.read_csv(bar_path)
    #     bar_5m_df.head()
    #     bar_5m_df.tail()
    #     # 利用历史数据来模拟股价波动
    #     # 读取历史的bar的low high close来模拟价格的波动（生成ticks）  bar --> ticks --> bar_generator()
    #     # ticks = [(datetime, 36.89), (datetime, 36.90).....,(,)]
    #     # history_A_stock_k_data.csv --> history_A_stock_k_data_ticks.csv
    #     ticks = []
    #     for index, row in bar_5m_df.iterrows():
    #         if row['open'] < 30:
    #             step = 0.01
    #         elif row['open'] < 60:
    #             step = 0.03
    #         elif row['open'] < 90:
    #             step = 0.05
    #         else:
    #             step = 0.1
    #         arr = np.arange(row['open'], row['high'], step)  # 在bar历史数据中生成时间序列数据
    #         arr = np.append(arr, row['high'])
    #         arr = np.append(arr, np.arange(row['open'] - 0.01, row['low'], -step))
    #         arr = np.append(arr, row['low'])
    #         arr = np.append(arr, row['close'])
    #
    #         i = 0
    #         for item in arr:
    #             # 开始解析数据的时间
    #             row_time = row['time']
    #             string_time = str(row_time)
    #             year = row_time // int(1e13)
    #             month = row_time // int(1e11) % 100
    #             day = row_time // int(1e9) % 100
    #             hour = row_time // int(1e7) % 100
    #             min = row_time // int(1e5) % 100
    #             second = row_time // int(1e3) % 100
    #             dt = datetime(year, month, day, hour, min, second) - timedelta(minutes=5)
    #             # print(dt)
    #             ticks.append(((dt + timedelta(seconds=0.1) * i), item))
    #             i += 1
    #     ticks_df = pd.DataFrame(ticks, columns=['datetime', 'price'])
    #     ticks_df.to_csv("/Users/superblackwoo/Desktop/Master1/Project1/data/history_A_stock_k_data_ticks.csv", index=0)
    #     # return ticks_df

    bar5_df = pd.read_csv(bar_path)
    # bar5_df.insert(0, 'datetime', 0)
    i = 0
    for index, row in bar5_df.iterrows():
        # 开始解析数据的时间
        row_time = row['time']
        string_time = str(row_time)
        year = row_time // int(1e13)
        month = row_time // int(1e11) % 100
        day = row_time // int(1e9) % 100
        hour = row_time // int(1e7) % 100
        min = row_time // int(1e5) % 100
        second = row_time // int(1e3) % 100
        dt = datetime(year, month, day, hour, min, second) - timedelta(minutes=5)
        # print(dt)
        bar5_df.loc[index, 'datetime'] = dt
        i += 1

    # 删除两列无关数据
    bar5_df = bar5_df.drop(['date', 'code', 'adjustflag', 'time'], axis=1)
    # 重新排列数据
    cols = list(bar5_df)
    cols.insert(0, cols.pop(cols.index('datetime')))
    bar5_df = bar5_df[['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount']]
    bar5_df.to_csv("/Users/superblackwoo/Desktop/Master1/Project1/data/history_A_stock_k_data_bar5.csv",
                   index=0)
    print('aha')
