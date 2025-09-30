import pymongo
import os
from dotenv import load_dotenv

# Load environment variables
env_path = r"d:\dev\caminando-onlinev11\src\backend\.env"
load_dotenv(dotenv_path=env_path)

# Connect to MongoDB
mongo_uri = os.getenv('MONGO_DIA_URI')
print(f"Loading .env from: {env_path}")
print(f"MONGO_DIA_URI: {mongo_uri}")
if not mongo_uri:
    print("ERROR: MONGO_DIA_URI not found!")
    exit(1)
client = pymongo.MongoClient(mongo_uri)
db = client.dia

print("=== ELIMINANDO SUBCATEGORÍAS CON featured: false ===")

# Check subcategories with featured: false
featured_false = list(db.subcategories.find({'featured': False}, {'name': 1, 'category': 1, '_id': 0}))
print(f'Subcategorías con featured: false encontradas: {len(featured_false)}')

if featured_false:
    print('Mostrando subcategorías a eliminar:')
    for i, subcat in enumerate(featured_false[:5], 1):  # Show first 5
        print(f'  {i}. {subcat["name"]} (categoría: {subcat.get("category", "N/A")})')
    if len(featured_false) > 5:
        print(f'  ... y {len(featured_false) - 5} más')

    print('\nEliminando subcategorías con featured: false...')
    result = db.subcategories.delete_many({'featured': False})
    print(f'✅ Eliminadas: {result.deleted_count} subcategorías')
else:
    print('No se encontraron subcategorías con featured: false')

# Verify remaining subcategories
remaining = db.subcategories.count_documents({})
total_almacen = db.subcategories.count_documents({'category': 'almacen'})
print(f'\n📊 Estadísticas finales:')
print(f'   Total de subcategorías restantes: {remaining}')
print(f'   Subcategorías de almacen: {total_almacen}')

print("\n✅ Proceso completado")