from Config.config import SUMMONERS_DATA
import pandas as pd
import os
from UTIL import utils
from MySQL_POOL.mysqlhelper import MySqLHelper

class main:

    def __init__(self):
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

        sql = '''
            insert ignore into RIOT.match_list
            (`accountId`,`platformId`,`gameId`,`champion`,`queue`,`season`,`timestamp`,`role`,`lane`)
            values
            (%s,%s,%s,%s,%s,%s,%s,%s,%s);
        '''
        csv = "DATA/match_list.csv"
        df = pd.read_csv(csv)
        data = [tuple(x) for x in df.to_numpy()]
        utils.populate_db(sql, data)

        # sql = """
        #     insert ignore into RIOT.match_list
        #     ("gameId","gameCreation","gameDuration",
        #     "team1_win","team1_firstBlood","team1_firstTower",
        #     "team1_firstInhibitor","team1_firstBaron","team1_firstDragon","team1_firstRiftHerald",
        #     "team1_towerKills","team1_inhibitorKills","team1_baronKills","team1_dragonKills","team1_vilemawKills",
        #     "team1_riftHeraldKills","team1_dominionVictoryScore",
        #     "team1_ban1","team1_ban2","team1_ban3","team1_ban4","team1_ban5",
        #     "team1_champ1_championId","team1_champ2_championId","team1_champ3_championId",
        #     "team1_champ4_championId","team1_champ5_championId","team1_champ1_statId","team1_champ2_statId",
        #     "team1_champ3_statId","team1_champ4_statId","team1_champ5_statId","team2_win","team2_firstBlood",
        #     "team2_firstTower","team2_firstInhibitor","team2_firstBaron","team2_firstDragon",
        #     "team2_firstRiftHerald","team2_towerKills","team2_inhibitorKills","team2_baronKills","team2_dragonKills",
        #     "team2_vilemawKills","team2_riftHeraldKills","team2_dominionVictoryScore","team2_ban1","team2_ban2","team2_ban3",
        #     "team2_ban4","team2_ban5","team2_champ1_championId","team2_champ2_championId","team2_champ3_championId",
        #     "team2_champ4_championId","team2_champ5_championId","team2_champ1_statId","team2_champ2_statId","team2_champ3_statId",
        #     "team2_champ4_statId","team2_champ5_statId")
        #     values
        #     (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
        #     ,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
        # """







if __name__ == "__main__":
    main()
