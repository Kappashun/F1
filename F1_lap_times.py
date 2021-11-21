import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import seaborn as sns
import matplotlib.pyplot as plt
pd.options.mode.chained_assignment = None
from scipy.interpolate import make_interp_spline, BSpline

"""
Module to work with time in F1 races

p1 - driver on first position
p2 - driver on second position

In F1 distance between drivers measures by time

"""

# Origin database
lap_times = pd.read_csv('lap_times.csv')

# Dropping useless rows
lap_times = lap_times.drop(['milliseconds', 'driverId'], axis=1)[lap_times['raceId'] < 2]

#Table with time intervals p2 over p1 on every lap in every race
lap_intervals = lap_times[['raceId', 'lap']].drop_duplicates()
length = list(lap_intervals.index.values)


def interval(i):
    """
    Function helps to build 'interval' column in lap_intervals table

    :param i: Index of unique pair of racedId and number of lap

    :return: Time gap change (in readable string format)
             of lap time from p2 to p1
    """

    time1 = lap_times[(lap_times['raceId'] == lap_intervals.loc[i]['raceId']) &
              (lap_times['lap'] == lap_intervals.loc[i]['lap']) &
              (lap_times['position'] == 1)]['time']
    time2 = lap_times[(lap_times['raceId'] == lap_intervals.loc[i]['raceId']) &
              (lap_times['lap'] == lap_intervals.loc[i]['lap']) &
              (lap_times['position'] == 2)]['time']

    # Time format
    FMT = '%M:%S.%f'

    time1 = time1.tolist()[0] # p1 lap time
    time2 = time2.tolist()[0] # p2 lap time

    try:
        delta = datetime.strptime(max(time1, time2), FMT) - \
                datetime.strptime(min(time1, time2), FMT)

    # Occures if time1 or time2 not in FMT pattern,
    # means lap time is over an hour, exceptional case
    except ValueError:
        delta = datetime.strptime(max(time1, time2), '%H:%M:%S.%f') - \
                datetime.strptime(min(time1, time2), '%H:%M:%S.%f')

    interval = str(delta)[3:-3]
    if time1 < time2:
        interval = '+' + interval
    elif time1 > time2:
        interval = '-' + interval
    return interval


def gap(i):
    """
    Function helps to build 'gap' column in lap_intervals table

    :param i: Index of unique pair of racedId and number of lap

    :return: Time difference (in readable string format)
              of total time between p1 and p2
    """
    res = 0
    for lap in range(1, lap_intervals.loc[i]['lap'] + 1):
        res += delta_to_seconds(lap_intervals[(lap_intervals['lap'] == lap) &
                                              (lap_intervals['raceId'] == lap_intervals.loc[i]['raceId'])
                                              ]['interval'].tolist()[0])
    return seconds_to_delta(res)


def delta_to_seconds(delta: str) -> float:
    """
    :param delta: String-type time
    :return: Float-type time

    """
    if delta[0] == '+' or delta[0] == '-':
        parsed_time = delta[1:]
    else:
        parsed_time = delta
    parsed_time = parsed_time.split(':')

    # If delta time is over an hour, exceptional case
    if len(parsed_time) == 3:
        try:
            result = float(parsed_time[0])*3600 + \
                     float(parsed_time[1])*60 + \
                     float(parsed_time[2])
        except ValueError:
            result = float(parsed_time[0].split(' ')[-1])*3600 + \
                     float(parsed_time[1])*60 + \
                     float(parsed_time[2])

    else:
        result = float(parsed_time[0])*60 + float(parsed_time[1])

    if delta[0] == '-':
        result = -result
    return result


def seconds_to_delta(val: float) -> str:
    """
    :param delta: Float-type time
    :return: String-type time

    """
    # If delta time is over an hour, exceptional case
    if int(abs(val)/3600) != 0:
        hours = str(int(abs(val)/3600))
        minutes = str(int((abs(val)%3600)/60))
        seconds = "{:.3f}".format(abs(val)%60)
        res = ':'.join([hours, minutes, seconds])

    else:
        minutes = str(int(abs(val)/60))
        seconds = "{:.3f}".format(abs(val)%60)
        res = ':'.join([minutes, seconds])
    return res


# Adding columns to 'lap_intervals'
#
# Interval: read function 'interval' docstring
# Gap: read function 'gap' docstring
# Ms: gap in milliseconds
#
lap_intervals['interval'] = [interval(i) for i in length]
lap_intervals['gap'] = [gap(i) for i in length]
lap_intervals['ms'] = [int((delta_to_seconds(gap(i)))*1000) for i in length]

# Table with average gap between p1 and p2 by every lap
average_gap = pd.DataFrame({'lap' : lap_intervals['lap'].unique(),
                             'ms' : [int(lap_intervals[lap_intervals['lap'] == i+1]['ms'].mean())
                                     for i in range(lap_intervals['lap'].unique().size)]})


def Graph():
    """
    Function shows graphic of average gap (in seconds)
    between p1 and p2 by every lap

    """
    laps = list(average_gap['lap'])
    ms = list(average_gap['ms'])
    sec = [i/1000 for i in ms]

    xnew = np.linspace(1, max(laps), 1000)
    spl = make_interp_spline(laps, sec, k=3)
    power_smooth = spl(xnew)

    plt.title('Gap between 1 and 2 pos')
    plt.xlabel("Lap")
    plt.ylabel("Seconds")
    plt.grid(True)
    plt.plot(xnew, power_smooth, color='red')
    plt.show()
