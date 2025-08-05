import sys
import multiprocessing
from contextlib import AbstractContextManager, ExitStack
from multiprocessing import Queue, Pipe
from multiprocessing.connection import Connection, wait
from threading import Thread, Event
from types import TracebackType
import time
from typing import ClassVar, Self, Final
from abc import abstractmethod
import tempfile
import atexit, shutil
import os
from os import SCHED_FIFO, SCHED_RR, SCHED_OTHER, sched_param

from .log import EndpointHandler, EndpointLogListener, LogRxThread, init_log_config, logging
from .com import Endpoint

_mp_context_set = False

def init():
    print("Initializing multiprocessing context...")
    global _mp_context_set
    if not _mp_context_set:
        multiprocessing.set_start_method('spawn', force=True)
        _mp_context_set = True
    # If we are the main process, initialize the temporary directory for IPC
    if multiprocessing.parent_process() is not None:
        temp_dir = tempfile.TemporaryDirectory(prefix="rt-rpi-")
        atexit.register(lambda: shutil.rmtree(temp_dir, ignore_errors=True))
        tempfile.tempdir = temp_dir
        print(f"Temporary directory set to: {tempfile.tempdir}")

init()

class ManagedProcess(multiprocessing.Process, AbstractContextManager):
    """A base class for managed processes that provides a context manager interface.

    This class extends multiprocessing.Process and provides a context manager interface
    to manage the lifecycle of the process. It initializes a logger and handles exceptions
    that occur during the process execution. It also provides a mechanism to send exceptions
    to an ExceptionManager for centralized handling.

    Attributes:
        TIMEOUT (int): The timeout for the process to finish.
        MANAGED_PROCESSES (list[Self]): A class variable that holds all instances of ManagedProcess.
        _lock (bool): A class variable that is used to lock the process manager to prevent
            multiple instances from being created.

    """
    TIMEOUT: Final[int]  = 1  # 
    MANAGED_PROCESSES: ClassVar[list[Self]] = []
    _lock: ClassVar[bool] = False

    def __init__(self, 
                 *args,
                 log_level: int = logging.NOTSET,
                 sched_policy: tuple[int, int] | None = None,
                 **kwargs):
        if self._lock:
            raise RuntimeError("Instance creation is locked.")

        super().__init__(*args, daemon=True, **kwargs)
        self._logger: logging.Logger = logging.getLogger(self.name)
        self._logger.setLevel(log_level)
        self.sched_policy = sched_policy
        self.exit_stack: ExitStack | None = None

        self._tempdir = tempfile.gettempdir()  # Ensure the temp directory is set for IPC

        # Add the process to the list of managed processes
        self.MANAGED_PROCESSES.append(self)

    def _process_setup(self):
        """Setup method to be called in the process context."""
        tempfile.tempdir = self._tempdir
        self.exit_stack = ExitStack()
        init_log_config()       # Initialize logging configuration
        self._set_scheduler()  # Set the scheduler if specified
        self._logger.debug(f"[INIT] Process {self.name} initialized with tempdir: {self._tempdir}")

    def __enter__(self):
        self._logger.info(f"[ENTER]")
        self.start()  # Start the thread when entering the context
        self._logger.info(f"[START]")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            info = (exc_type, exc_value, traceback)
            #self._logger.exception(f"Exception in {self.name}: {exc_value}", exc_info=info)

        if self.is_alive():
            self.join(timeout=self.TIMEOUT)  # Wait for the process to finish
            #self.terminate()  # Terminate the process if it is still alive
        return True  # Suppress the exception if any

    def run(self):
        try:
            self._process_setup()  # Call the setup method
            self._logger.info(f"[RUN]")
            self.task()
        except KeyboardInterrupt as e:
            self._logger.warning(f"KeyboardInterrupt received: {e}")
        except Exception as e:
            self._logger.error(f"Exception in {self.name}: {e}", exc_info=True)
            # Send the exception to the ExceptionManager
        finally:
            self.exit_stack.close()
            self._logger.info(f"[EXIT]")

    def _set_scheduler(self):
        if not self.pid:
            raise RuntimeError("Cannot set scheduler before process is started.")
        current_policy: int = os.sched_getscheduler(self.pid)
        current_param: os.sched_param = os.sched_getparam(self.pid)
        try:
            if self.sched_policy is not None:
                sched_policy, priority = self.sched_policy
                # Check the allowed priority range
                if (min_prio := os.sched_get_priority_min(sched_policy)) > priority \
                        or (max_prio := os.sched_get_priority_max(sched_policy)) < priority:
                    # Clamp the priority to the allowed range
                    self._logger.warning(f"Priority {priority} out of range for policy {sched_policy} "
                        f"(min: {min_prio}, max: {max_prio}), clamping to range.")
                    priority = max(min_prio, min(max_prio, priority))
                if current_policy != sched_policy or current_param.sched_priority != priority:
                    os.sched_setscheduler(self.pid, sched_policy, sched_param(priority))
                    self._logger.info(f"Scheduler set to {sched_policy} with priority {priority}")
                    os.sched_setaffinity(self.pid, [3])  # Set affinity to the current process's CPUs
        except Exception as e:
            self._logger.error(f"Failed to set scheduler for process {self.name}: {e}")


    @abstractmethod
    def task(self):
        """Override this method in subclasses to define process behavior."""
        pass



