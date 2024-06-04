import base64
from enum import Enum
from openai import OpenAI


class Model(Enum):
    dummy = 0
    budget = 1  # Runs on GPT3.5 and does NOT have image comprehension
    full = 2  # Runs on GPT4 turbo and can comprehend images


class Assistant:
    client = OpenAI(
        api_key='sk-proj-Hk7lQnG5hrFLSmZyrG8oT3BlbkFJLCWjue2TvpUOVDfEq13n',
        organization='org-FICIIuzL80yQVyXuJMAQB090',
        project='proj_lI6Wlpb9Cl2kgL2L9OON5c59'
    )

    def __init__(self):
        pass

    @staticmethod
    def __encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def singleImageRequest(self, message, mode, image_path):
        if mode == Model.dummy:
            return "HMMM...Give me a second to think!"

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo" if mode == Model.budget else "gpt-4o",
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
                            "url": f"data:image/jpeg;base64,{self.__encode_image(image_path)}"
                        }
                    }
                ]
            }],
            max_tokens=300
        )
        return response.choices[0].message.content

    def singleRequest(self, message, mode):
        if mode == Model.dummy:
            # return "HMMM...Give me a second to think!"
            return "What is Lorem Ipsum?\n\nLorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.\n\nWhy do we use it?\n\nIt is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English. Many desktop publishing packages and web page editors now use Lorem Ipsum as their default model text, and a search for 'lorem ipsum' will uncover many web sites still in their infancy. Various versions have evolved over the years, sometimes by accident, sometimes on purpose (injected humour and the like).\n\nWhere does it come from?\n\nContrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of 'de Finibus Bonorum et Malorum' (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, 'Lorem ipsum dolor sit amet..', comes from a line in section 1.10.32.\n\nThe standard chunk of Lorem Ipsum used since the 1500s is reproduced below for those interested. Sections 1.10.32 and 1.10.33 from 'de Finibus Bonorum et Malorum' by Cicero are also reproduced in their exact original form, accompanied by English versions from the 1914 translation by H. Rackham.\n\nWhere can I get some?\n\nThere are many variations of passages of Lorem Ipsum available, but the majority have suffered alteration in some form, by injected humour, or randomised words which don't look even slightly believable. If you are going to use a passage of Lorem Ipsum, you need to be sure there isn't anything embarrassing hidden in the middle of text. All the Lorem Ipsum generators on the Internet tend to repeat predefined chunks as necessary, making this the first true generator on the Internet. It uses a dictionary of over 200 Latin words, combined with a handful of model sentence structures, to generate Lorem Ipsum which looks reasonable. The generated Lorem Ipsum is therefore always free from repetition, injected humour, or non-characteristic words etc."

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo" if mode == Model.budget else "gpt-4o",
            messages=[{
                "role": "user",
                "content": message
            }],
            max_tokens=300
        )
        return response.choices[0].message.content
