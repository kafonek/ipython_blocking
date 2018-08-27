"""
ipython_blocking offers a context manager and IPython magic to capture cell execution.
That is useful when you want a "blocking widget" or other situations where cell execution
is paused until some trigger is met (like widget form validation)
"""

import sys
import time
import types

from IPython.core import magic_arguments
from IPython.core.magic import (
    Magics,
    magics_class,
    line_magic,
)

__version__ = '0.1.0'

### General context manager usage:

# ctx = CaptureExecution()
# with ctx:
#     while True:
#         if <something -- widget change or validation function returns True>:
#             break
#         ctx.step()


class CaptureExecution:
    "A context manager to capture execute_request events then replay them after exiting the manager"
    def __init__(self):
        self.captured_events = []
        self.shell = get_ipython()
        self.kernel = self.shell.kernel
        
    def step(self):
        self.kernel.do_one_iteration() 
    
    def capture_event(self, stream, ident, parent):
        "A 'capture' function to register instead of the default execute_request handling"
        self.captured_events.append((stream, ident, parent))

    def start_capturing(self):
        "Overwrite the kernel shell handler to capture instead of executing new cell-execution requests"
        self.kernel.shell_handlers['execute_request'] = self.capture_event

    def stop_capturing(self):
        "revert the kernel shell handler to the default execute_request behavior"
        self.kernel.shell_handlers['execute_request'] = self.kernel.execute_request
    
    def replay_captured_events(self):
        "Called at end of context -- replays all captured events once the default execution handler is in place"
        # need to flush before replaying so messages show up in current cell not replay cells
        sys.stdout.flush() 
        sys.stderr.flush()
        for stream, ident, parent in self.captured_events:
            # Using kernel.set_parent is the key to getting the output of the replayed events
            # to show up in the cells that were captured instead of the current cell
            self.kernel.set_parent(ident, parent) 
            self.kernel.execute_request(stream, ident, parent)
        self.captured_events = []
    
    def __enter__(self):
        self.start_capturing()
        self.shell.execution_count += 1 # increment execution count to avoid collision error
        
    def __exit__(self, *args):
        self.stop_capturing()
        self.replay_captured_events()

        
@magics_class        
class CaptureMagic(Magics):
    
    def capture(self, breaking_func, timeout=None):
        start = time.time()
        ctx = CaptureExecution()
        with ctx:
            while True:
                if breaking_func():
                    break
                if timeout:
                    if (time.time() - start) <= timeout:
                        break
                ctx.step()
    
    @line_magic
    @magic_arguments.magic_arguments()
    @magic_arguments.argument('break_value', help='Widget object or function that defines a break from the blocking context')
    @magic_arguments.argument('-t', '--timeout', default=None, help="Timeout in seconds to stop capturing")
    def block(self, line):
        line = line.strip()
        args = magic_arguments.parse_argstring(self.block, line)
        
        obj = get_ipython().user_ns[args.break_value]
        ### Support one of two inputs for break_value
        ### 1) a callable function that will break when the function returns True
        ### 2) a single Widget, which will cause the context to break when the value changes
        if isinstance(obj, (types.FunctionType, types.MethodType)):
            func = obj
        else:
            starting_value = obj.value
            func = lambda: obj.value != starting_value
        return self.capture(func, args.timeout)
            

def load_ipython_extensions():
    get_ipython().register_magics(CaptureMagic)
            