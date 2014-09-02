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



# ----------------------------------------------------------------------------


# This class represents a value - which can have multiple runs
# and statistical properties can be evaluated on them.
class Value(list):
	def __init__(self, value = None):
		self._values = []
		self._min = None
		self._max = None
		self._q1 = None
		self._q3 = None
		self._med = None
		self._avg = None
		
		if (value is not None):
			self._values.append(value)

	def add(self, value):
		self._values.append(value)
		# Reset the statistical properties as they are invalid now.
		# But do not compute them until needed.
		self._min = None
		self._max = None
		self._q1 = None
		self._q3 = None
		self._med = None
		self._avg = None

	def min(self):
		if(self._min is None):
			self._min = min(self._values)
		return self._min

	def max(self):
		if(self._max is None):
			self._max = max(self._values)
		return self._max

	def avg(self):
		if(self._avg is None):
			self._avg = sum(self._values)/float(len(self._values))
		return self._avg

	def q1(self):
		if(self._q1 is None):
			self._q1 = numpy.percentile(self._values, 25)
		return self._q1

	def med(self):
		if(self._med is None):
			self._med = numpy.percentile(self._values, 50)
		return self._med

	def q3(self):
		if(self._q3 is None):
			self._q3 = numpy.percentile(self._values, 75)
		return self._q3

	def __str__(self):
		return str(self._values)
	
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
		self.total_io = Value()
		self.bandwidth = Value()
		self.iops = Value()
		self.runtime = Value()
		Latency = namedtuple("Latency", "min max mean deviation")
		LatencyBW = namedtuple("Latency", "min max mean percentage deviation")
		self.submission_latency = Latency(Value(), Value(), Value(), Value())
		self.completion_latency = Latency(Value(), Value(), Value(), Value())
		self.completion_latency_percentiles = Value()
		self.total_latency = Latency(Value(), Value(), Value(), Value())
		self.bw = LatencyBW(Value(), Value(), Value(), Value(), Value())

		if (fields is not None):
			self.add(fields)

	def add(self, fields):
		i = Iter(0)

		self.total_io.add(int( fields[int(i.inc())])*1024)
		self.bandwidth.add(int( fields[int(i.inc())])*1024)
		self.iops.add(int( fields[int(i.inc())]))
		self.runtime.add(int( fields[int(i.inc())]))

		self.submission_latency.min.add(int(fields[int(i.inc())]))
		self.submission_latency.max.add(int(fields[int(i.inc())]))
		self.submission_latency.mean.add(float(fields[int(i.inc())]))
		self.submission_latency.deviation.add(float(fields[int(i.inc())]))
		
		self.completion_latency.min.add(int(fields[int(i.inc())]))
		self.completion_latency.max.add(int(fields[int(i.inc())]))
		self.completion_latency.mean.add(float(fields[int(i.inc())]))
		self.completion_latency.deviation.add(float(fields[int(i.inc())]))

		self.completion_latency_percentiles.add(fields[int(i):int(i+20)])

		self.total_latency.min.add(int(fields[int(i.inc())]))
		self.total_latency.max.add(int(fields[int(i.inc())]))
		self.total_latency.mean.add(float(fields[int(i.inc())]))
		self.total_latency.deviation.add(float(fields[int(i.inc())]))
		
		self.bw.min.add(int(fields[int(i.inc())]))
		self.bw.max.add(int(fields[int(i.inc())]))
		self.bw.percentage.add(fields[int(i.inc())])
		self.bw.mean.add(float(fields[int(i.inc())]))
		self.bw.deviation.add(float(fields[int(i.inc())]))
		
		
	def __str__(self):
		return "Total IO: %sB, bandwidth: %sB/sec, IOPS: %d, runtime: %d msec" % (size(self.total_io,system=iec), size(self.bandwidth,system=iec), self.iops, self.runtime)

# ..............................

class DiskUtilization(object):
	def __init__(self, fields = None):
		self.disk_name = Value()
		self.read_ios = Value()
		self.write_ios = Value()
		self.read_merges = Value()
		self.write_merges = Value()
		self.read_ticks = Value()
		self.write_ticks = Value()
		self.time_in_queue = Value()
		self.utilization = Value()

		if (fields is not None):
			self.add(fields)

	def add(self, fields):
		i = Iter()
		self.disk_name.add(fields[int(i.inc())])
		self.read_ios.add(fields[int(i.inc())])
		self.write_ios.add(fields[int(i.inc())])
		self.read_merges.add(fields[int(i.inc())])
		self.write_merges.add(fields[int(i.inc())])
		self.read_ticks.add(fields[int(i.inc())])
		self.write_ticks.add(fields[int(i.inc())])
		self.time_in_queue.add(fields[int(i.inc())])
		self.utilization.add(fields[int(i.inc())])
	# TODO printing

# ..............................

class FioJob(object):
	def __init__(self, name):
		self.name = name
		self.read_status = RWStatus()
		self.write_status = RWStatus()
		
		self.cpu_usage = Value()

		self.io_depths=Value()
		self.io_lat_us=Value()
		self.io_lat_ms=Value()
		self.disk_utilization = DiskUtilization()
			
	def add(self, fields):
		i = Iter(2)
		i.set(5)
		self.read_status.add(fields[int(i):int(i+41)])
		self.write_status.add(fields[int(i):int(i+41)])

		CpuUsage = namedtuple("CpuUsage", "user system context_switches major_faults minor_faults")
		self.cpu_usage.add(CpuUsage(
				user =  fields[int(i.inc())],
				system =  fields[int(i.inc())],
				context_switches =  fields[int(i.inc())],
				major_faults =  fields[int(i.inc())],
				minor_faults =  fields[int(i.inc())],
			))

		self.io_depths.add({
				'1':fields[int(i.inc())],
				'2':fields[int(i.inc())],
				'4':fields[int(i.inc())],
				'8':fields[int(i.inc())],
				'16':fields[int(i.inc())],
				'32':fields[int(i.inc())],
				'64+':fields[int(i.inc())],
			})
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
			})
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
			})
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

