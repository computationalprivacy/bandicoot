#!/usr/bin/env python
import bandicoot as bc
import cgi
import parse_survey
import config
import os

print "Content-Type:text/html"
print ""

HERE = os.path.dirname(__file__)
file_hash = cgi.FieldStorage()["hash"].value
with open(config.get_survey_path(), 'r') as f:
    questions = parse_survey.parse_survey(f)
survey_body = "<br />".join(q.to_html() for q in questions)
survey_template = bc.helper.tools.get_template(os.path.join(HERE, "survey", "survey_template.html"))
print survey_template.substitute(file_hash=file_hash, survey_body=survey_body)
