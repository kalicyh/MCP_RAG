__version__ = '0.1.0'

# Delay-import helper to access the repository's server module
def get_server_module():
    import importlib
    return importlib.import_module('server')
