import pandas as pd
import csv
import numpy as np
from UTIL import utils
from sklearn.model_selection import train_test_split
from copy import deepcopy
from tqdm import tqdm
from OPGG_crawler import OPGG


class DataPreprocess():
    match_cols = [
        # 'id', 'gameId', 'gameDuration',
        'team1_win',
        # 'team1_towerKills',
        # 'team1_inhibitorKills', 'team1_baronKills', 'team1_dragonKills','team1_vilemawKills', 'team1_riftHeraldKills',
        # 'team1_dominionVictoryScore',
        'team1_champ1_championId', 'team1_champ2_championId', 'team1_champ3_championId', 'team1_champ4_championId','team1_champ5_championId',
        'team1_ban1', 'team1_ban2', 'team1_ban3','team1_ban4', 'team1_ban5',
        # 'team1_champ1_statId', 'team1_champ2_statId', 'team1_champ3_statId','team1_champ4_statId', 'team1_champ5_statId',
        # 'team1_firstBlood', 'team1_firstTower', 'team1_firstInhibitor', 'team1_firstBaron', 'team1_firstDragon','team1_firstRiftHerald',
        # 'team2_win',
        # 'team2_towerKills', 'team2_inhibitorKills', 'team2_baronKills','team2_dragonKills', 'team2_vilemawKills', 'team2_riftHeraldKills',
        # 'team2_dominionVictoryScore',
        'team2_champ1_championId', 'team2_champ2_championId', 'team2_champ3_championId', 'team2_champ4_championId','team2_champ5_championId',
        'team2_ban1', 'team2_ban2', 'team2_ban3','team2_ban4', 'team2_ban5',
        # 'team2_champ1_statId', 'team2_champ2_statId', 'team2_champ3_statId','team2_champ4_statId', 'team2_champ5_statId',
        # 'team2_firstBlood', 'team2_firstTower', 'team2_firstInhibitor','team2_firstBaron', 'team2_firstDragon', 'team2_firstRiftHerald'
    ]
    match_stat_cols = [
        'statId',
        # 'gameId',
        # 'championId',
        'spell1Id', 'spell2Id',
        'item0', 'item1', 'item2', 'item3', 'item4', 'item5', 'item6',
        'kills', 'deaths', 'assists', 'largestKillingSpree', 'largestMultiKill',
        # 'longestTimeSpentLiving',
        'doubleKills', 'tripleKills', 'quadraKills', 'killingSprees', 'pentaKills',
        # 'unrealKills',
        'totalDamageDealt', 'magicDamageDealt', 'physicalDamageDealt', 'trueDamageDealt',
        # 'largestCriticalStrike',
        # 'totalDamageDealtToChampions', 'magicDamageDealtToChampions','physicalDamageDealtToChampions', 'trueDamageDealtToChampions',
        # 'totalHeal', 'totalUnitsHealed', 'damageSelfMitigated',
        # 'damageDealtToObjectives', 'damageDealtToTurrets', 'visionScore',
        # 'timeCCingOthers', 'totalDamageTaken', 'magicalDamageTaken',
        # 'physicalDamageTaken', 'trueDamageTaken',
        'goldEarned',
        # 'goldSpent',
        'turretKills', 'inhibitorKills', 'totalMinionsKilled',
        # 'neutralMinionsKilled', 'neutralMinionsKilledTeamJungle',
        # 'neutralMinionsKilledEnemyJungle', 'totalTimeCrowdControlDealt',
        'champLevel',
        # 'visionWardsBoughtInGame', 'sightWardsBoughtInGame',
        'wardsPlaced',
        #  'wardsKilled', 'firstBloodKill', 'firstBloodAssist',
        # 'firstTowerKill', 'firstTowerAssist', 'firstInhibitorKill',
        # 'firstInhibitorAssist'
    ]

    def __init__(self):
        self.matches_data_path = 'DATA/matches.csv'
        self.match_stat_path = 'DATA/match_stat.csv'
        self.game_data_path = 'DATA/game_data.csv'
        self.__train, self.__test = self.__reader()
        self.__baseline_train, self.__baseline_test = self.__baseline_data()

    def __reader(self):

        game_data = pd.read_csv(self.game_data_path, header=None).astype(int)
        game_data[game_data < 0] = 0

        # use target labels to uniformly split data set
        train, test = train_test_split(game_data, train_size=0.8, random_state=0,stratify=game_data[1])
        print(len(train), len(test))
        exit()

        # print(matches)
        # utils.missing_values(game_data)

        # check the data distribution using label
        # print(train.loc[:, 1].value_counts())

        return np.array(train), np.array(test)

    def __baseline_data(self):

        data = pd.read_csv(self.matches_data_path).astype(int)
        data[data < 0] = 0
        data = data[self.match_cols]

        cols = ['team1_champ1_championId', 'team1_champ2_championId','team1_champ3_championId', 'team1_champ4_championId','team1_champ5_championId',
                'team2_champ1_championId','team2_champ2_championId', 'team2_champ3_championId','team2_champ4_championId', 'team2_champ5_championId']
        # extract 10 champion ids and store in champ_ids
        champ_ids = data[cols].to_numpy()

        # get winning rates
        id_wr = OPGG().champion_WR()

        # store champions winning rates
        # win rates: [[winrate of champ1, winrate of champ2, ...], ...]
        win_rates = []
        for item in champ_ids:
            arr = [id_wr[i] for i in item]
            win_rates.append(arr)
        win_rates = pd.DataFrame(np.array(win_rates))

        # merge two df horizontally
        data = pd.concat([data,win_rates],axis=1)

        # use target labels to uniformly split data set
        train, test = train_test_split(data, train_size=0.8, random_state=0, stratify=data['team1_win'])

        return np.array(train), np.array(test)

    def get_train(self):
        return self.__train

    def get_test(self):
        return self.__test

    def get_baseline_train(self):
        return self.__baseline_train

    def get_baseline_test(self):
        return self.__baseline_test

if __name__ == '__main__':
    ds = DataPreprocess()