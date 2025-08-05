from functools import wraps
import logging
import threading
from threading import Thread, Event
from contextlib import ExitStack
from typing import Any, Callable, ClassVar, Self
from abc import abstractmethod

threading.main_thread().name = "Main"    # Ensure the main thread has a consistent name

def run_ctx(run_method: Callable[[Any], None]) -> Callable[[Any], None]:
    """ Decorator to handle subclassed run methods of ManagedThread.

    Ensures that the cleanup of thread resources if thread exits or
    raises and unhandles exception in the user-defined run method.

    Args:
        run_method: The original run method.

    Returns:
        Wrapped run method that executes within 'with self:'.
    """
    @wraps(run_method)
    def wrapper(self: ManagedThread, *args, **kwargs):
        self._exit_stack = ExitStack()
        self._exit_stack.callback(lambda: self._logger.debug(f"Exitstack for {self.name} cleanup."))
        try:
            self._logger.info(f"[RUN]")
            return run_method(self, *args, **kwargs)
        except Exception as e:
            self._logger.error(f"Exception in {self.name}: {e}", exc_info=True)
        finally:
            self._exit_stack.close()
            self._logger.info(f"[EXIT]")

    return wrapper


class ManagedThread(Thread):
    NAME_BASE: ClassVar[str] = "MThread"
    _DEFAULT_JOIN_TIMEOUT: ClassVar[float] = 2.0
    _instance_cnt: ClassVar[int] = 0

    def __init__(self, *args, log_level: int = logging.NOTSET, **kwargs):
        defname = self._default_name()
        super().__init__(name=defname,
                         daemon=True)
        self._stop_evt = Event()
        self._exit_stack: ExitStack | None = None
        self._logger = logging.getLogger(self.name)
        self._logger.setLevel(log_level)


    def __enter__(self):
        self._logger.info(f"[ENTER]")
        super().start()  # Start the thread when entering the context
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self._logger.error(f"(Suppressed) {exc_value}", exc_info=(exc_type, exc_value, traceback))

        self.stop(2)  # Ensure the thread is stopped when exiting the context
        return (exc_type, exc_value, traceback)

    def spawn(self, child: Self):
        try:
            # Inherit log level if not explicitly set
            if not child._logger.level:
                child._logger.setLevel(self._logger.level)
            # Enter via the parents exit stack to ensure cleanup.
            self._exit_stack.enter_context(child)
        except Exception as e:
            self._logger.error(f"Failed to spawn child thread: {e}", exc_info=True)
        
    def stop(self, timeout: float | None = None):
        # Check that the thread isn't calling stop on itself
        if self is threading.current_thread():
            raise RuntimeError("Cannot stop the current thread from within itself.")
        self.stop_signal = True  # Set the stop signal to True
        if timeout:
            self.join(timeout)  # Wait for the thread to finish
            if self.is_alive():
                self._logger.warning(f"{self.name} did not stop within {timeout} seconds.")

    
    @property
    def stop_signal(self) -> bool:
        return self._stop_evt.is_set()

    @stop_signal.setter
    def stop_signal(self, value: bool):
        if value and not self.stop_signal:
            self._stop_evt.set()
            self._logger.info(f"[STOPSIG]")

    @abstractmethod
    def run(self):
        """Override this method in subclasses to define thread behavior."""
        while not self.stop_signal:
            ...

    def _default_name(self) -> str:
        """Generate a default name for the thread, unique per subclass."""
        cls = self.__class__
        if not hasattr(cls, "_instance_cnt"):
            cls._instance_cnt = 0
        cls._instance_cnt += 1
        return f"{self.NAME_BASE}-{cls._instance_cnt}"

if __name__ == "__main__":
    # This module is not intended to be run directly.
    raise NotImplementedError("This module is not intended to be run directly.")