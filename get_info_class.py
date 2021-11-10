# http://hq.sinajs.cn/?format=text&list=sh600519
import requests
from time import sleep
from datetime import datetime, time, timedelta
from dateutil import parser  # 解析器：把字符串解析为datetime格式


def getTick():
    page = requests.get("http://hq.sinajs.cn/?format=text&list=sh600519")
    stock_info = page.text
    mt_info = stock_info.split(",")

    last = float(mt_info[1])  # 最成交价
    trade_datetime = mt_info[30] + ' ' + mt_info[31]
    # dt = parser.parse(trade_datetime)  # 解析器：把字符串解析为datetime格式
    # trade_datetime = dt.time()  # 只取时间

    tick = (trade_datetime, last)  # 容器打包数据
    return tick


class AstockTrading(object):
    def __init__(self, strategy_name):  # 构造函数
        self._strategy_name = strategy_name
        self._Dt = None
        self._Open = None
        self._High = None
        self._Low = None
        self._Close = None
        self._Volume = None
        self._tick = None
        self._last_bar_start_minute = None
        self._isNewBar = None

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

        self._tick = (last, trade_datetime)  # 容器打包数据

    def get_history_from_local_machine(self):
        self._Open = []
        self._High = []
        self._Low = []
        self._Close = []
        self._Dt = []

        # 初始化之后就要读取数据了

    def bar_generator(self, tick):
        """
                记录一个k线图中新的bar, 更新k线信息
            :param tick: tick[0]:datetime
                        tick[1]:[Open, High, Low, Close]
                        tick用于更新Open, High, Low, Close这些数据
            :return:
            """
        # last_bar_start_minute = None  # k线中每一个bar是5分钟一个（这个可以指定）

        if self._tick[0].minute % 5 == 0 and self._tick[0].minute != self._last_bar_start_minute:
            # 记录一个新的bar
            self._last_bar_start_minute = self._tick[0].minute
            self._Open.insert(0, self._tick[1])
            self._High.insert(0, self._tick[1])
            self._Low.insert(0, self._tick[1])
            self._Close.insert(0, self._tick[1])
            self._Dt.insert(0, self._tick[1])
            self._isNewBar = True
        else:
            # 更新目前这个bar下的low，high。。。
            self._High[0] = max(self._High[0], self._tick[1])
            self._Low[0] = max(self._High[0], self._tick[1])
            self._Close[0] = self._tick[1]
            self._Dt[0] = self._tick[0]
            self._isNewBar = False
            # return Dt, Open, High, Low, Close, Volume 面向对象就直接不用return了

    def strategy_naive(self):
        """
            交易策略: last < MA20 * 0.95 buy.   last > MA20 * 1.08 sell.
            基于 5min k线 的 bar
            假设已经拥有历史数据： tick：(datetime, [Open, Hight, Low, Close, Dt])

            1、update 5 minuts ma20, not daily data
            2、比较 ma 和 last 价格然后决定买入还是卖出
        :param tick:
        :return:
        """

        sum_ = 0
        for item in self._Close[1:21]:
            sum_ += item
        ma20 = sum_ / 20
        # 计算MA20（前面20个bar的平均价格）

        if self._Close[0] < ma20 * 0.95:
            self.buy()
        elif self._Close[0] > ma20 * 1.08:
            self.sell()
        else:
            # 策略边界里面，啥子都不做
            pass

    def buy(self):
        pass

    def sell(self):
        pass


def get_history_from_local_machine():
    return Dt_, Open_, High_, Low_, Close_, Volume_


def bar_generator(tick, Dt, Open, High, Low, Close, Volume):
    """
        记录一个k线图中新的bar, 更新k线信息
    :param tick: tick[0]:datetime
                tick[1]:[Open, High, Low, Close]
                tick用于更新Open, High, Low, Close这些数据
    :return:
    """
    last_bar_start_minute = None  # k线中每一个bar是5分钟一个（这个可以指定）
    if tick[0].minute % 5 == 0 and tick[0].minute != last_bar_start_minute:
        # 记录一个新的bar
        last_bar_start_minute = tick[0].minute
        Open.insert(0, tick[1])
        High.insert(0, tick[1])
        Low.insert(0, tick[1])
        Close.insert(0, tick[1])
        Dt.insert(0, tick[1])
    else:
        # 更新目前这个bar下的low，high。。。
        High[0] = max(High[0], tick[1])
        Low[0] = max(High[0], tick[1])
        Close[0] = tick[1]
        Dt[0] = tick[0]
    return Dt, Open, High, Low, Close, Volume


def buy():
    pass


def sell():
    pass


# 怎样导入历史数据？
def strategy_naive(Dt, Open, High, Low, Close, Volume):
    """
        交易策略: last < MA20 * 0.95 buy.   last > MA20 * 1.08 sell.
        基于 5min k线 的 bar
        假设已经拥有历史数据： tick：(datetime, [Open, Hight, Low, Close, Dt])

        1、update 5 minuts ma20, not daily data
        2、比较 ma 和 last 价格然后决定买入还是卖出
    :param tick:
    :return:
    """

    sum_ = 0
    for item in Close[1:21]:
        sum_ += item
    ma20 = sum_ / 20
    # 计算MA20（前面20个bar的平均价格）

    if Close[0] < ma20 * 0.95:
        buy()
    elif Close[0] > ma20 * 1.08:
        sell()
    else:
        # 策略边界里面，啥子都不做
        pass


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

    trade_time = time(9, 30)  # 表示9：30
    ast = AstockTrading('300888')  # 类的实例化
    ast.get_history_from_local_machine()

    while time(9) < trade_time < time(16):
        last_tick = getTick()
        ast.bar_generator(last_tick)  # 更新k线的数据
        ast.strategy_naive()
        trade_time = last_tick[1]  # TODO: ??????
    print("done")
