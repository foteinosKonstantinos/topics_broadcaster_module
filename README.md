### TOPICS BROADCASTER

Transmits messages published on UGV Jetson to Ground Station.

Contact details: Foteinos Konstantinos (kfoteinos@hua.gr) (HUA Computer Vision Group)

> TODO: Add code for more topics (including image topics, probably chunking is required)

### Running instructions

Adjust the configuration on the `___init__.py`:
```python
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
```

Run the following on both machines:
```bash
chmod +x ./build.bash ./run_reciever.bash ./run_transmitter.bash
```

Build the ROS package on both machines using:
```bash
./build.bash
```

Run the reciever client (Jetson):
```bash
./run_reciever.bash
```

Run the transmitter server (Ground Station):
```bash
./run_transmitter.bash
```