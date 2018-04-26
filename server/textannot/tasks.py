from __future__ import absolute_import, unicode_literals

import xml.etree.ElementTree as ET
from celery import task

from common.models import QualificationType


def _score_answers(answer_xml):
    XMLNS_NAMESPACE = '{http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionFormAnswers.xsd}'
    answer_options = {
        'Q0': {'LINCOLN': 10},
        'Q1': {'Photo': 10},
        'Q2': {"A's": 10},
        'Q3': {'DELICIOUS': 10, 'Delicious': 10},
        'Q4': {'ST': 10},
        'Q5': {'SMOOTH': 10, 'Smooth': 10},
        'Q6': {'Silk': 10, 'silk': 10},
        'Q7': {'Chocolate': 10},
        'Q8': {'L-17': 10},
        'Q9': {'kefalotyri': 10},
    }
    root = ET.fromstring(answer_xml)
    total_score = 0
    for answer in root.findall('{}Answer'.format(XMLNS_NAMESPACE)):
        question_id = answer.find('{}QuestionIdentifier'.format(XMLNS_NAMESPACE)).text
        answer_text = answer.find('{}FreeText'.format(XMLNS_NAMESPACE)).text
        if question_id in answer_options:
            if answer_text in answer_options[question_id]:
                total_score += answer_options[question_id][answer_text]
    return total_score


@task()
def process_qualification_requests():
    qtype = QualificationType.objects.get(slug='textannot-test-v1')
    qtype.sync(sync_requests=True)
    for qrequest in qtype.requests.filter(status='P'):
        score = _score_answers(qrequest.answer)
        if score >= 80:
            qrequest.accept(value=score)
        else:
            qrequest.reject()
