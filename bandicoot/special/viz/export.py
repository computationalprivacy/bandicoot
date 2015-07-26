import matplotlib
matplotlib.use('svg')
import matplotlib.pyplot as plt
import bandicoot as bc
import os
import shutil
import bandicoot as bc
import seaborn as sns
import numpy as np
import sys
import string

HERE = os.path.dirname(os.path.realpath(__file__))
FOLDER_NAME = 'my-bandicoot-viz'
SRC = os.path.join('resources', FOLDER_NAME)
BOWER_COMPONENTS = os.path.join('stuff', 'bower_compontents')

def _do_copy(overwrite, TARGET):
    # Perform sanity checks.
    assert os.path.isdir(SRC), "Check bandicoot installation"
    bower_components_abs = os.path.join(SRC, BOWER_COMPONENTS)
    assert os.path.isdir(bower_components_abs), "ERROR: Must install dependencies in the form of bower components.  Install Bower, then, in terminal, type 'cd " + os.path.dirname(bower_components_abs)+"; bower install'"
    assert overwrite or not(os.path.isdir(TARGET)), "There is already a folder at " + TARGET + ".  To over-write, set 'overwrite=True'"
    assert SRC != TARGET
    # Remove anything in the way of the target.
    if os.path.isdir(TARGET):
        shutil.rmtree(TARGET)

    # Do the copy. 
    shutil.copytree(SRC, TARGET)

def _do_csv_dumps(user, TARGET):
    stuff = os.path.join(TARGET, 'stuff');
    bc.special.demo.export_antennas(user, os.path.join(stuff, 'mobility_dump'))
    bc.special.demo.export_transitions(user, os.path.join(stuff, 'mobility_dump'))
    bc.special.demo.export_timeline(user, os.path.join(stuff, 'event_dump'))
    bc.special.demo.export_network(user, os.path.join(stuff, 'network_dump'))

def get_template(filepath):
    with open(filepath, 'r') as f:
        file_string = f.read()
    return string.Template(file_string)

def indicator_dumps_html(indicators, offline=True):
    node = lambda n: "<a href='' class='no_default'>" + n[-1] + "</a>"
    leaf = lambda l: "<a href='' class='no_default' onclick='switch_indicator(" + meta.get_name(l) + ")'>" + l[-1] + "</a>"
    indicator_listing_html = nested(indicators, node, leaf)
    with open(os.path.join(HERE, 'resources', 'templates', 'indicator_switch_script_offline.js')) as file_pointer:
        indicator_switch_js = file_pointer.read()
    out = get_template(os.path.join(HERE, 'resources', 'templates', 'indicator.html'))
    return out.substitute(indicator_switch_js=indicator_switch_js, indicator_list=indicator_list_html)

def _do_indicator_dumps(user, TARGET):
    exported = []
    indicators = os.path.join(TARGET, 'stuff', 'indicators')
    indicator_tuples = meta.indicator_tuples()
    for tup in indicator_tuples:
        name = meta.get_name(tup)
        func = meta.get_resource(tup)
        m = meta.get_indicator_meta(tup)

        data = func(user, groupby=None, summary=None)
        target = os.path.join(indicators, user_id + name)
        if m.kind == meta.distribution:
            exported.append(tup)
            with open(target + ".svg", 'wb') as file_target:
                export_histogram(data, m.axis, m.title, file_target)
            continue
    return exported

def export_histogram(data, x_axis, title, file_target):
    matplotlib.rcParams['ytick.labelsize'] = 12
    f, ax = plt.subplots(figsize=(12,8))
    sns.distplot(np.log(data['allweek']['allday']['call']), kde=True)
    plt.title(title, fontsize=35)
    plt.xlabel(x_axis, fontsize=20)
    plt.ylabel('PDF', fontsize=20)
    _ = plt.xticks(plt.xticks()[0], [int(np.exp(i)) for i in plt.xticks()[0]], fontsize=12)
    f.savefig(file_target)

def export_viz(user, overwrite=False):
    THERE = os.path.dirname(os.path.realpath(os.getcwd()))
    TARGET = os.path.join(THERE, FOLDER_NAME)
    _do_copy(overwrite, TARGET)
    _do_csv_dumps(user, TARGET)
    exported_indicators = _do_indicator_dumps(user, TARGET)
    indicator_html = indicator_dumps_html(exported_indicators)
    
    main_template = get_template(os.path.join(HERE, 'resources', 'templates', 'view.html'))
    main_output_filepath = os.path.join(TARGET, 'index.html')
    with open(main_output_filepath, 'w') as main_out:
        main_out_str = main_template.substitute(header_dump="", indicator_html=indicator_html)
        main_out.write(main_out_str)
    print "Export successful.  See the visualizations at " + main_out_filepath
