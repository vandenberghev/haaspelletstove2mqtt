#!/usr/bin/python3

import HaasPelletStove as haas
import json
import paho.mqtt.client as mqtt
import time

#### USER MQTT CONFIG ####
MQTT_BROKER = "mqtt.myhost.com"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 30

HASS_TOPIC_PREFIX = "homeassistant" # Default 'homeassistant'
HASS_ENTITY_NAME = "mypelletstove"  # Used for topics + sensor prefix
HASS_CONFIG_SUFFIX = "config"       # Should not be changed
HASS_STATE_SUFFIX = "state"         # Should not be changed

SECONDS_BETWEEN_REFRESH = 10

#### MAPPINGS TO HOME ASSISTANT ####
def getHassComponentTypeFor(key):
    if key in KNOWN_KEYS:
        config = KNOWN_KEYS[key]
        if CONFIG_SENSOR_TYPE in config: return config[CONFIG_SENSOR_TYPE]
    return "sensor" #Fallback

def getBaseTopic(key):
    return HASS_TOPIC_PREFIX + "/" + getHassComponentTypeFor(key) + "/" + HASS_ENTITY_NAME + "_" + key

def getStateTopic(key):
    return getBaseTopic(key) + "/" + HASS_STATE_SUFFIX

def getConfigTopic(key):
    return getBaseTopic(key) + "/" + HASS_CONFIG_SUFFIX

def getConfigInfo(key):
    configInfo = {}
    configInfo["state_topic"] = getStateTopic(key)
    configInfo["name"] = HASS_ENTITY_NAME + "_" + key
    if key in KNOWN_KEYS:
        config = KNOWN_KEYS[key]
        for ck in INCLUDED_CONFIG_KEYS:
            if ck in config: configInfo[ck] = config[ck]
    return str(json.dumps(configInfo))

#### KNOWN KEYS ####
#Index vs configuration
CONFIG_UNIT_OF_MEASUREMENT = "unit_of_measurement"
CONFIG_NAME = "friendly_name"
CONFIG_SENSOR_TYPE = "sensor_type"
CONFIG_DEVICE_CLASS = "device_class"
CONFIG_PAYLOAD_ON = "payload_on"
CONFIG_PAYLOAD_OFF = "payload_off"

INCLUDED_CONFIG_KEYS = [CONFIG_UNIT_OF_MEASUREMENT, CONFIG_DEVICE_CLASS, CONFIG_PAYLOAD_ON, CONFIG_PAYLOAD_OFF] #, CONFIG_NAME]

