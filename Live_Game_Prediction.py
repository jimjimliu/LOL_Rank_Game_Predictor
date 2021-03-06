from keras.models import load_model
import tensorflow as tf
from Live_Game import Live_Game
import numpy as np
from UTIL import utils
from sklearn.preprocessing import StandardScaler
import time

class GamePredict():

    def __init__(self, player_name):
        self.player_name = player_name

    def predict(self):
        '''

        :return:
        '''

        "load the model from file"
        # load neural network
        NN_clf = tf.keras.models.load_model("MODELS/FNN.h5")
        # load LR
        LR_clf = utils.load_pkl('LR', "MODELS")
        # load baseline
        BL_clf = tf.keras.models.load_model("MODELS/FNN_baseline.h5")
        # load naive bayes
        GNB_clf = utils.load_pkl('NB', 'MODELS')


        while True:

            try:
                "get active game data"
                game = Live_Game(self.player_name)
                game_data, game_lineup = game.live_game()
                # print(game_data)
                # print(len(game_data))

                # ss = StandardScaler()
                # start_data = ss.fit_transform(start_data)
                # game_data = ss.fit_transform(game_data)

                NN_prob = NN_clf.predict(game_data)
                LR_prob = LR_clf.predict_proba(game_data)
                # BL_prob = BL_clf.predict(game_lineup)
                # GNB_prob = GNB_clf.predict_proba(game_data)

                print("Neural network: ", NN_prob)
                print("Logistic regression: ", LR_prob)
                # print("baseline model: ", BL_prob)
                # print("Naive bayes: ", GNB_prob)

                final_pred = np.divide(np.add(NN_prob, LR_prob), 2)
                # print(final_pred)

                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
                red_win_rate = round(final_pred[0][0], 4)
                blue_win_rate = round(final_pred[0][1], 4)
                print("Blue team win rate: {}%".format(blue_win_rate*100))
                print("Red team win rate: {}%".format(red_win_rate*100))
                # predict every 1 minutes
                time.sleep(60)

            except Exception as e:
                print(e)
                print("No Active Game Found for User {}.".format(self.player_name))
                break

        return




if __name__ == '__main__':
    player_name = "jie mo"
    GamePredict(player_name).predict()