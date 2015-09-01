import matplotlib
matplotlib.use('svg')
import matplotlib.pyplot as plt
import bandicoot as bc
import os
import shutil
import seaborn as sns
import numpy as np
import tempfile
import webbrowser
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
FOLDER_NAME = 'my-bandicoot-viz'
SRC = os.path.join(HERE, 'resources', FOLDER_NAME)
BOWER_COMPONENTS = os.path.join('stuff', 'bower_components')

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

def _do_csv_dumps(user, targetfile, decode_name=lambda x: x):
    out = targetfile
    pre = """
    get_bandicoot_csv_file = function(){
    var map = new Object;
    """
    post = """return function(name, file_id){
                return map[name];
              }}();

    function bandicoot_is_csv_download_mode(){return false;}"""
    csv = bc.special.viz.csv
    out.write(pre)
    with tempfile.TemporaryFile() as antenna_file:
        out.write("map['antenna']='")
        csv.write_antenna_csv(user, antenna_file)
        antenna_file.seek(0)
        for line in antenna_file:
            out.write(line.replace("\n", "\\n"))
        out.write("';")
    with tempfile.TemporaryFile() as transitions_file:
        out.write("map['transitions']='")
        csv.write_transitions_csv(user, transitions_file)
        transitions_file.seek(0)
        for line in transitions_file:
            out.write(line.replace("\n", "\\n"))
        out.write("';")
    with tempfile.TemporaryFile() as timeline_file:
        out.write("map['timeline']='")
        csv.write_timeline_csv(user, timeline_file)
        timeline_file.seek(0)
        for line in timeline_file:
            out.write(line.replace("\n", "\\n"))
        out.write("';")
    with tempfile.TemporaryFile() as nodes_file:
        with tempfile.TemporaryFile() as links_file:
            csv.write_network_csv(user, nodes_file, links_file, decode_name)
            nodes_file.seek(0)
            links_file.seek(0)
            out.write("map['nodes']='")
            for line in nodes_file:
                out.write(line.replace("\n", "\\n"))
            out.write("';")
            out.write("map['links']='")
            for line in links_file:
                out.write(line.replace("\n", "\\n"))
            out.write("';")
    out.write(post)

def indicator_html(indicators, offline=True, uid=""):
    node = lambda n: "<a href='' class='no_default'>" + n[-1] + "</a>"
    leaf = lambda l: "<a href='' class='no_default' onclick='switch_indicator(\"" + uid + bc.special.meta.get_name(l) + "\")'>" + l[-1] + "</a>"
    indicator_list_html = bc.helper.nested.nested(indicators, node, leaf)
    with open(os.path.join(HERE, 'resources', 'templates', 'indicator_switch_script_offline.js')) as file_pointer:
        indicator_switch_js = file_pointer.read()
    out = bc.helper.tools.get_template(os.path.join(HERE, 'resources', 'templates', 'indicator.html'))
    return out.substitute(indicator_switch_js=indicator_switch_js, indicator_list=indicator_list_html)

def _move_indicator_html_blanks(TARGET):
    moves = [('network_index.html', 'network_dump'),
             ('mobility_index.html', 'mobility_dump'),
             ('event_index.html', 'event_dump')]
    for src, dest in moves:
        from_file = os.path.join(HERE, 'resources', 'templates', src)
        to_file = os.path.join(TARGET, 'stuff', dest, 'index.html')
        template = bc.helper.tools.get_template(from_file)
        with open(to_file, 'w') as file_h:
            output = template.substitute(file_id="")
            file_h.write(output)
            print "writing" + to_file

def do_indicator_dumps(user, TARGET, user_id=""):
    meta = bc.special.meta
    exported = []
    indicators = os.path.join(TARGET, 'stuff', 'indicators')
    indicator_tuples = meta.indicator_tuples()
    for tup in indicator_tuples:
        name = meta.get_name(tup)
        func = meta.get_resource(tup)
        m = meta.get_indicator_meta(tup)
        assert isinstance(user, bc.User)
        data = func(user, groupby=None, summary=None)['allweek']['allday']['call']
        try:#debug
            if len(data) <= 1:
                raise Exception
            if 0 in data:
                raise Exception
        except:
            continue
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
    sns.distplot(list(np.log(data)), kde=True)
    plt.title(title, fontsize=35)
    plt.xlabel(x_axis, fontsize=20)
    plt.ylabel('PDF', fontsize=20)
    _ = plt.xticks(plt.xticks()[0], [int(np.exp(i)) if np.exp(i) > 10 else round(float(np.exp(i)), 3) for i in plt.xticks()[0]], fontsize=12)
    f.savefig(file_target)

def export_viz(user, overwrite=False, show=True):
    THERE = os.path.realpath(os.getcwd())
    TARGET = os.path.join(THERE, FOLDER_NAME)
    _do_copy(overwrite, TARGET)
    # _move_indicator_html_blanks(TARGET)
    with open(os.path.join(TARGET, "stuff", "get_csv.js"), "w") as csv_file:
        _do_csv_dumps(user, csv_file)
    exported_indicators = do_indicator_dumps(user, TARGET)
    indicator_html_string = indicator_html(exported_indicators)

    main_template = bc.helper.tools.get_template(os.path.join(HERE, 'resources', 'templates', 'view.html'))
    main_output_filepath = os.path.join(TARGET, 'index.html')
    with open(main_output_filepath, 'w') as main_out:
        mobility_html = ""
        if user.has_antennas:
            mobility_html = """
            <h2>Mobility view</h2>
            <iframe src="stuff/mobility_dump/index.html" class="iframe_large" id="mobility_frame"></iframe>
            """
        main_out_str = main_template.substitute(header_dump="", indicator_html=indicator_html_string, mobility_html=mobility_html)
        main_out.write(main_out_str)
    print "Export successful.  See the visualizations at " + main_output_filepath
    if show:
        print "Opening browser. To avoid opening default browser in the future, call export_viz with keyword argument 'show=False'"
        webbrowser.open(main_output_filepath)

def export_viz_for_web(user, TARGET, uid, decode_name, main_out):
    exported_indicators = do_indicator_dumps(user, TARGET, uid)
    indicator_html_string = indicator_html(exported_indicators, uid=uid)
    with tempfile.TemporaryFile() as csv_file:
        _do_csv_dumps(user, csv_file, decode_name)
        csv_file.seek(0)
        indicator_data = csv_file.read()
    pre = "<script type='text/javascript'>"
    post = "</script>"
    indicator_js = pre + indicator_data + post
    main_template = bc.helper.tools.get_template(os.path.join(HERE, 'resources', 'templates', 'view.html'))
    view_page = main_template.substitute(header_dump=indicator_js, mobility_html="", indicator_html=indicator_html_string)
    main_out.write(view_page)
