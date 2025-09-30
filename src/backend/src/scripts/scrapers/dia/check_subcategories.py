import pymongo
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='../../.env')

# Connect to MongoDB
mongo_uri = os.getenv('MONGO_DIA_URI')
client = pymongo.MongoClient(mongo_uri)
db = client.dia

# Get all subcategories for 'almacen' category
subcategories = list(db.subcategories.find({'category': 'almacen'}, {'name': 1, 'slug': 1, '_id': 0}).sort('name'))

print('=== LISTADO COMPLETO DE SUBCATEGORÍAS PARA ALMACÉN ===')
print(f'Total de subcategorías: {len(subcategories)}')
print('=' * 60)

for i, subcat in enumerate(subcategories, 1):
    print(f'{i:2d}. {subcat["name"]}')

print('=' * 60)
print(f'Total: {len(subcategories)} subcategorías')