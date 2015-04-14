import sys
sys.path.append("../")
import bandicoot as bc
import glob
import multiprocessing as mp
import os

records_path = 'users_bandicoot/'
antenna_file = 'antennas.csv'
number_of_processors = 8


def load_and_compute(f):
    user_id = os.path.basename(f)[:-4]
    try:
        B = bc.read_csv(user_id, records_path, antenna_file, describe=False)
        metrics_dic = bc.utils.all(B)
    except Exception as e:
        metrics_dic = {'name': user_id, 'error': True}
    return metrics_dic

user_list = sorted(glob.glob(records_path + '*.csv'))
indicators = []
pool = mp.Pool(number_of_processors)
indicators = pool.map_async(load_and_compute, user_list)
indicators = indicators.get()
pool.close()
pool.join()

bc.io.to_csv(indicators, 'bandicoot_indicators_mp.csv')
