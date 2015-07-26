import string
import os
import bandicoot as bc
from nested import nested

def get_indicator_list_html(web=False):
    def node(tup):
        return ("<a href='' class='no_default'>" +
                tup[-1] + "</a>")
    indicators = bc.special.meta.indicator_tuples()
    return nested(indicators, node, node)

def get_indicator_html_page():
    here = os.path.dirname(__file__)
    template_path = os.path.join(here, 'resources', 'indicators',
                                 'dynamic', 'html_template.html')
    with open(template_path, "r") as temp:
        template_string = temp.read()
        template = string.Template(template_string)
        substitutions={
            "indicator_list": get_indicator_list_html()
        }
        return template.substitute(substitutions)
