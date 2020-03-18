from .ipython_blocking import CaptureExecution
import ipywidgets as widgets
import time
import types

from IPython.core import magic_arguments
from IPython.core.magic import (
    Magics,
    magics_class,
    line_magic,
)
from IPython.display import Javascript, display

def run_all_below():
    js = 'Jupyter.notebook.select_next().execute_cells_below()'
    display(Javascript(js))

@magics_class        
class CaptureMagic(Magics):
    def capture(self, breaking_func, timeout=None, replay=True):
        if timeout:
            timeout = int(timeout)
        start = time.time()
        ctx = CaptureExecution(replay=replay)
        with ctx:
            while True:
                if breaking_func():
                    break
                if timeout:
                    if (time.time() - start) >= timeout:
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
        ### Support the following options for a break value:
        ### 1) a callable function that will break when the function returns True
        ### 2) a ValueWidget, which will break when the value changes
        ### 3) a ButtonWidget, which will break when it is clicked
        if isinstance(obj, (types.FunctionType, types.MethodType)):
            func = obj
        elif isinstance(obj, widgets.ValueWidget):
            starting_value = obj.value
            func = lambda: obj.value != starting_value
        elif isinstance(obj, widgets.Button):
            obj._has_been_clicked = False
            def handler(w):
                w._has_been_clicked = True
            obj.on_click(handler)
            func = lambda: obj._has_been_clicked
        else:
            raise Exception('The positional argument to %block should be a ValueWidget, Button, or a function/method')
        return self.capture(func, args.timeout)
    
    @line_magic
    @magic_arguments.magic_arguments()
    @magic_arguments.argument('button_widget', help='A Button Widget to block-and-run-all-below on')
    @magic_arguments.argument('-t', '--timeout', default=None, help="Timeout in seconds to stop capturing")
    def blockrun(self, line):
        line = line.strip()
        args = magic_arguments.parse_argstring(self.blockrun, line)
        
        obj = get_ipython().user_ns[args.button_widget]
        ### When a cell -> run all is executed, add a _has_been_clicked attribute to the widget
        ###   and a handler for a "run all cells below"
        
        ### If _has_been_clicked is True, do nothing (let the rest of the notebook run)
        ### Otherwise block and replay=False
        if not hasattr(obj, '_has_been_clicked'):
            obj._has_been_clicked = False
            
            def handler(w):
                w._has_been_clicked = True
                run_all_below()
            obj.on_click(handler) 

        if not getattr(obj, '_has_been_clicked'):
            return self.capture(lambda: obj._has_been_clicked, timeout=args.timeout, replay=False)
            

def load_ipython_extensions():
    get_ipython().register_magics(CaptureMagic)
