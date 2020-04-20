import json
import uuid

from flask import jsonify
from flask import render_template
from flask import render_template_string
from flask import request

from app import app
from app import lp
from app import payments


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html', transactions=payments)


@app.route('/payment_form', methods=['GET'])
def payment_form():
    html = lp.cnb_form({
        'action': 'pay',
        'amount': '1',
        'currency': 'USD',
        'description': 'Платёж для лабароторной',
        'order_id': str(uuid.uuid4()),
        'version': '3',
        'sandbox': 1,
        'server_url': 'https://bptdlb5.herokuapp.com/callback'
    })

    return render_template_string(
        html.strip().replace('\n', '').replace('\t', '').replace("'", '"')
    )


@app.route('/callback', methods=['GET', 'POST'])
def callback():
    unhashed = lp.str_to_sign(
        app.config.get('private_key') + request.form.get('data') + app.config.get('private_key')
    )

    if unhashed == request.form.get('signature'):
        payments.append({
            'signature': request.form.get('signature'),
            'data': request.form.get('data'),
            'valid': unhashed == request.form.get('signature')
        })
    
    return jsonify(payments[-1])
