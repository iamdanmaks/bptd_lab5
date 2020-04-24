import json
import uuid

from datetime import datetime
from dateutil.parser import parse

from flask import get_flashed_messages
from flask import flash
from flask import jsonify
from flask import render_template
from flask import render_template_string
from flask import request

from app import app
from app import rooms
from app import lp
from app import payments


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html', data=rooms)


@app.route('/date_form', methods=['GET'])
def date_form():
    return render_template('date.html', room=rooms[int(request.args.get('id')) - 1])


@app.route('/payment_form', methods=['GET'])
def payment_form():
    room_id = int(request.args.get('id')) - 1

    order_id = str(uuid.uuid4())

    html = lp.cnb_form({
        'action': 'pay',
        'amount': str(int(request.args.get('days')) * \
            rooms[room_id]['price']),
        'currency': 'USD',
        'description': str(str(rooms[room_id]['id']) + '. For ' + \
            request.args.get('days') + ' days. ' + \
            rooms[room_id]['name'] + '. ' + rooms[room_id]['desc']),
        'order_id': order_id,
        'version': '3',
        'sandbox': 1,
        'server_url': 'https://bptdlb5.herokuapp.com/callback'
    })

    payments[order_id] = [False, room_id, int(request.args.get('days'))]
    rooms[room_id]['available_from'] = request.args.get('end')

    return render_template_string(
        html.strip().replace('\n', '').replace('\t', '').replace("'", '"')
    )


@app.route('/callback', methods=['GET', 'POST'])
def callback():
    unhashed = lp.str_to_sign(
        app.config.get('private_key') + request.form.get('data') + app.config.get('private_key')
    )

    if unhashed == request.form.get('signature'):
        for k, v in payments.items():
            if not v:
                res = lp.api("request", {
                    "action": "status",
                    "version": "3",
                    "order_id": k
                })

                if res['status'] == 'success':
                    payments[k][0] = True
                    rooms[v[1]]['available_from'] = \
                        parse(rooms[v[1]]['available_from']) + \
                            datetime.timedelta(days=v[2])
    
    return "done"
