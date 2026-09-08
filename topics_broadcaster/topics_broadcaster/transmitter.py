import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from sensor_msgs.msg import NavSatFix, Image, CameraInfo
from rclpy.executors import ExternalShutdownException
import socket
from . import Logger, CONFIGURATION, green_back, green_fore, red_back, red_fore, blue_back, blue_fore
import pickle
from typing import Callable
import threading


class Server_TCP:

    def __init__(self,
                port:int,                          # Port number
                callback:Callable[[bytes], bytes], # Function to apply to the message(s)
                send_buffer_size:int=1024,         # Maximum message size (send)
                rcv_buffer_size:int=1024,          # Maximum message size (receive)
                logger:Logger|None=None,           # Optional
                max_connections:int=1,             # Maxinum waiting connections
                address:str="",                    # Server address (localhost)
                name:str=""                        # Server name (useful if many servers are running)
                ):

        self.__port = port
        self.__address = address
        self.__send_buffer_size = send_buffer_size
        self.__rcv_buffer_size = rcv_buffer_size
        self.__callback = callback
        self.__logger = logger
        self.__max_connections = max_connections
        self.__name = name
        self.__counter = 0

    def start(self) -> None:

        prefix = f"\033[0;0m[TCP SERVER {blue_fore(self.__name)}]"

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # https://pubs.opengroup.org/onlinepubs/009695399/functions/setsockopt.html
        server.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.__send_buffer_size) # Send buffer
        server.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.__rcv_buffer_size)  # Receive buffer
        server.bind((self.__address, self.__port))
        server.listen(self.__max_connections)
        if self.__logger is not None:
            self.__logger.info(f"{prefix} {green_fore('\u25CF Activated')} @ {blue_fore(self.__address)}:{blue_fore(self.__port)} [in. buffer: {self.__rcv_buffer_size}] [max conn.: {self.__max_connections}]")

        while True:

            self.__counter += 1

            connection, client_address = server.accept()
            message = connection.recv(self.__rcv_buffer_size)
            if self.__logger is not None:
                self.__logger.info(f"{prefix} [{self.__counter}] New connection: {blue_fore(client_address[0])}:{blue_fore(client_address[1])}")

            response = self.__callback(message)
            response_size = connection.send(response)
            if self.__logger is not None:
                self.__logger.info(f"{prefix} [{self.__counter}] Server response: {response_size}B @ {blue_fore(client_address[0])}:{blue_fore(client_address[1])}")

            connection.close()
            if self.__logger is not None:
                self.__logger.info(f"{prefix} [{self.__counter}] Connection closed")


