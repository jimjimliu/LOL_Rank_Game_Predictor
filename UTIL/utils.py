import os
import pickle
from csv import DictReader
import pandas as pd
from MySQL_POOL.mysqlhelper import MySqLHelper
from Config.config import SUMMONERS_DATA
from tqdm import tqdm
import csv
import os
from datetime import datetime
import numpy as np


def save_pkl_model(model, file_name, path):
    '''
    save a model using python pickle

    :param model: (Object) the model to be saved
    :param file_name: (String) file name string
    :param path: (String) directory of position to save the model. Default=.../model
    :return: None
    '''
    if not os.path.exists(path):
        os.mkdir(path)

    with open(os.path.join(os.path.join(path, file_name)), 'wb') as handle:
        pickle.dump(model, handle)
    print(file_name, 'saved at: ', path)

def load_pkl(file_name, path):
    '''
    load an existing model using pickle

    :param file_name: (String) file name
    :param path: (String) directory where model is saved. Default=.../model
    :return: (Object) the model
    '''
    with open(os.path.join(path, file_name), 'rb') as handle:
        model_pkl = pickle.load(handle)

    return model_pkl

def missing_values(df):
    '''
    return the total count of missing values of each column

    :param data_path:
        (string)
    :return:
        (pandas.series)
    '''
    count = df.isnull().sum()
    print(count)
    return count

