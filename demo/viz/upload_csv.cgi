#!/usr/local/bin/python

import cgi
import hashlib
import bandicoot as bc
import os
import sys

devnull = open(os.devnull, 'w')
stdout, stderr = os.stdout, os.stderr

def get_file_string(file_h, limit=2000000):
    length = 0
    out = []
    while True:
        if length > limit:
            raise Error, "File length limited to "+str(limit)
        line = file_h.readline()
        if not line: 
            break
        out.append(line)
        length += len(line)
    return "".join(out)


form = cgi.FieldStorage()

# Get the file and save it. 
if form["csv"].file:
    file_string = get_file_string(form["csv"].file)
else:
    raise Error
file_hash = hashlib.md5(file_string).hexdigest()[0:12]
with open("raw_csv/" + file_hash + ".csv", "w") as file_h:
    file_h.write(file_string)

# Get the user object. 
user = bc.io.read_gps(file_hash, "raw_csv", describe=False, warnings=False, errors=False)
bc.special.demo.export_antennas(user, 'mobility_dump')
bc.special.demo.export_transitions(user, 'mobility_dump')
bc.special.demo.export_timeline(user, 'network_dump')
