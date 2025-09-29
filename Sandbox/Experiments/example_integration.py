"""
Ejemplo de cómo integrar el analizador inteligente en otros scrapers.
Este script demuestra cómo usar el nuevo algoritmo que NO usa keywords hardcodeadas,
sino que analiza patrones en los datos para crear subcategorías lógicas intermedias.

NUEVO ENFOQUE INTELIGENTE:
- Análisis contextual del nombre de categoría
- Aprendizaje automático de patrones en productos
- Subcategorías como agrupaciones INTERMEDIAS lógicas
- Sin hardcodeo de keywords - algoritmo adaptable
"""

from analyze_product_types_for_subcategories_refactored import (
    extract_product_types_from_category,
    generate_subcategories_dynamically
)

def example_integration_for_scraper():
    """
    Ejemplo de cómo un scraper podría usar el analizador inteligente.
    Muestra las mejoras con el nuevo enfoque sin keywords hardcodeadas.
    """

    # URL de una categoría que no tiene subcategorías predefinidas
    category_url = "https://www.carrefour.com.ar/Carnes-y-Pescados"

    print("🔍 Scraper detecta que no hay subcategorías predefinidas")
    print("🤖 Usando analizador INTELIGENTE sin keywords hardcodeadas...")
    print("   📊 Análisis contextual + aprendizaje de patrones")
    print("   🎯 Subcategorías lógicas intermedias (Vacuno, Porcino, Aves, etc.)")

    # Paso 1: Extraer tipos de producto
    product_types = extract_product_types_from_category(category_url)

    if not product_types:
        print("❌ No se pudieron extraer tipos de producto")
        return

    print(f"✅ Extraídos {len(product_types)} tipos de producto")

    # Paso 2: Generar subcategorías con algoritmo inteligente
    subcategories = generate_subcategories_dynamically(product_types, category_url)

    print(f"✅ Generadas {len(subcategories)} subcategorías lógicas")

    # Calcular estadísticas de mejora
    total_clasificados = sum(len(products) for products in subcategories.values())
    otros_count = len(subcategories.get('Otros', []))

    print("\n📈 RESULTADOS CON ENFOQUE INTELIGENTE:")
    print(f"   • Productos totales: {len(product_types)}")
    print(f"   • Subcategorías lógicas creadas: {len(subcategories)}")
    print(f"   • Productos clasificados: {total_clasificados}")
    print(f"   • Productos en 'Otros': {otros_count} ({otros_count/len(product_types)*100:.1f}%)")
    print("   • Subcategorías son AGRUPACIONES INTERMEDIAS (no específicas)")

    # Paso 3: El scraper puede usar estas subcategorías para organizar el scraping
    for subcategory_name, products in subcategories.items():
        if subcategory_name != 'Otros':  # Mostrar subcategorías específicas primero
            print(f"\n📁 Sub-categoría: {subcategory_name}")
            print(f"   Productos: {len(products)} - {products[:3]}{'...' if len(products) > 3 else ''}")

    if 'Otros' in subcategories:
        print(f"\n📁 Sub-categoría: Otros")
        print(f"   Productos: {otros_count} - Requiere revisión manual")

    print("\n🎯 Scraping completado usando subcategorías generadas inteligentemente!")

def example_database_integration():
    """
    Ejemplo de cómo guardar las subcategorías generadas en la base de datos.
    """

    # Simular conexión a MongoDB (usando la base raw de carrefour)
    # from pymongo import MongoClient
    # client = MongoClient("mongodb://localhost:27017/")
    # db = client.carrefour

    category_url = "https://www.carrefour.com.ar/Frutas-y-Verduras"

    # Generar subcategorías
    product_types = extract_product_types_from_category(category_url)
    subcategories = generate_subcategories_dynamically(product_types, category_url)

    # Guardar en base de datos
    for subcategory_name, products in subcategories.items():
        subcategory_doc = {
            "name": subcategory_name,
            "category": "Frutas y Verduras",
            "products": products,
            "generated_intelligently": True,
            "source_url": category_url,
            "algorithm_version": "intelligent_context_aware"
        }

        # db.subcategories.insert_one(subcategory_doc)
        print(f"💾 Guardado: {subcategory_name} ({len(products)} productos)")

if __name__ == "__main__":
    print("🚀 DEMOSTRACIÓN: Integración del Analizador Inteligente")
    print("=" * 70)

    # Demostrar integración básica
    example_integration_for_scraper()

    print("\n" + "=" * 70)
    print("💾 DEMOSTRACIÓN: Integración con Base de Datos")

    # Demostrar guardado en DB
    example_database_integration()

    print("\n✅ El analizador inteligente puede integrarse fácilmente en cualquier scraper!")
    print("💡 Ventajas del nuevo enfoque:")
    print("   • NO usa keywords hardcodeadas")
    print("   • Se adapta automáticamente a cualquier categoría")
    print("   • Crea subcategorías INTERMEDIAS lógicas")
    print("   • Algoritmo escalable y mantenible")
    print("   • Fácil integración con MongoDB")