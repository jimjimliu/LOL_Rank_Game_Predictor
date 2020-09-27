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

# directory where all generated and saved models at
MODEL_PATH = os.path.join(os.path.join(os.getcwd(), 'model'))
LABELS = ['agree', 'disagree', 'discuss', 'unrelated']
DATA_PATH = os.path.join(os.path.join(os.getcwd(), 'data'))
SUBMISSION_PATH = os.path.join(DATA_PATH, 'submissions')



def save_pkl_model(model, file_name, path=MODEL_PATH):
    '''
    save a model using python pickle

    :param model: (Object) the model to be saved
    :param file_name: (String) file name string
    :param path: (String) directory of position to save the model. Default=.../model
    :return: None
    '''
    if not os.path.exists(MODEL_PATH):
        os.mkdir(MODEL_PATH)

    with open(os.path.join(os.path.join(path, file_name)), 'wb') as handle:
        pickle.dump(model, handle)
    print(file_name, 'saved at: ', os.path.join(os.path.join(os.getcwd(), 'model', file_name)))

def load_pkl(file_name, path=MODEL_PATH):
    '''
    load an existing model using pickle

    :param file_name: (String) file name
    :param path: (String) directory where model is saved. Default=.../model
    :return: (Object) the model
    '''
    with open(os.path.join(path, file_name), 'rb') as handle:
        model_pkl = pickle.load(handle)

    return model_pkl

def read(filename):
    rows = []
    with open(os.path.join(DATA_PATH, filename), "r", encoding='utf-8') as table:
        r = DictReader(table)

        for line in r:
            rows.append(line)
    return rows

def missing_values(data_path):
    '''
    return the total count of missing values of each column

    :param data_path:
        (string)
    :return:
        (pandas.series)
    '''
    data = pd.read_csv(data_path)
    count = data.isnull().sum()
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
    check if the data set is balanced using the given column as label.
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
    populating database

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

