import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from sensor_msgs.msg import NavSatFix, Image, CameraInfo
from rclpy.executors import ExternalShutdownException
import socket
from . import Logger, blue_fore, blue_back, CONFIGURATION, red_fore
import pickle
import time

def send_TCP(message:bytes,                 #
            port:int,                       #
            address:str,                    #
            logger:Logger|None=None,        #
            name:str="",                    #
            send_buffer_size:int=1024,      #
            rcv_buffer_size:int=1024,       #
            ) -> bytes:
    
    prefix = f"\033[0;0m[SEND TCP {blue_fore(name)}]"

    try:

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, send_buffer_size) # Send buffer
        client.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, rcv_buffer_size)  # Receive buffer
        client.connect((address, port))
        request_size = client.send(message)

        if logger is not None:
            logger.info(f"{prefix} Message: {request_size}B @ {blue_fore(address)}:{blue_fore(port)}")

        response = client.recv(rcv_buffer_size)
        if logger is not None:
            logger.info(f"{prefix} Server response: {response}")

        return response

    except ConnectionRefusedError:
        if logger is not None:
            logger.warn(f"{prefix} {red_fore('Connection refused (server error)')}")
        return b"FAILURE"

    except ConnectionResetError:
        if logger is not None:
            logger.warn(f"{prefix} {red_fore('Connection reset (server error)')}")
        return b"FAILURE"


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

        self.__intrinsics_subscriber = self.create_subscription(
            msg_type=CameraInfo,
            topic=self.__config["intrinsics_topic_ugv"],
            callback=self.__intrinsics_callback,
            qos_profile=10
        )

        self.__rgb_subscriber = self.create_subscription(
            msg_type=Image,
            topic=self.__config["rgb_topic_ugv"],
            callback=self.__rgb_callback,
            qos_profile=10
        )

        self.__depth_subscriber = self.create_subscription(
            msg_type=Image,
            topic=self.__config["depth_topic_ugv"],
            callback=self.__depth_callback,
            qos_profile=10
        )

        self.info(blue_back("RUNNING RECEIVER (CLIENT) ON JETSON"))

        self.__previous = {
            "rgb": None,
            "depth": None,
            "intrinsics": None,
            "fix": None,
            "heading": None,
        }

        # TODO: FPS control

    def __fps_filter(self, key):
        fps = self.__config[f"{key}_fps"]
        name = self.__config[f"{key}_name"]
        previous = self.__previous[key]
        if previous is not None:
            appr_fps = 1 / (time.time() - previous)
            if appr_fps > fps:
                self.warn(f"[{name}] Callback rejected: approximated FPS = {appr_fps} > {fps}")
                return False
        return True

    def __update(self, key, response):
        self.__previous[key] = time.time() if response != b"FAILURE" else self.__previous[key]

    def info(self, msg):
        self.get_logger().info(msg)
    
    def warn(self, msg):
        self.get_logger().warning(msg)

    def error(self, msg):
        self.get_logger().error(msg)

    def __general_callback(self, msg, key):
        msg_bytes = pickle.dumps(msg)
        if not self.__fps_filter(key):
            return
        msg_bytes = pickle.dumps(msg)
        response = send_TCP(message=msg_bytes,
                port=self.__config[f"{key}_server_port"],
                address=self.__config[f"{key}_server_IP"],
                logger=self,
                name=self.__config[f"{key}_name"],
                send_buffer_size=self.__config[f"{key}_message_buffer_size"],
                rcv_buffer_size=self.__config[f"{key}_server_response_buffer_size"],
                )
        self.__update(key, response)
  
    def __heading_callback(self, msg:Float32):
        self.__general_callback(msg, "heading")

    def __fix_callback(self, msg:NavSatFix):
        self.__general_callback(msg, "fix")
        
    def __intrinsics_callback(self, msg:CameraInfo):
        self.__general_callback(msg, "intrinsics")

    def __rgb_callback(self, msg:Image):
        self.__general_callback(msg, "rgb")

    def __depth_callback(self, msg:Image):
        self.__general_callback(msg, "depth")



def main():
    try:
        rclpy.init()
        rclpy.spin(node=Receiver(config=CONFIGURATION))
    except (ExternalShutdownException, KeyboardInterrupt) as e:
        print(e)

if __name__ == '__main__':
    main()