import supabase

from src.URLUtils import getDomainName
from src.Assistant import Assistant, Model

import re


def extract_number(string):
    # Regular expression to match any sequence of digits
    match = re.search(r'\d+', string)
    if match:
        # Extract the matched digits and convert them to an integer
        return int(match.group())
    else:
        return None  # Return None if no number is found


class FAQDatabase:
    DATABASE_URL = "https://ptwlhvyvvukfvucjqfok.supabase.co"
    DATABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZi" + \
                   "I6InB0d2xodnl2dnVrZnZ1Y2pxZm9rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTc0M" + \
                   "jQxNTUsImV4cCI6MjAzMzAwMDE1NX0.PqzDZk2H_YlNrkQ5c2FkDjIq7bEBtN2JIE0gfASzKUE"
    current_domain_name = ""

    def __init__(self, AI):
        self.supabase = supabase.create_client(self.DATABASE_URL, self.DATABASE_KEY)
        self.AI = AI

    def getFAQ(self, domainName):
        self.current_domain_name = domainName
        self.addWebsiteToDomainTable(domainName)
        response = self.supabase.rpc('get_questions_by_domain', {'domainname': self.current_domain_name}).execute()
        return response.data

    def addFAQ(self, question, url):
        self.addWebsiteToDomainTable(url)
        question = self.findIfSimilarQuestionExists(question, url)
        self.supabase.rpc('addfaq', {'domainname': self.current_domain_name, 'ques': question}).execute()

    def findIfSimilarQuestionExists(self, question, url):
        currentFAQs = self.getFAQ(url)
        ids = [q["qid"] for q in currentFAQs]
        databaseStr = "\n".join([f"{q['qid']}) {q['question']}" for q in currentFAQs])

        if self.AI.modelType == Model.dummy:
            return question
        else:
            response = self.AI.singleRequest(f"""
            Your goal it to take the following input question and check it among the database of questions.
            If there is one the same question (in terms of meaning, not exact words).
            If there is a similar match, say NUMBER: "x". Otherwise say "NEW QUESTION". Do not say anything else
            Input: "{question}"
            Database:\n{databaseStr}""")
            number = extract_number(response)
            if number and number in ids:
                # Update Existing record
                return [q["question"] for q in currentFAQs if q["qid"] == number][0]
            else:
                # New Question
                return question

    def determineNewWebsiteType(self, url):
        response = self.supabase.table("websitetype").select("type").execute()
        existingTypes = [r["type"] for r in response.data]
        if self.AI.modelType == Model.dummy:
            return "NULL"
        else:
            return self.AI.singleRequest(
                f"Looking at the current website: {url}. \
                What category would you say this website is, given the following categories:\
                {list(existingTypes)}. If you do not think that any of them are suitable, you can give your own. \
                Give your answer in the following format only as a single word: \"Category\"").strip('"')

    def addWebsiteToDomainTable(self, domain):
        result = self.supabase.table("domains").select("dID").eq("domain", domain).execute().data
        if not result:
            # Website does not exist
            # print("Website does not exist, adding to domain table")
            # Need to determine its category
            category = self.determineNewWebsiteType(domain)
            # print(f"Category: {category} decided.")

            # Get tId of type
            result = self.supabase.table("websitetype").select("tId").eq("type", category).execute().data
            if result:
                # Type exists
                # print("Category already exists")
                tId = result[0]["tId"]
            else:
                # New type
                # print("Category does not exist, adding it to domain table")
                self.supabase.table("websitetype").insert({"type": category}).execute()
                tId = self.supabase.table("websitetype").select("tId").eq("type", category).execute().data[0]["tId"]

            self.supabase.table("domains").insert({"domain": domain, "tId": tId}).execute()
        # else:
        #     print("Website exists, nothing to do.")
