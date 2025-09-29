# Configuración de MongoDB para Carrefour Subcategories Scraper

## 🚀 Configuración para Prueba Real

Para ejecutar el scraper con una base de datos real (sin modo TEST), sigue estos pasos:

### 1. Obtener las Credenciales de MongoDB Atlas

1. Ve a [MongoDB Atlas](https://cloud.mongodb.com/)
2. Selecciona tu proyecto y cluster
3. Ve a **Database Access** y crea un usuario de base de datos (o usa uno existente)
4. Ve a **Network Access** y permite el acceso desde tu IP
5. Ve a **Clusters** → **Connect** → **Connect your application**
6. Copia la **connection string** completa

### 2. Configurar Variables de Entorno

Edita el archivo `.env` en esta carpeta y reemplaza los valores:

```env
# Reemplaza con tu connection string real de MongoDB Atlas
MONGO_CARREFOUR_URI=mongodb+srv://tu_usuario:tu_password@tu_cluster.mongodb.net/carrefour?retryWrites=true&w=majority
```

**Nota:** Reemplaza `tu_usuario`, `tu_password` y `tu_cluster` con tus credenciales reales. Nunca commits credenciales reales al repositorio. Usa variables de entorno y asegúrate de que `.env` esté en `.gitignore`.

**Ejemplo de placeholder:**
```env
MONGO_CARREFOUR_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/carrefour?retryWrites=true&w=majority
```

### 3. Verificar la Configuración

Ejecuta el script:
```bash
python 3-carrefour-subcategories.py
```

Si las credenciales son correctas, deberías ver:
- ✅ "Connected to MongoDB Atlas - carrefour database"
- ✅ "Retrieved X active categories from database"
- ✅ Los datos se guardarán realmente en la base de datos

### 4. Datos que se Guardarán

El script guardará:
- **Subcategorías** en la colección `subcategories`
- **Metadatos de categorías** actualizados
- **Registros de procesamiento** en los logs

### ⚠️ Importante

- **Backup primero**: Haz un backup de tu base de datos antes de ejecutar
- **IP Whitelist**: Asegúrate de que tu IP esté permitida en MongoDB Atlas
- **Credenciales**: Nunca commits el archivo `.env` al repositorio (ya está en .gitignore)

### 🔧 Solución de Problemas

Si ves errores:
- **"Authentication failed"**: Verifica usuario/contraseña
- **"Connection timed out"**: Verifica IP whitelist y firewall
- **"DNS query name does not exist"**: Connection string incorrecta

¡Listo para la prueba real! 🎯</content>
<parameter name="filePath">d:\dev\caminando-onlinev11\Sandbox\Experiments\README-MongoDB-Setup.md