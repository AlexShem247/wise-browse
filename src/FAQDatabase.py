import supabase


class FAQDatabase:
    DATABASE_URL = "https://sjkzlnubjyugjbcrhvdc.supabase.co"
    DATABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNqa3psbnVianl1Z2piY3Jodm" + \
                   "RjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTcxNTEwNDUsImV4cCI6MjAzMjcyNzA0NX0.wQgF7ybxI2RlwJ-d3Jaf8QEqg" + \
                   "hYMdNrUVfggSb17CXI"

    def __init__(self):
        self.supabase = supabase.create_client(self.DATABASE_URL, self.DATABASE_KEY)

    def getFAQ(self, domainName):
        response = self.supabase.table("domains").select("dID").eq("domain", domainName).execute()

        if response.data:
            dID = response.data[0]["dID"]
            response = self.supabase.table("questions").select("question").eq("dID", dID).execute()
            return [r["question"] for r in response.data]
        else:
            return []

