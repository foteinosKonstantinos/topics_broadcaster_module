ROS_DISTRO=lyrical
source /opt/ros/$ROS_DISTRO/setup.bash

echo LOCAL

source ./install/local_setup.bash
ros2 run topics_broadcaster image_producer