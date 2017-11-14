# mdsConnector
Connect to remote MDSplus server via SSH in python and use MDSplus python objects remotely

This module requires the rpyc module to be installed on the local host. The MDSplus software package
is not needed on the local host but you can utilize all of the MDSplus python objects remotely on
the server you connect to. The data remains on the remote system unless you retrieve an instance
of a python primitive object or an numpy array.

The following example demonstrates how this can be used.

```
>>> from mdsconnector import mdsConnector
>>> c = mdsConnector('hostname')
>>> t = c.Tree('mytree',42)
>>> n = c.getNode('\top:signal')
>>> rec = n.record
>>> nmpyarray = rec.data()
>>> ans = c.Data.execute('$ * 10',nmpyarray).data()
```
