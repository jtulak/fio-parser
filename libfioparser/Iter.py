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

# BIG UGLY WARNING!!!
# This class is not entirely idempotential.
# Operations like "+" can act unexpectedly: 
#   "obj + 42" is in fact "obj = obj + 42; return obj"
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


