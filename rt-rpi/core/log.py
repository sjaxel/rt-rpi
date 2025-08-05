import logging
from logging import LogRecord
from logging.handlers import QueueHandler
from multiprocessing import Queue, parent_process, current_process
from typing import ClassVar
from .threadmanager import run_ctx
from .com import ConnHandlerThread, ConnRxThread, Endpoint, ClientThread, ListenerThread

DEFAULT_LOG_EP = "log"

def init_log_config(level: int = logging.INFO):

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    ## Check if we are in the main process or a child process
    if hasattr(current_process(), "exit_stack"):
        # We are in a child process, set up the EndpointHandler
        proc = current_process()
        ep_handler = EndpointHandler(Endpoint(DEFAULT_LOG_EP))

        # Manage the endpoint handler lifecycle via the ManagedProcess.exit_stack
        if proc.exit_stack is None:
            raise RuntimeError("ManagedProcess exit_stack is not initialized.")
        proc.exit_stack.enter_context(ep_handler)
        root_logger.addHandler(ep_handler)
    elif parent_process() is None:
        # We are in the main process, set up the root logger
        root_logger.addHandler(ConsoleHandler())



class ColorFormatter(logging.Formatter):
    """
    A custom logging formatter that adds ANSI color codes to log level names for colored console output.

    Attributes:
        FORMAT (str): The log message format string.
        COLORS (dict): Mapping of log level names to their corresponding ANSI color codes.
        RESET (str): ANSI code to reset color formatting.

    Methods:
        __init__(fmt: str = FORMAT):
            Initializes the formatter with the specified format string.

        format(record: logging.LogRecord) -> str:
            Formats the specified log record, applying color to the level name based on its severity.
    """
    FORMAT = '[%(levelname)s][%(processName)s:%(threadName)s](%(name)s): %(message)s'
    COLORS = {
    'DEBUG': '\033[36m',    # Cyan
    'INFO': '\033[32m',     # Green
    'WARNING': '\033[33m',  # Yellow
    'ERROR': '\033[31m',    # Red
    'CRITICAL': '\033[41m', # Red background
    }
    RESET = '\033[0m'

    def __init__(self, fmt: str = FORMAT):
        super().__init__(fmt=fmt)

    def format(self, record: logging.LogRecord) -> str:
        levelname = record.levelname
        color = self.COLORS.get(levelname, '')
        record.levelname = f"{color}{levelname}{self.RESET}"
        return super().format(record)
    
class ConsoleHandler(logging.StreamHandler):
    """
    A custom logging handler that uses the ColorFormatter to format log messages with colors.
    
    Attributes:
        formatter (ColorFormatter): The formatter used to format log messages.
    """
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ConsoleHandler, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        super().__init__()
        self.setFormatter(ColorFormatter())


class EndpointHandler(QueueHandler):

    def __init__(self, ep: Endpoint | None = None):
        if not ep:
            ep = Endpoint(DEFAULT_LOG_EP)
        super().__init__(ep._tx_queue)
        self._client = ClientThread(ep, name="EndpointHandlerClient")

    def __enter__(self):
        """Start the client connection."""
        self._client.start()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Close the client connection."""
        self.close()
        return False

    def close(self):
        """Close the client connection."""
        self._client.stop(timeout=2)
        super().close()




class EndpointLogListener(ListenerThread):
    NAME_BASE = "EndpointLogListener"

    def __init__(self, 
            ep: Endpoint | None = None,
            *args,
            **kwargs):
        super().__init__(
            *args,
            endpoint=ep if ep else Endpoint(DEFAULT_LOG_EP),
            conn_handlers=(LogRxThread,),
            **kwargs
        )

class LogRxThread(ConnHandlerThread):
    """ The LogRxThread is a specialized ConnHandlerThread that handles log messages.
    It processes log records received from the connection and forwards them to the logger.
    """
    NAME_BASE: ClassVar[str] = "LogRx"

    @run_ctx
    def run(self):
        with self.conn:
            while not self.stop_signal:
                try:
                    record = self.conn.recv()
                    if isinstance(record, LogRecord):
                        self._logger.handle(record)
                    else:
                        self._logger.warning(f"Received non-LogRecord: {record}")
                except EOFError:
                    self._logger.info("Connection closed by the other end.")
                    break
                except Exception as e:
                    self._logger.error(f"Error in LogRxThread: {e}", exc_info=True)
                    break