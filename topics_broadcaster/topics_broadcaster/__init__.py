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

    "FPS": 0.5,

    "heading_topic_ugv": "/b2/nicla/magnetometer/heading",
    "heading_topic_gs": "/b2/nicla/magnetometer/heading_broadcasted",
    "heading_IP": "127.0.0.1",
    "heading_port": 49152,
    "heading_name": "Heading",
    "heading_buffer_size": 1024,
    "heading_key": "heading",

}