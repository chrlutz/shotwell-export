#!/usr/bin/env python
# coding=utf-8

''' 

This file is part of shotwell-export.

Copyright 2017 Christoph Lutz <chrlutz@gmail.com>

shotwell-export is free software: you can redistribute it and/or modify it 
under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option)
any later version.

shotwell-export is distributed in the hope that it will be useful, but 
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
shotwell-export. If not, see http://www.gnu.org/licenses/.

'''

import os
import sys
import re
import sqlite3
import datetime
import argparse
from tqdm import tqdm

reload(sys)
sys.setdefaultencoding('utf-8')

parser = argparse.ArgumentParser(
	description='Imports events from a directory structure (that contains event information) into the Shotwell DB.')
parser.add_argument('-d', '--db', default='~/.local/share/shotwell/data/photo.db', help='location of photo.db, defaults to local user\'s')
parser.add_argument('-n', '--filename', default='{y}/{y}-{m}-{d} {event}/{file}', metavar='PATTERN', help='template for file path, defaults to {y}/{y}-{m}-{d} {event}/{file}')
args = parser.parse_args()

if not os.path.exists(args.db):
	sys.stderr.write('could not find photo.db. Check option --db.\r\n')
	sys.exit()

db = sqlite3.connect(args.db)
db.row_factory = sqlite3.Row
cur = db.cursor()

pattern = args.filename.replace("/", "\/")
pattern = pattern.format(
	y = "\d{4}",
        m = "\d{2}",
        d = "\d{2}",
        event = "([^/]*(\/[^/]*)*)",
        file = "[^/]*"
)
pattern = "^.*\/" + pattern + "$"
print(pattern)
pattern = re.compile(pattern, re.UNICODE)

cur.execute('''SELECT id, filename from PhotoTable ORDER BY filename''')
for row in tqdm(list(cur)):
	try:
		filename = row['filename']
		result = pattern.match(filename)
		if result:
			event = result.groups()[0]
			event = event.replace("_", " ")
			event = event.replace("/", " - ")
			print("match {}, {}".format(filename, event))
		elif filename.startswith('/home/clutz/pics/20'):
			print("no match: {}".format(filename))
		
	except Exception as e:
		sys.stderr.write(u'ERROR: Could not handle file {}\n'.format(row['filename']))
		raise e	