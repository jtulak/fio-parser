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


