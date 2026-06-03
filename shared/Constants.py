import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'proto'))

GATEWAY_TCP_PORT = 5000
GATEWAY_UDP_PORT = 5001

MULTICAST_PORT = 5002
MULTICAST_GROUP = "224.1.1.1"

BUFFER = 1024

HOST = "127.0.0.1"

PORTA_SENSOR_TEMP = 6001
PORTA_SENSOR_AR = 6002