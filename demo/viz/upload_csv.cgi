#!/usr/bin/env python

import bandicoot as bc
import cgi
import hashlib
import os
import sys
import random
import shutil

print "Content-Type: text"
print ""

HERE = os.path.dirname(os.path.realpath(__file__))
MAIN_OUT_DIR = os.path.join(HERE, "data_and_html")

def redact_correspondants(src, dest_path):
    contents = []
    with open(dest, 'w') as out:
        encoder = bc.helper.IntMapper()
        heading = next(src)
        out.write(heading)
        fields = heading.split(",")
        assert("correspondent_id" in fields)
        redact_index = fields.index("correspondent_id")
        number_of_fields = len(fields)
        for line in src:
            values = line.split(",")
            assert(len(values) == number_of_fields)
            values[redact_index] = encoder.to_int(values[redact_index])
            line_out = ",".join(values)
            contents.append(line_out)
            out.write(line_out)
    return encoder, "".join(contents)

# Get the file.
form = cgi.FieldStorage()
uploaded_data = form["csv"].file

# Store a redacted version of the file at a 'random' location.
temp_filename = str(random.getrandbits(1024))
temp_filepath = os.path.join(MAIN_OUT_DIR, 'temp_csv', temp_filename)
encoder, contents = redact_correspondants(uploaded_data, temp_filepath)

# Move it to a permanent location based on the hash of the content.
permanent_filename = str(hashlib.md5(contents).hexdigest())+".csv"
permanent_filepath = os.path.join(MAIN_OUT_DIR, 'csv', permanent_filename)
shutil.move(temp_filepath, permanent_filepath)
