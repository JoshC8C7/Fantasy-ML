import csv
import requests
from bs4 import BeautifulSoup
import pandas as pd
from main import get_season_name

pd.set_option('display.max_columns', None)


def tablemaker():
    with open('20-21.csv','w') as csvo:
        writer = csv.writer(csvo, delimiter=',')
        for i in range(1,39):
            if i < 10:
                ind = '0'+str(i)
            else:
                ind = str(i)
            try:
                pdx = pd.read_html('https://www.eplreview.com/epl2020-21_table_matchweek'+ind+'.htm')
                pdx = pdx[1].iloc[:,0:4]
                #pdx = pdx.rename(columns=pdx.iloc[0]).drop(pdx.index[0])
                pdx = pdx.iloc[:,3]
                print(pdx)
                print("GAMEWEEK ",str(i))
            except:
                print("ERROR ON GW ", str(i))
                writer.writerow("GW"+ str(i)+" NONE FOUND")
            else:
                writer.writerow(pdx[:20].tolist())


def convert_names_to_ids(season=20):
    #bigdf = pd.read_csv('data/2016-17/gws/gw1.csv',encoding='latin-1').head(1)
    team_mapping = pd.read_csv('data/master_team_list.csv',encoding='latin-1')
    team_mapping = team_mapping[team_mapping['season'] == get_season_name(season)]
    team_map_dict = pd.Series(team_mapping.team_name.values, index=team_mapping.team).to_dict()
    flipped_dict = pd.Series(team_mapping.team.values, index=team_mapping.team_name).to_dict()
    print(flipped_dict)

    print(team_map_dict)
    with open('data/standings/20-21.csv') as edd:
        raw = edd.read()
    for xk, xv in flipped_dict.items():
        print(xk)
        raw = raw.replace(xk, str(xv))
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print(raw)
    with open('data/standings/20-21a.csv','w') as wdd:
        wdd.write(raw)

#convert_names_to_ids()