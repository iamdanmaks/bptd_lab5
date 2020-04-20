from flask import Flask
from liqpay import LiqPay


app = Flask(__name__)
app.config.update(
    SECRET_KEY='paymentApp',
    public_key='sandbox_i31321528342',
    private_key='sandbox_4E2WdIDxDV4KzdXeUkPlfqGwzt6ufXxsqqOaXpyz'
)

lp = LiqPay(
    app.config.get('public_key'),
    app.config.get('private_key')
)

payments = []


from app import routes
