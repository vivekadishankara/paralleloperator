## ParallelOperator: Parallel operation creator

The use case for this class is to use a monitor state function while a process is
carried out. For example, the task to be carried out is:
task_to_carryout(arg1) and the parallel monitoring operation looks like:
monitor_task_state(arg1="something1", arg2="something2") then the usage will look like this:
```python
from parallel_operator import ParallelOperator

with ParallelOperator(monitor_task_state, arg1="something1", arg2="something2") as task_monitor:
    task_to_carryout(arg1)

task_states = task_monitor.output
```
It also has a time measurement functionality so the time taken by the thread to complete the
given function can be counted. It should be noted that the MONITOR FUNCTION SHOULD BE ACTIVE
FOR MORE TIME THAN THE FUNCTION UNDER OBSERVATION. An example of that would look like this:

```python
with ParallelOperator(monitor_task_state1, arg1="something1", arg2="something2") \
        as thread1:
    with ParallelOperator(monitor_task_state2, arg1="something1", arg2="something2") \
            as thread2:
        pass

total_time1 = thread1.thread_time()
total_time2 = thread2.thread_time()
```

In case there are more threads and multiple nested "with" statements is not allowed by pylint,
the following syntax will be the usage

```python
threads = [ParallelOperator(func, **kwargs) for kwargs in kwargs_list]
for thread in threads:
    thread.start()
# ***** code in between *****
for thread in threads:
    thread.join()

output_2 = thread[2].output
```
