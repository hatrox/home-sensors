import requests
import signal
import common
from datetime import datetime

from hardware import Sensor

last_file = '../../last_readings.txt'
thread_timeout = 5 * 60 # in seconds
timestamp_fmt = '%Y-%m-%d %H:%M:%S'

def get_timestamp():
    now = datetime.now()
    return f'timestamp: {now.strftime(timestamp_fmt)}\n'

def __handler__(signum, frame):
    err = 'Error getting sensor data!'
    common.print_to_file(err, last_file)
    raise RuntimeError(err)

def __post_update__(client):
    sensor_data = {}
    for sensor in client.sensors:
        datum = {}
        if sensor in Sensor.BME:
            if sensor in sensor_data: continue

            info = sensor.reader().get()
            for i, v in enumerate(info):
                datum.update({ Sensor.BME[i]: v })

        else:
            datum = { sensor: sensor.reader().get() }

        sensor_data.update(common.round_num_dict(datum))

    readings = ''
    for k, v in sensor_data.items():
        readings += '%s: %s %s\n' % (k.name, v, k.unit)

    sensor_data = { k.name:v for (k, v) in sensor_data.items() }
    secret = common.read_line_from('secret.txt')

    data = { **sensor_data, 'secret': secret }

    # Most clients will probably be using Wi-Fi to post their updates. Some of
    # them might also be a long distance from the router. As a result, they
    # might not always be able to post their updates on the first try, so try
    # several times until we get a positive response from the server.
    backend_url = common.read_line_from('backend_url.txt') + '/update'
    last_res = None
    tries = 5
    for i in range(tries):
        last_res = requests.post(backend_url, json = data)
        if last_res.status_code == 202:
            last_res = f'{last_res} on try {i + 1}'
            break

    timestamp = get_timestamp()
    common.print_to_file('%s%s%s\n' % (
                readings,
                timestamp,
                last_res),
            last_file)


def post_update(client):
    # Some sensors use serial communication and are prone to hangs. In such
    # occasions, it's better to just crash, freeing all used resources, as the
    # next instantiation of this script may not be able to access the needed
    # serial ports otherwise.

    signal.signal(signal.SIGALRM, __handler__)
    signal.alarm(thread_timeout)

    __post_update__(client)

    # Disable the alarm
    signal.alarm(0)
