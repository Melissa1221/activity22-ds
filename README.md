# Fase 1

# Fase 2
#### Analizando main.py


Al inicio del archivo se importan las librerías necesarias: `ipaddress` para manejar direcciones IP, y `json` para trabajar con archivos JSON.

La función `get_network_metadata()` lee un archivo JSON que contiene información sobre la red (como el nombre y el rango de IPs) y devuelve esos dos valores. 

- Clase ServerConfiguration

Esta clase guarda toda la información de configuración de un servidor. Cuando se crea una instancia de esta clase, se puede especificar:
- El nombre del servidor
- Las etiquetas (tags) que describen para qué sirve
- El tipo de instancia (pequeña, mediana, grande)
- El ambiente donde va (desarrollo, producción)
- Quién es el dueño del servidor
- Una descripción de qué hace

Si no se especifica algunos valores, la clase usa valores por defecto.

- Clase ServerFactoryModule

Funciona como una "fábrica" que construye la configuración de Terraform para crear un servidor.

Cuando se inicializa esta clase, se le pasas una configuración de servidor (del tipo `ServerConfiguration`) y ella hace lo siguiente:
1. Toma la información de la red leyendo el archivo de metadatos
2. Calcula automáticamente qué IP usar para el servidor (específicamente la quinta IP disponible en el rango)

El método `_build()` toma toda la información (tanto del servidor como de la red) y la convierte en un formato que Terraform puede entender. Genera un archivo de configuración que dice "crea un servidor con estas características y ejecuta este comando para mostrar la información".

- Función main

Se crea una configuración específica para un servidor de producción. Aquí se define todas las características que requiere: se llama "web-server-prod", es de tipo "small", va en el ambiente de "production", pertenece al equipo "backend", y tiene varias etiquetas que lo describen.

Luego se crea la fábrica de servidores pasándole esa configuración. La fábrica la configuración, la combina con la información de la red, y genera automáticamente toda la configuración de Terraform necesaria.

Finalmente, toda esa configuración se guarda en un archivo llamado `server.tf.json` que Terraform puede leer y usar para crear realmente el servidor en la infraestructura.



Se refactorizó el archivo `main.py` para implementar el principio de **Inversión de Control (IoC)** e **Inyección de Dependencias**, agregando parámetros configurables del servidor como nombre, etiquetas, tipo de instancia, entorno y propietario.

## Principio de Inversión de Control Aplicado

En la versión original, la clase `ServerFactoryModule` tenía control directo sobre la configuración del servidor
- El nombre del servidor estaba hardcodeado como "hello-world"
- No había flexibilidad para configurar parámetros adicionales
- La clase controlaba completamente su inicialización

Después de la Modificación

**Inversión de Control**
Se invierte el control de la configuración del servidor:
- Se crea una clase `ServerConfiguration` que encapsula todos los parámetros configurables
- La clase `ServerFactoryModule` ya NO controla su configuración, sino que la recibe desde afuera
- El control de qué configuración usar ahora reside en el código cliente (función `main`)

**Inyección de Dependencias**

`ServerFactoryModule` recibe un objeto `ServerConfiguration` en su constructor
La configuración está abstraída en una clase separada
El factory no depende de implementaciones concretas de configuración
Implementé inyección de dependencias mediante:

En los beneficios de estas modificaciones
se pueden crear servidores son diferentes configuraciones sin modificar la clase factory, los cambios en la lógica de configuración no afectan al factory, y viceversa. La misma clase factory puede usarse para múltiples tipos de servidores.

Antes de la modificación:
```python
class ServerFactoryModule:
    def __init__(self, name, metadata_path="network/network_metadata.json"):
        self._name = name  # Control directo del nombre
```

La clase `ServerFactoryModule` tenía **control total** sobre la configuración del servidor. Solo podía crear servidores con el nombre que le pasaran y nada más.

### Después de la modificación:
```python
class ServerConfiguration:
    def __init__(self, name, tags, instance_type, environment, owner, description):
        # Encapsula toda la configuración

class ServerFactoryModule:
    def __init__(self, server_config, metadata_path="network/network_metadata.json"):
        self._config = server_config  # Recibe configuración desde afuera
```
Ahora la clase **no controla** qué configuración usar, sino que la **recibe como dependencia**.

# Fase 3