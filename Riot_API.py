from riotwatcher import LolWatcher, ApiError
import riotwatcher
from Config import config
import pandas as pd
from DBUtils.PooledDB import PooledDB
from threading import Timer
from tqdm import tqdm
from time import sleep
from DATABASE.mysqlhelper import MySqLHelper
import csv

class Riot:

    def __init__(self, access_key):
        self.access_key = access_key
        self.rank_tiers = config.RANK_TIERS
        self.division = config.DIVISIONS
        self.lol_watcher = LolWatcher(access_key)


    def __LEAGUE_EXP_V4(self, pages:tuple):
        """
        get all league entries
        :return:
        """
        leagueApiv4 = self.lol_watcher.league
        matchApiv4 = self.lol_watcher.match
        summonerApiv4 = self.lol_watcher.summoner

        entries = []
        for i in tqdm(range(pages[0], pages[1]), desc="Extracting Entries: "):
            # get league entries, each request returns about 200 rows
            result = leagueApiv4.entries(region="NA1", queue="RANKED_SOLO_5x5", tier="SILVER", division='I', page=i)
            if len(result) == 0:
                break
            else:
                entries += result

        # if no results in entries, means nothing returned by the API, return
        if len(entries) == 0:
            return None
        print(len(entries), "pages from ", pages[0], " to ", pages[1])

        # for each summoner in entries, get their account information from API
        arr = ('leagueId', 'queueType', 'tier', 'rank', 'summonerId', 'summonerName',
                'leaguePoints', 'wins', 'losses', 'veteran', 'inactive', 'freshBlood','hotStreak')
        result, summoner_batch = [], []
        for i in tqdm(range(len(entries)), desc="Extracting account info: "):
            # RIOT limits max request is 20 times per second, sleep for every 20 requests
            if i%20 != 0:
                # re-organize data items and put into result
                for label in arr:
                    if label in ('veteran', 'inactive', 'freshBlood','hotStreak'):
                        if entries[i][label] == False:
                            result.append(0)
                        else:
                            result.append(1)
                    else:
                        result.append(entries[i][label])
                # request account information from API
                sum_info = summonerApiv4.by_id('NA1', entries[i]['summonerId'])
                for label in ('accountId', 'puuid', 'summonerLevel'):
                    result.append(sum_info[label])
                summoner_batch.append(tuple(result))
                result = []
            else:
                # sleep for every 20 requests
                sleep(1.0)

        return summoner_batch

    def get_league_entry(self):
        start_page, end_page = 1, 200
        while start_page < end_page:
            entries = self.__LEAGUE_EXP_V4((start_page, start_page+20))
            if not entries:
                break
            else:
                # write data into csv
                header = ['leagueId', 'queueType', 'tier', 'rank', 'summonerId', 'summonerName',
                'leaguePoints', 'wins', 'losses', 'veteran', 'inactive', 'freshBlood','hotStreak','accountId', 'puuid', 'summonerLevel']
                with open('DATA/summoners.csv', 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    if csvfile.tell() == 0:
                        writer.writerow(header)
                    for item in entries:
                        writer.writerow(item)
                # sleep every 20 requests
                sleep(1.0)
                start_page += 20


    def pop_db(self, sql, data):
        # insert result into mysql, if no database, comment the following section
        db = MySqLHelper()
        sql = '''
                    insert into all_league_entry(`leagueId`, `queueType`, `tier`, `rank`,`summonerId`,`summonerName`,
                    `leaguePoints`,`wins`,`losses`,`veteran`,`inactive`,`freshBlood`,`hotStreak`,`accountId`,`puuid`,`summonerLevel`) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                '''

        start_index = 0
        step = 100
        if len(data) > 0:
            while start_index < len(data):
                result = db.insertmany(sql, data[start_index:start_index + step])
                print(result, " rows inserted.")
                start_index += step

if __name__ == "__main__":
    riot = Riot(access_key="RGAPI-fe6b56d3-546c-4610-ab68-9baf3b34ac16")
    print(riot.get_league_entry())
