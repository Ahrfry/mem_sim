
import paho.mqtt.subscribe as subscribe

topics = ['paho/test/single']

m = subscribe.simple(topics, hostname="localhost", retained=False, msg_count=2)
for a in m:
    print(a.topic)
    print(a.payload)