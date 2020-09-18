'''
    Retrieve data using APIs provided by RIOT: https://developer.riotgames.com/apis#match-v4/GET_getMatchlist
    Storing Data in DATA/summoner.csv, and MySQL DB.
'''


from riotwatcher import LolWatcher, ApiError
import riotwatcher
from Config.config import RANK_TIERS, DIVISIONS
from Config.riot_config import ACCESS_KEY
import pandas as pd
from DBUtils.PooledDB import PooledDB
from threading import Timer
from tqdm import tqdm
from time import sleep
import csv

class Riot:

    def __init__(self, access_key):
        self.access_key = access_key
        self.rank_tiers = RANK_TIERS
        self.division = DIVISIONS
        self.lol_watcher = LolWatcher(access_key)


    def __LEAGUE_EXP_V4(self, pages:tuple, tier, division):
        """

        :param pages:
        :param tier:
        :param division:
        :return:
        """

        leagueApiv4 = self.lol_watcher.league
        matchApiv4 = self.lol_watcher.match
        summonerApiv4 = self.lol_watcher.summoner

        entries = []
        for i in tqdm(range(pages[0], pages[1]), desc="Extracting Entries: "):
            # get league entries, each request returns about 200 rows
            result = leagueApiv4.entries(region="NA1", queue="RANKED_SOLO_5x5", tier=tier, division=division, page=i)
            # if no result, means API has retrieved everything, no more to request, return
            if len(result) == 0:
                break
            else:
                entries += result

        # if no results in entries, means nothing returned by the API, return
        if len(entries) == 0:
            return None
        print(len(entries), "summoners from page ", pages[0], " to ", pages[1])

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
        start_page, end_page = 61, 100
        # configure tier and divisions of summoners
        tier, division = self.rank_tiers[2], self.division[3]
        print(">>> Now extracting summoner information of [ {} {} ] from page {} to {}".format(tier, division,start_page,end_page))
        while start_page < end_page:
            # request summoner information from RIOT
            entries = self.__LEAGUE_EXP_V4((start_page, start_page+20), tier, division)
            # if no entries returned, means API retrieved nothing, stop
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
                    for item in tqdm(entries, desc="Writing to .csv"):
                        writer.writerow(item)
                # sleep every 20 requests
                sleep(1.0)
                start_page += 20

        print("Work finished, stop requesting from RIOT.")

    def MATCH_V4(self):
        return

if __name__ == "__main__":
    riot = Riot(access_key=ACCESS_KEY)
    print(riot.get_league_entry())
