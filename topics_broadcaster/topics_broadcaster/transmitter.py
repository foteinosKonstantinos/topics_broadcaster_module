import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from rclpy.executors import ExternalShutdownException
import socket
from . import Logger, CONFIGURATION, green_back, green_fore, red_back, red_fore, blue_back, blue_fore
import json
from typing import Callable
# TODO: import multithreading


class Server_TCP:

    def __init__(self,
                 port:int,                          # Port number
                 callback:Callable[[bytes], bytes], # Function to apply to the message(s)
                 buffer_size:int=1024,              # Maximum message size
                 logger:Logger|None=None,           # Optional
                 max_connections:int=1,             # Maxinum waiting connections
                 address:str="",                    # Server address (localhost)
                 name:str=""                        # Server name (useful if many servers are running)
                 ):

        self.__port = port
        self.__address = address
        self.__buffer_size = buffer_size
        self.__callback = callback
        self.__logger = logger
        self.__max_connections = max_connections
        self.__name = name
        self.__counter = 0

    def start(self) -> None:

        prefix = f"\033[0;0m[TCP SERVER {blue_fore(self.__name)}]"

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.__address, self.__port))
        server.listen(self.__max_connections)
        if self.__logger is not None:
            self.__logger.info(f"{prefix} {green_fore('\u25CF Activated')} @ {blue_fore(self.__address)}:{blue_fore(self.__port)} [buffer: {self.__buffer_size}] [max conn.: {self.__max_connections}]")

        while True:

            self.__counter += 1

            connection, client_address = server.accept()
            message = connection.recv(self.__buffer_size)
            if self.__logger is not None:
                self.__logger.info(f"{prefix} [{self.__counter}] New connection: {blue_fore(client_address[0])}:{blue_fore(client_address[1])}")

            response = self.__callback(message)
            response_size = connection.send(response)
            if self.__logger is not None:
                self.__logger.info(f"{prefix} [{self.__counter}] Response: {response_size}B @ {blue_fore(client_address[0])}:{blue_fore(client_address[1])}")

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

        self.info(blue_back("RUNNING TRANSMITTER (SERVER) ON GROUND STATION"))

        self.__heading_server = Server_TCP(port=self.__config["heading_port"],
                                           callback=self.__heading_callback,
                                           buffer_size=self.__config["heading_buffer_size"],
                                           logger=self,
                                           name=self.__config["heading_name"],
                                           address=self.__config["heading_IP"],
                                           )
        self.__heading_server.start()

    
    def info(self, msg):
        self.get_logger().info(msg)

    def warn(self, msg):
        self.get_logger().warning(msg)

    def error(self, msg):
        self.get_logger().error(msg)

    def __heading_callback(self, message:bytes) -> bytes:
        data = json.loads(message.decode())[self.__config["heading_key"]]
        msg = Float32()
        msg.data = float(data)
        self.__float_publisher.publish(msg)
        return b"OK"


def main():
    try:
        rclpy.init()
        rclpy.spin(node=Transmitter(config=CONFIGURATION))
    except (ExternalShutdownException, KeyboardInterrupt) as e:
        print(e)

if __name__ == '__main__':
    main()