from Config.config import SUMMONERS_DATA
import pandas as pd
import os
from UTIL import utils

class main:

    def __init__(self):
        sql = '''
            insert ignore into all_league_entry(`leagueId`, `queueType`, `tier`, `rank`,`summonerId`,`summonerName`,
            `leaguePoints`,`wins`,`losses`,`veteran`,`inactive`,`freshBlood`,`hotStreak`,`accountId`,`puuid`,`summonerLevel`)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        '''
        CSV_FILE_PATH = SUMMONERS_DATA
        header = ['leagueId', 'queueType', 'tier', 'rank', 'summonerId', 'summonerName',
                  'leaguePoints', 'wins', 'losses', 'veteran', 'inactive', 'freshBlood', 'hotStreak', 'accountId',
                  'puuid', 'summonerLevel']
        df = pd.read_csv(CSV_FILE_PATH, skiprows=1, names=header)
        data = [tuple(x) for x in df.to_numpy()]
        utils.populate_db(sql, data)








if __name__ == "__main__":
    main()
