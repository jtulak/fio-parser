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
from libfioparser.ValuesList import ValuesList
from libfioparser.Iter import Iter
from hurry.filesize import size, iec
from collections import namedtuple

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
		self.completion_latency_percentiles = ValuesList(unit="%")
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


