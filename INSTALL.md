# Guía de Instalación - Tabula Cloud Sync

> **Para usuarios finales que solo quieren instalar y usar el software**

Esta guía está diseñada para usuarios que simplemente quieren instalar Tabula Cloud Sync en su sistema y comenzar a usarlo inmediatamente, sin necesidad de conocimientos técnicos avanzados.

## 🚀 Instalación Rápida (Recomendada)

### Paso 1: Descargar

Ve a la página de [**Releases**](https://github.com/ysidromdenis/template-sync-tabula-cloud/releases/latest) y descarga el archivo para tu sistema operativo:

| Sistema Operativo | Archivo a Descargar                        |
| ----------------- | ------------------------------------------ |
| 🪟 **Windows**    | `tabula-cloud-sync-windows-standalone.zip` |
| 🐧 **Linux**      | `tabula-cloud-sync-linux-standalone.zip`   |
| 🍎 **macOS**      | `tabula-cloud-sync-macos-standalone.zip`   |

### Paso 2: Extraer

#### Windows:

1. Haz clic derecho en el archivo ZIP descargado
2. Selecciona "Extraer todo..."
3. Elige una carpeta (ej: `C:\tabula-cloud-sync\`)

#### Linux/macOS:

```bash
# Navegar a la carpeta de descargas
cd ~/Downloads

# Extraer el archivo
unzip tabula-cloud-sync-linux-standalone.zip
cd tabula-cloud-sync/
```

### Paso 3: Configurar

1. **Copiar plantilla de configuración:**

   ```bash
   # Linux/macOS
   cp config.ini.template config.ini

   # Windows (en el Explorador)
   # Copiar "config.ini.template" y renombrar la copia a "config.ini"
   ```

2. **Editar configuración:**

   Abre el archivo `config.ini` con tu editor de texto favorito y completa los datos:

   ```ini
   [mysql]
   host = tu_servidor_mysql
   user = tu_usuario
   password = tu_contraseña
   database = tu_base_de_datos
   port = 3306

   [sincronizador]
   token = tu_token_de_tabula_cloud
   interval = 30
   url = tu_dominio.tabula.com.py

   [servicio]
   log_level = INFO
   log_file = tabula_service.log
   max_retries = 3
   timeout = 30
   ```

   > **💡 Importante:** Pide estos datos a tu administrador de sistemas o revisa la documentación de tu empresa.

### Paso 4: Instalar como Servicio

#### Windows (ejecutar como Administrador):

```cmd
# Abrir CMD como Administrador
cd C:\tabula-cloud-sync\
tabula-cloud-sync.exe install --config config.ini
```

#### Linux:

```bash
# Instalar como servicio del sistema
sudo ./tabula-cloud-sync install --config config.ini
```

#### macOS:

```bash
# Instalar como servicio del sistema
sudo ./tabula-cloud-sync install --config config.ini
```

## 🎯 Gestión del Servicio

### Comandos Básicos

Una vez instalado, puedes gestionar el servicio con estos comandos:

#### Windows:

```cmd
# Iniciar el servicio
tabula-cloud-sync.exe start

# Detener el servicio
tabula-cloud-sync.exe stop

# Ver estado del servicio
tabula-cloud-sync.exe status

# Reiniciar el servicio
tabula-cloud-sync.exe restart
```

#### Linux/macOS:

```bash
# Iniciar el servicio
sudo tabula-cloud-sync start

# Detener el servicio
sudo tabula-cloud-sync stop

# Ver estado del servicio
sudo tabula-cloud-sync status

# Reiniciar el servicio
sudo tabula-cloud-sync restart
```

## 🔧 Verificar que Funciona

### Método 1: Ejecutar en Primer Plano (Recomendado para Pruebas)

Antes de instalar como servicio, puedes probar que todo funciona correctamente:

#### Windows:

```cmd
tabula-cloud-sync.exe --foreground --config config.ini
```

#### Linux/macOS:

```bash
./tabula-cloud-sync --foreground --config config.ini
```

Si ves mensajes como:

```
[INFO] Servicio iniciado correctamente
[INFO] Conectando a Tabula Cloud...
[INFO] Sincronización completada
```

¡Todo está funcionando bien! Presiona `Ctrl+C` para detener.

### Método 2: Verificar Logs del Servicio

#### Windows:

Los logs se guardan en: `%PROGRAMDATA%\TabulaCloudSync\logs\`

#### Linux:

```bash
# Ver logs en tiempo real
sudo journalctl -u tabula-cloud-sync -f

# Ver logs de archivo
tail -f /var/log/tabula-cloud-sync/service.log
```

#### macOS:

```bash
tail -f /usr/local/var/log/tabula-cloud-sync/service.log
```

## ⚠️ Solución de Problemas Comunes

### Error: "No se puede conectar a la base de datos"

- ✅ Verifica que los datos de `[mysql]` en `config.ini` sean correctos
- ✅ Asegúrate de que el servidor MySQL esté funcionando
- ✅ Verifica que tengas permisos de acceso a la base de datos

### Error: "Token inválido"

- ✅ Verifica que el `token` en `[sincronizador]` sea correcto
- ✅ Contacta a tu administrador para obtener un token válido

### Error: "Permiso denegado" (Linux/macOS)

- ✅ Asegúrate de ejecutar los comandos con `sudo`
- ✅ Verifica que el archivo ejecutable tenga permisos: `chmod +x tabula-cloud-sync`

### El servicio se detiene inmediatamente

- ✅ Revisa los logs para ver el error específico
- ✅ Ejecuta primero en modo `--foreground` para diagnóstico
- ✅ Verifica que el archivo `config.ini` esté en la ubicación correcta

## 🆘 Obtener Ayuda

### Logs Detallados

Si tienes problemas, ejecuta en modo debug:

```bash
# Cambiar nivel de log en config.ini
[servicio]
log_level = DEBUG

# Ejecutar en primer plano para ver todos los mensajes
./tabula-cloud-sync --foreground --config config.ini
```

### Contacto de Soporte

- 📧 **Issues**: [GitHub Issues](https://github.com/ysidromdenis/template-sync-tabula-cloud/issues)
- 📖 **Documentación completa**: [README](README.md)
- 🔧 **Para desarrolladores**: [README_UPDATED.md](README_UPDATED.md)

## 🔄 Desinstalar

Si necesitas desinstalar el servicio:

#### Windows:

```cmd
tabula-cloud-sync.exe remove
```

#### Linux/macOS:

```bash
sudo tabula-cloud-sync remove
```

Luego simplemente elimina la carpeta donde extrajiste los archivos.

---

## ✅ Resumen Rápido

1. **Descargar** → [Releases](https://github.com/ysidromdenis/template-sync-tabula-cloud/releases/latest)
2. **Extraer** → Descomprimir el ZIP
3. **Configurar** → Copiar y editar `config.ini`
4. **Instalar** → `tabula-cloud-sync install --config config.ini`
5. **Iniciar** → `tabula-cloud-sync start`

¡Listo! El servicio se ejecutará automáticamente en segundo plano y se iniciará con el sistema.
