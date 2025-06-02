# Troubleshooting Guide for TaskHub

Este documento proporciona soluciones a los problemas comunes encontrados en el proyecto TaskHub.

## Problemas Identificados y Soluciones

### 1. Errores de Sintaxis en Archivos Python

**Problema**: Errores de sintaxis en múltiples servicios, especialmente relacionados con anotaciones de tipo en funciones async.

**Solución**:
```bash
python fix_syntax_errors.py
```

### 2. Fallo al Cargar Módulos (ImportError)

**Problema**: Módulos faltantes o rutas de importación incorrectas.

**Solución**:
```bash
python fix_imports.py
```

### 3. Errores en Uvicorn

**Problema**: Uvicorn no puede cargar la aplicación debido a errores de sintaxis o importación.

**Solución**:
1. Ejecutar los scripts de reparación
2. Verificar que PYTHONPATH esté configurado correctamente
3. Usar `python -m uvicorn` en lugar de `uvicorn` directamente

### 4. Problemas con datetime.utcnow()

**Problema**: `datetime.utcnow()` está deprecado en Python 3.12+

**Solución**:
```bash
python fix_datetime_utcnow.py
```

### 5. Problemas de Atributos

**Problema**: Errores de acceso a atributos que pueden no existir.

**Solución**:
```bash
python fix_attribute_access.py
```

## Proceso de Reparación Completo

Para reparar todos los problemas de una vez, ejecuta:

```bash
python repair_project.py
```

Este script:
1. Ejecuta todos los scripts de corrección
2. Crea el archivo .env si no existe
3. Ejecuta diagnósticos
4. Construye las imágenes Docker

## Verificación Manual

### 1. Verificar la estructura de archivos
```bash
python diagnose.py
```

### 2. Verificar sintaxis de un archivo específico
```python
python -m py_compile api/auth_service/app/main.py
```

### 3. Probar importaciones
```python
python -c "import api.auth_service.app.main"
```

## Ejecución del Proyecto

### Opción 1: Docker Compose (Recomendado)
```bash
# Construir imágenes
docker-compose build

# Ejecutar todos los servicios
docker-compose up

# Ejecutar un servicio específico
docker-compose up auth_service
```

### Opción 2: Ejecución Local (Para Depuración)
```bash
# Configurar PYTHONPATH
export PYTHONPATH=/path/to/Backend-Default

# Ejecutar un servicio
python -m uvicorn api.auth_service.app.main:app --reload
```

## Logs y Depuración

### Ver logs de un servicio específico
```bash
docker-compose logs -f auth_service
```

### Ejecutar un servicio con más información de depuración
```bash
docker-compose run --rm auth_service python -m uvicorn api.auth_service.app.main:app --log-level debug
```

## Problemas Comunes y Soluciones Rápidas

### Error: "Module not found"
- Verificar que todos los directorios tengan `__init__.py`
- Verificar PYTHONPATH
- Reconstruir las imágenes Docker

### Error: "SyntaxError"
- Ejecutar `python fix_syntax_errors.py`
- Verificar la versión de Python (debe ser 3.12+)

### Error: "Connection refused"
- Verificar que RabbitMQ esté ejecutándose
- Verificar las URLs de los servicios en docker-compose.yml
- Verificar que los puertos no estén en uso

### Error: "Invalid token"
- Verificar que JWT_SECRET_KEY esté configurado en .env
- Verificar que todos los servicios usen la misma clave

## Reinicio Limpio

Si los problemas persisten, intenta un reinicio limpio:

```bash
# Detener y eliminar contenedores
docker-compose down -v

# Limpiar el sistema Docker
docker system prune -a

# Reconstruir desde cero
docker-compose build --no-cache
docker-compose up
```

## Contacto y Soporte

Si encuentras problemas adicionales:
1. Revisa los logs completos del servicio afectado
2. Verifica que todas las dependencias estén instaladas
3. Asegúrate de que las variables de entorno estén configuradas correctamente