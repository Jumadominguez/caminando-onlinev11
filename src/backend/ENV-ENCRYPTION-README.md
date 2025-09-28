# Encriptación de Variables de Entorno

Este proyecto usa encriptación para proteger las variables sensibles en `.env`.

## Cómo Funciona

- Las variables se almacenan en `.env.encrypted` (encriptado)
- Al iniciar el servidor, se desencripta automáticamente a `.env`
- La clave de encriptación está en variable de entorno del sistema `ENV_ENCRYPTION_KEY`

## Comandos

### Encriptar .env
```bash
node encrypt-env.js encrypt
```

### Desencriptar .env
```bash
node encrypt-env.js decrypt
```

## Configuración Inicial

1. **Setear clave de encriptación** (una sola vez):
   ```powershell
   [Environment]::SetEnvironmentVariable("ENV_ENCRYPTION_KEY", "tu-clave-hex-64-chars", "Machine")
   ```

2. **Encriptar el .env**:
   ```bash
   node encrypt-env.js encrypt
   ```

3. **Borrar .env** (opcional, se desencripta automáticamente):
   ```bash
   rm .env
   ```

4. **Iniciar servidor** (desencripta automáticamente):
   ```bash
   npm start
   ```

## Seguridad

- `.env` no debe commitearse (ya está en .gitignore)
- `.env.encrypted` puede commitearse (está encriptado)
- La clave `ENV_ENCRYPTION_KEY` debe mantenerse secreta y no commitearse