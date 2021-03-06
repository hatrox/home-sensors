#!/usr/bin/python3

from flask import Flask, request, redirect, abort, jsonify, render_template
from datetime import timedelta
import json
import os

import storage
from storage import Mode
import common
from hardware import Client, Sensor
import validator

app = Flask(__name__, template_folder=common.get_abs_path('templates'))

LOCAL_ENV = os.getenv('ENVIRONMENT', '') == 'local'
SECRET = common.read_line_from('secret.txt')

if LOCAL_ENV: print('Running in local/test mode...')

@app.route('/', methods = ['GET'])
def home():
    return redirect('/get', code=302)

@app.route('/update', methods = ['POST'])
def update():
    if 'secret' not in request.json or request.json['secret'] != SECRET:
        return abort(403)

    values = []
    client = None
    for rasp in Client.items:
        for sensor in rasp.sensors:
            name = sensor.name
            if name not in request.json: break

            if not validator.is_sane(sensor, request.json[name]):
                print('Got weird value for sensor %s: %s' % \
                    (name, request.json[name]))
                break

            values.append(request.json[name])
        else:
            if len(values) == len(rasp.sensors):
                client = rasp

    if not client:
        return abort(400)

    storage.put(LOCAL_ENV, client, values)
    return 'success', 202

def get(mode=Mode.avg):
    client = Client.from_str(request.args.get('client', default='', type=str))
    hours = request.args.get('hours', default=0, type=int)
    days = request.args.get('days', default=0, type=int)
    weeks = request.args.get('weeks', default=0, type=int)
    json = 'json' in request.args

    clients = [ client ] if client else Client.items

    data = storage.get(LOCAL_ENV, timedelta(
            hours=hours,
            days=days,
            weeks=weeks,
        ),
        mode,
        clients
    )

    if json:
        return jsonify(data)
    else:
        return render_template('get.html',
            readouts=data,
            header=','.join([ c['client'] for c in data ]),
            units=Sensor.get_map(),
        )

@app.route('/get', methods = ['GET'])
def get_default():
    return get()

@app.route('/get/avg', methods = ['GET'])
def get_avg():
    return get(mode=Mode.avg)

@app.route('/get/min', methods = ['GET'])
def get_min():
    return get(mode=Mode.min)

@app.route('/get/max', methods = ['GET'])
def get_max():
    return get(mode=Mode.max)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
