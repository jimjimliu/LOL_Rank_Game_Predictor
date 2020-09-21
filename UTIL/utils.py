import os
import pickle
from csv import DictReader
import pandas as pd
from MySQL_POOL.mysqlhelper import MySqLHelper
from Config.config import SUMMONERS_DATA
from tqdm import tqdm
import csv
import os
from datetime import datetime

# directory where all generated and saved models at
MODEL_PATH = os.path.join(os.path.join(os.getcwd(), 'model'))
LABELS = ['agree', 'disagree', 'discuss', 'unrelated']
DATA_PATH = os.path.join(os.path.join(os.getcwd(), 'data'))
SUBMISSION_PATH = os.path.join(DATA_PATH, 'submissions')



def save_pkl_model(model, file_name, path=MODEL_PATH):
    '''
    save a model using python pickle

    :param model: (Object) the model to be saved
    :param file_name: (String) file name string
    :param path: (String) directory of position to save the model. Default=.../model
    :return: None
    '''
    if not os.path.exists(MODEL_PATH):
        os.mkdir(MODEL_PATH)

    with open(os.path.join(os.path.join(path, file_name)), 'wb') as handle:
        pickle.dump(model, handle)
    print(file_name, 'saved at: ', os.path.join(os.path.join(os.getcwd(), 'model', file_name)))

def load_pkl(file_name, path=MODEL_PATH):
    '''
    load an existing model using pickle

    :param file_name: (String) file name
    :param path: (String) directory where model is saved. Default=.../model
    :return: (Object) the model
    '''
    with open(os.path.join(path, file_name), 'rb') as handle:
        model_pkl = pickle.load(handle)

    return model_pkl

def read(filename):
    rows = []
    with open(os.path.join(DATA_PATH, filename), "r", encoding='utf-8') as table:
        r = DictReader(table)

        for line in r:
            rows.append(line)
    return rows

def missing_values(data_path):
    '''
    return the total count of missing values of each column

    :param data_path:
        (string)
    :return:
        (pandas.series)
    '''
    data = pd.read_csv(data_path)
    count = data.isnull().sum()
    print(count)
    return count

def write_csv(header, data, path):
    '''
    write into csv.
    General function.

    :param data: list of tuples. [(), ()]
    :param header: (list) []
    :param path: (string)
    :return:
    '''
    if len(data) == 0:
        print("0 rows has been written to .csv")

    with open(path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        # if no header, write header
        if csvfile.tell() == 0:
            writer.writerow(header)
        for item in tqdm(data, desc="Writing to .csv"):
            writer.writerow(item)

    print("{} rows has been written to {}".format(len(data), path))

def check_balanced(df, column):
    '''
    check if the data set is balanced using the given column as label.
    Return each label's distribution percentage to see if the dataset is balanced.
    :return:
        (Dict): dictionary has key=label_name, value=label percentage
    '''

    # vc is pandas series
    vc = df[column].value_counts()
    # row counts of df
    row_count = df.shape[0]

    result_dict = {}
    for i, v in vc.items():
        result_dict[i] = v, v/row_count

    return result_dict

def print_info(text=None):
    print("================================================")
    print("|                                              |")
    print("|", text, " "*(len("================================================")-len(text)-5) , "|")
    print("|                                              |")
    print("================================================")

def populate_db(sql, data):
    '''
    populating database

    :param sql:
        sql = insert ignore into all_league_entry(`col`) VALUES (%s)

    :param data: List of tuples or tuples, [(), ()], ((), ())
    :return:
        return rows affected after populating database
    '''

    if len(data) == 0:
        raise Exception("Data is empty.")

    db = MySqLHelper()
    start_index = 0
    # populate 1000 rows into database per time
    step = 1000
    while start_index < len(data):
        print("Populating row {} to {}.".format(start_index, start_index+step))
        result = db.insertmany(sql, data[start_index:start_index + step])
        print(result, " rows inserted.")
        start_index += step

    print("Finish populating.")

def summoner_stats():

    data = pd.read_csv(os.path.join("..", SUMMONERS_DATA))
    # total count of each tier
    tier_distribution = data.loc[:,'tier'].value_counts()
    # tiers in the data
    tier_label = tier_distribution.keys().to_numpy()

    print(tier_distribution)

    for tier in tier_label:
        # divisions so far in the data set
        divisions = data[data['tier'] == tier].loc[:, 'rank'].unique()
        for div in divisions:
            # count unique account id of each rank
            unique_account = data.query("tier=='{}' & rank=='{}'".format(tier, div)).loc[:, 'accountId'].nunique()
            print("[{} {}] {}".format(tier, div, unique_account))



if __name__ =="__main__":
    summoner_stats()
    # missing_values("../DATA/all_champions.csv")
    # print(datetime.fromtimestamp(1600397242551/1000))
