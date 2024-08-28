import base64
import time
from enum import Enum
from openai import OpenAI


class Model(Enum):
    dummy = 0
    budget = 1
    full = 2


class Assistant:
    client = OpenAI(
        api_key='',
        organization='',
        project=''
    )

    def __init__(self, modelType, screenshotPath):
        self.modelType = modelType
        self.screenshotPath = screenshotPath

    @staticmethod
    def __encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def singleImageRequest(self, message):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo" if self.modelType == Model.budget else "gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": message
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{self.__encode_image(self.screenshotPath)}"
                        }
                    }
                ]
            }],
            max_tokens=300
        )
        return response.choices[0].message.content

    def singleRequest(self, message, imageLess=False):
        if self.modelType == Model.full and not imageLess:
            return self.singleImageRequest(message)

        elif self.modelType == Model.dummy:
            time.sleep(0.5)
            return ("What is Lorem Ipsum?\n\nLorem Ipsum is simply dummy text of the printing and typesetting "
                    "industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, "
                    "when an unknown printer took a galley of type and scrambled it to make a type specimen book. It "
                    "has survived not only five centuries, but also the leap into electronic typesetting, "
                    "remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset "
                    "sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like "
                    "Aldus PageMaker including versions of Lorem Ipsum.\n\nWhy do we use it?\n\nIt is a long "
                    "established fact that a reader will be distracted by the readable content of a page when looking "
                    "at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution "
                    "of letters, as opposed to using 'Content here, content here', making it look like readable "
                    "English. Many desktop publishing packages and web page editors now use Lorem Ipsum as their "
                    "default model text, and a search for 'lorem ipsum' will uncover many web sites still in their "
                    "infancy. Various versions have evolved over the years, sometimes by accident, sometimes on "
                    "purpose (injected humour and the like).\n\nWhere does it come from?\n\nContrary to popular "
                    "belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin "
                    "literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at "
                    "Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, "
                    "from a Lorem Ipsum passage, and going through the cites of the word in classical literature, "
                    "discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of 'de "
                    "Finibus Bonorum et Malorum' (The Extremes of Good and Evil) by Cicero, written in 45 BC. This "
                    "book is a treatise on the theory of ethics, very popular during the Renaissance. The first line "
                    "of Lorem Ipsum, 'Lorem ipsum dolor sit amet..', comes from a line in section 1.10.32.\n\nThe "
                    "standard chunk of Lorem Ipsum used since the 1500s is reproduced below for those interested. "
                    "Sections 1.10.32 and 1.10.33 from 'de Finibus Bonorum et Malorum' by Cicero are also reproduced "
                    "in their exact original form, accompanied by English versions from the 1914 translation by H. "
                    "Rackham.\n\nWhere can I get some?\n\nThere are many variations of passages of Lorem Ipsum "
                    "available, but the majority have suffered alteration in some form, by injected humour, "
                    "or randomised words which don't look even slightly believable. If you are going to use a passage "
                    "of Lorem Ipsum, you need to be sure there isn't anything embarrassing hidden in the middle of "
                    "text. All the Lorem Ipsum generators on the Internet tend to repeat predefined chunks as "
                    "necessary, making this the first true generator on the Internet. It uses a dictionary of over "
                    "200 Latin words, combined with a handful of model sentence structures, to generate Lorem Ipsum "
                    "which looks reasonable. The generated Lorem Ipsum is therefore always free from repetition, "
                    "injected humour, or non-characteristic words etc.")
        else:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo" if self.modelType == Model.budget else "gpt-4o",
                messages=[{
                    "role": "user",
                    "content": message
                }],
                max_tokens=300
            )
            return response.choices[0].message.content

    def validateQuestion(self, message, url):
        q = f"""
        Your job is to look at the following question inputted by a user regarding a website and 
        determine whether the question is relevant (an appropriate question that other people may have) 
        or irrelevant (something inappropriate or some random gibberish). 

        The question is regarding the website: {url}
        Answer with one word: either 'RELEVANT' or 'IRRELEVANT'
        Input: '{message}'
        """

        self.singleRequest(q)
        if self.modelType == Model.dummy:
            return None

        response = self.singleRequest(q)
        isRelevant = "IRRELEVANT" not in response.upper()
        if isRelevant:
            print(f"The AI thinks the question: '{message}' is RELEVANT")
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user",
                    "content": "Rewrite the following question using correct grammar, spelling, capitalisation, "
                               "punctuation so that it may be"
                               f"displayed in a FAQ: '{message}'"
                }],
                max_tokens=300
            )
            return response.choices[0].message.content
        else:
            print(f"The AI thinks the question: '{message}' is IRRELEVANT")
            return None



