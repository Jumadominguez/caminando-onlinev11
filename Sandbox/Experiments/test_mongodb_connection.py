#!/usr/bin/env python3
"""
MongoDB Connection Test Script
Quick test to verify MongoDB Atlas connection before running the full scraper
"""

import os
import sys
from pymongo.errors import ConnectionFailure
import pymongo

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed. Using system environment variables only.")

def test_mongodb_connection():
    """Test MongoDB Atlas connection"""
    try:
        # Get MongoDB URI from environment
        mongo_uri = os.getenv('MONGO_CARREFOUR_URI')

        if not mongo_uri:
            print("❌ MONGO_CARREFOUR_URI environment variable not set")
            print("📝 Please configure your .env file with the MongoDB connection string")
            return False

        print("🔄 Connecting to MongoDB Atlas...")
        client = pymongo.MongoClient(mongo_uri)

        # Test the connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")

        # Test database access
        db = client.carrefour
        collections = db.list_collection_names()
        print(f"✅ Database 'carrefour' accessible. Collections: {collections}")

        # Test categories collection
        categories_count = db.categories.count_documents({})
        print(f"✅ Categories collection has {categories_count} documents")

        client.close()
        return True

    except ConnectionFailure as e:
        print(f"❌ Connection failed: {e}")
        print("💡 Check your internet connection and MongoDB Atlas settings")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 MongoDB Connection Test")
    print("=" * 40)

    success = test_mongodb_connection()

    if success:
        print("\n🎉 Connection test PASSED! Ready to run the scraper.")
        print("🚀 You can now execute: python 3-carrefour-subcategories.py")
    else:
        print("\n❌ Connection test FAILED!")
        print("📖 Check the README-MongoDB-Setup.md for configuration instructions")

    sys.exit(0 if success else 1)