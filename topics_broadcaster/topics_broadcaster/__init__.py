import abc

class Logger(abc.ABC):
    @abc.abstractmethod
    def info(self, msg):pass
    @abc.abstractmethod
    def warn(self, msg):pass
    @abc.abstractmethod
    def error(self, msg):pass

red_back = lambda x:f"\033[1;101m{x}\033[0;0m"
green_back = lambda x:f"\033[1;102m{x}\033[0;0m"
blue_back = lambda x:f"\033[1;104m{x}\033[0;0m"

red_fore = lambda x:f"\033[1;91m{x}\033[0;0m"
green_fore = lambda x:f"\033[1;92m{x}\033[0;0m"
blue_fore = lambda x:f"\033[1;94m{x}\033[0;0m"

# Available ports: 49152-65535

CONFIGURATION = {

    "heading_topic_ugv": "/b2/nicla/magnetometer/heading",
    "heading_topic_gs": "/b2/nicla/magnetometer/heading_broadcasted",
    "heading_server_IP": "127.0.0.1",
    "heading_server_port": 49152,
    "heading_name": "Heading",
    "heading_server_response_buffer_size": 16,
    "heading_message_buffer_size": 1024,
    "heading_fps": 2,

    "fix_topic_ugv": "/fix",
    "fix_topic_gs": "/fix_broadcasted",
    "fix_server_IP": "127.0.0.1",
    "fix_server_port": 49153,
    "fix_name": "Fix",
    "fix_server_response_buffer_size": 16,
    "fix_message_buffer_size": 1024,
    "fix_fps": 2,

    "rgb_topic_ugv": "/b2/camera_front_435i/realsense_front_435i/color/image_raw",
    "rgb_topic_gs": "/b2/camera_front_435i/realsense_front_435i/color/image_raw_broadcasted",
    "rgb_server_IP": "127.0.0.1",
    "rgb_server_port": 49154,
    "rgb_name": "RGB",
    "rgb_server_response_buffer_size": 16,
    "rgb_message_buffer_size": 1_000_000, # 640 x 480
    "rgb_fps": 0.5,

    "depth_topic_ugv": "/b2/camera_front_435i/realsense_front_435i/depth/image_rect_raw",
    "depth_topic_gs": "/b2/camera_front_435i/realsense_front_435i/depth/image_rect_raw_broadcasted",
    "depth_server_IP": "127.0.0.1",
    "depth_server_port": 49155,
    "depth_name": "Depth",
    "depth_server_response_buffer_size": 16,
    "depth_message_buffer_size": 1_000_000, # 640 x 480
    "depth_fps": 0.5,

    "intrinsics_topic_ugv": "/b2/camera_front_435i/realsense_front_435i/color/camera_info",
    "intrinsics_topic_gs": "/b2/camera_front_435i/realsense_front_435i/color/camera_info_broadcasted",
    "intrinsics_server_IP": "127.0.0.1",
    "intrinsics_server_port": 49156,
    "intrinsics_name": "Intrinsics",
    "intrinsics_server_response_buffer_size": 16,
    "intrinsics_message_buffer_size": 1024,
    "intrinsics_fps": 2,

}