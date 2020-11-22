'''
Get live game data of a user using RIOT client API.
'''

from Config.riot_config import ACCESS_KEY
from riotwatcher import LolWatcher, ApiError
from urllib.error import HTTPError
import requests
import urllib3
import pandas as pd
import numpy as np
from OPGG_crawler import OPGG
from copy import deepcopy

class Live_Game():

    def __init__(self, summoner_name):
        '''

        :param summoner_name:
            (string) game user name, case insensitive
        '''
        self.__summoner_name = summoner_name
        self.lol_watcher = LolWatcher(ACCESS_KEY)
        self.__champions = pd.read_csv('DATA/all_champions.csv')

    def game_spectator(self):
        '''

            request active game data of a summoner using summoner's user name from RIOT API.

        :return:
            (dict), contains champions chosen and banned.
        '''

        # get summoner encrypted id using summoner name
        summonerApiv4 = self.lol_watcher.summoner
        user_info = summonerApiv4.by_name('NA1',self.__summoner_name)
        encrypted_id = user_info['id']

        spectatorApiV4 = self.lol_watcher.spectator
        active_game_data = []
        try:
            active_game_data = spectatorApiV4.by_summoner('NA1', encrypted_id)
        except:
            raise Exception

        participants = active_game_data['participants']
        banned_champs = active_game_data['bannedChampions']

        # get champion chosen and banned
        team1_champs, team2_champs, team1_ban, team2_ban = [], [], [], []
        team1_spells, team2_spells = {}, {}
        champ_info_dict = {}
        for item in participants:
            # print(item)
            if item['teamId'] == 100:
                team1_champs.append(item['championId'])
                team1_spells[item['championId']] = [item['spell1Id'], item['spell2Id']]
            else:
                team2_champs.append(item['championId'])
                team2_spells[item['championId']] = [item['spell1Id'], item['spell2Id']]


        for item in banned_champs:
            # print(item)
            if item['teamId'] == 100:
                team1_ban.append(item['championId'])
            else:
                team2_ban.append(item['championId'])

        result = {
            'team1_champs': team1_champs,
            'team2_champs': team2_champs,
            'team1_ban': team1_ban,
            'team2_ban': team2_ban,
            'team1_spells': team1_spells,
            'team2_spells': team2_spells
        }

        return result

    def live_game(self):
        '''

            Get active game data on a user's local machine.

        :return:
            (numpy array) active game stat. [team1's stats + team2's stats + each champion's stats]
            (numpy array) game linup. [champions chosen, banned, champions win rates]
        '''

        try:
            '''request for game information of a summoner using encypted ID from RIOT API'''
            team_info = self.game_spectator()
            '''
            try to request local native API for active game data, can only return data when there is a game in local machine
            it cannot request any other platform games, RIOT does not provide any APIs for checking others' game data
            '''
            content = self.get_all_game_data()
            # team_info = self.__test_server(content)
        except:
            raise Exception


        "-----------------------------------get active game data----------------------------------------"

        '''get champions lineup'''
        game_linup = self.__champion_linup(team_info)
        '''get team game map resources'''
        team1_res, team2_res = self.__get_team_stats(content, team_info)
        '''get champions game stats'''
        final_stat_result = self.__get_champions_stats(content, team_info)

        # for item in team1_res.items():
        #     print(item)
        # print()
        # for item in team2_res.items():
        #     print(item)
        # for item in final_stat_result.items():
        #     print(item)

        '''
            formulating the final feature set.
            Final feature set: [team1's stats + team2's stats + each champion's stats]
        '''
        team_data = list(team1_res.values()) + list(team2_res.values())
        for k, v in final_stat_result.items():
            for key, value in v.items():
                team_data += value

        return np.array([team_data]), np.array([game_linup])

    def __summoner_names(self, content_json, team1, team2):
        '''

            Extract 10 players' summoner names.

        :param team1:
            (array), team1 champions in integer format
        :param team2:
            (array), team2 champions in integer format
        :return:
            (array): team1 players summoner names
            (array): team2 players summoner names
        '''

        # champion data in all_champions.csv
        champions = self.__champions
        team1_champs, team2_champs = deepcopy(team1), deepcopy(team2)

        playerlist = content_json['allPlayers']

        team1_players, team2_players = set(), set()
        for item in playerlist:
            champion_key = champions.loc[champions['name'] == item['championName']]['key'].to_numpy()[0]
            if champion_key in team1_champs:
                team1_players.add(item['summonerName'])
                team1_champs.pop(team1_champs.index(champion_key))
            if champion_key in team2_champs:
                team2_players.add(item['summonerName'])
                team2_champs.pop(team2_champs.index(champion_key))


        return list(team1_players), list(team2_players)

    def __get_team_stats(self, content_json, team_info):
        '''

            From content_json, extract each team's game details.

        :param content_json:
            (json), active game data. example can be found at: https://static.developer.riotgames.com/docs/lol/liveclientdata_sample.json
        :param team_info:
            (dict), dictionary returned by game_spectator() function
        :return:
            (dict)
            (dict)
        '''

        team1_res = {
            'champ1_championId': 0,
            'champ2_championId': 0,
            'champ3_championId': 0,
            'champ4_championId': 0,
            'champ5_championId': 0,
            'ban1': 0,
            'ban2': 0,
            'ban3': 0,
            'ban4': 0,
            'ban5': 0,
            'firstBlood': 0,
            'firstTower': 0,
            'firstInhibitor': 0,
            'firstBaron': 0,
            'firstDragon': 0,
            'firstRiftHerald': 0,
            'towerKills': 0,
            'inhibitorKills': 0,
            'baronKills': 0,
            'dragonKills': 0,
            'totalKills': 0,
            'totalDeaths': 0,
            'totalGold': 0
        }
        team2_res = {
            'champ1_championId': 0,
            'champ2_championId': 0,
            'champ3_championId': 0,
            'champ4_championId': 0,
            'champ5_championId': 0,
            'ban1': 0,
            'ban2': 0,
            'ban3': 0,
            'ban4': 0,
            'ban5': 0,
            'firstBlood': 0,
            'firstTower': 0,
            'firstInhibitor': 0,
            'firstBaron': 0,
            'firstDragon': 0,
            'firstRiftHerald': 0,
            'towerKills': 0,
            'inhibitorKills': 0,
            'baronKills': 0,
            'dragonKills': 0,
            'totalKills': 0,
            'totalDeaths': 0,
            'totalGold': 0
        }

        "-----------------------------------get active game data----------------------------------------"
        team1_champs = team_info['team1_champs']
        team2_champs = team_info['team2_champs']
        team1_ban = team_info['team1_ban']
        team2_ban = team_info['team2_ban']

        # get champions chosen and banned
        for i in range(len(team1_champs)):
            team1_res['champ' + str(i + 1) + '_championId'] = team1_champs[i]
            team2_res['champ' + str(i + 1) + '_championId'] = team2_champs[i]
        for i in range(len(team1_ban)):
            team1_res['ban' + str(i + 1)] = team1_ban[i]
            team2_res['ban' + str(i + 1)] = team2_ban[i]

        # get team total kills
        team1_res['totalKills'], team2_res['totalKills'] = self.__team_totalKills(content_json,team1_champs, team2_champs)
        # get team total deaths
        team1_res['totalDeaths'], team2_res['totalDeaths'] = self.__team_totalDeaths(content_json,team1_champs, team2_champs)
        # get team total golds
        team1_res['totalGold'], team2_res['totalGold'] = self.__team_totalGold(content_json,team1_champs, team2_champs)


        "-----------------------------------get game events----------------------------------------"
        events = content_json['events']['Events']
        team1_players, team2_players = self.__summoner_names(content_json, team1_champs, team2_champs)

        # flags indicate whether the data has been labeled
        first_blood, first_tower, first_inhib, first_baron, first_dragon, first_rift=0,0,0,0,0,0

        for event in events:
            if event['EventName'] == 'FirstBlood' and not first_blood:
                if event['Recipient'] in team1_players:
                    team1_res['firstBlood'] = 1
                elif event['Recipient'] in team2_players:
                    team2_res['firstBlood'] = 1
                # mark first blood has been found
                first_blood = 1

            if event['EventName'] == 'TurretKilled':
                if not first_tower:
                    if event['KillerName'] in team1_players:
                        team1_res['firstTower'] = 1
                    elif event['KillerName'] in team2_players:
                        team2_res['firstTower'] = 1
                    else:
                        print(event['KillerName'])
                        killer_name = event['KillerName'].split('_')[1][:4]
                        # T100 means team 100
                        if killer_name == 'T100':
                            team1_res['firstTower'] = 1
                        else:
                            team2_res['firstTower'] = 1
                    first_tower = 1

                if event['KillerName'] in team1_players:
                    team1_res['towerKills'] += 1
                elif event['KillerName'] in team2_players:
                    team2_res['towerKills'] += 1
                else:
                    print(event['KillerName'])
                    killer_name = event['KillerName'].split('_')[1][:4]
                    # T100 means team 100
                    if killer_name == 'T100':
                        team1_res['towerKills'] += 1
                    else:
                        team2_res['towerKills'] += 1

            if event['EventName'] == 'DragonKill':
                if not first_dragon:
                    if event['KillerName'] in team1_players:
                        team1_res['firstDragon'] = 1
                    else:
                        team2_res['firstDragon'] = 1
                    first_dragon = 1

                if event['KillerName'] in team1_players:
                    team1_res['dragonKills'] += 1
                else:
                    team2_res['dragonKills'] += 1

            if event['EventName'] == 'InhibKilled':
                if not first_inhib:
                    if event['KillerName'] in team1_players:
                        team1_res['firstInhibitor'] = 1
                    elif event['KillerName'] in team2_players:
                        team2_res['firstInhibitor'] = 1
                    else:
                        print(event['KillerName'])
                        killer_name = event['KillerName'].split('_')[1][:4]
                        # T100 means team 100
                        if killer_name == 'T100':
                            team1_res['firstTower'] = 1
                        else:
                            team2_res['firstTower'] = 1
                    first_inhib = 1

                if event['KillerName'] in team1_players:
                    team1_res['inhibitorKills'] += 1
                elif event['KillerName'] in team2_players:
                    team2_res['inhibitorKills'] += 1
                else:
                    print(event['KillerName'])
                    killer_name = event['KillerName'].split('_')[1][:4]
                    # T100 means team 100
                    if killer_name == 'T100':
                        team1_res['inhibitorKills'] += 1
                    else:
                        team2_res['inhibitorKills'] += 1

            if event['EventName'] == 'BaronKill':
                if not first_baron:
                    if event['KillerName'] in team1_players:
                        team1_res['firstBaron'] = 1
                    else:
                        team2_res['firstBaron'] = 1
                    first_baron = 1

                if event['KillerName'] in team1_players:
                    team1_res['baronKills'] += 1
                else:
                    team2_res['baronKills'] += 1

            if event['EventName'] == 'HeraldKill' and not first_rift:
                if event['KillerName'] in team1_players:
                    team1_res['firstRiftHerald'] = 1
                else:
                    team2_res['firstRiftHerald'] = 1
                first_rift = 1

        return team1_res, team2_res

    def __get_champions_stats(self, content_json, team_info):
        '''

            From content_json, extract champions game stats.

        :param content_json:
            (json), active game data. example can be found at: https://static.developer.riotgames.com/docs/lol/liveclientdata_sample.json
        :param team_info:
            (dict), data returned by game_spectator() function.
        :return:
            (dict)
        '''

        # get champion ids
        team1_champs = team_info['team1_champs']
        team2_champs = team_info['team2_champs']

        '''store each champions game stat'''
        final_stat_result = {
            'team1': {},
            'team2': {}
        }
        '''dictionary to store each champion's game stats'''
        champ_stat = {
            # 'spell1Id': 0,
            # 'spell2Id': 0,
            # 'item0': 0,
            # 'item1': 0,
            # 'item2': 0,
            # 'item3': 0,
            # 'item4': 0,
            # 'item5': 0,
            # 'item6': 0,
            # 'kills': 0,
            # 'deaths': 0,
            # 'goldSpent': 0,
            # 'assists': 0,
            # 'largestKillingSpree': 0,
            # 'largestMultiKill': 0,
            'doubleKills': 0,
            'tripleKills': 0,
            'quadraKills': 0,
            # 'killingSprees': 0,
            'pentaKills': 0,
            # 'totalDamageDealt': 0,
            # 'magicDamageDealt': 0,
            # 'physicalDamageDealt': 0,
            # 'trueDamageDealt': 0,
            # 'goldEarned': 0,
            # 'turretKills': 0,
            # 'inhibitorKills': 0,
            # 'totalMinionsKilled': 0,
            'champLevel': 0,
            # 'wards': 0,
        }

        champions = self.__champions
        all_players = content_json['allPlayers']

        # retrieve information from each champion's data
        for item in all_players:
            data = []
            # get champion integer key from champion's name
            champion_key = champions.loc[champions['name'] == item['championName']]['key'].to_numpy()[0]

            # get items of each champion
            # for i in range(len(item['items'])):
            #     champ_stat['item' + str(i)] = item['items'][i]['itemID']

            # get scores
            # scores = item['scores']
            # champ_stat['kills'] = scores['kills']
            # champ_stat['deaths'] = scores['deaths']
            # champ_stat['assists'] = scores['assists']
            # champ_stat['totalMinionsKilled'] = scores['creepScore']

            # level
            champ_stat['champLevel'] = item['level']

            # get multiple kills information of each player
            multi_kills = self.__get_multiple_kills(content_json, item['summonerName'])
            champ_stat['doubleKills'] = multi_kills['double']
            champ_stat['tripleKills'] = multi_kills['triple']
            champ_stat['quadraKills'] = multi_kills['quadra']
            champ_stat['pentaKills'] = multi_kills['penta']

            # adding to final result
            if champion_key in team1_champs and champion_key not in final_stat_result['team1'].keys():
                final_stat_result['team1'][champion_key] = list(champ_stat.values())
            else:
                final_stat_result['team2'][champion_key] = list(champ_stat.values())

            # clear dictionary
            for k, v in champ_stat.items():
                champ_stat[k] = 0

        return final_stat_result

    def __champion_linup(self, team_info):
        '''

            Formulate baseline features including [champions chosen + champions banned + champions win rates]

        :param team_info:
            (dict)
        :return:
            (np array), lenth of 30.
        '''

        team1_champs = team_info['team1_champs']
        team2_champs = team_info['team2_champs']
        team1_ban = team_info['team1_ban']
        team2_ban = team_info['team2_ban']

        champion_chosen = team1_champs + team2_champs

        # get winning rates
        id_wr = OPGG().champion_WR()

        win_rates = []
        for item in champion_chosen:
            win_rates.append([id_wr[item]])

        result = team1_champs+team1_ban+team2_champs+team2_ban+win_rates
        return np.array(result)

    def __team_totalKills(self, content_json, team1_champs, team2_champs):

        team1_players, team2_players = self.__summoner_names(content_json, team1_champs, team2_champs)
        team1_kills, team2_kills = 0, 0
        all_players = content_json['allPlayers']
        for item in all_players:
            scores = item['scores']
            if item['summonerName'] in team1_players:
                team1_kills += scores['kills']
            if item['summonerName'] in team2_players:
                team2_kills += scores['kills']

        return team1_kills, team2_kills

    def __team_totalDeaths(self, content_json, team1_champs, team2_champs):

        team1_players, team2_players = self.__summoner_names(content_json, team1_champs, team2_champs)
        team1_deaths, team2_deaths = 0, 0
        all_players = content_json['allPlayers']
        for item in all_players:
            scores = item['scores']
            if item['summonerName'] in team1_players:
                team1_deaths += scores['deaths']
            if item['summonerName'] in team2_players:
                team2_deaths += scores['deaths']

        return team1_deaths, team2_deaths

    def __team_totalGold(self, content_json, team1_champs, team2_champs):

        team1_players, team2_players = self.__summoner_names(content_json, team1_champs, team2_champs)
        team1_gold, team2_gold = 0, 0
        all_players = content_json['allPlayers']
        for player in all_players:
            items = player['items']
            if player['summonerName'] in team1_players:
                for item in items:
                    team1_gold += item['price']
            if player['summonerName'] in team2_players:
                for item in items:
                    team2_gold += item['price']

        return team1_gold, team2_gold

    def __get_multiple_kills(self, content, player_name):
        '''
            from https://127.0.0.1:2999/liveclientdata/allgamedata, the event timeline,
            get multiple kills information of the player.

        :param content:
            (dict)
        :param player_name:
            (string)
        :return:
            (dict)
        '''

        events = content['events']['Events']
        double, triple, quadra, penta = 0,0,0,0
        for item in events:
            if item['EventName'] == 'Multikill':
                if item['KillerName'] == player_name and item['KillStreak'] == 2:
                    double += 1
                elif item['KillerName'] == player_name and item['KillStreak'] == 3:
                    triple += 1
                elif item['KillerName'] == player_name and item['KillStreak'] == 4:
                    quadra += 1
                elif item['KillerName'] == player_name and item['KillStreak'] == 5:
                    penta += 1

        return {
            'double': double,
            'triple': triple,
            'quadra': quadra,
            'penta': penta
        }

    def __get_champs(self, content):

        champions = pd.read_csv('DATA/all_champions.csv')
        all_players = content['allPlayers']

        result = []
        for item in all_players:
            champion_key = champions.loc[champions['name'] == item['championName']]['key'].to_numpy()[0]
            result.append(champion_key)

        return result[:5], result[5:]

    def __test_server(self, content):
        team1_champs, team2_champs = self.__get_champs(content)
        result = {
            'team1_champs': team1_champs,
            'team2_champs': team2_champs,
            'team1_ban': [0,0,0,0,0],
            'team2_ban': [0,0,0,0,0]
        }
        return result

    def get_all_players(self):

        '''

            GET ​https://127.0.0.1:2999/liveclientdata/playerlist.
            Retrieve the list of heroes in the game and their stats.
            Only returns information when there is an active game on the local machine.
            Also, one can only request his/her own game using his/her summoner's name.
            RIOT does not provide a way to access others' game information.

        :return:
            (json) [
                        {
                            "championName": "Annie",
                            "isBot": false,
                            "isDead": false,
                            "items": [...],
                            "level": 1,
                            "position": "MIDDLE",
                            "rawChampionName": "game_character_displayname_Annie",
                            "respawnTimer": 0.0,
                            "runes": {...},
                            "scores": {...},
                            "skinID": 0,
                            "summonerName": "Riot Tuxedo",
                            "summonerSpells": {...},
                            "team": "ORDER"
                        },
                        ...
                    ]
        '''

        try:
            # get all players information from API
            res = requests.get('​https://127.0.0.1:2999/liveclientdata/allgamedata', verify='SSL_files/riotgames.pem')
            print(res)
            if res.status_code == 200:
                playerlist = res.json()
                return playerlist
            else:
                raise Exception
        except:
            raise Exception

    def get_all_game_data(self):
        '''

            GET https://127.0.0.1:2999/liveclientdata/allgamedata
            Get all available data.
            Only returns information when there is an active game on the local machine.
            Also, one can only request his/her own game using his/her summoner's name.
            RIOT does not provide a way to access others' game information.

        :return:
            (json), active game data. samples available here: https://static.developer.riotgames.com/docs/lol/liveclientdata_sample.json
        '''

        try:
            res = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify='SSL_files/riotgames.pem')
            if res.status_code == 200:
                # active game data
                content = res.json()
                return content
            else:
                raise Exception
        except:
            raise Exception

if __name__ == '__main__':
    data = Live_Game('jie mo').live_game()