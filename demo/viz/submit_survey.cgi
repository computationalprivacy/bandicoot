#!/usr/bin/env python
import cgi
import sqlite3
import config
import parse_survey

def get_responses(form, questions):
    fails = []
    out = []
    for question in questions:
        question_name = question.name
        error = False
        try:
            value = form[question_name].value
        except KeyError:
            continue

        try:
            value = question.convert_answer(value)
        except question.QuestionConversionError:
            # If the conversion is unsuccessful, log
            # an error.
            error = True
            fails.append(question_name)
        out.append((question_name, value, error))
    return out, fails

def store_responses(hash_id, questions):
    dbname = config.get_db_path()
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    for question, answer, error in questions:
        c.execute(
            """INSERT INTO responses
            (time, hash, question, answer, error)
            VALUES(
            strftime('%s', 'now'),?,?,?,?
            )""", (hash_id, question, answer, error))
    conn.commit()
    conn.close()

print "Content-Type: text/html"
print ""
with open(config.get_survey_path(), 'r') as survey_file:
    survey_questions = parse_survey.parse_survey(survey_file)
form = cgi.FieldStorage()
hash_id = form["hash"].value
responses, messages = get_responses(form, survey_questions)
store_responses(hash_id, responses)
