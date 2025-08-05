from core.com import ConnHandlerThread, run_ctx
import json
import socket
from typing import ClassVar

class PlotJSThread(ConnHandlerThread):
    """ The PlotJSThread is a specialized ConnRxThread that handles plot updates.
    
    It recieves dict objects from the connection, encodes them as JSON, and sends
    them to PlotJuggler over an UDP socket.


    """
    NAME_BASE: ClassVar[str] = "PlotJSThread"
    PLOTJ_CLIENT = ("192.168.1.66", 5050)

    @run_ctx
    def run(self):
        with self.conn:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
                udp_sock.bind(("", 0))  # Bind to any available port
                udp_sock.settimeout(1.0)  # Set a timeout for the socket operations
                while not self.stop_signal:
                    try:
                        msg = self.conn.recv()
                        if not isinstance(msg, dict):
                            # Convert the dict to a JSON string and encode it
                            raise ValueError(f"Expected dict, got {type(msg)}")
                        json_msg = json.dumps(msg).encode("utf-8")
                        udp_sock.sendto(json_msg, self.PLOTJ_CLIENT)
                        #self._logger.debug(f"Sent message to PlotJuggler: {json_msg}")
                    except EOFError:
                        self._logger.info("Connection closed by the other end.")
                        break
                    except Exception as e:
                        self._logger.error(f"Error in PlotJSThread: {e}", exc_info=True)
                        break
