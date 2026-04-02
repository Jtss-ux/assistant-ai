import os
from pinecone import Pinecone
from dotenv import load_dotenv

# Ensure we have all necessary paths and keys
load_dotenv()

API_KEY = os.environ.get("PINECONE_API_KEY", "pcsk_5svSUB_ATeK3UhfCfaqWLQipJksjBTTvYQTH2tAf4tsXCnhzk6YSxrbqfxxhamptPVm8VM")
ASSISTANT_NAME = "jts"
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
FOLDER_PATH = os.path.join(PROJECT_ROOT, "jtspine")

# Initialize Pinecone
pc = Pinecone(api_key=API_KEY)
assistant = pc.assistant.Assistant(assistant_name=ASSISTANT_NAME)

def get_metadata(filename):
    """Generate basic metadata for categorized RAG retrieval."""
    meta = {"project": "Career AI", "source": "Hack2Skill_Project"}
    if "Career_AI" in filename:
        meta["category"] = "core_manifesto"
    elif "FAQ" in filename:
        meta["category"] = "competition_faq"
    elif "Guide" in filename or "Profile" in filename or "Difference" in filename:
        meta["category"] = "skills_lab_guide"
    elif "Pasted" in filename:
        meta["category"] = "source_fragments"
    return meta

def run_upload():
    if not os.path.exists(FOLDER_PATH):
        print(f"Error: Folder {FOLDER_PATH} not found.")
        return

    files = [f for f in os.listdir(FOLDER_PATH) if os.path.isfile(os.path.join(FOLDER_PATH, f))]
    print(f"Starting Pinecone SDK Sync for Assistant: '{ASSISTANT_NAME}'")
    print(f"Found {len(files)} files to upload.\n")

    for idx, filename in enumerate(files, 1):
        file_path = os.path.join(FOLDER_PATH, filename)
        meta = get_metadata(filename)
        
        print(f"[{idx}/{len(files)}] Uploading: {filename}")
        try:
            # We don't set timeout=None as the SDK handles this well, 
            # but we follow the docs if they explicitly asked.
            response = assistant.upload_file(
                file_path=file_path,
                metadata=meta
            )
            print(f"   Success. Status: {response.status}")
        except Exception as e:
            print(f"   Failed to upload {filename}. Error: {e}")

    print("\nSync Complete. Your Career AI is now grounded in its knowledge base.")

if __name__ == "__main__":
    run_upload()
