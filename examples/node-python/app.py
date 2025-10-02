import os, time, json
import paho.mqtt.client as mqtt

MQTT_URL = os.environ.get("MQTT_URL", "tcp://localhost:1883")
TOPIC = os.environ.get("TOPIC", "robot/demo")
client_id = f"example-python-{int(time.time())}"

def parse_url(url):
    # very small parser: tcp://host:port
    assert url.startswith("tcp://")
    host_port = url[len("tcp://"):]
    host, port = host_port.split(":")
    return host, int(port)

host, port = parse_url(MQTT_URL)
cli = mqtt.Client(client_id=client_id, clean_session=True, protocol=mqtt.MQTTv311)
cli.will_set("robot/status/example-python", payload="0", retain=True)
cli.connect(host, port, keepalive=30)
cli.loop_start()
cli.publish("robot/status/example-python", "1", retain=True)

i = 0
try:
    while True:
        msg = {"seq": i, "ts": time.time()}
        cli.publish(TOPIC, json.dumps(msg))
        i += 1
        time.sleep(1.0)
except KeyboardInterrupt:
    pass
finally:
    cli.publish("robot/status/example-python", "0", retain=True)
    cli.loop_stop()
    cli.disconnect()
