import supabase


class FAQDatabase:
    DATABASE_URL = "https://ptwlhvyvvukfvucjqfok.supabase.co"
    DATABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZi" + \
                   "I6InB0d2xodnl2dnVrZnZ1Y2pxZm9rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTc0M" + \
                   "jQxNTUsImV4cCI6MjAzMzAwMDE1NX0.PqzDZk2H_YlNrkQ5c2FkDjIq7bEBtN2JIE0gfASzKUE"
    current_domain_name = ""

    def __init__(self):
        self.supabase = supabase.create_client(self.DATABASE_URL, self.DATABASE_KEY)

    def getFAQ(self, domainName):
        self.current_domain_name = domainName

        dIDresponse = self.supabase.table("domains").select("dID").eq("domain", self.current_domain_name).execute()
        if dIDresponse.data:
            dID = dIDresponse.data[0]["dID"]
            qresponse = self.supabase.table("questions").select("question").eq("dID", dID).order("uses", desc=True).execute()
            return [r["question"] for r in qresponse.data]
        else:
            self.supabase.table("domains").insert({"domain": self.current_domain_name}).execute()
            return []
        
    def addFAQ(self, question):
        dID = self.supabase.table("domains").select("dID").eq("domain", self.current_domain_name).execute().data[0]["dID"]
        
        qIDresponse = self.supabase.table("questions").select("qID", "uses").eq("dID", dID).eq("question", question).execute()
        
        if qIDresponse.data:
            qID = qIDresponse.data[0]["qID"]
            uses = qIDresponse.data[0]["uses"]
            self.supabase.table("questions").update({"uses": uses+1}).eq("qID", qID).execute()
        else:
            self.supabase.table("questions").insert({"dID": dID, "question": question, "uses": 1}).execute()
        
 
