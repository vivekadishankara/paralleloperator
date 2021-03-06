"""
This module contains the class to test functioning of the parallel operator
"""
import time
import unittest
from library.parallel_operator import ParallelOperator
from library import framework_constants
from unittests.unittest_support import while_loop_global, LOOP_TIME


ALLOWANCE = 0.2


def wait_for_time(seconds):
    """ A function to make the thread the current wait for a few seconds"""
    time.sleep(seconds)


def append_given_list(given_list, to_append, time_btw_append):
    """
    An appender to a predefine list which can be called by multiple threads so that
    they can alternately append to the list
    :param given_list: a list object initiated before the start of the thread
    :param to_append: value to be appended to the list
    :param time_btw_append: time to wait after appending
    """
    for _ in range(4):
        given_list.append(to_append)
        wait_for_time(time_btw_append)


def make_result(*to_append_s):
    """
    This function makes the list similar to the one appended by the threads
    :param to_append_s: one or more appended values to the list by the threads
    """
    result = []
    for _ in range(4):
        for to_append in to_append_s:
            result.append(to_append)
    return result


def assert_false():
    """ A function that raises an AssertionError"""
    assert False


def return_true():
    """ This functions returns a True value"""
    return True


def while_loop_object(thread=None):
    start_time = time.time()
    while time.time() - start_time < LOOP_TIME:
        time.sleep(1)
        if thread and thread.loop_break:
            break


def loop_break_timeout_global():
    allowance = 0.2
    thread_time = 5
    with ParallelOperator(while_loop_global) as looper:
        wait_for_time(thread_time)
        framework_constants.LOOP_BREAK = True
    framework_constants.LOOP_BREAK = False
    print(thread_time - looper.thread_time())
    return abs(thread_time - looper.thread_time()) < allowance


def invaded_function_list(time_btw_append=1.0, invader_obj: ParallelOperator = None):
    if invader_obj:
        monitor = invader_obj.output = []
    else:
        monitor = []
    for i in range(4):
        monitor.append(i)
        wait_for_time(time_btw_append)

    return monitor


def invaded_function_singular(time_btw_change=1.0, invader_obj: ParallelOperator = None):
    monitor = None
    for i in range(4):
        if invader_obj:
            invader_obj.output = monitor = i
        else:
            monitor = i
        wait_for_time(time_btw_change)
    return monitor


class TestParallelOperator(unittest.TestCase):
    """ This class contains test of the parallel operator functions"""

    def test_parallel_operation(self):
        """ This tests the efficacy of the monitor function and one under observation"""
        test_list = []
        to_append_1 = 1
        to_append_2 = 2
        with ParallelOperator(append_given_list,
                              given_list=test_list, to_append=to_append_1, time_btw_append=1):
            # waiting time to avoid race condition
            wait_for_time(0.5)
            append_given_list(given_list=test_list, to_append=to_append_2, time_btw_append=1)

        self.assertEqual(test_list, make_result(to_append_1, to_append_2))
        self.assertFalse(framework_constants.LOOP_BREAK)

    def test_parallel_threads(self):
        """ This tests the efficacy of two parallel threads running in conjunction"""
        test_list = []
        to_append_1 = 1
        to_append_2 = 2
        with ParallelOperator(append_given_list,
                              given_list=test_list, to_append=to_append_1, time_btw_append=1):
            # waiting time to avoid race condition
            wait_for_time(0.5)
            with ParallelOperator(append_given_list,
                                  given_list=test_list, to_append=to_append_2, time_btw_append=1):
                # waiting time representing a task to be carried out while the threads execute
                wait_for_time(5)

        self.assertEqual(test_list, make_result(to_append_1, to_append_2))
        self.assertFalse(framework_constants.LOOP_BREAK)

    @unittest.expectedFailure
    def test_parallel_exception(self):
        """
        This tests that the exception raised in the parallel thread is raised in the
        main thread and the test fails
        """
        with ParallelOperator(assert_false):
            pass
        self.assertFalse(framework_constants.LOOP_BREAK)

    @unittest.expectedFailure
    def test_main_thread_exception(self):
        """
        This tests that the exception raised in the parallel thread is raised in the
        main thread and the test fails
        """
        with ParallelOperator(return_true):
            assert_false()
        self.assertFalse(framework_constants.LOOP_BREAK)

    def test_parallel_output(self):
        """
        This tests that the output of the function run by the parallel thread has been
        registered
        """
        with ParallelOperator(return_true) as thread:
            pass

        self.assertEqual(thread.output, True)
        self.assertFalse(framework_constants.LOOP_BREAK)

    def test_parallel_time_calculation(self):
        """ This test is for the time calculation of the operator"""
        thread1_time = 5
        thread2_time = 10

        with ParallelOperator(wait_for_time, seconds=thread1_time) as thread1:
            with ParallelOperator(wait_for_time, seconds=thread2_time) as thread2:
                pass

        self.assertTrue(abs(thread1_time - thread1.thread_time()) < ALLOWANCE)
        self.assertTrue(abs(thread2_time - thread2.thread_time()) < ALLOWANCE)
        self.assertFalse(framework_constants.LOOP_BREAK)

    def test_parallel_without(self):
        """
        This tests the efficacy of running 5 threads in parallel without using the with
        statement
        """
        test_list = []
        to_append_list = list(range(5))
        threads = [ParallelOperator(append_given_list,
                                    given_list=test_list, to_append=to_append,
                                    time_btw_append=1)
                   for to_append in to_append_list]

        for thread in threads:
            thread.start()
            # waiting time to avoid race condition
            wait_for_time(0.2)

        # waiting time representing a task to be carried out while the threads execute
        wait_for_time(5)

        for thread in threads:
            thread.join()

        self.assertEqual(test_list, make_result(*to_append_list))
        self.assertFalse(framework_constants.LOOP_BREAK)

    def test_parallel_loop_break_global(self):
        self.assertTrue(loop_break_timeout_global())

    def test_parallel_loop_break_global_second(self):
        self.assertTrue(loop_break_timeout_global())

    def test_parallel_loop_break_object(self):

        with ParallelOperator(while_loop_object) as looper:
            pass
        self.assertTrue((LOOP_TIME - looper.thread_time()) < ALLOWANCE)

        thread_time = 5
        with ParallelOperator(while_loop_object, add_self_as='thread') as looper:
            wait_for_time(thread_time)
            looper.loop_break = True
        print(thread_time - looper.thread_time())
        self.assertTrue((thread_time - looper.thread_time()) < ALLOWANCE)

    def test_parallel_real_time_list(self):
        with ParallelOperator(invaded_function_list) as non_invasive:
            pass
        self.assertTrue(non_invasive.output == [0, 1, 2, 3])

        with ParallelOperator(invaded_function_list, add_self_as='invader_obj') as invader:
            wait_for_time(0.5)
            for i in range(4):
                self.assertTrue(i == invader.output[-1])
                wait_for_time(1)

    def test_parallel_real_time_singular(self):
        with ParallelOperator(invaded_function_singular) as non_invasive:
            pass
        self.assertTrue(non_invasive.output == 3)

        with ParallelOperator(invaded_function_singular, add_self_as='invader_obj') as invader:
            wait_for_time(0.5)
            for i in range(4):
                self.assertTrue(i == invader.output)
                wait_for_time(1)
