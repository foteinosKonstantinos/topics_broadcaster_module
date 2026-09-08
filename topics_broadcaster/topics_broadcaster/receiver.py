import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from sensor_msgs.msg import NavSatFix, Image
from rclpy.executors import ExternalShutdownException
import socket
from . import Logger, blue_fore, blue_back, CONFIGURATION, red_fore
import pickle

def send_TCP(message:bytes,                 #
            port:int,                       #
            address:str,                    #
            logger:Logger|None=None,        #
            name:str="",                    #
            buffer_size:int=1024,           #
            ) -> bytes:
    
    prefix = f"\033[0;0m[SEND TCP {blue_fore(name)}]"

    try:

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        client.connect((address, port))
        request_size = client.send(message)

        if logger is not None:
            logger.info(f"{prefix} Request: {request_size}B @ {blue_fore(address)}:{blue_fore(port)}")

        response = client.recv(buffer_size)
        if logger is not None:
            logger.info(f"{prefix} Server response: {response}")

    except ConnectionRefusedError:
        if logger is not None:
            logger.warn(f"{prefix} {red_fore('Connection refused')}")


class Receiver(Node, Logger):

    def __init__(self, config:dict):
        super().__init__("receiver_client")
        self.__config = config

        self.__heading_subscriber = self.create_subscription(
            msg_type=Float32, 
            topic=self.__config["heading_topic_ugv"], 
            callback=self.__heading_callback,
            qos_profile=10
        )

        self.__fix_subscriber = self.create_subscription(
            msg_type=NavSatFix,
            topic=self.__config["fix_topic_ugv"],
            callback=self.__fix_callback,
            qos_profile=10
        )

        self.__rgb_subscriber = self.create_subscription(
            msg_type=Image,
            topic=self.__config["rgb_topic_ugv"],
            callback=self.__rgb_callback,
            qos_profile=10
        )

        self.info(blue_back("RUNNING RECEIVER (CLIENT) ON JETSON"))

        # TODO: FPS control

    def info(self, msg):
        self.get_logger().info(msg)
    
    def warn(self, msg):
        self.get_logger().warning(msg)

    def error(self, msg):
        self.get_logger().error(msg)
  
    def __heading_callback(self, msg:Float32):
        msg_bytes = pickle.dumps(msg)
        send_TCP(message=msg_bytes,
                port=self.__config["heading_server_port"],
                address=self.__config["heading_server_IP"],
                logger=self,
                name=self.__config["heading_name"],
                buffer_size=self.__config["heading_client_buffer_size"]
                )

    def __fix_callback(self, msg:NavSatFix):
        msg_bytes = pickle.dumps(msg)
        send_TCP(message=msg_bytes,
                port=self.__config["fix_server_port"],
                address=self.__config["fix_server_IP"],
                logger=self,
                name=self.__config["fix_name"],
                buffer_size=self.__config["fix_client_buffer_size"]
                )

    def __rgb_callback(self, msg:Image):
        msg_bytes = pickle.dumps(msg)
        print(len(msg_bytes))
        send_TCP(message=msg_bytes,
                port=self.__config["rgb_server_port"],
                address=self.__config["rgb_server_IP"],
                logger=self,
                name=self.__config["rgb_name"],
                buffer_size=self.__config["rgb_client_buffer_size"]
                )
  

def main():
    try:
        rclpy.init()
        rclpy.spin(node=Receiver(config=CONFIGURATION))
    except (ExternalShutdownException, KeyboardInterrupt) as e:
        print(e)

if __name__ == '__main__':
    main()