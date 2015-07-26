#!/usr/bin/env python

import cgi
import string
import cgitb
cgitb.enable()

print "Content-Type: text/html"
print ""

page_str = """
<!DOCTYPE html>
<meta charset="utf-8">
<body>
        <form>
          <input type="hidden" id="fid" name="fid" value="$file_id" />
         </form>
	<script type="text/javascript" src="../bower_components/d3/d3.min.js"></script> 
	<script type="text/javascript" src="../bower_components/moment/min/moment.min.js"></script> 
	<script type="text/javascript" src="../bower_components/moment-range/lib/moment-range.min.js"></script> 
	<script type="text/javascript" src="../bower_components/papaparse/papaparse.min.js"></script> 
	<script type="text/javascript" src="../bower_components/science.js/science.v1.min.js"></script> 
	<script type="text/javascript" src="../bower_components/simple-statistics/src/simple_statistics.js"></script>

	<link type="text/css" href="axis.css" rel="stylesheet" />
	<script type="text/javascript" src="timeline.js"></script> 
</body>
"""


form = cgi.FieldStorage()
if "fid" in form:
    file_id = form["fid"].value
else:
    file_id = ""
out = string.Template(page_str).substitute(file_id=file_id)
print out