# def populate_data():


    # sql = '''
    #     insert ignore into all_league_entry(`leagueId`, `queueType`, `tier`, `rank`,`summonerId`,`summonerName`,
    #     `leaguePoints`,`wins`,`losses`,`veteran`,`inactive`,`freshBlood`,`hotStreak`,`accountId`,`puuid`,`summonerLevel`)
    #     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
    # '''
    # CSV_FILE_PATH = SUMMONERS_DATA
    # df = pd.read_csv(CSV_FILE_PATH, skiprows=0)
    # data = [tuple(x) for x in df.to_numpy()]
    # utils.populate_db(sql, data)


    # sql = '''
    #     insert ignore into all_champion
    #     (`champion_id`, `version`,`key`,`name`,`title`,`tag1`,`tag2`,`hp`,`hpperlevel`,`mp`,`mpperlevel`,`movespeed`,`armor`,
    #     `armorperlevel`,`spellblock`,`spellblockperlevel`,`attackrange`,`hpregen`,`hpregenperlevel`,`mpregen`,`mpregenperlevel`,`crit`,
    #     `critperlevel`,`attackdamage`,`attackdamageperlevel`,`attackspeedperlevel`,`attackspeed`)
    #     values
    #     (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
    # '''
    # csv = "DATA/all_champions.csv"
    # df = pd.read_csv(csv, skiprows=0)
    # data = [tuple(x) for x in df.to_numpy()]
    # utils.populate_db(sql, data)

    # sql = '''
    #     insert ignore into RIOT.match_list
    #     (`accountId`,`platformId`,`gameId`,`champion`,`queue`,`season`,`timestamp`,`role`,`lane`)
    #     values
    #     (%s,%s,%s,%s,%s,%s,%s,%s,%s);
    # '''
    # csv = "DATA/match_list.csv"
    # df = pd.read_csv(csv)
    # data = [tuple(x) for x in df.to_numpy()]
    # utils.populate_db(sql, data)

    # sql = """
    #     insert ignore into RIOT.`match`
    #     (`gameId`,`gameDuration`,
    #     `team1_win`,`team1_firstBlood`,`team1_firstTower`,
    #     `team1_firstInhibitor`,`team1_firstBaron`,`team1_firstDragon`,`team1_firstRiftHerald`,
    #     `team1_towerKills`,`team1_inhibitorKills`,`team1_baronKills`,`team1_dragonKills`,`team1_vilemawKills`,
    #     `team1_riftHeraldKills`,`team1_dominionVictoryScore`,
    #     `team1_ban1`,`team1_ban2`,`team1_ban3`,`team1_ban4`,`team1_ban5`,
    #     `team1_champ1_championId`,`team1_champ2_championId`,`team1_champ3_championId`,
    #     `team1_champ4_championId`,`team1_champ5_championId`,`team1_champ1_statId`,`team1_champ2_statId`,
    #     `team1_champ3_statId`,`team1_champ4_statId`,`team1_champ5_statId`,`team2_win`,`team2_firstBlood`,
    #     `team2_firstTower`,`team2_firstInhibitor`,`team2_firstBaron`,`team2_firstDragon`,
    #     `team2_firstRiftHerald`,`team2_towerKills`,`team2_inhibitorKills`,`team2_baronKills`,`team2_dragonKills`,
    #     `team2_vilemawKills`,`team2_riftHeraldKills`,`team2_dominionVictoryScore`,`team2_ban1`,`team2_ban2`,`team2_ban3`,
    #     `team2_ban4`,`team2_ban5`,`team2_champ1_championId`,`team2_champ2_championId`,`team2_champ3_championId`,
    #     `team2_champ4_championId`,`team2_champ5_championId`,`team2_champ1_statId`,`team2_champ2_statId`,`team2_champ3_statId`,
    #     `team2_champ4_statId`,`team2_champ5_statId`)
    #     values
    #     (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
    #     ,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
    # """
    #
    # csv = 'DATA/matches.csv'
    # df = pd.read_csv(csv)
    # data = [tuple(np.asarray(x).astype(int).tolist()) for x in tqdm(df.to_numpy(), desc="Converting data to int.")]
    # utils.populate_db(sql, data)

    # sql = """
    #     insert ignore into RIOT.champ_game_stat
    #     (`statId`,`gameId`, `championId`, `spell1Id`, `spell2Id`, `item0`, `item1`, `item2`, `item3`, `item4`, `item5`,
    #     `item6`, `kills`, `deaths`, `assists`, `largestKillingSpree`, `largestMultiKill`, `killingSprees`,
    #     `longestTimeSpentLiving`, `doubleKills`, `tripleKills`, `quadraKills`, `pentaKills`, `unrealKills`,
    #     `totalDamageDealt`, `magicDamageDealt`, `physicalDamageDealt`, `trueDamageDealt`, `largestCriticalStrike`,
    #     `totalDamageDealtToChampions`, `magicDamageDealtToChampions`, `physicalDamageDealtToChampions`,
    #     `trueDamageDealtToChampions`, `totalHeal`, `totalUnitsHealed`, `damageSelfMitigated`,
    #     `damageDealtToObjectives`, `damageDealtToTurrets`, `visionScore`, `timeCCingOthers`, `totalDamageTaken`,
    #     `magicalDamageTaken`, `physicalDamageTaken`, `trueDamageTaken`, `goldEarned`, `goldSpent`, `turretKills`,
    #     `inhibitorKills`, `totalMinionsKilled`, `neutralMinionsKilled`, `neutralMinionsKilledTeamJungle`,
    #     `neutralMinionsKilledEnemyJungle`, `totalTimeCrowdControlDealt`, `champLevel`, `visionWardsBoughtInGame`,
    #     `sightWardsBoughtInGame`, `wardsPlaced`, `wardsKilled`, `firstBloodKill`, `firstBloodAssist`,
    #     `firstTowerKill`, `firstTowerAssist`, `firstInhibitorKill`, `firstInhibitorAssist`)
    #     values
    #     (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
    #     ,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
    # """
    # df = pd.read_csv('DATA/match_stat.csv')
    # data = [tuple(np.asarray(x).astype(int).tolist()) for x in tqdm(df.to_numpy(), desc="Converting data to int.")]
    # utils.populate_db(sql, data)

if __name__ =="__main__":
    summoner_stats()
    # missing_values("../DATA/all_champions.csv")
    # print(datetime.fromtimestamp(1600397242551/1000))
