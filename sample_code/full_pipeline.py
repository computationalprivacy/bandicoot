import sys
sys.path.append("../")

import bandicoot as bc
import glob
import os

records_path = 'users_bandicoot/'
antenna_file = 'antennas.csv'

indicators = []
for f in glob.glob(records_path + '*.csv'):
    user_id = os.path.basename(f)[:-4]

    try:
        B = bc.read_csv(user_id, records_path, antenna_file, describe=False)
        metrics_dict = bc.utils.all(B)
    except Exception as e:
        metrics_dic = {'name': user_id, 'error': True}

    indicators.append(metrics_dict)

bc.io.to_csv(indicators, 'bandicoot_indicators_full.csv')