KNOWN_KEYS = {
    "current_flue_gas_temp": { CONFIG_UNIT_OF_MEASUREMENT: "°C", CONFIG_NAME: "Flue gas", CONFIG_SENSOR_TYPE: "sensor" },
    "current_room_temp": { CONFIG_UNIT_OF_MEASUREMENT: "°C", CONFIG_NAME: "Room", CONFIG_SENSOR_TYPE: "sensor" },
    "desired_room_temp": { CONFIG_UNIT_OF_MEASUREMENT: "°C", CONFIG_NAME: "Room (target)", CONFIG_SENSOR_TYPE: "sensor" },
    "desired_flue_gas_temp": { CONFIG_UNIT_OF_MEASUREMENT: "°C", CONFIG_NAME: "Flue gas (target)", CONFIG_SENSOR_TYPE: "sensor" },
    "mat_soll_reg": { CONFIG_UNIT_OF_MEASUREMENT: "%", CONFIG_NAME: "mat_soll_reg", CONFIG_SENSOR_TYPE: "sensor" },
    "sz_soll_reg": { CONFIG_UNIT_OF_MEASUREMENT: "%", CONFIG_NAME: "sz_soll_reg", CONFIG_SENSOR_TYPE: "sensor" },
    "correction_fan_percent": { CONFIG_UNIT_OF_MEASUREMENT: "%", CONFIG_NAME: "Fan correction", CONFIG_SENSOR_TYPE: "sensor" },
    "desired_fan_percent": { CONFIG_UNIT_OF_MEASUREMENT: "%", CONFIG_NAME: "Fan (target)", CONFIG_SENSOR_TYPE: "sensor" },
    "desired_fan_rpm": { CONFIG_UNIT_OF_MEASUREMENT: "rpm", CONFIG_NAME: "Fan (target)", CONFIG_SENSOR_TYPE: "sensor" },
    "current_fan_rpm": { CONFIG_UNIT_OF_MEASUREMENT: "rpm", CONFIG_NAME: "Fan", CONFIG_SENSOR_TYPE: "sensor" },
    "desired_material_percent": { CONFIG_UNIT_OF_MEASUREMENT: "%", CONFIG_NAME: "Pellet feed", CONFIG_SENSOR_TYPE: "sensor" },
    "material_consumed_kg": { CONFIG_UNIT_OF_MEASUREMENT: "kg", CONFIG_NAME: "Pellets consumed", CONFIG_SENSOR_TYPE: "sensor" },
    "burning_time_hours": { CONFIG_UNIT_OF_MEASUREMENT: "h", CONFIG_NAME: "Total burning time", CONFIG_SENSOR_TYPE: "sensor" },
    "desired_chamber_temp": { CONFIG_UNIT_OF_MEASUREMENT: "°C", CONFIG_NAME: "Chamber (desired)", CONFIG_SENSOR_TYPE: "sensor" },
    "current_chamber_temp": { CONFIG_UNIT_OF_MEASUREMENT: "°C", CONFIG_NAME: "Chamber", CONFIG_SENSOR_TYPE: "sensor" },
    "current_chamber2_temp": { CONFIG_UNIT_OF_MEASUREMENT: "°C", CONFIG_NAME: "Chamber 2", CONFIG_SENSOR_TYPE: "sensor" },
    "seconds_in_current_stage": { CONFIG_UNIT_OF_MEASUREMENT: "s", CONFIG_NAME: "Seconds in stage", CONFIG_SENSOR_TYPE: "sensor" },
    "door_is_closed": { CONFIG_DEVICE_CLASS: "door", CONFIG_NAME: "Door", CONFIG_SENSOR_TYPE: "binary_sensor", CONFIG_PAYLOAD_ON: "True", CONFIG_PAYLOAD_OFF: "False" },
    "pelletfeed_is_on": { CONFIG_DEVICE_CLASS: "moving", CONFIG_NAME: "Pellet feed", CONFIG_SENSOR_TYPE: "binary_sensor", CONFIG_PAYLOAD_ON: "True", CONFIG_PAYLOAD_OFF: "False" },
    "igniter_is_on": { CONFIG_DEVICE_CLASS: "heat", CONFIG_NAME: "Igniter", CONFIG_SENSOR_TYPE: "binary_sensor", CONFIG_PAYLOAD_ON: "True", CONFIG_PAYLOAD_OFF: "False" },
    "stove_is_heating": { CONFIG_NAME: "Heating", CONFIG_SENSOR_TYPE: "binary_sensor", CONFIG_PAYLOAD_ON: "True", CONFIG_PAYLOAD_OFF: "False" }
    #"": { CONFIG_UNIT_OF_MEASUREMENT: "°C", CONFIG_NAME: "", CONFIG_SENSOR_TYPE: "sensor" },
    #"": { CONFIG_DEVICE_CLASS: "", CONFIG_NAME: "", CONFIG_SENSOR_TYPE: "binary_sensor" },
}

# Initiate MQTT Client
mqttc = mqtt.Client()
mqttc.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)

print('Configuring topics...')
#Configure HASS MQTT topics
for k in KNOWN_KEYS:
    configTopic = getConfigTopic(k)
    configInfo = getConfigInfo(k)
    mqttc.publish(configTopic, configInfo, retain=True)

#### RUN ####
while True:
    print('Fetching stove info...')
    haasJson = haas.getHaasPelletStoveInfo('/dev/ttyACM0')
    haasInfo = json.loads(haasJson)

    for k in haasInfo:
        if not k in KNOWN_KEYS: continue
        stateTopic = getStateTopic(k)
        mqttc.publish(stateTopic, haasInfo[k])

    mqttc.loop()
    time.sleep(SECONDS_BETWEEN_REFRESH)