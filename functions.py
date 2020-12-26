import folium
import pandas as pd
import streamlit as st
import geopandas



# Get Geopandas dataset
world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))

results = pd.read_csv("results.csv")

# Function to find winning or losing team
def find_winners_losers(df, column_to_check):
    results_array = []
    if column_to_check == 'winner':
        for i, row in df.iterrows():
            if row['home_score'] > row['away_score']:
                results_array.append(row['home_team'])
            elif row['home_score'] < row['away_score']:
                results_array.append(row['away_team'])
            else:
                results_array.append('Draw')
    elif column_to_check == 'loser':
        for i, row in df.iterrows():
            if row['home_score'] > row['away_score']:
                results_array.append(row['away_team'])
            elif row['home_score'] < row['away_score']:
                results_array.append(row['home_team'])
            else:
                results_array.append('Draw')


    return results_array

# Function to determine teams which draw.
# This function first place home drawers and away drawers in separate columns
def find_draw(df):
    array_home = []
    array_away = []

    for i, row in df.iterrows():
        if row['home_score'] == row['away_score']:
            array_home.append(row['home_team'])
            array_away.append(row['away_team'])
        else:
            array_home.append('No draw')
            array_away.append('No draw')
    return array_home, array_away

# def find_total_games(df):
#     array_total = []
#
#     for i, row in df.iterrows():
#         if row['home_team']
#

# Function to display folium Choropleth map
def map_display(map, map_result, column_to_check, legend_text):
    folium.Choropleth(
        geo_data=map_result,
        name='choropleth',
        data=map_result,
        columns=[column_to_check, 'Counts'],
        key_on='feature.properties.name',
        fill_color='OrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=legend_text
    ).add_to(map)


# Function to clean data and return final table
def clean_data(column_to_check):

    # Clean data if requested to find winners
    if column_to_check == 'winner':
        results[column_to_check] = find_winners_losers(results, column_to_check)
        countwinners = results.value_counts(results[column_to_check]).reset_index(name='Counts')
        countwinners = countwinners[countwinners[column_to_check] != 'Draw']
        st.write(countwinners)
        countwinners = world.merge(countwinners, how='inner', left_on='name', right_on=column_to_check)
        map_result = countwinners

    # Clean data if requested to find losers
    if column_to_check == 'loser':
        results[column_to_check] = find_winners_losers(results, column_to_check)
        countlosers = results.value_counts(results[column_to_check]).reset_index(name='Counts')
        countlosers = countlosers[countlosers[column_to_check] != 'Draw']
        st.write(countlosers)
        countlosers = world.merge(countlosers, how='inner', left_on='name', right_on=column_to_check)
        map_result = countlosers

    # Clean data if requested to find drawing teams
    if column_to_check == 'draw':
        draw_home, draw_away = find_draw(results)
        results['draw_home'] = draw_home
        results['draw_away'] = draw_away
        draw_teams = results['draw_home'].append(results['draw_away']).reset_index(name='draw')
        countdraws = draw_teams.value_counts(draw_teams[column_to_check]).reset_index(name='Counts')
        countdraws = countdraws[countdraws[column_to_check] != 'No draw']

        #Display in streamlit
        st.write(countdraws)
        countdraws = world.merge(countdraws, how="inner", left_on='name', right_on=column_to_check)
        map_result = countdraws

    # Clean data if requested to find % of wins
    if column_to_check == "percentage wins":
        #creating table of all countries that ever played
        total_games = results['home_team'].append(results['away_team']).reset_index(name=column_to_check)
        counttotal = total_games.value_counts(total_games[column_to_check]).reset_index(name='Counts')
        counttotal = counttotal[counttotal[column_to_check] != 'No draw']

        #creating table of all teams that ever won
        results["wins"] = find_winners_losers(results, "winner")
        countwinners = results.value_counts(results["wins"]).reset_index(name='Counts')
        countwinners = countwinners[countwinners["wins"] != 'Draw']

        # Joining both tables based on the country name
        joined_tables = countwinners.merge(counttotal, left_on="wins",right_on=column_to_check)
        joined_tables['Counts'] = (joined_tables['Counts_x'] / joined_tables['Counts_y'] ) * 100
        wins_percentage = joined_tables[["wins","Counts_y","Counts"]]
        wins_percentage.columns = ["Team", "Games played","Percentage of wins"]
        wins_percentage = wins_percentage.sort_values("Percentage of wins", ascending=False)

        #Displaying table in streamlit
        st.write(wins_percentage)
        wins_percentage.columns = [column_to_check, "Games played","Counts"]
        wins_percentage = world.merge(wins_percentage, how="inner", left_on='name', right_on=column_to_check)
        map_result = wins_percentage

    return map_result


# Function to select final data to be displayed in streamlit_folium
def select_statistic(statistic_choice):
    column_to_check = "None"
    legend_text = 'Text'
    if statistic_choice == 'Number of wins':
        column_to_check = 'winner'
        legend_text = 'Number of international won games'
        map_result = clean_data(column_to_check)

    if statistic_choice == 'Number of looses':
        column_to_check = 'loser'
        legend_text = 'Number of international lost games'
        map_result = clean_data(column_to_check)

    if statistic_choice == 'Number of draws':
        column_to_check = 'draw'
        legend_text = 'Number of international draws'
        map_result = clean_data(column_to_check)

    if statistic_choice == 'Percentage of wins':
        column_to_check = 'percentage wins'
        legend_text = 'Percentage of wins'
        map_result = clean_data(column_to_check)

    return map_result, column_to_check, legend_text