from __future__ import annotations

from dataclasses import dataclass
import json
from logging import LogRecord
import socket
from time import monotonic, sleep
from typing import ClassVar, Final, Self
from multiprocessing import current_process
from multiprocessing.connection import Connection, Listener, Client
from pathlib import PosixPath, PurePosixPath

from traitlets import Any
from core.threadmanager import ManagedThread, run_ctx
from queue import Empty, Full, Queue

import os
import tempfile


class Endpoint():
    """A class representing an endpoint for communication."""
    _instances: dict[str, Self] = {}

    def __new__(cls, address: str, *args, **kwargs) -> Self:
        if address in cls._instances:
            return cls._instances[address]
        instance = super().__new__(cls)
        cls._instances[address] = instance
        return instance
    
    def __init__(self, 
                 address: str,
                 conn_handlers: tuple[type[ConnHandlerThread], ...] = None):
        self.address = address
        self._rx_queue: Queue = Queue()
        self._tx_queue: Queue = Queue()
        self.conn_handlers = conn_handlers
        self._ep_handler: ClientThread | ListenerThread | None = None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close the endpoint and its connection handlers."""
        if self._ep_handler is not None:
            self._ep_handler.stop(timeout=2)
            self._ep_handler = None
        return False

    def recv(self, timeout: float = 1.0) -> Any:
        """Receive a message from the RX queue with a timeout.

        Args:
            timeout (float): The maximum time to wait for a message.
            
        Returns:
            The received message.
        Raises:
            Empty: If no message is received within the timeout.
        """
        return self._rx_queue.get(timeout=timeout)


    def send(self, msg, block: bool = False, timeout: float = None):
        """Send a message to the TX queue with a timeout.

        Args:
            msg: The message to send.
            timeout (float): The maximum time to wait for space in the queue.

        Raises:
            Full: If the queue is full and the timeout is reached.
        """
        self._tx_queue.put(msg, block=block, timeout=timeout)

    def listen(self) -> Self:
        """Start listening for incoming connections and spawn connection handlers."""
        if self._ep_handler is not None:
            raise RuntimeError(f"Endpoint is already in use by {self._ep_handler.name}.")
        self._ep_handler = ListenerThread(self) if self.conn_handlers is None \
                            else ListenerThread(self, conn_handlers=self.conn_handlers)
        self._ep_handler.start()
        return self

    def connect(self) -> Self:
        """Connect to the endpoint and spawn connection handlers."""
        if self._ep_handler is not None:
            raise RuntimeError(f"Endpoint is already in use by {self._ep_handler.name}.")
        self._ep_handler =  ClientThread(self) if self.conn_handlers is None \
                            else ClientThread(self, conn_handlers=self.conn_handlers)
        self._ep_handler.start()
        return self

    @property
    def sock_addr(self) -> str:
        """Return the address as a string."""
        return tempfile.gettempdir() + "/" + self.address + ".sock"




class ConnHandlerThread(ManagedThread):
    """A base class for connection threads that handles the connection lifecycle."""

    def __init__(self, 
                 endpoint: Endpoint,
                 connection: Connection,
                 *args, 
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint: Endpoint = endpoint
        self.conn: Connection = connection
            

class ConnRxThread(ConnHandlerThread):
    """ The ConnRxThread takes care of handling incoming messages from a multiprocessing.connection.Connection object
    """
    NAME_BASE: ClassVar[str] = "ConnRx"
    TIMEOUT = 1

    @run_ctx
    def run(self):
        with self.conn:
            while not self.stop_signal:
                try:
                    msg = self.conn.recv()
                    self._logger.debug(f"Received message: {msg}")
                    self.endpoint._rx_queue.put(msg, block=False)
                except Full:
                    self._logger.warning("RX queue is full, dropping message")
                except EOFError:
                    self._logger.info("Connection closed by the other end.")
                    break
                except Exception as e:
                    self._logger.error(f"Error in ConnHandlerThread: {e}", exc_info=True)
                    break




class ConnTxThread(ConnHandlerThread):
    """ The ConnTxThread takes care of sending messages to a multiprocessing.connection.Connection object
    """
    NAME_BASE: ClassVar[str] = "ConnTx"
    TIMEOUT = 1
    _sentinel: Final[None] = None

    @run_ctx
    def run(self):
        with self.conn:
            while not self.stop_signal:
                try:
                    msg = self.endpoint._tx_queue.get()
                    if( msg is self._sentinel):
                        break
                    self.conn.send(msg)
                except Empty:
                    pass
                except Exception as e:
                    self._logger.error(f"Error in ConnTxThread: {e}", exc_info=True)
                    break
        
    def stop(self, *args, **kwargs):
        # Enqueue the sentinel to stop the thread
        try:
            timeout = kwargs.get('timeout', None)
            self.endpoint._tx_queue.put(self._sentinel, timeout=timeout)
        except Full:
            self._logger.warning("TX queue is full, dropping sentinel message")
        finally:
            super().stop(*args, **kwargs)

class ClientThread(ManagedThread):
    NAME_BASE: ClassVar[str] = "ConnClient"
    TIMEOUT: ClassVar[float] = 1.0  # Timeout for connection attempts in seconds
    """ A thread that connects to an enpoints and spawns connection handler threads for the connection.

    Args:
        ep (Endpoint): The endpoint to connect to.
        conn_handlers (tuple[type[ConnThread], ...]): A tuple of connection handler classes to spawn for the connection.
        *args: Additional positional arguments for the thread.
        **kwargs: Additional keyword arguments for the thread.
    Raises:
        ValueError: If no connection handler is provided.
    
    """

    def __init__(self,
                    ep: Endpoint,
                    conn_handlers = (ConnTxThread,),
                    *args,
                    **kwargs
                    ):
        super().__init__(*args, **kwargs)
        self.endpoint = ep
        self._conn_handlers: tuple[type[ConnHandlerThread]] = conn_handlers

    @run_ctx
    def run(self) -> None:
        """Run the client thread to connect to the server and handle communication."""
        try:
            self._logger.info(f"Connecting to {self.endpoint.sock_addr}")
            conn = ClientThread.connect(self.endpoint, self.TIMEOUT)
            self._logger.info(f"Connected to {self.endpoint.sock_addr}")

            for handler_class in self._conn_handlers:
                if not issubclass(handler_class, ConnHandlerThread):
                    self._logger.error(f"{handler_class.__name__} is not a subclass of ConnThread")
                    continue
                else:
                    self.spawn(handler_class(
                        endpoint=self.endpoint,
                        connection=conn
                    ))
            self._stop_evt.wait()  # Wait for the stop event to be set

        except ConnectionError as e:
            self._logger.error(f"Failed to connect to {self.endpoint.sock_addr}: {e}", exc_info=True)
            return        

        except Exception as e:
            self._logger.error(f"Error in ClientThread: {e}", exc_info=True)
            return

    @classmethod
    def connect(cls, ep: Endpoint,
                timeout: float = TIMEOUT) -> Connection:
        """Connect to a server using a Client with exponential backoff."""
        start_time: float = monotonic()
        backoff: float = 1/1000  # Initial backoff time in seconds
        # Retry connection until successful or timeout
        while True:
            try:
                return Client(ep.sock_addr, 
                              authkey=current_process().authkey)
            except Exception as e:
                if monotonic() - start_time > timeout:
                    raise ConnectionError(f"Failed to connect to {ep.sock_addr} within {timeout} seconds") from e
                sleep(backoff)
                backoff *= 2

class ListenerThread(ManagedThread):
    NAME_BASE: ClassVar[str] = "ConnList"
    TIMEOUT: ClassVar[float] = 1.0  # Timeout for connection attempts in seconds
    _sentinel: Final[None] = None
    """ A thread that listens for incoming connections and spawns handler threads for each connection.

    Args:
        endpoint (Endpoint): The endpoint to listen on.
        backlog (int): The maximum number of queued connections.
        timeout (float): The timeout for accepting connections.
        conn_handlers (tuple[type[ConnThread], ...]): A tuple of connection handler classes to spawn for each accepted connection.
        *args: Additional positional arguments for the thread.
        **kwargs: Additional keyword arguments for the thread.
        
    Raises:
        ValueError: If no connection handler is provided.
    """
    def __init__(self, 
                 endpoint: Endpoint, 
                 backlog: int = 5, 
                 timeout: float = None,
                 conn_handlers: tuple[type[ConnHandlerThread], ...] = (ConnRxThread,),
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint: Endpoint = endpoint
        self.backlog = backlog
        self.TIMEOUT: float = timeout if timeout is not None else self.TIMEOUT
        self._listener: Listener | None = None
        self._conn_handlers: tuple[type[ConnHandlerThread], ...] = conn_handlers
        if not self._conn_handlers:
            raise ValueError("At least one connection handler must be provided.")

    @run_ctx
    def run(self) -> None:
        try:
            authkey: bytes = current_process().authkey
            self._logger.info(f"Creating Listener on {self.endpoint.sock_addr}")
            with Listener(address=self.endpoint.sock_addr, 
                            authkey=authkey, 
                            backlog=self.backlog) as listener:
                self._listener = listener
                self._logger.info(f"Listener created on {self.endpoint.sock_addr}")
                while not self.stop_signal:
                    conn = listener.accept()
                    self._logger.info(f"Connection accepted from {listener.last_accepted}")

                    # Spawn connection handler threads for the accepted connection
                    for handler_class in self._conn_handlers:
                        if not issubclass(handler_class, ConnHandlerThread):
                            self._logger.error(f"{handler_class.__name__} is not a subclass of ConnHandlerThread")
                            continue
                        else:
                            self.spawn(handler_class(
                                endpoint=self.endpoint,
                                connection=conn
                            ))


            self._listener = None

        except Exception as e:
            self._logger.error(f"Error creating Listener: {e}", exc_info=True)
            return
        self._logger.info("[RUN] ConnListenerThread stopped")

    def stop(self, timeout: float | None = None):
        super().stop()

        # Trigger a connection accept to unblock the Listener
        try:
            ClientThread.connect(self.endpoint, self.TIMEOUT*2)
        except ConnectionError as e:
            self._logger.error(f"Failed to unblock Listener: {e}", exc_info=True)
        # Optionally, wait for the thread to stop
        if timeout is not None:
            self._logger.debug(f"Waiting for ConnListenerThread to stop with timeout {timeout} seconds")
            super().stop(timeout)