def write_csv(header, data, path):
    '''
    write into csv.
    General function.

    :param data: list of tuples. [(), ()]
    :param header: (list) []
    :param path: (string)
    :return:
    '''
    if len(data) == 0:
        print("0 rows has been written to .csv")

    with open(path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        # if no header, write header
        if csvfile.tell() == 0:
            writer.writerow(header)
        for item in tqdm(data, desc="Writing to .csv"):
            writer.writerow(item)

    print("{} rows has been written to {}".format(len(data), path))

def check_balanced(df, column):
    '''
    check if the data frame is balanced using the given column as label.
    Return each label's distribution percentage to see if the dataset is balanced.
    :return:
        (Dict): dictionary has key=label_name, value=label percentage
    '''

    # vc is pandas series
    vc = df[column].value_counts()
    # row counts of df
    row_count = df.shape[0]

    result_dict = {}
    for i, v in vc.items():
        result_dict[i] = v, v/row_count

    return result_dict

def print_info(text=None):
    print("================================================")
    print("|                                              |")
    print("|", text, " "*(len("================================================")-len(text)-5) , "|")
    print("|                                              |")
    print("================================================")

def populate_db(sql, data):
    '''
    populating database in batches, 1000 rows at a time.

    :param sql:
        sql = insert ignore into all_league_entry(`col`) VALUES (%s)

    :param data: List of tuples or tuples, [(), ()], ((), ())
    :return:
        return rows affected after populating database
    '''

    if len(data) == 0:
        raise Exception("Data is empty.")

    db = MySqLHelper()
    start_index = 0
    # populate 1000 rows into database per time
    step = 1000
    while start_index < len(data):
        print("Populating row {} to {}.".format(start_index, start_index+step))
        result = db.insertmany(sql, data[start_index:start_index + step])
        print(result, " rows inserted.")
        start_index += step

    print("Finish populating.")

def summoner_stats():

    data = pd.read_csv(os.path.join("..", SUMMONERS_DATA))
    # total count of each tier
    tier_distribution = data.loc[:,'tier'].value_counts()
    # tiers in the data
    tier_label = tier_distribution.keys().to_numpy()

    print(tier_distribution)
    total_distinct = 0
    for tier in tier_label:
        # divisions so far in the data set
        divisions = data[data['tier'] == tier].loc[:, 'rank'].unique()
        for div in divisions:
            # count unique account id of each rank
            unique_account = data.query("tier=='{}' & rank=='{}'".format(tier, div)).loc[:, 'accountId'].nunique()
            total_distinct += unique_account
            print("[{} {}] {}".format(tier, div, unique_account))
    print("Total distinct count: {}".format(total_distinct))

def populate_data():


    sql = '''
        insert ignore into all_league_entry(`leagueId`, `queueType`, `tier`, `rank`,`summonerId`,`summonerName`,
        `leaguePoints`,`wins`,`losses`,`veteran`,`inactive`,`freshBlood`,`hotStreak`,`accountId`,`puuid`,`summonerLevel`)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
    '''
    CSV_FILE_PATH = SUMMONERS_DATA
    df = pd.read_csv(CSV_FILE_PATH, skiprows=0)
    data = [tuple(x) for x in df.to_numpy()]
    populate_db(sql, data)


    sql = '''
        insert ignore into all_champion
        (`champion_id`, `version`,`key`,`name`,`title`,`tag1`,`tag2`,`hp`,`hpperlevel`,`mp`,`mpperlevel`,`movespeed`,`armor`,
        `armorperlevel`,`spellblock`,`spellblockperlevel`,`attackrange`,`hpregen`,`hpregenperlevel`,`mpregen`,`mpregenperlevel`,`crit`,
        `critperlevel`,`attackdamage`,`attackdamageperlevel`,`attackspeedperlevel`,`attackspeed`)
        values
        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
    '''
    csv = "DATA/all_champions.csv"
    df = pd.read_csv(csv, skiprows=0)
    data = [tuple(x) for x in df.to_numpy()]
    populate_db(sql, data)

    sql = '''
        insert ignore into RIOT.match_list
        (`accountId`,`platformId`,`gameId`,`champion`,`queue`,`season`,`timestamp`,`role`,`lane`)
        values
        (%s,%s,%s,%s,%s,%s,%s,%s,%s);
    '''
    csv = "DATA/match_list.csv"
    df = pd.read_csv(csv)
    data = [tuple(x) for x in df.to_numpy()]
    populate_db(sql, data)

    sql = """
        insert ignore into RIOT.`match`
        (`gameId`,`gameDuration`,
        `team1_win`,`team1_firstBlood`,`team1_firstTower`,
        `team1_firstInhibitor`,`team1_firstBaron`,`team1_firstDragon`,`team1_firstRiftHerald`,
        `team1_towerKills`,`team1_inhibitorKills`,`team1_baronKills`,`team1_dragonKills`,`team1_vilemawKills`,
        `team1_riftHeraldKills`,`team1_dominionVictoryScore`,
        `team1_ban1`,`team1_ban2`,`team1_ban3`,`team1_ban4`,`team1_ban5`,
        `team1_champ1_championId`,`team1_champ2_championId`,`team1_champ3_championId`,
        `team1_champ4_championId`,`team1_champ5_championId`,`team1_champ1_statId`,`team1_champ2_statId`,
        `team1_champ3_statId`,`team1_champ4_statId`,`team1_champ5_statId`,`team2_win`,`team2_firstBlood`,
        `team2_firstTower`,`team2_firstInhibitor`,`team2_firstBaron`,`team2_firstDragon`,
        `team2_firstRiftHerald`,`team2_towerKills`,`team2_inhibitorKills`,`team2_baronKills`,`team2_dragonKills`,
        `team2_vilemawKills`,`team2_riftHeraldKills`,`team2_dominionVictoryScore`,`team2_ban1`,`team2_ban2`,`team2_ban3`,
        `team2_ban4`,`team2_ban5`,`team2_champ1_championId`,`team2_champ2_championId`,`team2_champ3_championId`,
        `team2_champ4_championId`,`team2_champ5_championId`,`team2_champ1_statId`,`team2_champ2_statId`,`team2_champ3_statId`,
        `team2_champ4_statId`,`team2_champ5_statId`)
        values
        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
        ,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
    """

    csv = 'DATA/matches.csv'
    df = pd.read_csv(csv)
    data = [tuple(np.asarray(x).astype(int).tolist()) for x in tqdm(df.to_numpy(), desc="Converting data to int.")]
    populate_db(sql, data)

    sql = """
        insert ignore into RIOT.champ_game_stat
        (`statId`,`gameId`, `championId`, `spell1Id`, `spell2Id`, `item0`, `item1`, `item2`, `item3`, `item4`, `item5`,
        `item6`, `kills`, `deaths`, `assists`, `largestKillingSpree`, `largestMultiKill`, `killingSprees`,
        `longestTimeSpentLiving`, `doubleKills`, `tripleKills`, `quadraKills`, `pentaKills`, `unrealKills`,
        `totalDamageDealt`, `magicDamageDealt`, `physicalDamageDealt`, `trueDamageDealt`, `largestCriticalStrike`,
        `totalDamageDealtToChampions`, `magicDamageDealtToChampions`, `physicalDamageDealtToChampions`,
        `trueDamageDealtToChampions`, `totalHeal`, `totalUnitsHealed`, `damageSelfMitigated`,
        `damageDealtToObjectives`, `damageDealtToTurrets`, `visionScore`, `timeCCingOthers`, `totalDamageTaken`,
        `magicalDamageTaken`, `physicalDamageTaken`, `trueDamageTaken`, `goldEarned`, `goldSpent`, `turretKills`,
        `inhibitorKills`, `totalMinionsKilled`, `neutralMinionsKilled`, `neutralMinionsKilledTeamJungle`,
        `neutralMinionsKilledEnemyJungle`, `totalTimeCrowdControlDealt`, `champLevel`, `visionWardsBoughtInGame`,
        `sightWardsBoughtInGame`, `wardsPlaced`, `wardsKilled`, `firstBloodKill`, `firstBloodAssist`,
        `firstTowerKill`, `firstTowerAssist`, `firstInhibitorKill`, `firstInhibitorAssist`)
        values
        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
        ,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
    """
    df = pd.read_csv('DATA/match_stat.csv')
    data = [tuple(np.asarray(x).astype(int).tolist()) for x in tqdm(df.to_numpy(), desc="Converting data to int.")]
    populate_db(sql, data)

def get_game_data():
    '''
        join match data tabel and match champions data together.
        store data into game_data.csv

    :return:
    '''

    sql = '''
        select 
            -- team1_champ1_statId, team1_champ2_statId, team1_champ3_statId,team1_champ4_statId, team1_champ5_statId, 
        M.gameId,
        team1_win,
        
		team1_champ1_championId, team1_champ2_championId, team1_champ3_championId, team1_champ4_championId,team1_champ5_championId,
		team1_ban1, team1_ban2, team1_ban3,team1_ban4, team1_ban5,
		team1_firstBlood, team1_firstTower, team1_firstInhibitor, team1_firstBaron, team1_firstDragon,team1_firstRiftHerald,
		team1_towerKills, team1_inhibitorKills, team1_baronKills, team1_dragonKills,
		(S1.kills+S2.kills+S3.kills+S4.kills+S5.kills) as team1_totalKills,
		(S1.deaths+S2.deaths+S3.deaths+S4.deaths+S5.deaths) as team1_totalDeaths,
		(S1.goldSpent+S2.goldSpent+S3.goldSpent+S4.goldSpent+S5.goldSpent) as team1_goldSpent,
		
		team2_champ1_championId, team2_champ2_championId, team2_champ3_championId, team2_champ4_championId,team2_champ5_championId,
		team2_ban1, team2_ban2, team2_ban3,team2_ban4, team2_ban5,
		team2_firstBlood, team2_firstTower, team2_firstInhibitor,team2_firstBaron, team2_firstDragon, team2_firstRiftHerald,
		team2_towerKills, team2_inhibitorKills, team2_baronKills, team2_dragonKills,
		(S6.kills+S7.kills+S8.kills+S9.kills+S10.kills) as team2_totalKills,
		(S6.deaths+S7.deaths+S8.deaths+S9.deaths+S10.deaths) as team2_totalDeaths,
		(S6.goldSpent+S7.goldSpent+S8.goldSpent+S9.goldSpent+S10.goldSpent) as team2_goldSpent,
        
        S1.doubleKills, S1.tripleKills, S1.quadraKills, S1.pentaKills,S1.champLevel,

        S2.doubleKills, S2.tripleKills, S2.quadraKills, S2.pentaKills,S2.champLevel,

        S3.doubleKills, S3.tripleKills, S3.quadraKills, S3.pentaKills,  S3.champLevel,

        S4.doubleKills, S4.tripleKills, S4.quadraKills, S4.pentaKills,  S4.champLevel,

        S5.doubleKills, S5.tripleKills, S5.quadraKills, S5.pentaKills,  S5.champLevel,

         S6.doubleKills, S6.tripleKills, S6.quadraKills, S6.pentaKills,  S6.champLevel,

        S7.doubleKills, S7.tripleKills, S7.quadraKills, S7.pentaKills,  S7.champLevel,

         S8.doubleKills, S8.tripleKills, S8.quadraKills, S8.pentaKills,  S8.champLevel,

         S9.doubleKills, S9.tripleKills, S9.quadraKills, S9.pentaKills,  S9.champLevel,

        S10.doubleKills, S10.tripleKills, S10.quadraKills, S10.pentaKills,  S10.champLevel    
    from `match` M
    left join champ_game_stat S1 on team1_champ1_statId = S1.statId
    left join champ_game_stat S2 on team1_champ2_statId = S2.statId
    left join champ_game_stat S3 on team1_champ3_statId = S3.statId
    left join champ_game_stat S4 on team1_champ4_statId = S4.statId
    left join champ_game_stat S5 on team1_champ5_statId = S5.statId
    left join champ_game_stat S6 on team2_champ1_statId = S6.statId
    left join champ_game_stat S7 on team2_champ2_statId = S7.statId
    left join champ_game_stat S8 on team2_champ3_statId = S8.statId
    left join champ_game_stat S9 on team2_champ4_statId = S9.statId
    left join champ_game_stat S10 on team2_champ5_statId = S10.statId;
        '''
    db = MySqLHelper()
    result = db.selectall(sql)
    # print(result)
    with open('../DATA/game_data.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for item in tqdm(result, desc="Writing to csv."):
            writer.writerow(item)



if __name__ =="__main__":
    # summoner_stats()
    # missing_values("../DATA/all_champions.csv")
    # print(datetime.fromtimestamp(1601186435041/1000))
    get_game_data()