class Transmitter(Node, Logger):

    def __init__(self, config:dict):
        super().__init__("transmitter_server")
        self.__config = config
        
        self.__float_publisher=self.create_publisher(
            msg_type = Float32,
            topic = self.__config["heading_topic_gs"],
            qos_profile = 10,
        )

        self.__fix_publisher=self.create_publisher(
            msg_type = NavSatFix,
            topic = self.__config["fix_topic_gs"],
            qos_profile = 10,
        )

        self.__intrinsics_publisher=self.create_publisher(
            msg_type = CameraInfo,
            topic = self.__config["intrinsics_topic_gs"],
            qos_profile = 10,
        )

        self.__rgb_publisher=self.create_publisher(
            msg_type = Image,
            topic = self.__config["rgb_topic_gs"],
            qos_profile = 10,
        )

        self.__depth_publisher=self.create_publisher(
            msg_type = Image,
            topic = self.__config["depth_topic_gs"],
            qos_profile = 10,
        )

        self.info(blue_back("RUNNING TRANSMITTER (SERVER) ON GROUND STATION"))

        self.__servers = {
            "heading_server": Server_TCP(port=self.__config["heading_server_port"],
                                        callback=self.__heading_callback,
                                        send_buffer_size=self.__config["heading_server_response_buffer_size"],
                                        rcv_buffer_size=self.__config["heading_message_buffer_size"],
                                        logger=self,
                                        name=self.__config["heading_name"],
                                        address=self.__config["heading_server_IP"],
                                        ),
            "fix_server": Server_TCP(port=self.__config["fix_server_port"],
                                        callback=self.__fix_callback,
                                        send_buffer_size=self.__config["fix_server_response_buffer_size"],
                                        rcv_buffer_size=self.__config["fix_message_buffer_size"],
                                        logger=self,
                                        name=self.__config["fix_name"],
                                        address=self.__config["fix_server_IP"],
                                        ),
            "rgb_server": Server_TCP(port=self.__config["rgb_server_port"],
                                        callback=self.__rgb_callback,
                                        send_buffer_size=self.__config["rgb_server_response_buffer_size"],
                                        rcv_buffer_size=self.__config["rgb_message_buffer_size"],
                                        logger=self,
                                        name=self.__config["rgb_name"],
                                        address=self.__config["rgb_server_IP"],
                                        ),
            "depth_server": Server_TCP(port=self.__config["depth_server_port"],
                                        callback=self.__depth_callback,
                                        send_buffer_size=self.__config["depth_server_response_buffer_size"],
                                        rcv_buffer_size=self.__config["depth_message_buffer_size"],
                                        logger=self,
                                        name=self.__config["depth_name"],
                                        address=self.__config["depth_server_IP"],
                                        ),
            "intrinsics_server": Server_TCP(port=self.__config["intrinsics_server_port"],
                                        callback=self.__intrinsics_callback,
                                        send_buffer_size=self.__config["intrinsics_server_response_buffer_size"],
                                        rcv_buffer_size=self.__config["intrinsics_message_buffer_size"],
                                        logger=self,
                                        name=self.__config["intrinsics_name"],
                                        address=self.__config["intrinsics_server_IP"],
                                        ),
        }

        self.__threads = []

        for server in self.__servers.keys():
            # self.info(f"Starting {blue_fore(server)} server ...")
            self.__threads.append(threading.Thread(target=self.__servers[server].start))
            self.__threads[-1].start()

        for thread in self.__threads:
            thread.join()

    def info(self, msg):
        self.get_logger().info(msg)

    def warn(self, msg):
        self.get_logger().warning(msg)

    def error(self, msg):
        self.get_logger().error(msg)

    def __heading_callback(self, message:bytes) -> bytes:
        try:
            msg = pickle.loads(message)
            self.__float_publisher.publish(msg)
            return b"OK"
        except BaseException as e:
            self.error(str(e))
            return b"FAILURE"

    def __fix_callback(self, message:bytes) -> bytes:
        try:
            msg = pickle.loads(message)
            self.__fix_publisher.publish(msg)
            return b"OK"
        except BaseException as e:
            self.error(str(e))
            return b"FAILURE"

    def __intrinsics_callback(self, message:bytes) -> bytes:
        try:
            msg = pickle.loads(message)
            self.__intrinsics_publisher.publish(msg)
            return b"OK"
        except BaseException as e:
            self.error(str(e))
            return b"FAILURE"

    def __rgb_callback(self, message:bytes) -> bytes:
        try:
            msg = pickle.loads(message)
            self.__rgb_publisher.publish(msg)
            return b"OK"
        except pickle.UnpicklingError:
            self.error(f"[{self.__config['rgb_name']}] Data were truncated (received {len(message)}B) - probably buffer size was reduced by the OS")
            return b"FAILURE"
        except BaseException as e:
            self.error(str(e))
            return b"FAILURE"

    def __depth_callback(self, message:bytes) -> bytes:
        try:
            msg = pickle.loads(message)
            self.__depth_publisher.publish(msg)
            return b"OK"
        except pickle.UnpicklingError:
            self.error(f"[{self.__config['depth_name']}] Data were truncated (received {len(message)}B) - probably buffer size was reduced by the OS")
            return b"FAILURE"
        except BaseException as e:
            self.error(str(e))
            return b"FAILURE"
    

def main():
    try:
        rclpy.init()
        rclpy.spin(node=Transmitter(config=CONFIGURATION))
    except (ExternalShutdownException, KeyboardInterrupt) as e:
        print(e)

if __name__ == '__main__':
    main()