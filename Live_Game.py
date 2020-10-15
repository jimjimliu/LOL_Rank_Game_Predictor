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

class Live_Game():

    def __init__(self, summoner_name):
        '''

        :param summoner_name:
            (string) game user name, case insensitive
        '''
        self.__summoner_name = summoner_name
        self.lol_watcher = LolWatcher(ACCESS_KEY)

    def game_spectator(self):
        '''
            request active game data of a summoner using summoner's user name from RIOT API.

        :return:
            (array) champions chosen and champion banned
        '''

        # get summoner encrypted id using summoner name
        summonerApiv4 = self.lol_watcher.summoner
        user_info = summonerApiv4.by_name('NA1',self.__summoner_name)
        encrypted_id = user_info['id']

        spectatorApiV4 = self.lol_watcher.spectator
        active_game_data = []
        try:
            active_game_data = spectatorApiV4.by_summoner('NA1', encrypted_id)
            # print(active_game_data)
        except:
            # print("No active game data found.")
            raise Exception
            return

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
            (numpy array) active game stat
        '''

        team1_stat = {
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
            'firstDragon':0,
            'firstRiftHerald': 0,
            'towerKills': 0,
            'inhibitorKills': 0,
            'baronKills': 0,
            'dragonKills': 0
        }

        team2_stat = {
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
            'firstDragon':0,
            'firstRiftHerald': 0,
            'towerKills': 0,
            'inhibitorKills': 0,
            'baronKills': 0,
            'dragonKills': 0
        }

        champ_stat = {
            # 'spell1Id': 0,
            # 'spell2Id': 0,
            'item0': 0,
            'item1': 0,
            'item2': 0,
            'item3': 0,
            'item4': 0,
            'item5': 0,
            'item6': 0,
            'kills': 0,
            'deaths': 0,
            'assists': 0,
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
            'totalMinionsKilled': 0,
            'champLevel': 0,
            # 'wards': 0
        }

        # try to request RIOT API for active game data,data contains champion chosen and banned
        try:
            team_info = self.game_spectator()
            # team1_champs = team_info['team1_champs']
            # team2_champs = team_info['team2_champs']
            team1_ban = team_info['team1_ban']
            team2_ban = team_info['team2_ban']
            team1_spells = team_info['team1_spells']
            team2_spells = team_info['team2_spells']
            # for k,v in team_info.items():
            #     print(k, v)
        except:
            print("No active data found on RIOT API.")

        # try to request local native API for active game data, can only return data when there is a game in local machine
        # it cannot request any other platform games, RIOT does not provide any APIs for checking others games' data
        try:
            res = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify='SSL_files/riotgames.pem')
            if res.status_code == 200:
                # active game data
                content = res.json()
                # print(type(content))
            else:
                raise Exception
        except:
            print("No active game found for user.")
            return []


        "-----------------------------------get active game data----------------------------------------"

        team1_champs, team2_champs = self.__get_champs(content)

        # get champions chosen and banned
        for i in range(len(team1_champs)):
            team1_stat['champ'+str(i+1)+'_championId'] = team1_champs[i]
            team2_stat['champ' + str(i + 1) + '_championId'] = team2_champs[i]
        # for i in range(len(team1_ban)):
        #     team1_stat['ban'+str(i+1)] = team1_ban[i]
        #     team2_stat['ban' + str(i + 1)] = team2_ban[i]

        "get team game map resources"
        team1_res, team2_res = self.__get_team_resources(content, team1_champs, team2_champs)
        # update team stat dictionary, same key's value will be replace by the values in the new dictionary
        team1_stat = {**team1_stat, **team1_res}
        team2_stat = {**team2_stat, **team2_res}

        # read in champion file to get all champions of current version
        champions = pd.read_csv('DATA/all_champions.csv')
        all_players = content['allPlayers']

        # store the final champ_stat
        final_stat_result = {
            'team1': {},
            'team2': {}
        }

        # retrieve information from each champion's data
        for item in all_players:
            data = []
            # get champion integer key from champion's name
            champion_key = champions.loc[champions['name'] == item['championName']]['key'].to_numpy()[0]

            # adding spells to team data
            # if champion_key in team1_champs:
            #     champ_stat['spell1Id'] = team1_spells[champion_key][0]
            #     champ_stat['spell2Id'] = team1_spells[champion_key][1]
            # if champion_key in team2_champs:
            #     champ_stat['spell1Id'] = team2_spells[champion_key][0]
            #     champ_stat['spell2Id'] = team2_spells[champion_key][1]

            # get items of each champion
            for i in range(len(item['items'])):
                champ_stat['item'+str(i)] = item['items'][i]['itemID']

            # get scores
            scores = item['scores']
            champ_stat['kills'] = scores['kills']
            champ_stat['deaths'] = scores['deaths']
            champ_stat['assists'] = scores['assists']
            champ_stat['totalMinionsKilled'] = scores['creepScore']

            # level
            champ_stat['champLevel'] = item['level']

            # get multiple kills information of each player
            multi_kills = self.__get_multiple_kills(content, item['summonerName'])
            champ_stat['doubleKills'] = multi_kills['double']
            champ_stat['tripleKills'] = multi_kills['triple']
            champ_stat['quadraKills'] = multi_kills['quadra']
            champ_stat['pentaKills'] = multi_kills['penta']

            # adding to final result array
            if champion_key in team1_champs and champion_key not in final_stat_result['team1'].keys():
                final_stat_result['team1'][champion_key] = list(champ_stat.values())
            else:
                final_stat_result['team2'][champion_key] = list(champ_stat.values())

            # clear dictionary
            for k, v in champ_stat.items():
                champ_stat[k] = 0

        # for item in team1_stat.items():
        #     print(item)
        # print()
        # for item in team2_stat.items():
        #     print(item)
        # for item in final_stat_result.items():
        #     print(item)

        team_data = list(team1_stat.values()) + list(team2_stat.values())
        for k, v in final_stat_result.items():
            for key, value in v.items():
                team_data += value

        # print(np.array(team_data))
        # print(len(np.array(team_data)))
        return np.array(team_data)

    def __team_players(self, players_json, team1, team2):
        '''
            from player_json, get the players names of each team and return their player names.

        :param players_json:
        :param team1:
            (array), team1 champions in integer format
        :param team2:
            (array), team2 champions in integer format
        :return:
            (array): team1 players names
            (array): team2 players names
        '''
        champions = pd.read_csv('DATA/all_champions.csv')

        players = []
        team1_players, team2_players = [], []
        for item in players_json:
            champion_key = champions.loc[champions['name'] == item['championName']]['key'].to_numpy()[0]
            if champion_key in team1:
                team1_players.append(item['summonerName'])
            if champion_key in team2:
                team2_players.append(item['summonerName'])


        return team1_players, team2_players

    def __get_team_resources(self, content_json, team1, team2):

        team1_res = {
            'firstBlood': 0,
            'firstTower': 0,
            'firstInhibitor': 0,
            'firstBaron': 0,
            'firstDragon': 0,
            'firstRiftHerald': 0,
            'towerKills': 0,
            'inhibitorKills': 0,
            'baronKills': 0,
            'dragonKills': 0
        }
        team2_res = {
            'firstBlood': 0,
            'firstTower': 0,
            'firstInhibitor': 0,
            'firstBaron': 0,
            'firstDragon': 0,
            'firstRiftHerald': 0,
            'towerKills': 0,
            'inhibitorKills': 0,
            'baronKills': 0,
            'dragonKills': 0
        }
        events = content_json['events']['Events']
        players = content_json['allPlayers']
        team1_players, team2_players = self.__team_players(players, team1, team2)

        # flags indicate whether the data has been labeled
        first_blood, first_tower, first_inhib, first_baron, first_dragon, first_rift=0,0,0,0,0,0
        # first blood
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

    def __get_champs(self, content):

        champions = pd.read_csv('DATA/all_champions.csv')
        all_players = content['allPlayers']

        result = []
        for item in all_players:
            champion_key = champions.loc[champions['name'] == item['championName']]['key'].to_numpy()[0]
            result.append(champion_key)

        return result[:5], result[5:]

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


        return

if __name__ == '__main__':
    data = Live_Game('jie mo').live_game()