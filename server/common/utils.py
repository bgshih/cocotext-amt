import re
import json
from django.conf import settings
import boto3


def get_mturk_client():
    endpoint_url = settings.MTURK_ENDPOINT_URL
    client = boto3.client('mturk', endpoint_url=endpoint_url)
    return client


PARSE_REGEX = re.compile(r"<FreeText>(.*)</FreeText>", re.MULTILINE)

def parse_answer_xml(answer_xml):
    answer_text = PARSE_REGEX.search(answer_xml).group(1)
    answer = json.loads(answer_text)
    return answer
