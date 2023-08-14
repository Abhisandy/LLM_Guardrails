import streamlit as st
import os
from dotenv import load_dotenv
import openai
from profanity_check import predict
from pydantic.fields import ModelField
import guardrails as gd
from rich import print

from typing import Dict, List



load_dotenv()

#openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = "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"

def without_guardrails(text):
    response = openai.Completion.create(
        prompt="Translate the texts to English language\n"+text,
        engine="text-davinci-003",
        max_tokens=2048,
        temperature=0)

    result = response['choices'][0]['text']
    return result

rail_str = """
<rail version="0.1">

<script language = 'python'>

from guardrails.validators import Validator, EventDetail, register_validator
from typing import Dict, List
from profanity_check import predict

@register_validator(name="is-profanity-free", data_type="string")

class IsProfanityFree(Validator):
    global predict
    global EventDetail

    def validate(self, key, value, schema) -> Dict:
        text = value
        prediction = predict([value])
        if prediction[0] == 1:
            raise EventDetail(
            key,
            value,
            schema,
            f"Value {value} contains profanity language",
            "Sorry,It contains profanity language. I can't return the results",
            )

        return schema
</script>

<output>
    <string
        name = "translated_statement"
        description = "Translate the given statement into english language"
        format = "is-profanity-free"
        on-fail-is-profanity-free = "fix"
    />
</output>

<prompt>

Translate the given Statement into English language:

{{statement_to_be_translated}}

@complete_json_suffix

</prompt>


</rail>
"""

guard = gd.Guard.from_rail_string(rail_str)

def main():
    st.title("Guardrails Demo")
    text_area = st.text_area("Enter Query to translate")

    if st.button("Translate"):
        if len(text_area) > 0:
            st.info(text_area)

            st.warning("Translating without Guardrails")

            without_guardrails_result = without_guardrails(text_area)
            st.success(without_guardrails_result)

            st.warning("Translating with Guardrails")

           
            
            raw_llm_response, validated_response = guard(
                openai.Completion.create,
                prompt_params={"statement_to_be_translated": text_area},
                engine="text-davinci-003",
                max_tokens=2048,
                temperature=0)

            st.write(validated_response)
            #st.success(f"Validated Output: {validated_response}")
            

if __name__ == '__main__':
    main()