# iotcomms
Benchmarking for emerging IoT application​ Benchmarks and Metrics​

# Please note that this work is a working in progress

# Description

The variety of different sensors, transport protocols and compute kernels involved in a single IoT applications impose a very challenging scenario for whoever decides to venture in this realm. That is because properly simulating IoT workload alone requires a lot of effort.

This framework aims to ease this burden. It allows users to quickly developt different IoT workloads, with different data rates even within the same application. To accomplish this, IoTCOMMS takes a probability distribution as input and generates patterns and hierarchical IoT structures that best simulate message rates coming from different sections of the applications.

# Setup and Configuration /app_gen/config.json

- topic_size_min: the minimum allowed topic size (per /). 
- topic_size_max: the maximum allowed topic size (per /).
- dest_port: destination port (cloud of gateway).
- dest_ip: destination ip (cloud of gateway).
- protocol: transport protocol (currently only supports MQTT).
- hierarchy: how devices are split across nodes of the application.
  - dist_type: poisson, normal, random etc.
  - dist: array of area nodes (1 factory --> 3 sectors --> 10 rooms --> 25 devices).
  - dist_params: lambdas, constants etc.
 
Once the application is configured run /deployment/run.sh to run application  
