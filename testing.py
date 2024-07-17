from utils import load_data
def get_index(name,documents):
    for i in range(len(documents)):
        if documents[i].name == name:
            return i
    
documents = load_data.company_info.documents
documents.pop(get_index('ahmed',documents))
print(documents)
        


