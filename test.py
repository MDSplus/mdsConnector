#!/bin/env python
import sys
from time import time
from mdsconnector import mdsConnector

host = sys.argv[1]
samples = int(sys.argv[2])
if len(sys.argv) == 4:
    mdsip = sys.argv[3]
else:
    mdsip = None
c=mdsConnector(host)
if c.dill:
    usingDill="yes"
else:
    usingDill="no"

start=time()
d=c.Data.execute('random($)', samples).data()
end=time()
print("""
Speed test for connection to %s

Using dill for pickling:          %s
Floating point samples retrieved: %d
MBytes received:                  %g
Transaction time in seconds:      %g
Transfer speed in MB/s:           %g
""" % (host, usingDill, samples, d.nbytes * 1E-6, end-start, d.nbytes * 1E-6/(end-start)))
c.connection.close()
if mdsip is not None:
    from MDSplus import Connection
    c=Connection(mdsip)
    start=time()
    d=c.get('random($)',samples).data()
    end=time()
    print("""
Speed test for mdsip connection to %s
Floating point samples retrieved: %d
MBytes received:                  %g
Transaction time in seconds:      %g
Transfer speed in MB/s:           %g
""" % (mdsip, samples, d.nbytes * 1E-6, end-start, d.nbytes * 1E-6/(end-start)))
