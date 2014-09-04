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
from libfioparser import *
import numbers
import numpy


""" This class represents a value - which can have multiple runs
	and statistical properties can be evaluated on them.

	Unit is an optional argument that can contain unit of the values, 
	like 'kB', or '%'.
"""
class ValuesList(list):
	def __init__(self, value = None, unit = ''):
		self._values = []														  
		self._unit = unit

		self._min = None
		self._max = None
		self._q1 = None
		self._q3 = None
		self._med = None
		self._avg = None

		# control flag, any string insertion switch it to false to prevents
		# statistical methods usage
		self._numeric = True

		if (value is not None):
			self._values.append(value)

	""" Add a new item into the list. If only_numeric is set to True,
		non-number values raise an exception.
	"""
	def add(self, value, only_numeric = True):
		if isinstance(value, numbers.Number):
			self._values.append(value)
		else:
			# try to convert input to numbers
			try:
				try:
					self._values.append(int(value))
				except ValueError:
					self._values.append(float(value))
			except (TypeError, ValueError):
				if only_numeric:
					raise Exception("Added value is not a number: %s" % str(value))
				self._values.append(value)
				self._numeric = False

		# Reset the statistical properties as they are invalid now.
		# But do not compute them until needed.
		self._min = None
		self._max = None
		self._q1 = None
		self._q3 = None
		self._med = None
		self._avg = None

	""" Get value of specific run (according index) with unit. 
		Shortcut for value[x]+value.unit().
	"""
	def s(self, key):
		 return str(self._values[key])+str(self._unit)

	def unit(self):
		return self._unit

	def min(self):
		if not self._numeric:
			raise Exception("ValuesLists are not numeric.")
		if(self._min is None):
			self._min = min(self._values)
		return self._min

	def max(self):
		if not self._numeric:
			raise Exception("ValuesLists are not numeric.")
		if(self._max is None):
			self._max = max(self._values)
		return self._max

	def avg(self):
		if not self._numeric:
			raise Exception("ValuesLists are not numeric.")
		if(self._avg is None):
			self._avg = sum(self._values)/float(len(self._values))
		return self._avg

	def q1(self):
		if not self._numeric:
			raise Exception("ValuesLists are not numeric.")
		if(self._q1 is None):
			self._q1 = numpy.percentile(self._values, 25)
		return self._q1

	def med(self):
		if not self._numeric:
			raise Exception("ValuesLists are not numeric.")
		if(self._med is None):
			self._med = numpy.percentile(self._values, 50)
		return self._med

	def q3(self):
		if not self._numeric:
			raise Exception("ValuesLists are not numeric.")
		if(self._q3 is None):
			self._q3 = numpy.percentile(self._values, 75)
		return self._q3

	def __str__(self):
		return str(self._values)+str(self._unit)

	def __len__(self):
		return len(self._values)

	def __getitem__(self, key):
		return self._values[key]

	def __iter__(self):
		for item in self._values:
			yield item

