#!/usr/bin/env python

import bandicoot as bc
import cgi
import hashlib
import os
import sys
import random
import shutil
import sqlite3

def store_upload_md(upload_hash):
    name = config.get_db_path()
    conn = sqlite3.connect(name)
    c = conn.cursor()
    c.execute("INSERT INTO uploads VALUES(filehash=?, upload_time=strftime('%s', 'now'), serve_time=NULL)", (upload_hash,))
    idout = cursor.lastrowid
    conn.commit()
    conn.close()
    return idout

def store_upload_success(key):
    name = config.get_db_path()
    conn = sqlite3.connect(name)
    c = conn.cursor()
    c.execute("""UPDATE uploads
                 SET serve_time=strftime('%s', 'now')
                 WHERE key=?""", (key,))
    c.commit()

def redact_correspondants(src, dest_path):
    contents = []
    with open(dest_path, 'w') as out:
        encoder = bc.helper.intmapper.IntMapper()
        heading = next(src)
        out.write(heading)
        fields = heading.split(",")
        assert("correspondent_id" in fields)
        redact_index = fields.index("correspondent_id")
        number_of_fields = len(fields)
        for line in src:
            if line.strip() == "":
                continue
            values = line.split(",")
            assert (len(values) == number_of_fields), values
            values[redact_index] = str(encoder.to_int(values[redact_index]))
            line_out = ",".join(values)
            contents.append(line_out)
            out.write(line_out)
    return encoder, "".join(contents)

print "Content-Type: text/html"
print ""


# Redirect all stdout and stderr to /dev/null

STDOUT = sys.stdout
sys.stdout = open(os.devnull, 'w')
print """If you are seeing this message, there is a problem with the setup.
Note that Windows often has a problem redirecting stdout.  Also note that
this file is intended to be run only on a server."""

HERE = os.path.dirname(os.path.realpath(__file__))
MAIN_OUT_DIR = os.path.join(HERE, "stuff")

# Get the file.
form = cgi.FieldStorage()
uploaded_data = form["csv"].file

# Store a redacted version of the file at a 'random' location.
temp_filename = str(random.getrandbits(256))
temp_filepath = os.path.join(MAIN_OUT_DIR, 'temp_csv', temp_filename)
encoder, contents = redact_correspondants(uploaded_data, temp_filepath)

# Move it to a permanent location based on the hash of the content.
permanent_filetitle = str(hashlib.md5(contents).hexdigest())
permanent_filename = permanent_filetitle+".csv"
permanent_filepath = os.path.join(MAIN_OUT_DIR, 'csv', permanent_filename)
shutil.move(temp_filepath, permanent_filepath)

# TODO: Add a record of the upload to the database. (This will help us
# get statistics on how many people re-upload the same file, etc.)

# load the CSV file as a bandicoot user for further processing.
def decode_name(inp):
    try:
        return encoder.to_object(int(inp))
    except ValueError:
        return "User"

user = bc.io.read_combined_csv_gps(permanent_filetitle, os.path.dirname(permanent_filepath), network=True)
bc.special.viz.export.export_viz_for_web(user, HERE, permanent_filetitle, decode_name, STDOUT)
