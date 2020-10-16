'''

From OPGG.com, scrap champions' winning rates.

'''

import scrapy
import pandas as pd

class OPGG():

    def __init__(self):
        self.path = ''

    def champion_WR(self):
        '''

        From OPGG.com, get champions' winning rates.

        :return:
            (dict), key: champion key, value: winning rate
        '''

        winrate = pd.read_csv('DATA/champ_winrate.csv', header=None)
        champions = pd.read_csv('DATA/all_champions.csv')
        winrate[2] = 0

        for index, row in winrate.iterrows():
            champion_key = champions.loc[champions['name'] == row[0]]['key'].to_numpy()[0]
            winrate.loc[index, 2] = champion_key

        df = winrate[[2, 1]]
        id_wr = {}
        # store the win rate in the dictionary, key is the champion id, value is the winning rate
        for index, row in df.iterrows():
            id_wr[int(row[2])] = round(row[1]/100,4)
        # print(id_wr)

        return id_wr

if __name__ == '__main__':
    OPGG().champion_WR()