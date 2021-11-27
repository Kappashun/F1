import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

pd.options.mode.chained_assignment = None
pd.set_option('display.max_rows', None)
"""

Module to analyse constructor teams results in F1

"""

# Origin databases
constructors = pd.read_csv('databases\constructors.csv')
results = pd.read_csv('databases\constructor_results.csv')
standings = pd.read_csv('databases\constructor_standings.csv')

# Dropping useless rows
constructors = constructors.drop('url', axis=1)
results = results.drop('status', axis=1)
standings = standings.drop('positionText', axis=1)

# Table with sum of all points of every team
total_points = results[['constructorId', 'points']].groupby(['constructorId']).sum()


def ShowPoints():
    """
    Function builds bar graph of points of first 20 teams with
    the most points, also showing from which country they are

    """
    # Making Dataframe, adding names of teams to points table
    graph_df = total_points.merge(constructors, on='constructorId', how='inner')

    # Getting needed rows for graph
    graph_df = graph_df.sort_values('points', ascending=False)[:20]

    # Values that we are displaying
    points = graph_df['points']
    name = graph_df['name']

    # Dict of colors by countries
    colors = pd.DataFrame({'country': ['British', 'French', 'German', 'Italian', 'Other'],
                           'color' : ['blue', 'red', 'purple', 'green', 'grey']
                           })

    # Adding colors to table
    graph_df = graph_df.merge(colors, left_on='nationality', right_on='country', how='left').drop('country', axis=1)
    graph_df['color'] = graph_df['color'].fillna('grey')
    color_list = graph_df['color']

    # 2 variables for legend
    handles = [plt.Rectangle((0,0),1,1, color=col) for col in colors['color'].tolist()]
    labels = colors['country'].tolist()

    # Not needed anymore
    del graph_df

    # Creating table
    plt.figure(figsize=(25, 16))
    plt.title('Constructor points', fontsize=60, color='blanchedalmond')
    plt.bar(name, points, width=0.8, align='edge', color=color_list, edgecolor='black', linewidth=1.5, zorder=3)
    # Grid
    plt.grid(color='black', zorder=0, axis='y', lw=0.5)
    # Labels
    plt.xlabel('Team', fontsize=50, color='pink')
    plt.ylabel('Points', fontsize=50, color='pink')
    # Ticks
    plt.xticks(rotation=65, fontsize=20, color='white')
    plt.yticks(fontsize=18, color='white')
    # Background color
    ax = plt.gca()
    ax.set_facecolor('#CCECE5')
    # Legend
    plt.legend(handles, labels, fontsize=25, facecolor='white', loc='upper right', framealpha=1)
    # Display
    plt.show()