class ProcessManager(ExitStack):
    """ Manages the lifecycle of ManagedProcesses.

    This class provides a context manager interface to start and stop
    ManagedProcesses. It ensures that all processes are started when
    entering the context and stopped when exiting.

    It uses ExitStack to manage the lifecycle of ManagedProcesses.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint_listener: EndpointLogListener = EndpointLogListener()
        self._logger = logging.getLogger("ProcessManager")
        self._logger.info(f"[INIT]")

    def __enter__(self):
        ep = Endpoint("log", conn_handlers=(LogRxThread,))  # Initialize the log endpoint
        self.enter_context(ep.listen())  # Start listening for log messages
        #self.enter_context(self.endpoint_listener)
        self._logger.info(f"[ENTER]")
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)
        # Ensure all processes are stopped
        self._logger.info(f"[EXIT]")

    def enter_context(self, cm):
        self._logger.debug(f"Entering context: {cm}")
        self._logger.debug(f"Current context stack: {self._exit_callbacks}")
        return super().enter_context(cm)
    
    def set_scheduler(self, process: ManagedProcess, policy: int, priority: int):
        os.sched_setscheduler(process.pid, policy, priority)

    def start(self):
        """Start all registered ManagedProcesses."""
        # Lock the process manager to prevent multiple starts
        if ManagedProcess._lock:
            raise RuntimeError("ProcessManager is locked, cannot start processes.")
        else :
            ManagedProcess._lock = True

        for process in ManagedProcess.MANAGED_PROCESSES:
            self.enter_context(process)

    def wait_processes(self, timeout: float = None) -> list[int | None]:
        """Wait for all managed processes to finish."""
        return wait([proc.sentinel for proc in ManagedProcess.MANAGED_PROCESSES if proc.is_alive()], timeout=timeout)


class TestManagedProcess(ManagedProcess):
    def task(self):
        while True:
            self._logger.info(f"Hello from {self.name}!")
            #sleep(2)  # Simulate work by sleeping for a second
            raise RuntimeError("Simulated error in process")  # Simulate an error
        #raise RuntimeError("Simulated error in process")  # Simulate an error


if __name__ == "__main__":
    # NOTE: main method is for development, should not be run standalone.

    #multiprocessing.set_start_method("spawn")
    init_log_config()  # Initialize logging configuration
    logger = logging.getLogger("main")
    logger.info("[START]")

    # Init manager objects
    # Create processes and register them with the ExceptionManager



    with ProcessManager() as proc_mgr:

        TestManagedProcess(proc_mgr.log_mgr.queue, name="Test1")
        TestManagedProcess(proc_mgr.log_mgr.queue, name="Test2")

        proc_mgr.start()  # All ManagedProcesses will be started here
        
        while True:
            try:
                # Check if processes are alive
                time.sleep(1)  # Sleep to avoid busy waiting
            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt received, exiting...")
                break
            except Exception as e:
                logger.error(f"An error occurred: {e}")
    logger.info("Context manager has been exited")
