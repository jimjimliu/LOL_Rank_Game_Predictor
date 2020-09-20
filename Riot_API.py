'''
    Retrieve data using APIs provided by RIOT: https://developer.riotgames.com/apis#match-v4/GET_getMatchlist
    Storing Data in DATA/summoner.csv, and MySQL DB.
'''


from riotwatcher import LolWatcher, ApiError
import riotwatcher
from Config.config import RANK_TIERS, DIVISIONS
from Config.riot_config import ACCESS_KEY, ACCESS_KEY2
import pandas as pd
from DBUtils.PooledDB import PooledDB
from threading import Timer
from tqdm import tqdm
from time import sleep
import csv
from MySQL_POOL.mysqlhelper import MySqLHelper
from UTIL.utils import utils
ENCODING = 'utf-8'
from Config.config import RANK_TIERS, DIVISIONS
import sys

class Riot:

    def __init__(self, access_key):
        # access key after you register on https://developer.riotgames.com
        self.access_key = access_key
        # riot watch API: https://riot-watcher.readthedocs.io/en/latest/riotwatcher/LeagueOfLegends/index.html
        self.lol_watcher = LolWatcher(access_key)


    def LEAGUE_EXP_V4(self, pages:tuple, tier, division):
        """
        Request data from [LEAGUE-EXP-V4] and [SUMMONER-V4] on https://developer.riotgames.com/apis#summoner-v4/GET_getBySummonerId.
        Request users' data using API provided by RIOT company.
        Data provided are the official datas stored by RIOT company.
        Request data of users' of rank [tier] and level [division].
        For example, tier=diamond, division=IV.

        :param pages:
            (int) the page for the query to paginate to. Starts at 1. Each page contains about 200 rows.
        :param tier:
            (string) rank tier. for example: diamond
        :param division:
            (string) rank tier level in roman numerals. for example: IV
        :return:
            list of tuples. [(), ()]
            each item in list contains information of a summoner's account.
        """

        # get API object
        leagueApiv4 = self.lol_watcher.league
        summonerApiv4 = self.lol_watcher.summoner

        # storing summoner information, [{}, {}]
        entries = []

        print("\nNow requesting from page {} to {}".format(pages[0], pages[1]))

        for i in tqdm(range(pages[0], pages[1]), desc="Extracting Entries: "):
            # get league entries, each request returns about 200 rows
            # API doc: https://riot-watcher.readthedocs.io/en/latest/riotwatcher/LeagueOfLegends
            #       /LeagueApiV4.html#riotwatcher._apis.league_of_legends.LeagueApiV4
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
            if i%20 != 0 or i==0:
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

    def get_league_entry(self, rank_tier, division):
        '''
        Call self.LEAGUE_EXP_V4() to request data from RIOT API.
        Request 100 pages from each tier-division. For example, request 100 pages for [diamond IV].
        Write returned data into summoner.csv

        :param rank_tier:
            (string) rank tier. For example: diamond
        :param division:
            (string) tier level in roman numerals. For example: IV
        :return:
            None
        '''

        start_page, end_page = 1, 100

        print(">>> Now extracting summoner information of [ {} {} ].".format(rank_tier, division))
        while start_page < end_page:
            # request summoner information from RIOT, 20 pages a time
            entries = self.LEAGUE_EXP_V4((start_page, start_page+20), rank_tier, division)
            # if no entries returned, means API retrieved nothing, stop
            if not entries:
                break
            else:
                # write data into csv
                header = ['leagueId', 'queueType', 'tier', 'rank', 'summonerId', 'summonerName',
                'leaguePoints', 'wins', 'losses', 'veteran', 'inactive', 'freshBlood','hotStreak','accountId', 'puuid', 'summonerLevel']
                utils.write_csv(header, entries, 'DATA/summoners.csv')

                # sleep every 20 requests
                sleep(1.0)
                start_page += 20

        print("Work finished, stop requesting from RIOT.")

    def MATCH_V4(self):
        '''
        select accounts from DB.
        Request 100 matchlist from each account.
        Store all the matchlist into match_list.csv.

        :return:
            None
        '''

        matchApiv4 = self.lol_watcher.match
        db = MySqLHelper()
        sql_count = '''
            select count(*) from RIOT.all_league_entry;
        '''
        # total rows in the table
        row_count = db.selectall(sql_count)[0][0]
        batch_size = 1000
        start_row, flag = 0, 0

        while start_row < row_count:
            # select 1000 rows at a time
            sql_data = '''
                select accountId from all_league_entry where id > {} limit {};
            '''.format(start_row, batch_size)
            summoner_acnt = db.selectall(sql_data)

            print("Selected {} rows from all_league_entry. ID: {} to {}.".format(len(summoner_acnt),start_row,start_row+batch_size))

            match_data, header = [], []
            for i in tqdm(range(len(summoner_acnt)), desc="Requesting matchlist of each account."):
                # sleep 1 second every 20 request, RIOT has a request limit of 20 request /second
                if i%20 != 0 or i == 0:
                    # convery binary string to string
                    accountId = str(summoner_acnt[i][0], ENCODING)
                    # API: https://developer.riotgames.com/apis#match-v4/GET_getMatchlist
                    # get the most recent 100 matches from each account id
                    matchlist = matchApiv4.matchlist_by_account(region="NA1", encrypted_account_id=accountId)
                    matches = matchlist['matches']

                    # convert dict keys as header, convert just once. After header is assigned, turn flag to 1
                    if not flag and len(matches) > 0:
                        header = ['accountId']+list(matches[0].keys())
                        flag = 1

                    for item in matches:
                        values = [accountId]+list(item.values())
                        match_data.append(values)

                else:
                    sleep(1.0)

            # write to csv every 1000 summoners, there's 100 matches returned for each summoner.
            utils.write_csv(header, match_data, 'DATA/match_list.csv')
            start_row += batch_size


        print("Finish retrieving matchlist from {} accounts.".format(row_count))

if __name__ == "__main__":
    riot = Riot(access_key=ACCESS_KEY)
    for div in ["II", "III", "IV"]:
        print(riot.get_league_entry(RANK_TIERS[1], div))

    # riot.MATCH_V4()