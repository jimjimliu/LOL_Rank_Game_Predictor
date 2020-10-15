from Config.config import SUMMONERS_DATA
import pandas as pd
import os
from UTIL import utils
from MySQL_POOL.mysqlhelper import MySqLHelper
from datetime import datetime
import numpy as np
from tqdm import tqdm
from DataPreprocess import DataPreprocess
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix
from keras.datasets import mnist
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D, MaxPooling2D
from keras.utils import np_utils
from keras import backend as K
from keras.optimizers import SGD, Adam, RMSprop
import gzip
import sys
from six.moves import cPickle
from keras import initializers

class Models:

    def __init__(self):
        return

    def baseline(self):
        '''
            Predict the winning rate of each team using simply the champions chosen and banned.

        :return:
        '''

        utils.print_info("Extracting Data.")
        ds = DataPreprocess()
        train = ds.get_baseline_train()
        test = ds.get_baseline_test()

        ss = StandardScaler()
        "training data"
        train_X = train[:, 1:]
        train_y = train[:, 0]
        train_X = ss.fit_transform(train_X)
        train_y = np_utils.to_categorical(train_y, 2)
        "test data"
        test_X = test[:, 1:]
        test_y = test[:, 0]
        y_true = test_y
        test_X = ss.fit_transform(test_X)
        test_y = np_utils.to_categorical(test_y, 2)

        utils.print_info("Building baseline model")
        "neural network"
        init = initializers.glorot_uniform(seed=1)
        model = Sequential()
        model.add(Dense(800, input_dim=20, kernel_initializer=init, activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(units=400, kernel_initializer=init, activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(units=100, kernel_initializer=init, activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(units=2, kernel_initializer=init, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer=RMSprop(), metrics=['accuracy'])
        model.summary()
        model.fit(train_X, train_y, batch_size=56, epochs=30, verbose=2)
        score = model.evaluate(test_X, test_y)
        print('Test score:', score[0])
        print('Test accuracy:', score[1])

        y_prob = model.predict(test_X)
        y_pred = np.argmax(y_prob, axis=-1)
        print(y_prob)
        print(confusion_matrix(y_true, y_pred))

        # save neural network
        model.save(os.path.join(os.getcwd(), 'MODELS', 'FNN_baseline.h5'))



    def build_FNN(self):
        utils.print_info("Extracting Data.")
        ds = DataPreprocess()
        train_set = ds.get_train()
        test_set = ds.get_test()

        ss = StandardScaler()
        # training data
        train_X = train_set[:, 2:]
        train_y = train_set[:, 1]
        y_train = train_y
        train_X  = ss.fit_transform(train_X)
        train_y = np_utils.to_categorical(train_y, 2)

        # testing data
        test_X = test_set[:, 2:]
        test_y = test_set[:, 1]
        y_test = test_y
        test_X = ss.fit_transform(test_X)
        test_y = np_utils.to_categorical(test_y, 2)

        # print(len(train_X[0]))
        # exit()
        # print(len(train_y))

        utils.print_info("Building model.")

        "logistic regression"
        clf = LogisticRegression(random_state=0)
        clf.fit(train_X, y_train)
        # predict the probability of each class
        y_pred_prob = clf.predict_proba(test_X)
        # predict class
        y_pred = clf.predict(test_X)
        print(clf.score(test_X, y_test))
        # print(confusion_matrix(y_test, y_pred))


        "neural network"
        init = initializers.glorot_uniform(seed=1)
        model = Sequential()
        model.add(Dense(1500, input_dim=200, kernel_initializer=init,  activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(units=800, kernel_initializer=init, activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(units=100, kernel_initializer=init, activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(units=2, kernel_initializer=init, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer=RMSprop(), metrics=['accuracy'])
        model.summary()
        model.fit(train_X, train_y, batch_size=56, epochs=30,verbose=2)
        score = model.evaluate(test_X, test_y)
        print('Test score:', score[0])
        print('Test accuracy:', score[1])

        # predict probability
        percentage_pred = model.predict(test_X)

        # get the binary prediction of labels in integer format
        # y_pred = np.argmax(model.predict(test_X), axis=-1)
        # print(confusion_matrix(y_test, y_pred))

        "combine two models"
        y_final_pred_prob = self.combine_models(y_pred_prob, percentage_pred)
        # print(y_final_pred_prob)
        y_final_pred = np.argmax(y_final_pred_prob, axis=-1)
        print(confusion_matrix(y_test, y_final_pred))

        "save the model"
        utils.print_info("Saving model.")
        # save neural network
        model.save(os.path.join(os.getcwd(), 'MODELS', 'FNN.h5'))
        # save LR
        utils.save_pkl_model(clf, 'LR', 'MODELS')

    def combine_models(self, LR_prob, NN_prob):
        '''
            combine the result prediction of two models.

        :param LR_prob:
            (np array)
        :param NN_prob:
            (np array)
        :return:
            (np array)
        '''

        return np.divide(np.add(LR_prob, NN_prob), 2)



if __name__ == "__main__":
    Models().baseline()
    # Models().build_FNN()


