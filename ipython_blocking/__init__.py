from .ipython_blocking import CaptureExecution
from .ipython_magic import CaptureMagic, load_ipython_extensions

__version__ = '0.2.1'

try:
    # This won't load when get_ipython() isn't defined, e.g. in default python shell.
    # In an IPython/Jupyter environment, I want the %block and %blockrun magic 
    # to be available by default
    load_ipython_extensions()
except:
    pass