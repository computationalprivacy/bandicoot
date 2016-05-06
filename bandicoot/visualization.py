# The MIT License (MIT)
#
# Copyright (c) 2015-2016 Massachusetts Institute of Technology.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from distutils.dir_util import copy_tree
import tempfile
import os

try:
    import http.server as SimpleHTTPServer
    import socketserver as SocketServer
except ImportError:
    import SimpleHTTPServer
    import SocketServer


from bandicoot.helper.tools import OrderedDict
from bandicoot.helper.group import _group_range
import bandicoot as bc
import itertools


def user_data(user):
    """
    Compute indicators and statistics used by the visualization
    and returns a dictionnary.
    """
    # For the dasboard, indicators are computed on a daily basis
    # and by taking into account empty time windows
    _range = _group_range(user.records, 'day')
    export = OrderedDict([
        ('name', 'me'),
        ('date_range', [x.strftime('%Y-%m-%d') for x in _range]),
        ('groupby', 'day'),
        ('indicators', OrderedDict()),
        ('agg', OrderedDict())
    ])

    class Indicator(object):
        def __init__(self, name, function, interaction=None, **args):
            self.name = name
            self.function = function
            self.interaction = interaction
            self.args = args

    I = Indicator
    import bandicoot.individual as iv

    indicators_list = [
        I('nb_out_call', iv.number_of_interactions, 'call', direction='out'),
        I('nb_out_text', iv.number_of_interactions, 'text', direction='out'),
        I('nb_inc_call', iv.number_of_interactions, 'call', direction='in'),
        I('nb_inc_text', iv.number_of_interactions, 'text', direction='in'),
        I('nb_out_all', iv.number_of_interactions, 'callandtext', direction='out'),
        I('nb_inc_all', iv.number_of_interactions, 'callandtext', direction='in'),
        I('nb_all', iv.number_of_interactions, 'callandtext'),
        I('response_delay', iv.response_delay_text, 'callandtext'),
        I('response_rate', iv.response_rate_text, 'callandtext'),
        I('call_duration', iv.call_duration, 'call'),
        I('percent_initiated_interactions', iv.percent_initiated_interactions, 'call'),
        I('percent_initiated_conversations', iv.percent_initiated_interactions, 'callandtext'),
        I('active_day', iv.active_days, 'callandtext'),
        I('number_of_contacts', iv.number_of_contacts, 'callandtext'),
        I('percent_nocturnal', iv.percent_nocturnal, 'callandtext'),
        I('balance_of_contacts', iv.balance_of_contacts, 'callandtext', weighted=False),
    ]

    ARGS = {'groupby': 'day', 'summary': None, 'filter_empty': False}
    for i in indicators_list:
        arguments = i.args
        arguments.update(ARGS)
        rv = i.function(user, interaction=i.interaction, **arguments)
        export['indicators'][i.name] = rv['allweek']['allday'][i.interaction]

    # Format percentages from [0, 1] to [0, 100]
    with_percentage = ['percent_initiated_interactions', 'percent_nocturnal',
                       'response_rate', 'balance_of_contacts',
                       'percent_initiated_conversations']

    def apply_percent(d):
        if isinstance(d, list):
            return [apply_percent(dd) for dd in d]
        elif d is None:
            return d
        else:
            return 100. * d

    for i in with_percentage:
        export['indicators'][i] = apply_percent(export['indicators'][i])

    # Day by day network
    def groupby_day_correspondent(r):
        return (r.datetime.strftime('%Y-%m-%d'), r.correspondent_id)
    it = itertools.groupby(user.records, groupby_day_correspondent)
    export['network'] = [list(key) + [len(list(value))] for key, value in it]

    return export


def export(user, directory=None, warnings=True):
    """
    Build a temporary directory with the visualization.
    Returns the local path where files have been written.

    Examples
    --------

        >>> bandicoot.visualization.export(U)
        Successfully exported the visualization to /tmp/tmpsIyncS

    """
    # Get dashboard directory
    current_file = os.path.realpath(__file__)
    current_path = os.path.dirname(current_file)
    dashboard_path = os.path.join(current_path, '../dashboard_src')

    # Create a temporary directory if needed and copy all files
    if directory:
        dirpath = directory
    else:
        dirpath = tempfile.mkdtemp()

    # Copy all files except source code
    copy_tree(dashboard_path + '/public', dirpath, update=1)

    # Export indicators
    data = user_data(user)
    bc.io.to_json(data, dirpath + '/data/bc_export.json', warnings=False)

    if warnings:
        print("Successfully exported the visualization to %s" % dirpath)

    return dirpath


def run(user, port=4242):
    """
    Build a temporary directory with a visualization and serve it over HTTP.

    Examples
    --------

        >>> bandicoot.visualization.run(U)
        Successfully exported the visualization to /tmp/tmpsIyncS
        Serving bandicoot visualization at http://0.0.0.0:4242
    """
    owd = os.getcwd()
    dir = export(user)
    os.chdir(dir)

    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    try:
        httpd = SocketServer.TCPServer(("", port), Handler)
        print("Serving bandicoot visualization at http://0.0.0.0:%i" % port)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("^C received, shutting down the web server")
        httpd.server_close()
    finally:
        os.chdir(owd)
