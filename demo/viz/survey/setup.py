import sqlite3
import os
'''
Create two tables in the database located at 'survey_db.db' (the
db is created by the script and should not exist at runtime).
Creates tables 'uploads' and 'responses'.
'''


HERE = os.path.dirname(__file__)
db_path = os.path.join(HERE, "survey_db.db")
exists_already = os.path.isfile(db_path)
if exists_already:
    print "DB ALREADY CREATED.  EXITING"
    exit()
with open(db_path, "w+"):
    pass
conn = sqlite3.connect("survey_db.db")
c = conn.cursor()
c.execute("""CREATE TABLE uploads
(
key int AUTO_INCREMENT,
filehash string,
upload_time timestamp,
serve_time timestamp
);
""")
c.execute("""CREATE TABLE responses
(
time timestamp,
hash string,
question string,
answer string,
error boolean
)
""")
conn.commit()
conn.close()
