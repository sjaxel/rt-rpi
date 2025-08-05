# Scratpad for testing small code snippets or debugging
import os
from typing import Iterator, Tuple
from attr import dataclass
from typing_extensions import Final
import core
import pathlib
from pathlib import PurePath, PurePosixPath
from multiprocessing import current_process
from multiprocessing.connection import Connection, Listener, Client, wait
from threading import current_thread
import tempfile
from time import sleep

import time


from core.com import Endpoint, ConnHandlerThread, run_ctx

class EndpointSubclass(Endpoint):
    def __init__(self, args, **kwargs):
        super().__init__("log", *args, **kwargs)

if __name__ == "__main__":
    # This file is intended to be run directly for testing purposes.

    
    ep1 = Endpoint('log')

    print(Endpoint._instances)

    ep2 = Endpoint('log')

    print(Endpoint._instances)

    ep3 = EndpointSubclass('log')

    print(Endpoint._instances)

    print(f"ep1 is ep3: {ep1 is ep3}")


