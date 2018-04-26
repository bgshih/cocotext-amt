TEST_TEMPALTE = \
"""<QuestionForm xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionForm.xsd">
  <Overview>
    <Title>Read the instructions and finish the tests.</Title>
    <FormattedContent><![CDATA[
      <h2>Job Description</h2>

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

      <h2>Examples</h2>
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


def generate_test():
    questions_str = '\n\n'.join([QUESTION_TEMPALTE.format(i) for i in range(10)])
    test_str = TEST_TEMPALTE.format(questions_str)

    with open('test.xml', 'w') as f:
        f.write(test_str)


if __name__ == '__main__':
    generate_test()
