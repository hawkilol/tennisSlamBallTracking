import operator
import os
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

def match_pbp_and_rally_data(player_id, tournament, league):
    player_id = player_id
    print("tournament: ", tournament)
    print("league: ", league)
    matches_with_player = []

    # Loop through all files in the directory
    pbp_dir = f'pbp_data_csvs/{tournament}/{league}/'
    
    for filename in os.listdir(pbp_dir):
        if filename.endswith("_pbp.csv"):
            pbp_file_path = os.path.join(pbp_dir, filename)
            rally_file_path = f'rally_data_csvs/{tournament}/{league}/{filename.replace("_pbp.csv", "_ball_trajectory.csv")}'

            # Check if the files exist
            if not os.path.exists(rally_file_path):
                print(f"Rally data file not found for {filename}")
                continue

            pbp_data = pd.read_csv(pbp_file_path)
            pbp_data = pbp_data[(pbp_data['server_id'] == player_id) | (pbp_data['returner_id'] == player_id)]
                
                #print("pbp_file_path", pbp_file_path)
                # print("rally_file_path", rally_file_path)
            rally_data = pd.read_csv(rally_file_path)
            matches_with_player.append((pbp_data, rally_data))
                
    print("matches: ",len(matches_with_player))     

    return matches_with_player

#get matches for player
def get_pbp_data(player_id, tournament, league):
    player_id = player_id
    print("tournament: ", tournament)
    print("league: ", league)
    matches_with_player = []

    pbp_dir = f'pbp_data_csvs/{tournament}/{league}/'
    
    for filename in os.listdir(pbp_dir):
        if filename.endswith("_pbp.csv"):
            pbp_file_path = os.path.join(pbp_dir, filename)

            pbp_data = pd.read_csv(pbp_file_path)
            pbp_data = pbp_data[(pbp_data['server_id'] == player_id) | (pbp_data['returner_id'] == player_id)]

                #print("pbp_file_path", pbp_file_path)
            pbp_data = pbp_data[pbp_data['is_track_avail'] == True]
            if(pbp_data.size > 0):
                matches_with_player.append(pbp_data)
    print("matches: ",len(matches_with_player))     
    return matches_with_player

def get_matches_pbp_with_tracking_available(tournament, league):
    '''
    returns only the pbp data that has coordinate data available (so the serve count might not add up)
    '''
    print("tournament: ", tournament)
    print("league: ", league)
    matches_with_player = []

    pbp_dir = f'pbp_data_csvs/{tournament}/{league}/'
    
    for filename in os.listdir(pbp_dir):
        if filename.endswith("_pbp.csv"):
            pbp_file_path = os.path.join(pbp_dir, filename)

            pbp_data = pd.read_csv(pbp_file_path)

            pbp_data = pbp_data[pbp_data['is_track_avail'] == True]
            #print("size:", pbp_data.size )
            if(pbp_data.size > 0):
                matches_with_player.append(pbp_data)
                
    print("matches: ",len(matches_with_player))
    return matches_with_player
def get_server_name(df_pbp):
    players_df = pd.read_csv("players.csv")
    
    player_id_name = players_df.set_index("player_id_rg")["player_name"].to_dict()
    player_id_name.update(players_df.set_index("player_id_ao")["player_name"].to_dict())
    
    df_pbp["server_name"] = df_pbp["server_id"].map(player_id_name)
    
    first_match = df_pbp["server_name"].dropna().iloc[0] if not df_pbp["server_name"].dropna().empty else None
    
    return first_match

def add_points_to_df(df, file_path):
    catalogue_path = "players_matches_catalogue/catalogue_all_matches_available.csv"
    catalogue_df = pd.read_csv(catalogue_path)
    
    year = int(file_path.split('_')[-3])
    match_id = file_path.split('_')[-2] 
    match = catalogue_df[(catalogue_df['year'] == year) & (catalogue_df['match_id'].str.split('_').str[-1] == match_id)]    
    
    player_name = get_server_name(df)
    points = 0
    # print("year_match_id: ", str(year) + ' ' + match_id)
    # print("player_name: ", player_name)
    # print('match[player1]: ', match['player1'])
    # print('match[player1].iloc: ', match['player1'].iloc[0])
    # print('match[player2]: ', match['player2'])
    # print('match[player2].iloc: ', match['player2'].iloc[0])
    
    if (match['player1'].iloc[0] == player_name):
        points = match['player1_points'].iloc[0]
    
    if (match['player2'].iloc[0] == player_name):
        points = match['player2_points'].iloc[0]

    df['rank_points'] = points
    return df    
           
