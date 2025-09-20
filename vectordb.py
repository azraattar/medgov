import chromadb
from chromadb.utils import embedding_functions
import os

# --- Configuration ---
KNOWLEDGE_BASE_FILE = "knowledge_base.txt"
PERSIST_DIRECTORY = "db"  # The folder where the database will be stored
COLLECTION_NAME = "health_insights" # A name for your collection of insights

def main():
    """
    Main function to create and populate the vector database.
    """
    # 1. Check if the knowledge base file exists
    if not os.path.exists(KNOWLEDGE_BASE_FILE):
        print(f"Error: Knowledge base file '{KNOWLEDGE_BASE_FILE}' not found.")
        print("Please run generate_knowledge_base.py first to create it.")
        return

    # 2. Set up the ChromaDB client with persistence
    # This will save the database to the 'db' folder
    client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)

    # 3. Set up the embedding function using a pre-trained model
    # ChromaDB will automatically download and use this model
    # 'all-MiniLM-L6-v2' is a great, lightweight default model [102]
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # 4. Create or get the collection
    # The embedding_function parameter is crucial for automatic processing
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=sentence_transformer_ef
    )

    # 5. Read the insights from your text file
    with open(KNOWLEDGE_BASE_FILE, "r", encoding="utf-8") as f:
        # Read all lines, stripping out any whitespace
        documents = [line.strip() for line in f.readlines() if line.strip()]

    # 6. Generate unique IDs for each document
    # This is important for managing data in the collection
    ids = [f"insight_{i}" for i in range(len(documents))]

    # 7. Add the documents to the collection
    # ChromaDB will automatically handle the process of creating embeddings
    # because we specified the embedding_function when creating the collection.
    # Note: If you run this script again, it will add duplicates unless you
    # clear the collection first. For simplicity, we are assuming a fresh start.
    collection.add(
        documents=documents,
        ids=ids
    )

    print("-" * 50)
    print(f"✅ Success! Vector database has been created/updated.")
    print(f"   - Stored in: '{PERSIST_DIRECTORY}/' directory")
    print(f"   - Collection: '{COLLECTION_NAME}'")
    print(f"   - Total insights indexed: {collection.count()}")
    print("-" * 50)


# --- Run the main function ---
if __name__ == "__main__":
    main()

