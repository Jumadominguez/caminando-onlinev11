from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import sys

def initialize_database():
    try:
        # Conectar a MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client.caminando_online

        print("Conectado a MongoDB. Inicializando estructura de base de datos...")

        # Crear colecciones si no existen
        collections = ['categories', 'subcategories', 'products', 'supermarkets', 'users']

        for collection_name in collections:
            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
                print(f"Colección '{collection_name}' creada.")
            else:
                print(f"Colección '{collection_name}' ya existe.")

        # Insertar datos iniciales para categorías
        categories_data = [
            {"_id": "frutas-verduras", "name": "Frutas y Verduras", "icon": "🥕"},
            {"_id": "carnes", "name": "Carnes", "icon": "🥩"},
            {"_id": "lacteos", "name": "Lácteos", "icon": "🥛"},
            {"_id": "panaderia", "name": "Panadería", "icon": "🍞"},
            {"_id": "bebidas", "name": "Bebidas", "icon": "🥤"},
            {"_id": "despensa", "name": "Despensa", "icon": "🥫"}
        ]

        if db.categories.count_documents({}) == 0:
            db.categories.insert_many(categories_data)
            print("Datos iniciales de categorías insertados.")
        else:
            print("Categorías ya tienen datos.")

        # Insertar supermercados iniciales
        supermarkets_data = [
            {"_id": "carrefour", "name": "Carrefour", "logo": "🏪", "active": True},
            {"_id": "jumbo", "name": "Jumbo", "logo": "🛒", "active": True},
            {"_id": "dia", "name": "Dia", "logo": "🏬", "active": True},
            {"_id": "vea", "name": "Vea", "logo": "🛍️", "active": True},
            {"_id": "disco", "name": "Disco", "logo": "🏪", "active": True}
        ]

        if db.supermarkets.count_documents({}) == 0:
            db.supermarkets.insert_many(supermarkets_data)
            print("Datos iniciales de supermercados insertados.")
        else:
            print("Supermercados ya tienen datos.")

        # Crear índices para optimización
        db.products.create_index([("name", 1)])
        db.products.create_index([("category", 1)])
        db.products.create_index([("supermarket", 1)])
        db.products.create_index([("price", 1)])
        print("Índices creados para la colección 'products'.")

        print("Estructura de base de datos inicializada exitosamente.")

        client.close()

    except ConnectionFailure:
        print("Error: No se puede conectar a MongoDB. Asegúrate de que el servidor esté ejecutándose.")
        sys.exit(1)
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
        sys.exit(1)

if __name__ == "__main__":
    initialize_database()