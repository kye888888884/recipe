from openai import OpenAI
import json

API_KEY = "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"
prompt = """당신은 요리사입니다. 재치있게 레시피를 설명해주세요. 형식은
    1. 재료
    - 재료 1
    - 재료 2
    - 재료 3
    2. 조리법
    1) 조리법 1
    2) 조리법 2
    3) 조리법 3
    과 같습니다. 조리법을 자세히 설명해주세요. 중간중간에 어울리는 이모지를 추가해주세요. 일반 텍스트만 사용해주세요."""

class GPT:
    def __init__(self):
        self.client = OpenAI(api_key=API_KEY)
        self.msgs = [
            {
                "role": "system",
                "content": prompt,
            }
        ]

    def chat(self, input_text):
        self.msgs.append({
            "role": "user",
            "content": input_text
        })

        for chunk in self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.msgs,
            temperature=0.3,
            # max_tokens=300,
            # top_p=1,
            # frequency_penalty=0,
            # presence_penalty=0,
            stream=True
        ):
            # print(chunk.choices[0].delta)
            chatcompletion_delta = chunk.choices[0].delta
            data = json.dumps(dict(chatcompletion_delta))
            # print(data)
            # json to dict
            data = json.loads(data)
            text = data["content"]
            if text == None:
                text = ""
            text = text.replace("\n", "@")
            yield f'{text}'

        # chat_response = completion.choices[0].message.content.strip()
        # self.msgs.append({
        #     "role": "assistant",
        #     "content": chat_response
        # })