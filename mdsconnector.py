from rpyc.utils.zerodeploy import DeployedServer
from plumbum import SshMachine
import rpyc

class mdsNetref(object):
    def __init__(self,connection,obj):
        self.connection=connection
        self.obj=obj

    def __getattr__(self,name):
        ans=self.obj.__getattr__(name)
        if isinstance(ans,rpyc.core.netref.BaseNetref): 
            return mdsNetref(self.connection,ans)
        else:
            return ans

    def __repr__(self): return self.obj.__repr__()

    def __str__(self):  return self.obj.__str__()
                


    def fixArgsAndKwargs(self,args,kwargs):
        import numpy
        l_args=list(args)
        for idx in range(len(l_args)):
            arg=l_args[idx]
            if isinstance(arg,numpy.ndarray):
                l_args[idx] = rpyc.utils.classic.deliver(self.connection,arg)
        args=tuple(l_args)
        for key,value in kwargs.iteritems():
            if isinstance(value,numpy.ndarray):
                kwargs[key] = rpyc.utils.classic.deliver(self.connection,value)
        return (args,kwargs)
    
    def __call__(self,*args,**kwargs):
        if self.connection:
            args,kwargs = self.fixArgsAndKwargs(args,kwargs)
        ans=self.obj(*args,**kwargs)
        if 'numpy' in str(type(ans)):
            return rpyc.utils.classic.obtain(ans)
        elif isinstance(ans,rpyc.core.netref.BaseNetref):
            return mdsNetref(self.connection,self.obj(*args,**kwargs))
        else:
            return ans

class mdsConnector(object):
    """The mdsConnector class enables the use of MDSplus objects over an SSH
connection to a remote host. All MDSplus objects are available and the data
associated with MDSplus objects remain on the remote host until they are
converted into native python objects or numpy data types. An application
written based on the mdsConnector class can be used using the local MDSplus
objects simply by not specifying a host when constructing the mdsConnector
so those applications can work on local or remote data. One particularly
interesting feature of the mdsConnector class is that unless you do not
specify a host, the mdsConnector class works without the need to have any
MDSplus packages or software installed on the local computer. The following
is an example on its use:

    >>> from mdsconnector import mdsConnector
    >>> c=mdsConnector('remote-hostname')
    >>> t=c.Tree('treename',shotnum)
    >>> n=t.getNode('node-spec')
    >>> d1=n.record                ##### data remains on remote host
    >>> d2=n.execute('$ + 10',d1)  ##### data remains on remote host
    >>> d3=d2.data()               ##### d3 is a numpy array on local host
    >>> d4=c.Data.execute('$ + 10',d3) ### d3 is sent to remote data remains on remote
    >>> d5=d4.data()               ##### d5 is a numpy array on local host
"""

    def __init__(self, host=None,
                 user=None,
                 port=None,
                 keyfile=None,
                 password=None,
                 python_executable='python',
                 hop=None,
                 hop_user=None,
                 hop_port=None,
                 hop_keyfile=None,
                 hop_password=None,
                 hop_python_executable='python'):
        """mdsConnector constructor. Specify host to connect to a remote host via ssh or omit host or specify None to use local MDSplus objects. Specify the full path of the python executable on the remote host if python is not in the default path"""
        
        if host is None:
            self.local=True
            import MDSplus
            self.mdsplus=MDSplus
            self.connection=None
        else:
            self.local=False
            self.mach=SshMachine(host,user=user,port=port,keyfile=keyfile,password=password)
            self.server=DeployedServer(self.mach,python_executable=python_executable)
            self.connection=self.server.classic_connect()
            if hop is None:
                self.mdsplus=self.connection.modules['MDSplus']
            else:
                self.hop_connection=self.connection.modules['mdsconnector'].mdsConnector(hop,
                                                                                         user=hop_user,
                                                                                         port=hop_port,
                                                                                         keyfile=hop_keyfile,
                                                                                         password=hop_password,
                                                                                         python_executable=hop_python_executable)
                self.mdsplus=self.hop_connection.mdsplus

    def __getattr__(self,name):
        if self.connection:
                return mdsNetref(self.connection,self.mdsplus.__dict__[name])
        else:
            return self.mdsplus.__dict__[name]
    
