from pymongo import MongoClient

def setup_mongodb():
    print("Setting up MongoDB database...")
    try:
        # Connect to MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client["stock_analysis"]

        # Create collections for sentimental analysis
        if "sentimental_analysis" not in db.list_collection_names():
            db.create_collection("sentimental_analysis")
            print("Collection 'sentimental_analysis' created.")
        else:
            print("Collection 'sentimental_analysis' already exists.")

    except Exception as e:
        print(f"Error setting up MongoDB: {e}")

if __name__ == "__main__":
    setup_mongodb()