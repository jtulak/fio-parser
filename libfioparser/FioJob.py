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
from libfioparser.RWStatus import RWStatus
from libfioparser.DiskUtilization import DiskUtilization
from libfioparser.ValuesList import ValuesList
from libfioparser.Iter import Iter
from collections import namedtuple

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
		return  "%s\n"%(self.name)+\
				"READ status:\n"+\
				str(self.read_status)+\
				"\nWRITE status:\n"+\
				str(self.write_status)+\
				"\n"+\
				str(self.cpu_usage)+\
				""


