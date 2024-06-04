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
        response = self.supabase.rpc('getfaqs', {'domainname': self.current_domain_name}).execute()
        return response.data
        
    def addFAQ(self, question):
        self.supabase.rpc('addfaq', {'domainname': self.current_domain_name, 'ques': question}).execute()