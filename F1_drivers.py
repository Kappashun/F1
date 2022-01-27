import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

pd.options.mode.chained_assignment = None
pd.set_option('display.max_rows', None)
pd.options.display.float_format = '{:.0f}'.format

"""

Module to analyse drivers results in F1 races

"""

# Databases
drivers = pd.read_csv('databases\drivers.csv')
races = pd.read_csv('databases\\races.csv')
standings = pd.read_csv('databases\driver_standings.csv')
results = pd.read_csv('databases\\results.csv')


def create_table(drivers=drivers, races=races, standings=standings, results=results, purpose='work'):
    """
    Function that builds main table of this module

    :param drivers: drivers dataset
    :param races: races dataset
    :param standings: standings dataset
    :param results: results dataset
    :param purpose: defining if table is for reading or for further working
    :return: table
    """

    # Filtering datasets before merging
    drivers['driver'] = drivers['forename'] + ' ' + drivers['surname']
    drivers.drop(columns=['driverRef', 'dob', 'nationality',
                          'url', 'forename', 'surname'], inplace=True)

    races.drop(columns=['date', 'time', 'url'], inplace=True)
    races.rename(columns={'name' : 'GP'}, inplace=True)
    races['GP'] = races.apply(lambda row: row['GP'].replace(' Grand Prix', ''), axis=1)

    standings.drop(columns=['positionText', 'driverStandingsId'], inplace=True)

    results.rename(columns={'positionOrder' : 'finish'}, inplace=True)
    results = results[['resultId', 'raceId', 'driverId',
                       'grid', 'finish', 'time', 'fastestLapTime']]

    # Merging datasets
    new_df = races.merge(right=standings, on='raceId', how='inner')
    new_df = new_df.merge(right=drivers, on='driverId', how='inner')
    new_df = new_df.merge(right=results, on=['raceId', 'driverId'], how='inner')

    # Swapping columns for better readability
    swap_col = ['driverId', 'circuitId', 'raceId', 'resultId', 'year', 'round',
                'GP', 'number', 'code', 'driver', 'grid', 'finish', 'time',
                'fastestLapTime', 'wins', 'points', 'position']
    new_df = new_df.reindex(columns=swap_col)

    # Defining purpose
    if purpose == 'work':
        new_df.sort_values(by=['year', 'round', 'finish'], inplace=True)
        return new_df

    if purpose == 'read':
        new_df.drop(columns=['driverId', 'circuitId', 'resultId',
                             'raceId', 'round'], inplace=True)
        new_df.set_index(['year', 'GP', 'finish'], inplace=True)
        new_df.sort_index(inplace=True)
        return new_df



def IsThatGlock():
    """
    Comic function, referencing to first Hamilton title win
    and Timo Glock last lap incident

    :return: IS THAT GLOCK GOING SLOWLY??
    """
    df = create_table()
    df1 = df[df['year'] == 2008][df['GP'] == 'Brazilian']
    return df1[df1['code'].isin(['HAM', 'MAS', 'GLO'])].iloc[:, 4:]
