import os
import google.cloud.dialogflow_v2 as dialogflow
import json

KEY_PATH = 'private_key.json'
DIALOGFLOW_LANGUAGE_CODE ='ko'

class Intent:
    def __init__(self, key_path: str, session_id: str = 'me'):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
        with open(key_path) as f:
            key = json.load(f)
            self.__DIALOGFLOW_PROJECT_ID = key["project_id"]
        self.__session_client = dialogflow.SessionsClient()
        self.__session = self.__session_client.session_path(self.__DIALOGFLOW_PROJECT_ID, session_id)
        self.__response = None

    def input(self, query: str):
        our_input = dialogflow.types.TextInput(text=query,language_code=DIALOGFLOW_LANGUAGE_CODE)
        query = dialogflow.types.QueryInput(text=our_input)
        self.__response = self.__session_client.detect_intent(session=self.__session,query_input=query)
        return self.get_response()
    
    def get_response(self) -> str:
        if self.__response is None:
            return "No response"
        return self.__response.query_result.fulfillment_text
    
    def get_intent(self) -> str:
        if self.__response is None:
            return "No response"
        return self.__response.query_result.intent.display_name
    
    def get_session_id(self) -> None:
        return self.__session_id
    
    def get_context(self) -> str:
        if self.__response is None:
            return "No response"
        return self.__response.query_result.output_contexts

if __name__ == "__main__":
    intent = Intent(KEY_PATH)
    while True:
        input_text = input("Input: ")
        data = intent.input(input_text)
        print("Output:", data)
        print("Intent:", intent.get_intent())
        # print("context:", intent.get_context())