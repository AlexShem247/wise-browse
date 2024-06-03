import supabase


class FAQDatabase:
    DATABASE_URL = "https://ptwlhvyvvukfvucjqfok.supabase.co"
    DATABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZi" + \
                   "I6InB0d2xodnl2dnVrZnZ1Y2pxZm9rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTc0M" + \
                   "jQxNTUsImV4cCI6MjAzMzAwMDE1NX0.PqzDZk2H_YlNrkQ5c2FkDjIq7bEBtN2JIE0gfASzKUE"

    def __init__(self):
        self.supabase = supabase.create_client(self.DATABASE_URL, self.DATABASE_KEY)

    def getFAQ(self, domainName):
        response = self.supabase.table("Domains").select("dID").eq("domain", domainName).execute()

        if response.data:
            return []
            # dID = response.data[0]["dID"]
            # response = self.supabase.table("Questions").select("question").eq("dID", dID).order("references").execute()
            # return [r["question"] for r in response.data]
        else:
            self.supabase.table("Domains").insert({"domain": domainName}).execute()
            return []
 
