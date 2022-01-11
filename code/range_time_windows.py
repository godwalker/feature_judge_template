import os

from feature_judge import *
from util import *


if __name__ == "__main__":
    timeseries_name = "QF_01_1RCP604MP_AVALUE"
    data_source = "iotdb"

    config_path = "../config/" + timeseries_name
    image_path = "../images/" + timeseries_name+"/"
    if not os.path.exists(image_path):
        os.mkdir(image_path)
    timeseries_path = "../data/" + timeseries_name + ".csv"

    trend_config, threshold_config, timeseries_config, resample_frequency = read_config(config_path)

    # 遍历整个时间段，从而获取时间序列的误报率
    one_day = 60*60*24
    slide_step = 10
    tot = 0
    drop = 0
    if data_source == "csv":
        history_start_time, history_end_time = get_start_end_time(timeseries_path, data_source)
    elif data_source == "iotdb":
        history_start_time, history_end_time = get_start_end_time(timeseries_name, data_source)
    history_start_time = history_start_time + one_day*timeseries_config["trend_range_day"]*1000

    # 遍历窗口的终止时间
    for end_time in range(int(history_start_time), int(history_end_time), one_day*slide_step*1000):
        end_time /= 1000
        timeseries_config["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))
        timeseries_config["start_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time-one_day*timeseries_config["trend_range_day"]))
        if data_source == "csv":
            timeseries = read_timeseries(timeseries_path, timeseries_config, str(resample_frequency) + "min")
        elif data_source == "iotdb":
            timeseries_sql = "select re_sample(" + timeseries_name + ", 'every'='720.0m', 'interp'='linear')" + " from root.CNNP." + timeseries_name[
                                                                                                                                :2] + "." + "ID"
            timeseries_sql = timeseries_sql + " where time < " + timeseries_config["end_time"] + " and time > " + \
                             timeseries_config["start_time"] + ";"
            timeseries = read_timeseries_iotdb(timeseries_sql, resample_frequency)
        Dplot = 'yes'
        # Dplot = 'no'
        s_tf = trend_features(timeseries, timeseries_name, trend_config, image_path, Dplot, timeseries_config["start_time"])
        # print(s_tf)
        # 满足某个特定的征兆，进行特殊的显示
        if (s_tf[4]):
            drop += 1
            print('\033[0;35;46m {}, {} \033[0m'.format(timeseries_config["start_time"], timeseries_config["end_time"]))

        tot += 1

    print("总测试窗口的大小：{}".format(tot))
    print("满足单调缓慢下降次数：{}".format(drop))
