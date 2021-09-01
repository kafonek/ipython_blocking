import sys

import ipykernel
import tornado.queues
from nbclient.util import just_run

# If ipykernel is 6+, use just_run to execute async kernel.* methods
# otherwise use traditional sync kernel.* methods
MAJ_VERSION = int(ipykernel.__version__.split(".")[0])

### General context manager usage:

# ctx = CaptureExecution()
# with ctx:
#     while True:
#         if <something -- widget change or validation function returns True>:
#             break
#         ctx.step()


class CaptureExecution:
    "A context manager to capture execute_request events then either replay or disregard them after exiting the manager"

    def __init__(self, replay=True):
        self.captured_events = []
        self._replay = replay
        self.shell = get_ipython()
        self.kernel = self.shell.kernel

    def step(self):
        if MAJ_VERSION >= 6:
            try:
                just_run(self.kernel.do_one_iteration())
            except tornado.queues.QueueEmpty:
                pass
        else:
            self.kernel.do_one_iteration()

    def capture_event(self, stream, ident, parent):
        "A 'capture' function to register instead of the default execute_request handling"
        self.captured_events.append((stream, ident, parent))

    def start_capturing(self):
        "Overwrite the kernel shell handler to capture instead of executing new cell-execution requests"
        self.kernel.shell_handlers["execute_request"] = self.capture_event

    def stop_capturing(self):
        "revert the kernel shell handler to the default execute_request behavior"
        self.kernel.shell_handlers["execute_request"] = self.kernel.execute_request

    def replay_captured_events(self):
        "Called at end of context -- replays all captured events once the default execution handler is in place"
        # need to flush before replaying so messages show up in current cell not replay cells
        sys.stdout.flush()
        sys.stderr.flush()
        for stream, ident, parent in self.captured_events:
            # Using kernel.set_parent is the key to getting the output of the replayed events
            # to show up in the cells that were captured instead of the current cell
            self.kernel.set_parent(ident, parent)
            if MAJ_VERSION >= 6:
                just_run(self.kernel.execute_request(stream, ident, parent))
            else:
                self.kernel.execute_request(stream, ident, parent)

    def __enter__(self):
        self.start_capturing()
        # increment execution count to avoid collision error
        self.shell.execution_count += 1

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            # let the error propogate up, such as a keyboard interrupt while capturing cell execution
            return False
        self.stop_capturing()
        if self._replay:
            self.replay_captured_events()
