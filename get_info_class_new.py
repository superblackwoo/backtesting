# http://hq.sinajs.cn/?format=text&list=sh600519
import requests
from time import sleep
from datetime import datetime, time, timedelta
from dateutil import parser  # 解析器：把字符串解析为datetime格式
import pandas as pd
import os
import numpy as np
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.pyplot as plt
from matplotlib.dates import date2num

bar_path = '/Users/superblackwoo/Desktop/Master1/Project1/data/history_A_stock_k_data.csv'
ticks_path = '/Users/superblackwoo/Desktop/Master1/Project1/data/history_A_stock_k_data_ticks.csv'


# 300888
# bar_path = '/Users/superblackwoo/Desktop/Master1/Project1/data/history_A_stock_k_data_300888.csv'
# ticks_path = '/Users/superblackwoo/Desktop/Master1/Project1/data/history_A_stock_k_data_ticks_300888.csv'
#

class AstockTrading(object):
    def __init__(self, strategy_name):
        # attributes
        self._strategy_name = strategy_name
        self._Open = []
        self._High = []
        self._Low = []
        self._Close = []
        self._Dt = []
        self._Volume = []
        self._tick = None  # or tuple
        self._last_bar_start_minute = None
        self._isNewBar = False
        self._ma20 = None
        self._current_orders = {  # 用来记录订单（仓位）信息
            # 'order1': {
            #     'open_price': 1,
            #     'open_datetime': '2021-11-06 9:50',
            #     'comment': {}
            # }
        }
        self._history_orders = {}
        self._order_number = 0
        self._init = False  # for backtesting

    def getTick(self):
        # A股的开盘时间是9：15  9：15-9：25为集合竞价 -》 开盘价：9：25
        # 9：25 —— 9：30 不交易
        page = requests.get("http://hq.sinajs.cn/?format=text&list=sh600519")
        stock_info = page.text
        mt_info = stock_info.split(",")

        last = float(mt_info[1])  # 最成交价
        trade_datetime = mt_info[30] + ' ' + mt_info[31]
        # dt = parser.parse(trade_datetime)  # 解析器：把字符串解析为datetime格式
        # trade_datetime = dt.time()  # 只取时间

        self._tick = (trade_datetime, last)  # 容器打包数据
        temp_tick = self._tick
        return temp_tick

    def get_history_from_local_machine(self):
        # 从硬盘或者服务器上获取的往期数据
        self._Open = []
        self._High = []
        self._Low = []
        self._Close = []
        self._Dt = []
        pass

    def bar_generator(self):
        """
            记录一个k线图中新的bar, 更新k线信息
        :param tick: tick[0]:datetime
                    tick[1]:price
                    tick用于更新Open, High, Low, Close这些数据
        :return:
        """
        # last_bar_start_minute = None  # k线中每一个bar是5分钟一个（这个可以指定）
        if self._tick[0].minute % 5 == 0 and self._tick[0].minute != self._last_bar_start_minute:
            # 记录一个新的bar,信息全是新的，所以统一赋值当前价格
            self._last_bar_start_minute = self._tick[0].minute
            self._Open.insert(0, self._tick[1])
            self._High.insert(0, self._tick[1])
            self._Low.insert(0, self._tick[1])
            self._Close.insert(0, self._tick[1])
            self._Dt.insert(0, self._tick[0])
            self._isNewBar = True
        else:
            # 更新目前这个bar下的low，high。。。  一个bar时间内的价格浮动
            self._High[0] = max(self._High[0], self._tick[1])
            self._Low[0] = max(self._High[0], self._tick[1])
            self._Close[0] = self._tick[1]
            self._Dt[0] = self._tick[0]
            self._isNewBar = False

    def buy(self, price, volume):
        # creat an order
        self._order_number += 1
        key = "order" + str(self._order_number)
        self._current_orders[key] = {
            "open_datetime": self._Dt[0],
            "open_price": price,
            "volume": volume}

    def sell(self, key, price):
        self._current_orders[key]['close_price'] = price
        self._current_orders[key]['close_datetime'] = self._Dt[0]
        # 在字典中记录这两个属性
        # 计算利润
        self._current_orders[key]['profit'] = (price - self._current_orders[key]['open_price']) \
                                              * self._current_orders[key]['volume'] \
                                              - price * self._current_orders[key]['volume'] * 1 / 1000 \
                                              - ((price + self._current_orders[key]['open_price']) \
                                                 * self._current_orders[key]['volume']) * 3 / 10000
        # 将订单从当前仓位订单移动到历史订单中
        self._history_orders[key] = self._current_orders.pop(key)

    def strategy_naive(self):
        """
            交易策略: last < MA20 * 0.95 buy.   last > MA20 * 1.08 sell.
            基于 5min k线 的 bar
            假设已经拥有历史数据： tick：(datetime, price)

            1、update 5 minuts ma20, not daily data
            2、比较 ma 和 last 价格然后决定买入还是卖出
        :param tick:
        :return:
        """
        if self._isNewBar:
            sum_ = 0
            for item in self._Close[1:21]:
                sum_ += item
            self._ma20 = sum_ / 20
        # 计算MA20（前面20个bar的平均价格）

        if len(self._current_orders) == 0:
            # 如果还有仓位
            if self._Close[0] < self._ma20 * 0.98:
                # 100000/44.28 = 2258股 （只能100股为单位买入）
                # 2258 --> 2200
                volume = int(100000 / self._Close[0] / 100) * 100  # 2200 share
                self.buy(self._Close[0] + 0.01, volume)

        elif 1 == len(self._current_orders):
            # 没有仓位了
            if self._Close[0] > self._ma20 * 1.02:
                # 获取要平仓的那个order的key
                key = list(self._current_orders.keys())[0]
                # self.sell(key, self._Close[0] - 0.01)
                if self._Dt[0].date() != self._current_orders[key]['open_datetime'].date():  # T+0限制
                    self.sell(key, self._Close[0] - 0.01)

                else:
                    print("limited by T+0!!!")
                    print('Open datetime is ', self._current_orders[key]['open_datetime'].date(),
                          ', Close datetime is ', self._Dt[0].date(), '\n')
                    # print很多是因为这里有很多卖出的信号
                    pass

        else:
            raise ValueError("we have more than 1 current orders!!!")

    def bar_generator_for_back(self, tick):
        """
            记录一个k线图中新的bar, 更新k线信息
        :param tick: tick[0]:datetime
                    tick[1]:[Open, High, Low, Close]
                    tick用于更新Open, High, Low, Close这些数据
        :return:
        """
        # last_bar_start_minute = None  # k线中每一个bar是5分钟一个（这个可以指定）
        if tick[0].minute % 5 == 0 and tick[0].minute != self._last_bar_start_minute:
            # 记录一个新的bar,信息全是新的，所以统一赋值当前价格
            self._last_bar_start_minute = tick[0].minute
            self._Open.insert(0, tick[1])
            self._High.insert(0, tick[1])
            self._Low.insert(0, tick[1])
            self._Close.insert(0, tick[1])
            self._Dt.insert(0, tick[0])
            self._isNewBar = True
        else:
            # 更新目前这个bar下的low，high。。。  一个bar时间内的价格浮动
            self._High[0] = max(self._High[0], tick[1])
            self._Low[0] = max(self._High[0], tick[1])
            self._Close[0] = tick[1]
            self._Dt[0] = tick[0]
            self._isNewBar = False

    def run_backtesting(self, ticks):
        for tick in ticks:
            self.bar_generator_for_back(tick)

            if self._init:
                self.strategy_naive()
            else:
                if len(self._Open) > 100:
                    self._init = True
                    self.strategy_naive()


