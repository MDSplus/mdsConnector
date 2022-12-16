import dill
import rpyc
from rpyc.utils.zerodeploy import DeployedServer


def _mimport(name, level=1):
    try:
        if not __package__:
            return __import__(name, globals())
        return __import__(name, globals(), level=level)
    except:
        return __import__(name, globals())


SshMachine = _mimport("mds_ssh_machine").SshMachine


class mdsNetref(object):
    def __init__(self, connector, obj):
        self.connector = connector
        self.obj = obj

    def __getattr__(self, name):
        ans = self.obj.__getattr__(name)
        if isinstance(ans, rpyc.core.netref.BaseNetref):
            return mdsNetref(self.connector, ans)
        else:
            return ans

    def __repr__(self):
        return self.obj.__repr__()

    def __str__(self):
        return self.obj.__str__()

    def deliver(self, arg):
        if self.connector.connection and (
            "numpy" in str(type(arg)) or "type" in str(type(arg))
        ):
            if self.connector.dill:
                ans = self.connector.dill.loads(dill.dumps(arg))
            else:
                ans = rpyc.utils.classic.deliver(
                    self.connector.connection, arg
                )
        else:
            ans = arg
        return ans

    def obtain(self, arg):
        if self.connector.connection and (
            "numpy" in str(type(arg)) or "type" in str(type(arg))
        ):
            if self.connector.dill:
                ans = dill.loads(self.connector.dill.dumps(arg))
            else:
                ans = rpyc.utils.classic.obtain(arg)
        else:
            ans = arg
        return ans

    def fixArgsAndKwargs(self, args, kwargs):
        import numpy

        l_args = list(args)
        for idx in range(len(l_args)):
            l_args[idx] = self.deliver(l_args[idx])
        args = tuple(l_args)
        for key, value in kwargs.items():
            kwargs[key] = self.deliver(value)
        return (args, kwargs)

    def __call__(self, *args, **kwargs):
        if self.connector.connection:
            args, kwargs = self.fixArgsAndKwargs(args, kwargs)
        ans = self.obtain(self.obj(*args, **kwargs))
        if isinstance(ans, rpyc.core.netref.BaseNetref):
            ans = mdsNetref(self.connector, self.obj(*args, **kwargs))
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
        >>> d5=d4.data()               ##### d5 is a numpy array on local host"""

    def __init__(
        self,
        host=None,
        user=None,
        port=None,
        keyfile=None,
        password=None,
        python_executable="python",
        ssh_opts=[],
        hop=None,
        hop_user=None,
        hop_port=None,
        hop_keyfile=None,
        hop_password=None,
        hop_python_executable="python",
    ):
        """mdsConnector constructor. Specify host to connect to a remote host via ssh or omit host or specify None to use local MDSplus objects. Specify the full path of the python executable on the remote host if python is not in the default path"""

        if host is None:
            self.local = True
            import MDSplus

            self.mdsplus = MDSplus
            self.connection = None
        else:
            if python_executable == "python":
                import sys

                if sys.version_info[0] == 3:
                    python_executable = "python3"
            self.local = False
            self.mach = SshMachine(
                host,
                user=user,
                port=port,
                keyfile=keyfile,
                password=password,
                ssh_opts=ssh_opts,
            )
            self.server = DeployedServer(
                self.mach, python_executable=python_executable
            )
            self.connection = self.server.classic_connect()
            if hop is None:
                self.mdsplus = self.connection.modules["MDSplus"]
                try:
                    self.dill = self.connection.modules["dill"]
                except:
                    self.dill = None
            else:
                self.hop_connection = self.connection.modules[
                    "mdsconnector"
                ].mdsConnector(
                    hop,
                    user=hop_user,
                    port=hop_port,
                    keyfile=hop_keyfile,
                    password=hop_password,
                    python_executable=hop_python_executable,
                )
                self.mdsplus = self.hop_connection.mdsplus

    def __getattr__(self, name):
        if self.connection:
            return mdsNetref(self, self.mdsplus.__dict__[name])
        else:
            return self.mdsplus.__dict__[name]
