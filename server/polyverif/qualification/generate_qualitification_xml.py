from lxml import etree


TEST_TEMPALTE = \
"""<QuestionForm xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionForm.xsd">
  <Overview>
    <Title>Read the instructions and finish the tests.</Title>
    <FormattedContent><![CDATA[
      <h3>Job Description</h3>

      <p>We are collecting a dataset of text in natural images. In this dataset, each word should be annotated by a polygon that tightly surrounds it. We have some existing annotations. Your job is to judge these annotations.</p>
      <p>You will see a grid of cards, each an annotation. Click on the cards to mark them as correct (green) or wrong (red). Submit after marking all cards.</p>

      <h3>Examples (click to enlarge)</h3>
      <a href="https://s3.amazonaws.com/cocotext-amt-resource/polygon-verification-examples.jpg">
        <img alt="Examples"
             src="https://s3.amazonaws.com/cocotext-amt-resource/polygon-verification-examples.jpg"
             width="800" />
      </a>
    ]]></FormattedContent>
  </Overview>

{0}
</QuestionForm>
"""

QUESTION_TEMPALTE = \
"""  <Question>
    <!-- Q{0} -->
    <QuestionIdentifier>Q{0}</QuestionIdentifier>
    <DisplayName>Question-{0}</DisplayName>
    <IsRequired>true</IsRequired>
    <QuestionContent>
      <Text>Is this annotation correct?</Text>
      <Binary>
        <MimeType>
          <Type>image</Type>
          <SubType>png</SubType>
        </MimeType>
        <DataURL>
          https://s3.amazonaws.com/cocotext-amt-resource/test_questions/q{0}.png
        </DataURL>
        <AltText>Question-{0}</AltText>
      </Binary>
    </QuestionContent>

    <AnswerSpecification>
      <SelectionAnswer>
        <StyleSuggestion>radiobutton</StyleSuggestion>
        <Selections>
          <Selection>
            <SelectionIdentifier>W</SelectionIdentifier>
            <Text>Wrong</Text>
          </Selection>
          <Selection>
            <SelectionIdentifier>C</SelectionIdentifier>
            <Text>Correct</Text>
          </Selection>
        </Selections>
      </SelectionAnswer>
    </AnswerSpecification>
  </Question>
"""

ANSWER_KEY_TEMPLATE = \
"""<AnswerKey xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/AnswerKey.xsd">
{0}
  <QualificationValueMapping>
    <PercentageMapping>
      <MaximumSummedScore>100</MaximumSummedScore>
    </PercentageMapping>
  </QualificationValueMapping>
</AnswerKey>
"""

QUESTION_ANSWER_TEMPLATE = \
"""  <Question>
    <QuestionIdentifier>Q{0}</QuestionIdentifier>
    <AnswerOption>
      <SelectionIdentifier>{1}</SelectionIdentifier>
      <AnswerScore>10</AnswerScore>
    </AnswerOption>
  </Question>
"""

GROUNDTRUTH_ANSWERS = ['C', 'W', 'W', 'W', 'W', 'C', 'C', 'W', 'W', 'C']

def generate_test():
    questions_str = '\n\n'.join([QUESTION_TEMPALTE.format(i+1) for i in range(10)])
    test_str = TEST_TEMPALTE.format(questions_str)

    with open('test.xml', 'w') as f:
        f.write(test_str)


def generate_answer_key():
    questions = [
        QUESTION_ANSWER_TEMPLATE.format(i+1, GROUNDTRUTH_ANSWERS[i]) for i in range(10)
    ]
    question_answers_str = '\n\n'.join(questions)
    answer_key_str = ANSWER_KEY_TEMPLATE.format(question_answers_str)

    with open('answer_key.xml', 'w') as f:
        f.write(answer_key_str)


if __name__ == '__main__':
    generate_test()
    generate_answer_key()