def get_ticks_for_back():
    if os.path.exists(ticks_path):
        ticks = pd.read_csv(ticks_path, parse_dates=['datetime'], index_col=['datetime'])
        # ticks_df = pd.read_csv(ticks_path)
        tick_list = []
        for index, row in ticks.iterrows():
            tick_list.append((index, row[0]))
        ticks = np.array(tick_list)

    else:
        bar_5m_df = pd.read_csv(bar_path)
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
        ticks = np.array(ticks)
        ticks_df = pd.DataFrame(ticks, columns=['datetime', 'price'])
        ticks_df.to_csv("/Users/superblackwoo/Desktop/Master1/Project1/data/history_A_stock_k_data_ticks.csv",
                        index=0)
    return ticks


if __name__ == '__main__':
    # Dt, Open, High, Low, Close, Volume = get_history_from_local_machine()
    # trade_time = time(9, 30)  # 表示9：30
    # while time(9) < trade_time < time(16):
    #     last_tick = getTick()
    #     Dt, Open, High, Low, Close, Volume = bar_generator(last_tick, Dt, Open, High, Low, Close, Volume)
    #     # 更新数据
    #     strategy_naive(Dt, Open, High, Low, Close, Volume)
    #     # trade_time = parser.parse(last_tick[1]).time()  # 解析器：把字符串解析为datetime格式. 只取时间
    #     # print(last_tick)
    #     sleep(1)
    # # TODO: 用类重构。避免function中的数据被内存释放，以及参数的频繁传递。 类：attribute+method 不会轻易被覆盖
    '''
        trade_time = time(9, 30)  # 表示9：30
        ast = AstockTrading('300888')  # 类的实例化
        ast.get_history_from_local_machine()
    
        while time(9) < trade_time < time(16):
            last_tick = ast.getTick()
            ast.bar_generator(last_tick)  # 更新k线的数据
            ast.strategy_naive()
            trade_time = last_tick[1]  # TODO: ??????
        print("done")
    
        ma = AstockTrading("ma")  # 量化策略创建对象
        ma.get_history_from_local_machine()  # 硬盘载入数据
    
        while time(9, 26) < datetime.now().time() < time(11, 32) or time(13) < datetime.now().time() < time(15, 2):
            ma.getTick()
            ma.bar_generator()
            ma.strategy_naive()
    
        # backtesting
        # history data
        # 15 minute bar -> tick data
        # pands
        df = pd.read_csv("/Users/superblackwoo/Desktop/Master1/Project1/data/history_A_stock_k_data.csv")
    '''
    ticks = get_ticks_for_back()
    ast = AstockTrading('ma')
    ast.run_backtesting(ticks)

    profit_orders = 0
    lose_orders = 0

    # 计算盈亏
    orders = ast._history_orders
    all_profit = 0
    for key in orders.keys():
        if orders[key]['profit'] >= 0:
            profit_orders += 1
        else:
            lose_orders += 1
        all_profit += orders[key]['profit']

    # 绘制盈亏直方图
    orders_df = pd.DataFrame(orders).T  # 转置
    orders_df.loc[:, 'profit'].plot.bar()

    # bar图绘制出来，在上面观察买卖点
    fig, ax = plt.subplots()
    bar5 = pd.read_csv("/Users/superblackwoo/Desktop/Master1/Project1/data/history_A_stock_k_data_bar5.csv",
                       parse_dates=['datetime'])
    bar5.loc[:, 'datetime'] = [date2num(x) for x in bar5.loc[:, 'datetime']]

    fig, ax = plt.subplots()
    candlestick_ohlc(
        ax,
        bar5.values,
        width=0.2,
        colorup='r',
        colordown='green',
        alpha=1.0
    )

    # put orders in candle sticks
    for index, row in orders_df.iterrows():
        ax.plot([date2num(row['open_datetime']), date2num(row['close_datetime'])],
                [row['open_price'], row['close_price']],
                c='darkblue',
                marker='o')
    print('done')
