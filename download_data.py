# http://baostock.com/baostock/index.php/A%E8%82%A1K%E7%BA%BF%E6%95%B0%E6%8D%AE
import tushare as ts
import baostock as bs
import pandas as pd

if __name__ == '__main__':
    # ts.set_token('7bddc6eff016377e5a91af483464002d26eed5c58a4514e9849d74d1')
    # df = ts.pro_bar(ts_code='600036', start_date='2021-1-2 9:00', end_date='2021-11-5 16:00', freq='5min')

    print(ts.__version__)
    print('PyCharm')
    #### 登陆系统 ####
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)

    #### 获取沪深A股历史K线数据 ####
    # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。“分钟线”不包含指数。
    # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
    # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
    rs = bs.query_history_k_data_plus("sz.300888",
                                      "date,time,code,open,high,low,close,volume,amount,adjustflag",
                                      start_date='2018-01-02', end_date='2021-11-05',
                                      frequency="5", adjustflag="3")
    print('query_history_k_data_plus respond error_code:' + rs.error_code)
    print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)

    #### 打印结果集 ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)

    #### 结果集输出到csv文件 ####
    result.to_csv("/Users/superblackwoo/Desktop/Master1/Project1/data/history_A_stock_k_data_300888.csv", index=False)
    print(result)

    #### 登出系统 ####
    bs.logout()

    df = pd.read_csv("/Users/superblackwoo/Desktop/Master1/Project1/data/history_A_stock_k_data.csv")