def get_global_pbp_data_with_tracking_available(tournament, league, add_rank_points_to_serves=True):
    print("tournament: ", tournament)
    print("league: ", league)
    all_pbp_data = pd.DataFrame()
    matches = 0
    
    pbp_dir = f'pbp_data_csvs/{tournament}/{league}/'
    
    for filename in os.listdir(pbp_dir):
        if filename.endswith("_pbp.csv"):
            pbp_file_path = os.path.join(pbp_dir, filename)
        
            pbp_data = pd.read_csv(pbp_file_path)

            pbp_data = pbp_data[pbp_data['is_track_avail'] == True]
            #print("size:", pbp_data.size )
            if pbp_data.size > 0:
                matches+=1
                if (add_rank_points_to_serves):
                    pbp_data = add_points_to_df(pbp_data, pbp_file_path)
                all_pbp_data = pd.concat([all_pbp_data, pbp_data], ignore_index=True)
                
    print("Matches: ", matches)       
    print("Points: ", len(all_pbp_data)) 
          
    return all_pbp_data
def get_global_pbp_data_tracking_optional(tournament, league):
    print("tournament: ", tournament)
    print("league: ", league)
    all_pbp_data = pd.DataFrame()
    matches = 0

    pbp_dir = f'pbp_data_csvs/{tournament}/{league}/'
    
    for filename in os.listdir(pbp_dir):
        if filename.endswith("_pbp.csv"):
            pbp_file_path = os.path.join(pbp_dir, filename)

            pbp_data = pd.read_csv(pbp_file_path)

            if pbp_data.size > 0:
                matches+=1
                all_pbp_data = pd.concat([all_pbp_data, pbp_data], ignore_index=True)
    print("Matches: ", matches)
    print("Points: ", len(all_pbp_data))       
    return all_pbp_data



def get_pbp_data_tracking_available(player_id, tournament, league):
    player_id = player_id
    print("tournament: ", tournament)
    print("league: ", league)
    matches_with_player = []

    pbp_dir = f'pbp_data_csvs/{tournament}/{league}/'
    
    for filename in os.listdir(pbp_dir):
        if filename.endswith("_pbp.csv"):
            pbp_file_path = os.path.join(pbp_dir, filename)

            pbp_data = pd.read_csv(pbp_file_path)
            pbp_data = pbp_data[(pbp_data['server_id'] == player_id) | (pbp_data['returner_id'] == player_id)]

                #print("pbp_file_path", pbp_file_path)
            pbp_data = pbp_data[pbp_data['is_track_avail'] == True]
                #print("size:", pbp_data.size )
            if(pbp_data.size > 0):
                matches_with_player.append(pbp_data)
                    
    print("matches: ", len(matches_with_player))
    return matches_with_player


def get_player_pbp_data_tracking_available(player_id, tournament, league):
    print("tournament:", tournament)
    print("league:", league)
    
    pbp_dir = f'pbp_data_csvs/{tournament}/{league}/'
    pbp_files = [os.path.join(pbp_dir, f) for f in os.listdir(pbp_dir) if f.endswith("_pbp.csv")]

    filtered_data = []

    for pbp_file_path in pbp_files:
        pbp_data = pd.read_csv(pbp_file_path)
        pbp_data = pbp_data[
            ((pbp_data['server_id'] == player_id) | (pbp_data['returner_id'] == player_id)) & 
            (pbp_data['is_track_avail'])
        ]
        
        if not pbp_data.empty:
            filtered_data.append(pbp_data)
    
    all_pbp_data = pd.concat(filtered_data, ignore_index=True) if filtered_data else pd.DataFrame()
    
    print("global total points:", len(all_pbp_data))
    return all_pbp_data

###################################################################
def get_player_ids_by_name(player_name):
    catalogue_path = "players.csv"
    players_df = pd.read_csv(catalogue_path)
    player_entry = players_df[players_df['player_name'] == player_name]
    player_id_ao = ""
    player_id_rg = 0
    if (player_entry['player_id_ao'].any()):
        player_id_ao = str(player_entry['player_id_ao'].iloc[0])
    if (player_entry['player_id_rg'].any()):
        player_id_rg = int(player_entry['player_id_rg'].iloc[0])
    return player_id_ao, player_id_rg

def get_player_by_name_df(player_name):
    catalogue_path = "players.csv"
    players_df = pd.read_csv(catalogue_path)
    player_entry = players_df[players_df['player_name'] == player_name]
    return player_entry

#####################################################################################################
def get_unique_player_ids(catalogue_df, tournament):
    tournament_df = catalogue_df[catalogue_df['tournament'] == tournament]
    unique_ids = set()
    for index, row in tournament_df.iterrows():
        unique_ids.add(row['player1_id'])
        unique_ids.add(row['player2_id'])
    
    return unique_ids
