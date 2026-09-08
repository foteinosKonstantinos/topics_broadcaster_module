ROS_DISTRO=lyrical
source /opt/ros/$ROS_DISTRO/setup.bash

echo GROUND STATION

source ./install/local_setup.bash
ros2 run topics_broadcaster transmitter_server