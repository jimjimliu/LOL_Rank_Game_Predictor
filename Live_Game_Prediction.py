from keras.models import load_model
from Live_Game import Live_Game
import numpy as np
from UTIL import utils

class GamePredict():

    def __init__(self, player_name, NN_model_path='MODELS/FNN.h5'):
        self.NN_model = NN_model_path
        self.player_name = player_name

    def predict(self):
        '''

        :return:
        '''

        "load the model from file"
        # load neural network
        NN_clf = load_model(self.NN_model)
        # load LR
        LR_clf = utils.load_pkl('LR', "MODELS")


        "get active game data"
        game_data = Live_Game(self.player_name).live_game()

        # if there is data returned, means there is an active game on native machine
        if len(game_data) != 0:
            # print(game_data)
            # print(len(game_data))

            NN_prob = NN_clf.predict(np.array([game_data]))
            LR_prob = LR_clf.predict_proba(np.array([game_data]))
            final_pred = np.divide(np.add(LR_prob, NN_prob), 2)
            print(final_pred)

            red_win_rate = round(final_pred[0][0], 10)
            blue_win_rate = round(final_pred[0][1], 10)
            print("Blue team win rate: {}".format(blue_win_rate))
            print("Red team win rate: {}".format(red_win_rate))


        else:
            print("No Active Game Found for User {}.".format(self.player_name))


        return




if __name__ == '__main__':
    model_path = "MODELS/FNN.h5"
    player_name = "jie mo"
    GamePredict(player_name, model_path).predict()