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


import fileinput
import re
from collections import namedtuple,OrderedDict
from hurry.filesize import size, iec
import numpy
import numbers


def is_number(obj):
	return isinstance(obj, numbers.Number)

# ----------------------------------------------------------------------------


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
		if is_number(value):
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

# ..............................

# BIG UGLY WARNING!!!
# This class is not entirely idempotential.
# Operations like "+" can act unexpectedly: 
# 	"obj + 42" is in fact "obj = obj + 42; return obj"
class Iter(object):
	def __init__(self, origin=0, step=1):
		self.origin = origin
		self.i = origin
		self.step = step

	# post increment, i++ replacement
	def inc(self):
		current = self.i
		self.i += self.step
		return current

	# pre increment with different step size
	def add(self, step):
		self.i += step
		return self.i 
	
	def set(self, val):
		self.i = val
		return val

	def __int__(self):
		return self.i 

	def __str__(self):
		return str(self.i)

	def __add__(self, other):
		self.i += int(other)
		return self.i
	
	def __radd__(self, other):
		return self.__add__(other)

	def __iadd__(self, other):
		return self.__radd__(other)

# ..............................

class RWStatus(object):
	def __init__(self, fields = None):
		self.total_io = ValuesList(unit="B")
		self.bandwidth = ValuesList(unit="B")
		self.iops = ValuesList()
		self.runtime = ValuesList(unit="ms")
		Latency = namedtuple("Latency", "min max mean deviation")
		LatencyBW = namedtuple("Latency", "min max mean percentage deviation")
		self.submission_latency = Latency(
				ValuesList(unit="ms"), 
				ValuesList(unit="ms"), 
				ValuesList(unit="ms"), 
				ValuesList(unit="ms")
				)
		self.completion_latency = Latency(
				ValuesList(unit="ms"), 
				ValuesList(unit="ms"), 
				ValuesList(unit="ms"), 
				ValuesList(unit="ms")
				)
		self.completion_latency_percentiles = ValuesList()
		self.total_latency = Latency(
				ValuesList(unit="ms"), 
				ValuesList(unit="ms"), 
				ValuesList(unit="ms"), 
				ValuesList(unit="ms")
				)
		self.bw = LatencyBW(
				ValuesList(unit="ms"), 
				ValuesList(unit="ms"), 
				ValuesList(unit="ms"), 
				ValuesList(unit="%"),
				ValuesList(unit="ms"),
				)

		if (fields is not None):
			self.add(fields)

	def add(self, fields):
		i = Iter(0)

		self.total_io.add(int( fields[int(i.inc())])*1024)
		self.bandwidth.add(int( fields[int(i.inc())])*1024)
		self.iops.add( fields[int(i.inc())])
		self.runtime.add( fields[int(i.inc())])

		self.submission_latency.min.add(fields[int(i.inc())])
		self.submission_latency.max.add(fields[int(i.inc())])
		self.submission_latency.mean.add(fields[int(i.inc())])
		self.submission_latency.deviation.add(fields[int(i.inc())])
		
		self.completion_latency.min.add(fields[int(i.inc())])
		self.completion_latency.max.add(fields[int(i.inc())])
		self.completion_latency.mean.add(fields[int(i.inc())])
		self.completion_latency.deviation.add(fields[int(i.inc())])

		self.completion_latency_percentiles.add(fields[int(i):int(i+20)], False)

		self.total_latency.min.add(fields[int(i.inc())])
		self.total_latency.max.add(fields[int(i.inc())])
		self.total_latency.mean.add(fields[int(i.inc())])
		self.total_latency.deviation.add(fields[int(i.inc())])
		
		self.bw.min.add(fields[int(i.inc())])
		self.bw.max.add(fields[int(i.inc())])
		self.bw.percentage.add(fields[int(i.inc())][:-1])
		self.bw.mean.add(fields[int(i.inc())])
		self.bw.deviation.add(fields[int(i.inc())])
		
		
	def __str__(self):
		return "Total IO: %sB, bandwidth: %sB/sec, IOPS: %d, runtime: %d msec" % (size(self.total_io,system=iec), size(self.bandwidth,system=iec), self.iops, self.runtime)

