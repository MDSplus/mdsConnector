
def _import(name, level=1):
    try:
        if not __package__:
            return __import__(name, globals())
        return __import__(name, globals(), level=level)
    except:
        return __import__(name, globals())
mdsConnector=_import('mdsconnector').mdsConnector
