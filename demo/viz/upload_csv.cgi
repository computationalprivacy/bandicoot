#!/usr/bin/env python

import cgi
import hashlib
import bandicoot as bc
import os
import sys

print "Content-Type: text"
print ""

def get_file_string(file_h, limit=2000000):
    length = 0
    out = []
    while True:
        if length > limit:
            raise Exception, "File length limited to "+str(limit)
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
    raise Exception

file_hash = hashlib.md5(file_string).hexdigest()
with open("raw_csv/" + file_hash + ".csv", "w") as file_h:
    file_h.write(file_string)

# Get the user object. 
user = bc.io.read_csv(file_hash, "raw_csv", describe=False, warnings=False, errors=False)
bc.special.demo.export_antennas(user, 'mobility_dump', fid=file_hash)
bc.special.demo.export_transitions(user, 'mobility_dump', fid=file_hash)
bc.special.demo.export_timeline(user, 'event_dump', fid=file_hash)

print file_hash
