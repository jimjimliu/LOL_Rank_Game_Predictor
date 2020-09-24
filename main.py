from Config.config import SUMMONERS_DATA
import pandas as pd
import os
from UTIL import utils
from MySQL_POOL.mysqlhelper import MySqLHelper

class main:

    def __init__(self):
        sql = '''
            insert ignore into all_league_entry(`leagueId`, `queueType`, `tier`, `rank`,`summonerId`,`summonerName`,
            `leaguePoints`,`wins`,`losses`,`veteran`,`inactive`,`freshBlood`,`hotStreak`,`accountId`,`puuid`,`summonerLevel`)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
        '''
        CSV_FILE_PATH = SUMMONERS_DATA
        df = pd.read_csv(CSV_FILE_PATH, skiprows=0)
        data = [tuple(x) for x in df.to_numpy()]
        utils.populate_db(sql, data)


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







if __name__ == "__main__":
    main()
