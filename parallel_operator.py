""" The threading function to help verification parallel to an action"""
import time
import threading

# pylint: disable=too-many-instance-attributes


class ParallelOperator(threading.Thread):
    """
    Parallel operation creator

    The use case for this class is to use a monitor state function while a process is
    carried out. For example, the task to be carried out is:
    task_to_carryout(arg1) and the parallel monitoring operation looks like:
    monitor_task_state(arg1="something1", arg2="something2") then the usage will look like this:

    with ParallelOperator(monitor_task_state, arg1="something1", arg2="something2") as task_monitor:
        task_to_carryout(arg1)

    task_states = task_monitor.output

    It also has a time measurement functionality so the time taken by the thread to complete the
    given function can be counted. It should be noted that the MONITOR FUNCTION SHOULD BE ACTIVE
    FOR MORE TIME THAN THE FUNCTION UNDER OBSERVATION. An example of that would look like this:

    with ParallelOperator(monitor_task_state1, arg1="something1", arg2="something2") \
            as thread1:
        with ParallelOperator(monitor_task_state2, arg1="something1", arg2="something2") \
                as thread2:
            pass

    total_time1 = thread1.thread_time()
    total_time2 = thread2.thread_time()

    In case there are more threads and multiple nested "with" statements is not allowed by pylint,
    the following syntax will be the usage

    threads = [ParallelOperator(func, **kwargs) for kwargs in kwargs_list]
    for thread in threads:
        thread.start()
    ***** code in between *****
    for thread in threads:
        thread.join()

    output_2 = thread[2].output
    """
    def __init__(self, fp_operation, delay=0, add_self_as=None, **kwargs):
        """ initializes the function to be run in a thread"""
        self.fp_operation = fp_operation
        self.kwargs = kwargs
        self.start_delay = delay
        self.output = None
        self.exc = None
        self.start_time = None
        self.end_time = None
        self.loop_break = False
        if add_self_as:
            more_kwargs = {add_self_as: self}
            self.kwargs = dict(self.kwargs, **more_kwargs)
        super().__init__()

    def run(self) -> None:
        """ overriding the threading run method so that the output and exception can be captured"""
        self.start_time = time.time()
        try:
            output = self.fp_operation(**self.kwargs)
            if self.output is None:
                self.output = output
        except Exception as exc:
            self.exc = exc
        self.end_time = time.time()
        self.loop_break = False

    def join(self, timeout: float = 0.0) -> None:
        """ overriding the threading join method to raise the exception caught by the thread"""
        super().join()
        if self.exc:
            raise self.exc

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.join()

    def thread_time(self):
        """ time taken by the thread to run"""
        try:
            return self.end_time - self.start_time
        except TypeError:
            return None
