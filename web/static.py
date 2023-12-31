import io
import gzip
import os
from botocore.exceptions import ClientError
from boto3.session import Session
from flask import Blueprint, request, send_file
from server import app
from util.config import config


static = Blueprint('static', app.name)

session = Session()
s3 = session.client(
    service_name='s3',
    aws_access_key_id=config.storage.access_key,
    aws_secret_access_key=config.storage.secret_key,
    endpoint_url='https://' + config.storage.host,
    region_name=config.storage.region,
)


@static.get('/images/<path:path>')
def send_images(path):
    bucket = config.storage.bucket

    # get object from object storage
    try:
        o = s3.get_object(Bucket=bucket, Key=path)

        ae = request.headers.get('Accept-Encoding', '')
        if 'gzip' in ae.lower():
            # write bytes as gzip
            g = io.BytesIO()
            gf = gzip.GzipFile(mode='w+b', compresslevel=5, fileobj=g)
            gf.write(o.get('Body').read())
            gf.close()

            # seek the first byte
            g.seek(0)

            # write to response
            response = send_file(g, mimetype='image/webp')
            response.headers['Content-Encoding'] = 'gzip'
            return response

        b = io.BytesIO(o.get('Body').read())
        return send_file(b, mimetype='image/webp')
    except ClientError:
        path = os.getcwd() + '/assets/images/default.webp'
        with open(path, 'rb') as f:
            b = io.BytesIO(f.read())
            return send_file(b, mimetype='image/webp')
