TEST_TEMPALTE = \
"""<QuestionForm xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionForm.xsd">
  <Overview>
    <Title>Read the instructions and finish the tests.</Title>
    <FormattedContent><![CDATA[
      <h3>Job Description</h3>

      <h3>Job Description</h3>

      <p>
        <b>Your task: Annotate text in every image.</b>
      </p>
      <p>
        If text is illegible (unable to read) check the "Illegible" checkbox.
        If text is not in a langauge that you know, check the "Unknown Language" checkbox.
      </p>

      <p>
        Punctuations and symbols should be annotated as well.
        For your convenience, common symbols have been provided on the toolbar for you to copy and paste.
      </p>

      <h3>Examples (click to enlarge)</h3>
      <a href="https://s3.amazonaws.com/cocotext-amt-resource/text-annotation-examples.png">
        <img alt="Examples"
             src="https://s3.amazonaws.com/cocotext-amt-resource/text-annotation-examples.png"
             width="800" />
      </a>
    ]]></FormattedContent>
  </Overview>

{0}
</QuestionForm>
"""

QUESTION_TEMPALTE = \
"""  <Question>
    <QuestionIdentifier>Q{0}</QuestionIdentifier>
    <DisplayName>Question-{0}</DisplayName>
    <IsRequired>true</IsRequired>
    <QuestionContent>
      <Text>Annotate the text in this image.</Text>
      <Binary>
        <MimeType>
          <Type>image</Type>
          <SubType>jpg</SubType>
        </MimeType>
        <DataURL>https://s3.amazonaws.com/cocotext-amt-resource/textannot-test-questions/q{0}.jpg</DataURL>
        <AltText>Question-{0}</AltText>
      </Binary>
    </QuestionContent>

    <AnswerSpecification>
      <FreeTextAnswer>
        <Constraints>
          <Length maxLength="128" />
        </Constraints>
      </FreeTextAnswer>
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
"""<Question>
    <QuestionIdentifier>Q{0}</QuestionIdentifier>
    <Answer>
      <FreeText>{1}</FreeText>
      <AnswerScore>10</AnswerScore>
    </Answer>
  </Question>
"""

GROUNDTRUTH_ANSWERS = [
  "LINCOLN",
  "Photo",
  "A's",
  "DELICIOUS",
  "ST",
  "SMOOTH",
  "Silk",
  "Chocolate",
  "L-17",
  "kefalotyri"
]


def generate_test():
    questions_str = '\n\n'.join([QUESTION_TEMPALTE.format(i) for i in range(10)])
    test_str = TEST_TEMPALTE.format(questions_str)

    with open('test.xml', 'w') as f:
        f.write(test_str)


def generate_answer_key():
    questions = [
        QUESTION_ANSWER_TEMPLATE.format(i, GROUNDTRUTH_ANSWERS[i]) for i in range(10)
    ]
    question_answers_str = '\n\n'.join(questions)
    answer_key_str = ANSWER_KEY_TEMPLATE.format(question_answers_str)

    with open('answer_key.xml', 'w') as f:
        f.write(answer_key_str)


if __name__ == '__main__':
    generate_test()
    generate_answer_key()
