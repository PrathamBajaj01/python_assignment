from aws_lambda_wsgi import response
from app import create_app

app = create_app()

def lambda_handler(event, context):
    return response(app, event, context)
