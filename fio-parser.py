#!/usr/bin/env python2.7

# (C)2014 Red Hat, Inc., Jan Tulak <jtulak@redhat.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# fio-parser
#
# run fio with --minimal 

import sys
import getopt
import fileinput
import re
from libparse import TestSuite

"""
This function prints results.
Change it for whatever you want to see.
"""
def parse(jobs):

	# print the layout
	print "iodepth\t%s\t%s\t%s" % (
			"read","write", "cpu_user"
		)
	
	for job_name in jobs:
		job = jobs[job_name]

		# parse the name of the job
		name_split = re.split("-", job.name)
		# and print just jobs that starts with "multi-" prefix
		if (name_split[1] == "multi"):
			print "%s\t%d\t%d\t%s" % (
					name_split[4],
					int(job.read_status.bandwidth.med()),
					int(job.write_status.bandwidth.med()),
					job.cpu_usage.user[0]
				)

#
#------------- End of the parse() function ---------------
#




def print_help():
	print "%s [-h] [-i|--input FILENAME]" % (sys.argv[0])


def main(argv):
	
	instream = None

	try:
		opts, args = getopt.getopt(argv,"hi:", ["input="])
	except getopt.GetoptError:
		print_help()
		sys.exit(2)

	for opt, arg in opts:
		if (opt == '-h'):
			print_help()
			sys.exit()
		elif (opt in ("-i","--input")):
			instream = open(arg)
	
	if (instream is None):
		instream = fileinput.input()

	# parse the data
	ts = TestSuite(instream)
	parse(ts.get_all())


if __name__ == "__main__":
	main(sys.argv[1:])
