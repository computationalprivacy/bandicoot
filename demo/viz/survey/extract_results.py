'''
This script extracts survey results from the database and stores them
in attributess files.
'''

import parse_survey
import sqlite3
import os

HERE = os.path.dirname(__file__)

def get_question_names(all_questions=False):
    file_path = os.path.join(HERE, "survey_questions.dat")
    with open(file_path, 'r') as f:
        survey = parse_survey.parse_survey(f)
        return [q.name for q in survey]

def get_results(all_questions=False):
    question_names = get_question_names(all_questions)
    conn = sqlite3.connect("survey_db.db")
    c = conn.cursor()
    all_hashes = [r[0] for r in c.execute("SELECT DISTINCT hash FROM responses")]
    query =     """
    SELECT answer FROM responses
    WHERE hash=? AND question=? error=0
    ORDER BY time DESC
    LIMIT 1
    """# For a given user and question, get their most recent valid answer that
       # is valid.
    for hash_code in all_hashes:
        # For each user who filled out the survey.
        with open(os.path.join(HERE, 'attributes', str(hash_code) + '.csv'), 'w') as attributes_file:
            for question in question_names:
                try:
                    q_result = c.execute(query, (hash_code, question))
                    answer = str(q_result.next()[0])
                except StopIteration:
                    # If there is no valid response, do nothing.
                    continue
                # Otherwise, store the valid response.
                attributes_file.write(question)
                attributes_file.write(",")
                attributes_file.write(answer)
                attributes_file.write("\n")
get_results()
