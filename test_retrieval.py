import os
from dotenv import load_dotenv
load_dotenv()

# Set up paths to import the local package
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from assistant_agent.agent import query_knowledge_base

def test_retrieval():
    print("Starting Grounded Retrieval Test...")
    
    # Question based on Google Skill Labs and Codelabs Difference.docx
    query = "What is the difference between Google Skill Labs and Codelabs?"
    
    print(f"Query: {query}")
    result = query_knowledge_base(query)
    
    print("\nResult:")
    print("-" * 50)
    print(result)
    print("-" * 50)
    
    if "Source: Verified Project Documentation" in result:
        print("\nSuccess: Retrieval came from Pinecone.")
    elif "Falling back to Internal Logic" in result:
        print("\nFailure: Retrieval fell back to static knowledge.")
    else:
        print("\nError: Unexpected result format.")

if __name__ == "__main__":
    test_retrieval()
