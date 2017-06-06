from django.conf import settings
import boto3

def get_mturk_client():
    endpoint_url = settings.ENDPOINT_URL
    client = boto3.client('mturk', endpoint_url=endpoint_url)
    return client
