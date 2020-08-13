# Provider class and methods 
# TO BE FINISHED LATER
# By: Annika Wille

class provider:
    def __init__(self):
        self.providerlist = {'awille': 15,
            'mjohnson':1, 
            'ebart':2, 
            'jeaston':3,
            'lwest':4, 
            'cwalker':5, 
            'bschaefer':6, 
            'tgreen':7, 
            'olongmore':8, 
            'estrange':9, 
            'lwallace':10,
            'gdavis':11, 
            'ejames':12,
            'bsmith':13, 
            'sgordon':14}

    def get_count(self):
        return len(self.providerlist)

    def add_provider(self, username):
        c = self.get_count()+1
        self.providerlist.update({username:c})

    def get_provider_id(self, username):
        for provider, value in self.providerlist.items():
            if username == provider:
                return self.providerlist[provider]