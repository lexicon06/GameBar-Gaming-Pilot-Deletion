# Eliminar "Gaming Pilot" (Espía de Windows)

Este repositorio contiene instrucciones para eliminar el componente de IA "Gaming Pilot" de Windows, que funciona en segundo plano.

## ⚠️ Advertencia

Estos comandos modifican componentes del sistema operativo Windows. Úsalos bajo tu propia responsabilidad. Se recomienda crear un punto de restauración antes de proceder.

## 📋 Requisitos

- Windows 10/11
- Permisos de administrador
- PowerShell o Terminal de Windows

## 🚀 Instrucciones

### Paso 1: Abrir PowerShell como Administrador

1. Haz clic derecho en el botón de **Inicio de Windows**
2. Selecciona **PowerShell (Administrador)** o **Terminal (Admin)**
3. Acepta el control de cuentas de usuario (UAC) si aparece

### Paso 2: Ejecutar los comandos

#### Eliminar el proceso de IA de fondo (Gaming Pilot)

Copia y pega el siguiente comando en PowerShell y pulsa **Enter**:

```powershell
Get-AppxPackage -AllUsers Microsoft.Windows.Ai.Copilot.Provider | Remove-AppxPackage
```

#### (Opcional) Eliminar la Game Bar completa

Si no utilizas la barra de juegos de Xbox y deseas eliminarla por completo, ejecuta:

```powershell
Get-AppxPackage -AllUsers Microsoft.XboxGamingOverlay | Remove-AppxPackage
```

## ✅ Verificación

Después de ejecutar los comandos:

- Reinicia tu computadora
- El proceso de Gaming Pilot ya no debería estar ejecutándose
- Puedes verificar en el Administrador de tareas que el proceso ha sido eliminado

## 🔄 Restauración

Si deseas restaurar estos componentes:

1. Abre la **Microsoft Store**
2. Busca "Xbox Game Bar"
3. Reinstala la aplicación

O ejecuta Windows Update para restaurar los componentes del sistema.

## 📝 Notas

- Estos comandos eliminan paquetes de aplicaciones de Windows
- La eliminación de Gaming Pilot puede mejorar el rendimiento del sistema
- La Game Bar es opcional y solo necesaria si usas funciones de grabación de pantalla o streaming

## 🤝 Contribuciones

Si encuentras mejoras o alternativas, siéntete libre de crear un issue o pull request.

## 📄 Licencia

Este contenido se proporciona "tal cual" sin garantías de ningún tipo.

---

**Nota:** Esta guía es solo para fines informativos. El autor no se responsabiliza por daños al sistema operativo.
