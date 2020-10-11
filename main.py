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

class main:

    def __init__(self):
        return

    def baseline(self):
        utils.print_info("Extracting Data.")
        ds = DataPreprocess()
        train_set = ds.get_baseline_train()
        test_set = ds.get_baseline_test()

        ss = StandardScaler()
        # training data
        train_X = train_set[:, 2:]
        train_y = train_set[:, 1]
        train_X  = ss.fit_transform(train_X)
        train_y = np_utils.to_categorical(train_y, 2)

        # testing data
        test_X = test_set[:, 2:]
        test_y = test_set[:, 1]
        test_X = ss.fit_transform(test_X)
        test_y = np_utils.to_categorical(test_y, 2)

        print(len(train_X[0]))
        # exit()
        # print(len(train_y))

        utils.print_info("Building baseline model.")
        # clf = LogisticRegression(random_state=0)
        # clf.fit(train_X, train_y)
        # y_pred = clf.predict(test_X)
        # print(clf.score(test_X, test_y))
        # print(confusion_matrix(test_y, y_pred))

        init = initializers.glorot_uniform(seed=1)
        model = Sequential()
        model.add(Dense(1500, input_dim=322, kernel_initializer=init,  activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(units=800, kernel_initializer=init, activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(units=100, kernel_initializer=init, activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(units=2, kernel_initializer=init, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer=RMSprop(), metrics=['accuracy'])
        model.summary()
        model.fit(train_X, train_y, batch_size=256, epochs=30,verbose=2)
        score = model.evaluate(test_X, test_y)
        print('Test score:', score[0])
        print('Test accuracy:', score[1])

    def NN_model(self):
        return


if __name__ == "__main__":
    main().baseline()



