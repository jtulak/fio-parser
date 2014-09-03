fio-parser
==========

This program parse FIO output and allows easy access to the measured values,
to conduct any computations with them, or to print them in any format.

FIO must be run with --minimal argument for dense output. 
This program can either read it directly from stdin as in this example:
    fio test.fio --minimal | ./fio-parser.py

Or it can read the data from a file:
    ./fio-parser.py --input fio-test.out

If more jobs with the same name are found in the file, 
values are added to a set and basic statistics can be done with them:
- average value
- minimal and maximal value
- 1st, 2nd (median) and 3rd quartil

*Currently, percentile lists (like Read status completion latency percentiles)
are not available for the statistic. You can read them just as list of results
for each job run using index.*

Printing custom columns
=======================

The default behaviour, working with attached fio-test, is to print 
only median of read and write bandwidth in dependance on IO depth.
To change it or to do any computation on the data, see fio-parser.py file, 
function parse at the beginning of the file.

Getting some value is simple. For the bandwidth median, it is as easy as:
    job.read_status.bandwidth.med()

Requirements
============

These python libraries are required:
- Hurry
- Numpy

Author
======

(C)2014 Red Hat, Inc., Jan Tulak <jtulak@redhat.com>

