from openai import OpenAI


class Conversation:
    # The API Reference suggests that (even though they have the same
    # key/org/proj) a client should be generated for each instance.
    client = OpenAI(
        api_key='sk-proj-Hk7lQnG5hrFLSmZyrG8oT3BlbkFJLCWjue2TvpUOVDfEq13n',
        organization='org-FICIIuzL80yQVyXuJMAQB090',
        project='proj_lI6Wlpb9Cl2kgL2L9OON5c59'
    )

    def __init__(self, user_id: str, assistant_id: str, keepHistory: bool, keepFiles: bool, filepath):
        self.user_id = user_id
        self.assistant_id = assistant_id
        self.filepath = filepath

        self.keepHistory = keepHistory
        self.content_history = []

        self.keepFiles = keepFiles
        self.file_ids = []

        self.current_step = 0
        self.steps = []

        # Initialises a new conversation for which, if neccesary

    # saves up it's history and files and dedicates an assistant
    # for it.
    def start(self):
        return ("Hello! I'm here to assist you with your web-browsing tasks step-by-step. "
                "Let's get started! What can I assist you with today?")

    # Depending on the set privileges it 
    def end(self):
        if not self.keepFiles:
            self.__erase_files()
            print("Files erased")

        if not self.keepHistory:
            self.__erase_history()
            print("History erased")

        return "Thank you for using Web Bud"

    def request(self, message):

        # Preparing the screenshot
        file = self.client.files.create(
            file=open(self.filepath, "rb"),
            purpose="vision"
        )
        self.file_ids.append(file.id)

        # Saving the question to in local history
        self.content_history.append(("user", self.__to_content(message, file.id)))

        # Preparing the thread
        threadToRun = self.client.beta.threads.create(
            messages=self.__get_history()
        )

        # Running the thread
        run = self.client.beta.threads.runs.create(
            assistant_id=self.assistant_id,
            thread_id=threadToRun.id
        )

        # Waiting for the thread to finish.
        while True:
            response = self.client.beta.threads.runs.retrieve(
                run_id=run.id,
                thread_id=threadToRun.id
            )

            if response.status == 'completed':
                break

        # Extracting the message from the result
        last_message = self.client.beta.threads.messages.list(
            thread_id=threadToRun.id,
            order='desc',
            limit=1
        ).data[0].content[0].text.value

        # Saving the message in local history
        self.content_history.append(("assistant", self.__to_content(last_message, None)))

        # Add step to list 
        self.steps.append(last_message)

        return last_message

    def curr_step(self):
        return self.steps[self.current_step]

    def next_step(self):
        self.current_step += 1
        return self.request("NEXT")

    def prev_step_exists(self):
        return self.current_step > 0

    def prev_step(self):
        self.current_step -= 1
        return self.steps[self.current_step]

    # Private helpers.
    def __erase_files(self):
        for file in self.file_ids:
            self.client.files.delete(file)

    def __erase_history(self):
        pass

    def __to_content(self, message, file_id):
        content = []
        if message is not None:
            content.append({"type": "text", "text": message})

        if file_id is not None:
            content.append({"type": "image_file", "image_file": {"file_id": file_id}})

        return content

    def __get_history(self):
        return [{"role": person, "content": content} for (person, content) in self.content_history]
