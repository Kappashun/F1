import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

pd.options.mode.chained_assignment = None

"""
Module to work with time in F1 races

p1 - driver on first position
p2 - driver on second position

In F1 distance between drivers measures by time

"""

# Origin database
lap_times = pd.read_csv('databases\lap_times.csv')

# Dropping useless rows
lap_times = lap_times.drop(['milliseconds', 'driverId'], axis=1)[:20]


def delta_to_ms(delta: str):
    """
    :param delta: String-type time
    :return: Int-type time

    """
    if delta == '--:--':
        return 0

    if delta[0] == '+' or delta[0] == '-':
        parsed_time = delta[1:]
    else:
        parsed_time = delta
    parsed_time = parsed_time.split(':')

    # If delta time is over an hour, exceptional case
    if len(parsed_time) == 3:
        try:
            result = float(parsed_time[0]) * 3600 + \
                     float(parsed_time[1]) * 60 + \
                     float(parsed_time[2])
        except ValueError:
            result = float(parsed_time[0].split(' ')[-1]) * 3600 + \
                     float(parsed_time[1]) * 60 + \
                     float(parsed_time[2])
    elif len(parsed_time) == 1:
        result = float(parsed_time[0])
    else:
        result = float(parsed_time[0]) * 60 + float(parsed_time[1])

    if delta[0] == '-':
        result = -result

    return int(result*1000)


def ms_to_delta(val) -> str:
    """
    :param delta: Int-type time
    :return: String-type time

    """
    if val == None:
        return '--:--'

    val = float(val)/1000
    # If delta time is over an hour, exceptional case
    if int(abs(val) / 3600) != 0:
        hours = str(int(abs(val) / 3600))
        minutes = str(int((abs(val) % 3600) / 60))
        seconds = "{:.3f}".format(abs(val) % 60)
        res = ':'.join([hours, minutes, seconds])

    else:
        minutes = str(int(abs(val) / 60))
        seconds = "{:.3f}".format(abs(val) % 60)
        res = ':'.join([minutes, seconds])
    return res


def interval(id):
    """
    Function helps to build 'interval' column in table

    :param i: Index of unique row in table

    :return: Time gap change (in readable string format)
             of lap time from driver to driver ahead
    """
    pos = lap_times.loc[id]['position']
    if pos == 1:
        return '--:--'

    race_id = lap_times.loc[id]['raceId']
    lap = lap_times.loc[id]['lap']

    time1 = lap_times[(lap_times['raceId'] == race_id) &
                      (lap_times['lap'] == lap) &
                      (lap_times['position'] == pos - 1)]['time']
    time2 = lap_times[(lap_times['raceId'] == race_id) &
                      (lap_times['lap'] == lap) &
                      (lap_times['position'] == pos)]['time']

    time1 = delta_to_ms(time1.tolist()[0])  # p1 lap time
    time2 = delta_to_ms(time2.tolist()[0])  # p2 lap time

    interval = ms_to_delta(abs(time1 - time2))

    if time1 < time2:
        interval = '+' + interval
    elif time1 > time2:
        interval = '-' + interval
    return interval


# Intervals
lap_times['interval'] = [interval(i) for i in lap_times.index.values]

# Intervals in milliseconds
lap_times['ms'] = lap_times['interval'].map(delta_to_ms)


def Graph():
    """
    Function shows graphic of average gap (in seconds)
    between p1 and p2 by every lap

    """

    # Average interval per every lap, not counting exceptional cases
    aver_int = lap_times[lap_times['position'] == 2][['lap', 'ms']]
    aver_int = aver_int.drop(aver_int[abs(aver_int['ms']) > 200000].index)
    aver_int = aver_int.groupby(['lap']).mean()

    laps = aver_int.index
    gaps = []
    res = 0
    for lap, ms in aver_int.iterrows():
        res += ms
        gaps.append(res.tolist()[0])

    sec = [i / 1000 for i in gaps]
    del aver_int

    plt.figure(figsize=(10, 6))
    plt.title('Gap between 1 and 2 pos')
    plt.xlabel("Lap")
    plt.ylabel("Seconds")
    plt.grid(True)
    plt.axvline(60, color='blue', linestyle='--')
    plt.text(60, 3, 'Average number of laps', rotation=-90, verticalalignment='bottom', fontsize=10)
    plt.plot(laps, sec, color='red')
    plt.show()
