import sklearn as sk
import pandas as pd
import numpy as np
import csv
from sklearn import linear_model

DEBUG = False



def get_season_name(year,prefix=True):
    if prefix:
        return('20'+str(year)+'-'+str(year+1))
    else:
        return(str(year)+'-'+str(year+1))

def dprint(*args):
    if DEBUG:
        print(*args)
    return


np.random.seed(99)
pd.set_option('display.max_columns', 15)

def home_print(home):
    if home:
        return "(H)"
    else:
        return "(A)"


def fixtures2scalar(fixture_difficulties):
    return sum(x**2 for x in fixture_difficulties)

def get_next_n_fixtures(standings, team_map_dict, bigdf, current_gw, n):
    ret_list = []
    dprint("Current Gameweek:", current_gw, ",Fixtures for next ", n, "are:")
    for i in range(current_gw+1,min(39,current_gw+1+n)):
        opponent = bigdf.loc[i-1,'opponent_team']
        at_home = bigdf.loc[i-1,'was_home']
        difficulty = (get_approx_difficulty(standings=standings, current_gw=current_gw, opponent_id=opponent, is_opponent_at_home=(not at_home)))
        dprint("GW ",i, " :",opponent,team_map_dict[opponent], home_print(at_home), "Difficulty: ", difficulty)
        ret_list.append(difficulty)
    return fixtures2scalar(ret_list)

def get_standing(standings,team_id, gw):
    npdf1 = (standings.loc[:,gw-1].to_numpy())
    return 1+np.where(npdf1==team_id)[0][0]


#Gets difficulty on 1-5 scale based on current table ranking +1 if away
# i.e. (1st-5th = 4, 6th-10th = 3, 11-15th = 2, 16-20th = 1) + 1 if away
def get_approx_difficulty(standings,current_gw, opponent_id, is_opponent_at_home):
    #Current_gw = Gameweek of the match upcoming; so table will be checked for standings after gameweek = current_gw-1
    if current_gw == 1:
        return 3
    opponent_standing = get_standing(standings,opponent_id,current_gw-1)

    return ((20-opponent_standing) // 5) + 1 + int(is_opponent_at_home)


def marshall_features(bigdf, gw):
    return


def main(season=16):

    bigdf = pd.read_csv('data/2016-17/gws/gw1.csv',encoding='latin-1').head(1)
    standings = pd.read_csv('data/standings/' + get_season_name(season, prefix=False) + '.csv', header=None, index_col=None)
    team_mapping = pd.read_csv('data/master_team_list.csv',encoding='latin-1')
    team_mapping = team_mapping[team_mapping['season'] == get_season_name(season)]
    team_map_dict = pd.Series(team_mapping.team_name.values, index=team_mapping.team).to_dict()
    for i in range(2,39):
        dprint("Gameweek ", str(i))
        p1 = pd.read_csv('data/2016-17/gws/gw'+str(i)+'.csv',encoding='latin-1')
        bigdf = pd.merge(bigdf,p1.head(1),how='outer')

    bigdf['team_scored'] = np.where(bigdf['was_home'], bigdf['team_h_score'], bigdf['team_a_score'])
    bigdf['team_conceded'] = np.where(bigdf['was_home'], bigdf['team_a_score'], bigdf['team_h_score'])
    bigdf=bigdf.drop(columns=['team_a_score','team_h_score','id','kickoff_time','kickoff_time_formatted','value'])
    dprint(bigdf.corr()['total_points'].sort_values())
    cumulativedf = bigdf.cumsum()
    cumulativedf['total_points'] = bigdf['total_points']
    dprint(bigdf[['name','opponent_team','round']])

    bigdfx = pd.read_csv('data/2016-17/gws/gw1.csv',encoding='latin-1').head(1)
    player_data = pd.read_csv('data/2016-17/players_raw.csv',encoding='latin-1',index_col='id')[['element_type','team']]
    bigdf_for_player_data = bigdfx.join(player_data,on='element',rsuffix='r')[['name','element_type','team']]
    print(bigdf_for_player_data)

    #Feature vector for each player per GW:
    #1. Sum over season thus far for key stats
    #2. Last GWs stats incl fixture difficulty (param m for how many GWs to go back)
    #3. Difficulty of upcoming fixtures (param n for how many weeks to look ahead)

    #Label for each player per GW: Points that week

    n = 3
    m = 3
    gw = 15

    f1 = cumulativedf.iloc[gw-1]
    f2a = bigdf.iloc[max(gw-1-m,0):gw-1].cumsum().iloc[-1] if gw > 1 else 0
    f2b = get_next_n_fixtures(standings=standings, team_map_dict=team_map_dict, bigdf=bigdf, current_gw=gw-m, n=m)
    f3 = get_next_n_fixtures(standings=standings, team_map_dict=team_map_dict, bigdf=bigdf, current_gw=gw, n=n)
    print()

    if bigdf_for_player_data['element_type'].values[0] == 1:
        print("GK")
        chosen_cols = ['assists', 'bps', 'clean_sheets', 'clearences_blocks_interceptions', 'completed_passes',
                       'errors_leading_to_goal_attempt', 'fouls', 'goals_conceded', 'ict_index', 'influence',
                       'key_passes', 'own_goals', 'penalties_conceded', 'penalties_saved', 'red_cards', 'saves',
                       'selected', 'tackles', 'threat', 'total_points', 'transfers_balance', 'yellow_cards',]

    else:
        chosen_cols= ['assists', 'big_chances_created', 'bps', 'clean_sheets', 'own_goals', 'offside',
                                'clearances_blocks_interceptions', 'completed_passes', 'creativity', 'dribbles',
                                'errors_leading_to_goal_attempt', 'fouls', 'goals_conceded', 'goals_scored',
                                'ict_index', 'influence', 'key_passes', 'open_play_crosses', 'recoveries', 'red_cards',
                                'selected', 'tackles', 'tackled', 'threat', 'total_points', 'transfers_balance',
                                'yellow_cards', 'team_scored', 'team_conceded']

    dprint("F1:")
    ff1 = ((f1[chosen_cols].replace('total_points','round_points')).values)
    dprint(ff1)
    dprint("F2a:")
    ff2a = (f2a[chosen_cols].values)
    dprint(ff2a)
    dprint("F2b: ", f2b)
    dprint("F3: ",f3)
    ff3 = np.array([f2b,f3])
    x = np.concatenate((ff1,ff2a,ff3))
    print(len(x))
    y = bigdf.iloc[gw-1]['total_points']

    bigxs = np.fromfunction(a,(p,60))

    return

def train(xs, ys):
    regr = linear_model.LinearRegression()
    regr.fit(xs,ys)
    print(regr.coef_, regr.intercept_)

if __name__ == '__main__':
    main()
