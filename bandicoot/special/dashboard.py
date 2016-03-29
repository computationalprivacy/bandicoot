from shutil import copytree
import tempfile
import os

try:
    import http.server as SimpleHTTPServer
    import socketserver as SocketServer
except ImportError:
    import SimpleHTTPServer
    import SocketServer

import webbrowser

import bandicoot as bc
from collections import namedtuple
import itertools


def dashboard_data(user):
    """
    Compute indicators and statistics used by the dashboard and returns a
    dictionnary.
    """
    # For the dasboard, indicators are computed on a daily basis
    # and by taking into account empty time windows
    _range = bc.helper.group._group_range(user.records, 'day')
    export = {
        'name': 'me',
        'date_range': [x.strftime('%Y-%m-%d') for x in _range],
        'groupby': 'day',
        'indicators': {},
        'agg': {}
    }

    I = namedtuple('Indicator',
                   ['name', 'function', 'interaction', 'direction'])
    indicators_list = [
        I('nb_out_call', bc.individual.number_of_interactions, 'call', 'out'),
        I('nb_out_text', bc.individual.number_of_interactions, 'text', 'out'),
        I('nb_inc_call', bc.individual.number_of_interactions, 'call', 'in'),
        I('nb_inc_text', bc.individual.number_of_interactions, 'text', 'in'),
        I('nb_out_all', bc.individual.number_of_interactions,
          'callandtext', 'out'),
        I('nb_inc_all', bc.individual.number_of_interactions,
          'callandtext', 'in'),
        I('nb_all', bc.individual.number_of_interactions, 'callandtext', None),
        I('response_delay', bc.individual.response_delay_text, 'callandtext', None),
        I('response_rate', bc.individual.response_rate_text, 'callandtext', None),
        I('call_duration', bc.individual.call_duration, 'call', None),
        I('percent_initiated_interactions',
          bc.individual.percent_initiated_interactions, 'call', None),
        I('percent_initiated_conversations',
          bc.individual.percent_initiated_interactions, 'callandtext', None),
        I('active_day', bc.individual.active_days, 'callandtext', None),
        I('number_of_contacts', bc.individual.number_of_contacts,
          'callandtext', None),
        I('percent_nocturnal', bc.individual.percent_nocturnal,
          'callandtext', None),
        I('balance_of_contacts', bc.individual.balance_of_contacts,
          'callandtext', None),
    ]

    ARGS = {'groupby': 'day', 'summary': None, 'filter_empty': False}
    for i in indicators_list:
        if i.direction:
            rv = i.function(user, interaction=i.interaction,
                            direction=i.direction, **ARGS)
        else:
            rv = i.function(user, interaction=i.interaction, **ARGS)
        export['indicators'][i.name] = rv['allweek']['allday'][i.interaction]

    # Format percentages from [0, 1] to [0, 100]
    with_percentage = ['percent_initiated_interactions', 'percent_nocturnal',
                       'response_rate', 'call_duration',
                       'percent_initiated_conversations']
    for i in with_percentage:
        export['indicators'][i] = [None if x is None else x * 100
                                   for x in export['indicators'][i]]

    # Day by day network
    def groupby_day_correspondent(r):
        return (r.datetime.strftime('%Y-%m-%d'), r.correspondent_id)
    it = itertools.groupby(user.records, groupby_day_correspondent)
    export['network'] = [key + (len(list(value)), ) for key, value in it]

    return export


def build(user, directory=None):
    """
    Build a temporary directory with the dashboard. Returns the local path
    where files have been written.

    Examples
    --------

        >>> bandicoot.special.dashboard.build(U)
        '/var/folders/n_/hmzkw2vs1vq9lxs4cjgt2gmm0000gn/T/tmpsIyncS/public'

    """
    # Get dashboard directory
    current_file = os.path.realpath(__file__)
    current_path = os.path.dirname(current_file)
    dashboard_path = os.path.join(current_path, '../../dashboard_src')

    # Create a temporary directory if needed and copy all files
    if directory:
        dirpath = directory
    else:
        dirpath = tempfile.mkdtemp()

    copytree(dashboard_path + '/public', dirpath + '/public')

    # Export indicators
    data = dashboard_data(user)
    bc.io.to_json(data, dirpath + '/public/data/bc_export.json')

    return dirpath + '/public'


def server(user, port=4242):
    """
    Build a temporary directory with a dashboard and serve it over HTTP.

    Examples
    --------

        >>> bandicoot.special.dashboard.server(U)
        Successfully exported 1 object(s) to /var/folders/n_/hmzkw2vs1vq9lxs4cjgt2gmm0000gn/T/tmpdcPE38/public/data/bc_export.json
        Serving bandicoot dashboard at http://0.0.0.0:4242
    """
    dir = build(user)
    os.chdir(dir)

    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    try:
        httpd = SocketServer.TCPServer(("", port), Handler)
        print(("Serving bandicoot dashboard at http://0.0.0.0:{}".format(port)))
        webbrowser.open('0.0.0.0:{}'.format(port))
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("^C received, shutting down the web server")
        httpd.server_close()
