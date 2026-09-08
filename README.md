### TOPICS BROADCASTER

Transmits messages published on UGV Jetson to Ground Station.

Contact details: Foteinos Konstantinos (kfoteinos@hua.gr) (HUA Computer Vision Group)

> TODO: Add code for more topics (including image topics, probably chunking is required)

### Running instructions

Change the ROS distribution on all `.bash` scripts (on both machines):
```bash
ROS_DISTRO=<your distro>
source /opt/ros/$ROS_DISTRO/setup.bash
```

Adjust the configuration on the `__init__.py` (on both machines):
```python
CONFIGURATION = {

    ...

}
```

Run the following (on both machines):
```bash
chmod +x ./build.bash ./run_receiver.bash ./run_transmitter.bash
```

Build the ROS package (on both machines):
```bash
./build.bash
```

Run the receiver client (only on the UGV's Jetson):
```bash
./run_receiver.bash
```

Run the transmitter server (only on Ground Station):
```bash
./run_transmitter.bash
```