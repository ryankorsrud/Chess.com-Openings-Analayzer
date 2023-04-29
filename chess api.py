from chessdotcom import get_player_game_archives, get_player_stats
import requests
import pandas as pd
from io import StringIO
import chess.pgn



user = 'r_kors'



def get_games(user):
    data = get_player_game_archives(user).json
    games = {'games':[]}
    for url in data['archives']:
        games['games'] += (requests.get(url).json()['games'])
    return games['games']



def get_pgns(games):
    pgns = []
    for game in games:
        pgn = chess.pgn.read_game(StringIO(game['pgn']))
        pgns.append(pgn)
    return pgns



def white_result(result):
    if result == '1-0':
        return 'win'
    elif result == '0-1':
        return 'loss'
    return 'draw'



def black_result(result):
    if result == '1-0':
        return 'loss'
    elif result == '0-1':
        return 'win'
    return 'draw'



def get_game_stats(pgn):
    if pgn.headers['White'] == user:
        colour = 'white'
    else:
        colour = 'black'
            
    result = pgn.headers['Result']
    if colour == 'white':
        res = white_result(result)
    else:
        res = black_result(result)
    
    opening = pgn.headers['ECO']
    
    return opening,res



games = get_games(user)
pgns = get_pgns(games)
stats = []
for pgn in pgns:
    try:
        stats.append(get_game_stats(pgn))
    except:
        pass

df = pd.DataFrame(stats, columns=['Opening', 'Result']) 

openings = df['Opening'].unique()

data = []
for i in openings:
    o = df.loc[df['Opening'] == i]
    games_played = len(o)
    try:
        wins = o['Result'].value_counts()['win']
    except:
        wins = 0
    try:
        draw = o['Result'].value_counts()['draw']
    except:
        draw = 0
    try:
        loss = o['Result'].value_counts()['loss']
    except:
        loss = 0

    try:
        win_rate = (wins/(wins+loss)) * 100
        data.append([i, games_played, win_rate, wins, draw, loss])
    except:
        pass

opening_stats = pd.DataFrame(data, columns=['Opening', 'Games', 'W/L', 'Wins', 'Draws', 'Losses'])
opening_stats = opening_stats[opening_stats['Games'] >= 20]
print(opening_stats.sort_values('W/L', ascending=False).to_string())