def get_player_ids(player1_name, player2_name):
    catalogue_path = "players_matches_catalogue/catalogue_all_matches_available.csv"
    catalogue_df = pd.read_csv(catalogue_path)
    get_unique_player_ids(catalogue_df)
    
    player1_ao_id = catalogue_df.loc[(catalogue_df['player1'] == player1_name) | (catalogue_df['player2'] == player1_name), 'player1_id'].iloc[0] if player1_name in catalogue_df.values else None
    player2_rg_id = catalogue_df.loc[(catalogue_df['player1'] == player2_name) | (catalogue_df['player2'] == player2_name), 'player2_id'].iloc[0] if player2_name in catalogue_df.values else None
    # tournament = catalogue_df['tournament'].iloc[0]
    player1_ao_id = player1_ao_id
    player2_rg_id = player2_rg_id

    return player1_ao_id, player2_rg_id
def get_all_players_names():
    catalogue_path = "players_matches_catalogue/catalogue_all_matches_available.csv"
    catalogue_df = pd.read_csv(catalogue_path)
    
    unique_player_names = np.unique(np.concatenate((catalogue_df['player1'].unique(), catalogue_df['player2'].unique())))

    return unique_player_names


def get_surname(sentence):
    parts = sentence.split('.')
    last_part = parts[-1]
    
    if ' ' in last_part:
        last_word = last_part.split()[-1]
    else:
        last_word = last_part
    
    return last_word.upper()

def normalize_name(sentence):
    return sentence.replace(' ', '').upper()


def get_all_surnames(player_names):
    surnames = []
    for full_name in player_names:
        surname = get_surname(full_name)
        surnames.append(surname)
    return surnames

def get_all_names(player_names):
    surnames = []
    for full_name in player_names:
        surname = normalize_name(full_name)
        surnames.append(surname)
    return surnames

def get_all_players_names_tour_league_catalogue(tournament, league):
    catalogue_path = "players_matches_catalogue/catalogue_all_matches_available.csv"
    catalogue_df = pd.read_csv(catalogue_path)
    
    filtered_df = catalogue_df[(catalogue_df['tournament'] == tournament) & (catalogue_df['league'] == league)]

    unique_player_names = np.unique(np.concatenate((filtered_df['player1'].unique(), filtered_df['player2'].unique())))
    #all_names = get_all_names(unique_player_names)

    return unique_player_names

def get_all_players_names_league_catalogue(league):
    catalogue_path = "players_matches_catalogue/catalogue_all_matches_available.csv"
    catalogue_df = pd.read_csv(catalogue_path)
    
    filtered_df = catalogue_df[catalogue_df['league'] == league]

    unique_player_names = np.unique(np.concatenate((filtered_df['player1'].unique(), filtered_df['player2'].unique())))

    return unique_player_names


def get_all_players_names_league(league):
    players_path = "players.csv"
    players_df = pd.read_csv(players_path)
    
    filtered_df = players_df[players_df['league'] == league]

    player_names = np.array(filtered_df['player_name'])

    return player_names

def get_all_players_names_tour_league(tournament, league):
    players_path = "players.csv"
    players_df = pd.read_csv(players_path)
    
    if(tournament == 'roland_garros'):
        player_id = 'player_id_rg'
            
    if(tournament == 'australian_open'):
        player_id = 'player_id_ao'
        
    filtered_df = players_df[(players_df[player_id].notna()) & (players_df['league'] == league)]

    player_names = np.array(filtered_df['player_name'])

    return player_names


###############################################

def get_all_players_info(tournament, league):
    '''
    return a list of tuples with the (player_id, player_name)
    or return a list of tuples with the (player_ao_id, player_rg_id, player_name) if a tournament is not ""
    '''
    np.random.seed(42)

    if(tournament == ''):
        players = get_all_players_names_league(league)
    else:  
        players = get_all_players_names_tour_league(tournament, league)
        
    players_info = set()
    player_id = 0
    for player_name in players:
        player_ao_id, player_rg_id = get_player_ids_by_name(player_name)

        print("player_name", player_name)
        print("player_id", player_rg_id)
        if(tournament == 'roland_garros'):
            player_id = player_rg_id
            
        if(tournament == 'australian_open'):
            player_id = player_ao_id
        
        if(tournament == ''):
            players_info.add((player_ao_id, player_rg_id,  str(player_name)))
            continue

        players_info.add((player_id, str(player_name)))
    
    #players_info = sorted(players_info, key=lambda x: x[1][0].upper())
    #players_info = sorted(players_info, key=operator.itemgetter(1))  
    players_info = sorted(players_info, key=lambda x: x[-1])

    # players = sorted(players, key=operator.itemgetter(1))  
    
    return players_info

