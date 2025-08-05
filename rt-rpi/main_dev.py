# rt-rpi/main_dev.py
# Development file for functions not yet ready to be moved to a separate module.

from contextlib import AbstractContextManager, ContextDecorator, ExitStack, contextmanager
from functools import wraps
import logging
import multiprocessing
from multiprocessing import Pipe
from multiprocessing.connection import Client, Listener, Connection, wait
from queue import Empty
from threading import Event, Thread, current_thread
from time import sleep, monotonic, monotonic_ns
from types import TracebackType
from typing import Any, Callable, ClassVar, Final, Self
import traceback
import sys
import os
import tempfile

import core
from core.procmanager import ManagedProcess, ProcessManager, SCHED_FIFO, SCHED_RR, SCHED_OTHER, sched_param
from core.utils import LoopTimer
from core.com import ClientThread, Endpoint, ListenerThread
from stream.plotjuggler import PlotJSThread
 

from mpu6050 import mpu6050


class ClientProcess(ManagedProcess):
    """A simple process for testing purposes."""
    def task(self):
        period: float = 0.01 # seconds
        lt = LoopTimer(period)
        
        ep_plotj = Endpoint("log.plotj")
        self.exit_stack.enter_context(ep_plotj.connect())

        sensor = mpu6050(0x68)

        try:
            logtime = 0
            for elapsed, error in lt:
                accel = sensor.get_accel_data()
                gyro = sensor.get_gyro_data()
                temp = sensor.get_temp()
                data = {
                    "accel": accel,
                    "gyro": gyro,
                    "temp": temp,
                    "error": error,
                    "timestamp": logtime,
                }
                ep_plotj._tx_queue.put(data)
                logtime += elapsed
                
        except KeyboardInterrupt:
            self._logger.info("KeyboardInterrupt received, stopping process...")
        except Exception as e:
            self._logger.error(f"Exception in ClientProcess {self.name}: {e}", exc_info=True)

        self._logger.info(str(lt.stats))
        print(f"Process {self.name} finished with stats: {lt.stats}")

if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="rt-rpi-") as tempdir:
        core.init_log_config(level=logging.INFO)
        logger = core.logging.getLogger("main")

        logger.info(f"Temporary directory created: {tempdir}")
        tempfile.tempdir = tempdir

        ep_plotj = Endpoint("log.plotj", conn_handlers=(PlotJSThread,))

        

        # Example usage of ManagedThread and ConnListenerThread
        # plotj_listener = ListenerThread(
        #     ep_plotj, conn_handlers=(PlotJSThread,)
        # )
        with ep_plotj.listen(), ProcessManager() as proc_mgr:

            ClientProcess(name="Client1",  sched_policy=(SCHED_FIFO, 60))
            proc_mgr.start()
            while True:
                try:

                    sleep(1)  # Replace with actual logic
                except Empty:
                    logger.info("No message received, continuing...")
                except KeyboardInterrupt:
                    logger.info("KeyboardInterrupt received, stopping processes...")
                    break
                except Exception as e:
                    logger.error(f"Exception in main process: {e}", exc_info=True)
                    break
