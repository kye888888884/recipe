from openai import OpenAI

API_KEY = "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"
prompt = """너는 즐거운 요리사야. 재치있게 레시피를 설명해줘. 형식은
    1. 재료
    - 재료 1
    - 재료 2
    - 재료 3
    2. 조리법
    1) 조리법 1
    2) 조리법 2
    3) 조리법 3
    3. 팁
    - 팁 1
    - 팁 2
    과 같아. 상대는 초보 요리사니까 조리법을 자세히 설명해줘야 해.
    중간중간에 어울리는 이모지를 하나씩만 추가해줘. 5개 이상은 안돼."""

class GPT:
    def __init__(self):
        self.client = OpenAI(api_key=API_KEY)
        self.msgs = [
            {
                "role": "system",
                "content": prompt
            }
        ]

    def chat(self, input_text):
        self.msgs.append({
            "role": "user",
            "content": input_text
        })

        completion = self.client.chat.completions.create(
            model="gpt-4",
            messages=self.msgs
        )

        chat_response = completion.choices[0].message.content.strip()
        self.msgs.append({
            "role": "assistant",
            "content": chat_response
        })

        return chat_response