def get_all_players_info_df(tournament, league):
    '''
    or return a df with the (player_ao_id, player_rg_id, player_name) if a tournament is not ""
    '''
    np.random.seed(42)

    players_path = "players.csv"
    players_df = pd.read_csv(players_path)
    
    if(tournament != ''):
        if(tournament == 'roland_garros'):
            player_id = 'player_id_rg'
                
        if(tournament == 'australian_open'):
            player_id = 'player_id_ao'
            
        filtered_df = players_df[(players_df[player_id].notna()) & (players_df['league'] == league)]
    else:
        filtered_df = players_df[players_df['league'] == league]


    return filtered_df


def get_all_player_serves(player_id, tournament, league):
    matches_with_player_rg = get_player_pbp_data_tracking_available(player_id, tournament, league)
    if(len(matches_with_player_rg) > 0):
        return matches_with_player_rg[matches_with_player_rg['server_id'] == player_id]
    else:
        print("Not found :( get_all_player_serves")
        return []
    
def get_all_player_aces(player_id, tournament, league):
    matches_with_player_rg = get_player_pbp_data_tracking_available(player_id, tournament, league)
    if(len(matches_with_player_rg) > 0):
        #matches_with_player_rg['point_end_type'] == 'ACE'
        return matches_with_player_rg[(matches_with_player_rg['server_id'] == player_id) & (matches_with_player_rg['is_ace'])]
    else:
        print("Not found :( get_all_player_aces")
        return []
    
def get_player_pbp_filter_column(player_id, column_name, column_value, tournament, league):
    matches_with_player_rg = get_player_pbp_data_tracking_available(player_id, tournament, league)
    if(len(matches_with_player_rg) > 0):
        serves = matches_with_player_rg[(matches_with_player_rg['server_id'] == player_id) & (matches_with_player_rg[column_name] == column_value)]
        print("Player serves: ", len(serves))
        #print("Player serves: ", serves)
        print("servestest:", serves['point_ID'])
        return serves
    else:
        print("Not found :( get_player_pbp_filter_column")
        return []

def df_filter(data, filters):
    """ data -> df
        filters -> (column, value)"""
        
    filtered_data = data
    for column, value in filters:
        filtered_data = filtered_data[filtered_data[column] == value]
    return filtered_data   
    
def get_all_player_serves_vs_player(server_player_id, returner_player2_id, tournament, league):
    return get_player_pbp_filter_column(server_player_id, 'returner_id', returner_player2_id, tournament, league)

def get_all_player_serves_vs_player_names(server_player_name, returner_player2_name, tournament, league):
    server_ao_id, server_rg_id = get_player_ids_by_name(server_player_name)
    returner_ao_id, returner_rg_id  = get_player_ids_by_name(returner_player2_name)
    
    if(tournament == "roland_garros"):
        server_player_id = int(server_rg_id)
        returner_player2_id = int(returner_rg_id)
        
    if(tournament == "australian_open"):
        server_player_id = server_ao_id
        returner_player2_id = returner_ao_id

    print("server_player_id: ", server_player_id)
    print("returner_player2_id: ", returner_player2_id)
    return get_player_pbp_filter_column(server_player_id, 'returner_id', returner_player2_id, tournament, league)



def get_head_to_head_pbp(player1_id, player2_id, tournament, league):
    global_pbp = get_global_pbp_data_with_tracking_available(tournament, league)
    head_to_head_pbp = global_pbp[((global_pbp['player1'] == player1_id) & (global_pbp['player2'] == player2_id)) |
                                  ((global_pbp['player1'] == player2_id) & (global_pbp['player2'] == player1_id))]
    
    return head_to_head_pbp


def get_player_ranking_history(player_id_atp, league):
    '''
    Args:
    -----
    player_id: str
        Player ID to fetch ranking history for.
    processed_data_folder: str
        Directory where processed CSV files are saved.
        
    Returns:
    --------
    pandas DataFrame with ranking history for the specified player.
    '''

    #directory_list = ['atp', 'wta']
    players_hist_path = "ranking_data_csvs/" + league + "/" + league + "_" + player_id_atp + "_player_ranking_history.csv"

    player_hist_df = pd.read_csv(players_hist_path)
    
    return player_hist_df
    
def apply_filters(df, filters):
    for column, value in filters.items():
        df = df[df[column] == value]
    return df

