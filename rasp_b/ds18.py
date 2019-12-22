import os, glob, time
from common import Sensor, round_num_dict

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

long_id = '28-00000674764e'
short_id = '28-000006747eff'
base_dir = '/sys/bus/w1/devices/'

long_file = glob.glob(base_dir + long_id)[0] + '/w1_slave'
short_file = glob.glob(base_dir + short_id)[0] + '/w1_slave'

def read_temp_raw(device_file):
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp(device_file):
    lines = read_temp_raw(device_file)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c

def get():
    return round_num_dict({
        Sensor.ds18_long_temp.name: read_temp(long_file),
        Sensor.ds18_short_temp.name: read_temp(short_file)
    })