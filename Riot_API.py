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
from UTIL import utils
ENCODING = 'utf-8'
from Config.config import RANK_TIERS, DIVISIONS
import sys
from datetime import datetime
pd.set_option('display.max_rows', 10)

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
        apex_tier, queue, leagueId = '','',''

        # processing apex tiers
        if tier == 'MASTER':
            result = leagueApiv4.masters_by_queue('NA1', "RANKED_SOLO_5x5")
            entries = result['entries']
            apex_tier,queue,leagueId = result['tier'], result['queue'],result['leagueId']
        elif tier == 'GRANDMASTER':
            result = leagueApiv4.grandmaster_by_queue('NA1', "RANKED_SOLO_5x5")
            entries = result['entries']
            apex_tier, queue, leagueId = result['tier'], result['queue'], result['leagueId']
        elif tier == 'CHALLENGER':
            result = leagueApiv4.challenger_by_queue('NA1', "RANKED_SOLO_5x5")
            entries = result['entries']
            apex_tier, queue, leagueId = result['tier'], result['queue'], result['leagueId']
        else:
            # processing normal tiers
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
            if i%20 == 0 and i != 0:
                sleep(1.0)

            if tier in ("MASTER", "GRANDMASTER", "CHALLENGER"):
                entries[i]['leagueId'] = leagueId
                entries[i]['queueType'] = queue
                entries[i]['tier'] = apex_tier

            # re-organize data items and put into result
            for label in arr:
                if label in ('veteran', 'inactive', 'freshBlood', 'hotStreak'):
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

        start_page, end_page = 1, 10

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
        select accounts from DB, 1000 summoners at a time.
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
                select accountId from all_league_entry where id > {} and id <= {};
            '''.format(start_row, start_row+batch_size)
            summoner_acnt = db.selectall(sql_data)

            print("Selected {} rows from all_league_entry. ID: {} to {}.".format(len(summoner_acnt),start_row,start_row+batch_size))

            match_data, header = [], []
            for i in tqdm(range(len(summoner_acnt)), desc="Requesting matchlist of each account."):
                # sleep 1 second every 20 request, RIOT has a request limit of 20 request /second
                if i%20 == 0 and i!=0:
                    sleep(1.0)

                # convery binary string to string
                accountId = str(summoner_acnt[i][0], ENCODING)
                # API: https://developer.riotgames.com/apis#match-v4/GET_getMatchlist
                # get the most recent 100 matches from each account id
                matchlist = matchApiv4.matchlist_by_account(region="NA1", encrypted_account_id=accountId,queue=420)
                matches = matchlist['matches']

                if len(matches) == 0: continue

                # convert dict keys as header, convert just once. After header is assigned, turn flag to 1
                if not flag and len(matches) > 0:
                    header = ['accountId'] + list(matches[0].keys())
                    flag = 1

                for item in matches:
                    # change timestamp string to datetime
                    # code here
                    item['timestamp'] = datetime.fromtimestamp(item['timestamp'] / 1000)
                    values = [accountId] + list(item.values())
                    match_data.append(values)

            # write to csv every 1000 summoners, there's 100 matches returned for each summoner.
            utils.write_csv(header, match_data, 'DATA/match_list.csv')
            start_row += batch_size


        print("Finish retrieving matchlist from {} accounts.".format(row_count))

    def get_champions(self):
        '''
        Request all champions' data from RIOT.
        Store data in all_champions.csv.

        :return:
        '''

        data_dragon = self.lol_watcher.data_dragon
        all_champions = data_dragon.champions(version="10.19.1")
        print(all_champions)
        print(len(all_champions['data']))
        header = ['id', 'version','key','name','title','tag1','tag2','hp','hpperlevel','mp','mpperlevel','movespeed','armor',
                'armorperlevel','spellblock','spellblockperlevel','attackrange','hpregen','hpregenperlevel','mpregen','mpregenperlevel','crit',
                'critperlevel','attackdamage','attackdamageperlevel','attackspeedperlevel','attackspeed']
        csv = "DATA/all_champions.csv"

        result = []
        for item in all_champions['data'].values():
            arr = []
            stat = item['stats']
            for i in header[:5]:
                arr.append(item[i])

            arr.append(item['tags'][0])
            if len(item['tags']) > 1:
                arr.append(item['tags'][1])
            else:
                arr.append(item['tags'][0])

            for i in header[7:]:
                arr.append(stat[i])
            result.append(tuple(arr))

        utils.write_csv(header, result, csv)

    def get_match_by_id(self):
        '''
        From MySQL, retrieve match list, process 1000 matches at a time.
        use match id to request match details from RIOT;
        store match data in matches.csv, match_stat.csv

        :return:
        '''

        matchApiv4 = self.lol_watcher.match
        db = MySqLHelper()
        sql_count = '''
            select count(*) from RIOT.match_list;
        '''
        total_row = db.selectall(sql_count)[0][0]

        batch = 1000
        start = 0
        statId = 1

        # header of tabel "match"
        header = [
            "gameId","gameCreation","gameDuration",
            "team1_win","team1_firstBlood","team1_firstTower",
            "team1_firstInhibitor","team1_firstBaron","team1_firstDragon","team1_firstRiftHerald",
            "team1_towerKills","team1_inhibitorKills","team1_baronKills","team1_dragonKills","team1_vilemawKills",
            "team1_riftHeraldKills","team1_dominionVictoryScore",
            "team1_ban1","team1_ban2","team1_ban3","team1_ban4","team1_ban5",
            "team1_champ1_championId","team1_champ2_championId","team1_champ3_championId",
            "team1_champ4_championId","team1_champ5_championId","team1_champ1_statId","team1_champ2_statId",
            "team1_champ3_statId","team1_champ4_statId","team1_champ5_statId","team2_win","team2_firstBlood",
            "team2_firstTower","team2_firstInhibitor","team2_firstBaron","team2_firstDragon",
            "team2_firstRiftHerald","team2_towerKills","team2_inhibitorKills","team2_baronKills","team2_dragonKills",
            "team2_vilemawKills","team2_riftHeraldKills","team2_dominionVictoryScore","team2_ban1","team2_ban2","team2_ban3",
            "team2_ban4","team2_ban5","team2_champ1_championId","team2_champ2_championId","team2_champ3_championId",
            "team2_champ4_championId","team2_champ5_championId","team2_champ1_statId","team2_champ2_statId","team2_champ3_statId",
            "team2_champ4_statId","team2_champ5_statId"
        ]
        # intermidiate collection to store match data
        match_dict = {}
        for item in header:
            match_dict[item] = ''

        # header of table match_stat
        header_stat = [
            "statId","gameId", "championId", "spell1Id", "spell2Id", "item0", "item1", "item2", "item3", "item4", "item5",
            "item6", "kills", "deaths", "assists", "largestKillingSpree", "largestMultiKill", "killingSprees",
            "longestTimeSpentLiving", "doubleKills", "tripleKills", "quadraKills", "pentaKills", "unrealKills",
            "totalDamageDealt", "magicDamageDealt", "physicalDamageDealt", "trueDamageDealt", "largestCriticalStrike",
            "totalDamageDealtToChampions", "magicDamageDealtToChampions", "physicalDamageDealtToChampions",
            "trueDamageDealtToChampions", "totalHeal", "totalUnitsHealed", "damageSelfMitigated",
            "damageDealtToObjectives", "damageDealtToTurrets", "visionScore", "timeCCingOthers", "totalDamageTaken",
            "magicalDamageTaken", "physicalDamageTaken", "trueDamageTaken", "goldEarned", "goldSpent", "turretKills",
            "inhibitorKills", "totalMinionsKilled", "neutralMinionsKilled", "neutralMinionsKilledTeamJungle",
            "neutralMinionsKilledEnemyJungle", "totalTimeCrowdControlDealt", "champLevel", "visionWardsBoughtInGame",
            "sightWardsBoughtInGame", "wardsPlaced", "wardsKilled", "firstBloodKill", "firstBloodAssist",
            "firstTowerKill", "firstTowerAssist", "firstInhibitorKill", "firstInhibitorAssist"
        ]
        # intermediate collection to store match stat data
        match_stat_dict = {}
        for item in header_stat:
            match_stat_dict[item] = ''

        # select 1000 matches from DB a time
        while start < total_row:
            match, match_stat = pd.DataFrame([], columns=header), pd.DataFrame([], columns=header_stat)

            # select 1000 rows at a time
            sql_data = '''
                select gameId from RIOT.match_list where id > {} and id <= {};
            '''.format(start, start+batch)
            start += batch
            match_list = db.selectall(sql_data)

            # request 1000 match data of a match from RIOT
            for i in range(len(match_list)):
                # sleep for every 20 requests posted to the server of RIOT
                if i%20 == 0 and i!=0:
                    sleep(1.0)

                # request data from API
                game_data = matchApiv4.by_id(region='NA1', match_id=match_list[i][0])
                gameId = game_data['gameId']

                match_dict['gameId'] = game_data['gameId']
                match_dict['gameCreation'] = str(datetime.fromtimestamp(game_data['gameCreation'] / 1000))
                match_dict['gameDuration'] = game_data['gameDuration']

                # team 1 data
                team1 = game_data['teams'][0]
                team1_id = team1['teamId']
                team1_ban = [item['championId'] for item in team1['bans']]
                for item in team1:
                    if item not in ['teamId','bans']:
                        if team1[item] == 'Win' or team1[item] == True:
                            match_dict[str("team1_"+item)] = 1
                        elif team1[item] == 'Fail' or team1[item] == False:
                            match_dict[str("team1_"+item)] = 0
                        else:
                            match_dict[str("team1_" + item)] = team1[item]
                for i in range(1, len(team1_ban)+1):
                    match_dict["team1_ban"+str(i)] = team1_ban[i-1]

                # team 2 data
                team2 = game_data['teams'][1]
                team2_id = team2['teamId']
                team2_ban = [item['championId'] for item in team2['bans']]
                for item in team2:
                    if item not in ['teamId','bans']:
                        if team2[item] == 'Win' or team2[item] == True:
                            match_dict[str("team2_"+item)] = 1
                        elif team2[item] == 'Fail' or team2[item] == False:
                            match_dict[str("team2_"+item)] = 0
                        else:
                            match_dict[str("team2_" + item)] = team2[item]
                for i in range(1, len(team2_ban)+1):
                    match_dict["team2_ban"+str(i)] = team2_ban[i-1]

                # every match has 10 participants' data
                participants_data = game_data['participants']
                for item in participants_data:
                    if item['teamId'] == 100:
                        match_dict['team1_champ'+str(item['participantId'])+'_championId'] = item['championId']
                        match_dict['team1_champ'+str(item['participantId'])+'_statId'] = statId
                    elif item['teamId'] == 200:
                        match_dict['team2_champ'+str(item['participantId']-5)+'_championId'] = item['championId']
                        match_dict['team2_champ' + str(item['participantId']-5) + '_statId'] = statId

                    # add to match collection
                    match = match.append(match_dict, ignore_index=True)
                    print(match)
                    exit()

                    stats = item['stats']
                    stats['statId'] = statId
                    stats['championId'] = item['championId']
                    stats['spell1Id'], stats['spell2Id'] = item['spell1Id'], item['spell2Id']
                    stats['gameId'] = gameId
                    for item in stats:
                        if item in header_stat:
                            if stats[item] == False:
                                match_stat_dict[item] = 0
                            elif stats[item] == True:
                                match_stat_dict[item] = 1
                            else:
                                match_stat_dict[item] = stats[item]

                    statId += 1
                    for item in match_stat_dict.items():
                        print(item)

                print(game_data)
                for item in match_dict.items():
                    print(item)
                exit()

            # write to csv every 1000 matches
        return

if __name__ == "__main__":
    riot = Riot(access_key=ACCESS_KEY)

    for div in DIVISIONS:
        print(riot.get_league_entry(RANK_TIERS[0], div))

    # riot.get_champions()
    # riot.MATCH_V4()
    # riot.get_match_by_id()