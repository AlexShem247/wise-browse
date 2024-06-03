import base64
from enum import Enum
from openai import OpenAI

class Model(Enum):
    dummy = 0
    budget = 1 #Runs on GPT3.5 and does NOT have image comprehension
    full = 2  #Runs on GPT4 turbo and can comprehend images
    
class Assistant:
    client = OpenAI(
        api_key = 'sk-proj-Hk7lQnG5hrFLSmZyrG8oT3BlbkFJLCWjue2TvpUOVDfEq13n',
        organization = 'org-FICIIuzL80yQVyXuJMAQB090',
        project = 'proj_lI6Wlpb9Cl2kgL2L9OON5c59'
    )

    def __init__(self):
        pass
    
    def __encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def singleImageRequest(self, message, mode, image_path):
        if mode == Model.dummy: 
            return "HMMM...Give me a second to think!"
            
        response = self.client.chat.completions.create(
            model = "gpt-3.5-turbo" if mode == Model.budget else "gpt-4o" ,
            messages = [{
                "role" : "user", 
                "content" : [
                    {
                        "type" : "text",
                        "text" : message
                    },
                    {
                        "type" : "image_url",
                        "image_url" : {
                            "url" : f"data:image/jpeg;base64,{self.__encode_image(image_path)}"
                        }
                    }
                ]
            }],
            max_tokens = 300
        )
        return response.choices[0]

    def singleRequest(self, message, mode):
        if mode == Model.dummy: 
            return "HMMM...Give me a second to think!"
        
        response = self.client.chat.completions.create(
            model = "gpt-3.5-turbo" if mode == Model.budget else "gpt-4o" ,
            messages = [{
                "role" : "user", 
                "content" : message
            }],
            max_tokens = 300
        )
        return response.choices[0].message.content

        

