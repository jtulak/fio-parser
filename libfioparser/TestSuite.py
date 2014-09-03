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
from libfioparser import *
from libfioparser.FioJob import FioJob

import fileinput
import re
from collections import OrderedDict


class TestSuite(object):
	def __init__(self, f):
		# multiple runs of the same test suite
		self._results = OrderedDict()

		for line in f:
			self.parse_line(line)

	def parse_line(self,line):

		if (re.match("^3;fio", line)):
			cols = re.split(";", line)
			name = cols[2]
			#name_split = re.split("-", cols[2]))
			# if this job wasn't found yet, add it to the dict
			if (not name in self._results):
				self._results[name] = FioJob(name)
			# add the job into the list
			self._results[name].add(cols)

	# return list of all runs in a single list
	def get_all(self):
		return self._results

