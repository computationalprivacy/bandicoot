import bandicoot as bc
from os.path import dirname, abspath, join

if __name__ == '__main__':
    empty_user = bc.User()
    empty_user.attributes['empty'] = True
    empty_path = join(dirname(abspath(__file__)), 'samples/empty_user.json')
    bc.io.to_json(bc.utils.all(empty_user, summary='extended', flatten=True), empty_path)

    sample_user = bc.tests.generate_user.sample_user()
    sample_path = join(dirname(abspath(__file__)), 'samples/sample_user_all_metrics.json')
    bc.io.to_json(bc.utils.all(sample_user, summary='extended', groupby=None, flatten=True), sample_path)
