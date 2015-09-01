import os
import sqlite3

HERE = os.path.dirname(__file__)
survey_folder = "survey"
get_db_path = lambda: os.path.join(HERE, survey_folder, "survey_db.db")
get_survey_path = lambda: os.path.join(HERE, survey_folder, "survey_questions.dat")