# ..............................

class DiskUtilization(object):
	def __init__(self, fields = None):
		self.disk_name = ValuesList()
		self.read_ios = ValuesList()
		self.write_ios = ValuesList()
		self.read_merges = ValuesList()
		self.write_merges = ValuesList()
		self.read_ticks = ValuesList()
		self.write_ticks = ValuesList()
		self.time_in_queue = ValuesList()
		self.utilization = ValuesList(unit="%")

		if (fields is not None):
			self.add(fields)

	def add(self, fields):
		i = Iter()
		self.disk_name.add(fields[int(i.inc())],False)
		self.read_ios.add(fields[int(i.inc())])
		self.write_ios.add(fields[int(i.inc())])
		self.read_merges.add(fields[int(i.inc())])
		self.write_merges.add(fields[int(i.inc())])
		self.read_ticks.add(fields[int(i.inc())])
		self.write_ticks.add(fields[int(i.inc())])
		self.time_in_queue.add(fields[int(i.inc())])
		self.utilization.add(fields[int(i.inc())][:-2]) # last item on line
	# TODO printing

# ..............................

class FioJob(object):
	def __init__(self, name):
		self.name = name
		self.read_status = RWStatus()
		self.write_status = RWStatus()
		
		CpuUsage = namedtuple("CpuUsage", "user system context_switches major_faults minor_faults")
		self.cpu_usage = CpuUsage(
				ValuesList(unit="%"),
				ValuesList(unit="%"),
				ValuesList(),
				ValuesList(),
				ValuesList(),
			)

		self.io_depths=ValuesList()
		self.io_lat_us=ValuesList()
		self.io_lat_ms=ValuesList()
		self.disk_utilization = DiskUtilization()
			
	def add(self, fields):
		i = Iter(2)
		i.set(5)
		self.read_status.add(fields[int(i):int(i+41)])
		self.write_status.add(fields[int(i):int(i+41)])

		self.cpu_usage.user.add(fields[int(i.inc())][:-1])
		self.cpu_usage.system.add( fields[int(i.inc())][:-1])
		self.cpu_usage.context_switches.add(fields[int(i.inc())])
		self.cpu_usage.major_faults.add(fields[int(i.inc())])
		self.cpu_usage.minor_faults.add(fields[int(i.inc())])

		self.io_depths.add({
				'1':fields[int(i.inc())],
				'2':fields[int(i.inc())],
				'4':fields[int(i.inc())],
				'8':fields[int(i.inc())],
				'16':fields[int(i.inc())],
				'32':fields[int(i.inc())],
				'64+':fields[int(i.inc())],
			}, False)
		self.io_lat_us.add({
				'2':fields[int(i.inc())],
				'4':fields[int(i.inc())],
				'10':fields[int(i.inc())],
				'20':fields[int(i.inc())],
				'50':fields[int(i.inc())],
				'100':fields[int(i.inc())],
				'250':fields[int(i.inc())],
				'500':fields[int(i.inc())],
				'750':fields[int(i.inc())],
				'1000':fields[int(i.inc())],
			}, False)
		self.io_lat_ms.add({
				'2':fields[int(i.inc())],
				'4':fields[int(i.inc())],
				'10':fields[int(i.inc())],
				'20':fields[int(i.inc())],
				'50':fields[int(i.inc())],
				'100':fields[int(i.inc())],
				'250':fields[int(i.inc())],
				'500':fields[int(i.inc())],
				'750':fields[int(i.inc())],
				'1000':fields[int(i.inc())],
				'2000':fields[int(i.inc())],
				'2000+':fields[int(i.inc())],
			},False)
		self.disk_utilization.add(fields[int(i):int(i+9)])

		# TODO what are the next fields?

	def __str__(self):
		return 	"%s\n"%(self.name)+\
				"READ status:\n"+\
				str(self.read_status)+\
				"\nWRITE status:\n"+\
				str(self.write_status)+\
				"\n"+\
				str(self.cpu_usage)+\
				""

# ..............................

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
# ----------------------------------------------------------------------------

