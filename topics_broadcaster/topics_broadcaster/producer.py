from PIL import Image as PILImage
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image as SensorImage
from rclpy.executors import ExternalShutdownException
from . import CONFIGURATION

class Producer(Node):

    def __init__(self):
        super().__init__("image_producer")
        
        self.__color_publisher=self.create_publisher(
            msg_type = SensorImage,
            topic = CONFIGURATION["rgb_topic_ugv"],
            qos_profile = 10
        )

        self.__timer = self.create_timer(0.5, self.publish) # 2 FPS

    def publish(self, path="/home/konstantinosf/Projects/topics_broadcaster_module/topics_broadcaster/topics_broadcaster/image.png"):
        color = np.asarray(PILImage.open(path).convert("RGB"))
        msg = SensorImage()
        msg.height = color.shape[0]
        msg.width = color.shape[1]
        msg.encoding = "rgb8"
        msg.is_bigendian = False
        msg.step = 3 * color.shape[1]
        msg.data = color.tobytes()
        self.__color_publisher.publish(msg)
        self.get_logger().info("Published.")

def main():
    try:
        rclpy.init()
        rclpy.spin(node=Producer())
    except (ExternalShutdownException, KeyboardInterrupt) as e:
        print(e)

if __name__ == '__main__':
    main()