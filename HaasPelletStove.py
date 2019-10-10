#!/usr/bin/python3

import serial
import json

#### USER CONFIGURATION ####
DECODE_BITMASKS = True

#### BITMASKS ####
MASK_DOOR_CLOSED = 0b10
MASK_PELLETFEEDER_ON = 0b01
MASK_IGNITER_ON = 0b10
MASK_STOVE_HEATING = 0b10

#### DECLARATIONS ####

decodeMask = lambda input, mask: ((input & mask) == mask)

def getHaasPelletStoveInfo(serialPort):
    if serialPort is None: return None
    with serial.Serial(serialPort, 19200, timeout=2) as serialConn:
        line = None
        while not str(line).startswith('pm'):
            bytesRead = serialConn.readline()
            line = bytesRead.decode()

        line = line.strip('\r\n').strip('pm ')
        #print(line)

        #valueList = list(map(float, line.split(' ')))
        valueList = line.split(' ')
        #print(valueList)

        outputList = {
            'unknown_0' : float(valueList[0]),
            'current_flue_gas_temp' : float(valueList[1]),
            'unknown_2' : int(valueList[2]),
            'unknown_sz_soll' : float(valueList[3]),
            'unknown_4' : int(valueList[4]),
            'current_room_temp' : float(valueList[5]),
            'desired_room_temp' : int(valueList[6]),
            'desired_flue_gas_temp' : float(valueList[7]),
            'mat_soll_reg' : float(valueList[8]),
            'sz_soll_reg' : float(valueList[9]),
            'unknown_10' : float(valueList[10]),
            'correction_fan_percent' : float(valueList[11]),
            'desired_fan_percent' : int(valueList[12]),
            'desired_fan_rpm' : int(valueList[13]),
            'current_fan_rpm' : int(valueList[14]),
            'desired_material_percent' : float(valueList[15]),
            'material_consumed_kg' : int(valueList[16]),
            'burning_time_hours' : int(valueList[17]),
            'desired_chamber_temp' : float(valueList[18]),
            'current_chamber_temp' : float(valueList[19]),
            'current_chamber2_temp' : float(valueList[20]),
            'unknown_21' : int(valueList[21]),
            'seconds_in_current_stage' : int(valueList[22]),
            'unknown_23' : int(valueList[23]),
            'bitmask_24' : int(valueList[24]), #0b01 = STB??; 0b10 = DOOR CLOSED YES/NO
            'bitmask_25' : int(valueList[25]), #0b01 = PELLET FEEDER ON/OFF; 0b10 = IGNITER ON/OFF
            'bitmask_26' : int(valueList[26]), #0b10 = Heating ON/OFF?
            'bitmask_27' : int(valueList[27]),
            'bitmask_28' : int(valueList[28]),
            'bitmask_29' : int(valueList[29]),
            'bitmask_30' : int(valueList[30]),
            'bitmask_31' : int(valueList[31])
            }

        if DECODE_BITMASKS:
            isDoorClosed = decodeMask(int(valueList[24]), MASK_DOOR_CLOSED)
            isPelletFeederOn = decodeMask(int(valueList[25]), MASK_PELLETFEEDER_ON)
            isIgniterOn = decodeMask(int(valueList[25]), MASK_IGNITER_ON)
            isStoveHeating = decodeMask(int(valueList[26]), MASK_STOVE_HEATING)

            outputList['door_is_closed'] = isDoorClosed
            outputList['pelletfeed_is_on'] = isPelletFeederOn
            outputList['igniter_is_on'] = isIgniterOn
            outputList['stove_is_heating'] = isStoveHeating

        return json.dumps(outputList)