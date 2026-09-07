import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from rclpy.executors import ExternalShutdownException
import socket
import json
from . import Logger, blue_fore, blue_back, CONFIGURATION, red_fore


def send_TCP(message:bytes,                 #
             port:int,                      #
             address:str,                   #
             logger:Logger|None=None,       #
             name:str="",                   #
             ) -> bytes:
    
    prefix = f"\033[0;0m[SEND TCP {blue_fore(name)}]"

    try:

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((address, port))
        request_size = client.send(message)

        if logger is not None:
            logger.info(f"{prefix} Request: {request_size}B @ {address}:{port}")

        response = client.recv(1024)
        if logger is not None:
            logger.info(f"{prefix} Reponse: {response}")

    except ConnectionRefusedError:
        if logger is not None:
            logger.warn(f"{prefix} {red_fore('Connection refused')}")


class Reciever(Node, Logger):

    def __init__(self, config:dict):
        super().__init__("reciever_client")
        self.__config = config

        self.__heading_subscriber = self.create_subscription(
            msg_type=Float32, 
            topic=self.__config["heading_topic_ugv"], 
            callback=self.__heading_callback,
            qos_profile=10
        )

        self.info(blue_back("RUNNING RECIEVER (CLIENT) ON JETSON"))

        # TODO: FPS control

    def info(self, msg):
        self.get_logger().info(msg)
    
    def warn(self, msg):
        self.get_logger().warning(msg)

    def error(self, msg):
        self.get_logger().error(msg)
  
    def __heading_callback(self, msg:Float32):
        msg_bytes = json.dumps({self.__config["heading_key"]: float(msg.data)}).encode()
        send_TCP(message=msg_bytes,
                 port=self.__config["heading_port"],
                 address=self.__config["heading_IP"],
                 logger=self,
                 name=self.__config["heading_name"]
                 )

  

def main():
    try:
        rclpy.init()
        rclpy.spin(node=Reciever(config=CONFIGURATION))
    except (ExternalShutdownException, KeyboardInterrupt) as e:
        print(e)

if __name__ == '__main__':
    main()