import tushare as ts
import baostock as bs
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
from dateutil import parser  # 解析器：把字符串解析为datetime格式

if __name__ == '__main__':
    time_now = int(time.time())
    bar_5m_df = pd.read_csv("/Users/superblackwoo/Desktop/Master1/Project1/data/history_A_stock_k_data.csv")
    bar_5m_df.head()
    bar_5m_df.tail()
    # 利用历史数据来模拟股价波动
    # 读取历史的bar的low high close来模拟价格的波动（生成ticks）  bar --> ticks --> bar_generator()
    # ticks = [(datetime, 36.89), (datetime, 36.90).....,(,)]
    # history_A_stock_k_data.csv --> history_A_stock_k_data_ticks.csv
    ticks = []
    for index, row in bar_5m_df.iterrows():
        if row['open'] < 30:
            step = 0.01
        elif row['open'] < 60:
            step = 0.03
        elif row['open'] < 90:
            step = 0.05
        else:
            step = 0.1
        arr = np.arange(row['open'], row['high'], step)  # 在bar历史数据中生成时间序列数据
        arr = np.append(arr, row['high'])
        arr = np.append(arr, np.arange(row['open'] - 0.01, row['low'], -step))
        arr = np.append(arr, row['low'])
        arr = np.append(arr, row['close'])

        i = 0
        for item in arr:
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
            ticks.append(((dt + timedelta(seconds=0.1) * i), item))
            i += 1
    ticks_df = pd.DataFrame(ticks, columns=['datetime', 'price'])
    ticks_df.to_csv("/Users/superblackwoo/Desktop/Master1/Project1/data/history_A_stock_k_data_ticks.csv", index=0)
    print('aha')
