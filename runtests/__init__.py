try:
  from .version import __version__
except:
  __version__ = "1.0.0"

import runtests.remote_control
import runtests.test_registry
import runtests.overrides

# global variables
test_start_time = None
quick_tests_only = False
