import common
import requests

last_file = "../../last_readings.txt"

def post_update(sensor_data):
    sensor_data = { k.name:v for (k, v) in sensor_data.items() }
    units = common.get_units()

    readings = ''
    for k, v in sensor_data.items():
        readings += '%s: %s %s\n' % (k, v, units[k])

    backend_url = common.read_line_from('backend_url.txt') + '/update'
    secret = common.read_line_from('secret.txt')

    data = { **sensor_data, 'secret': secret }

    # Most clients will probably be using Wi-Fi to post their updates. Some of
    # them might also be a long distance from the router. As a result, they
    # might not always be able to post their updates on the first try, so try
    # several times until we get a positive response from the server.
    last_res = None
    tries = 5
    for i in range(tries):
        last_res = requests.post(backend_url, json = data)
        if last_res.status_code == 202:
            last_res = f'{last_res} on try {i + 1}\n'
            break

    common.print_to_file(readings + last_res, last_file)
