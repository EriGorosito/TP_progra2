# TP_progra2

# 🐾 PetCare — Plataforma de gestión de cuidadores de mascotas

**PetCare** es una aplicación desarrollada en **Python** que conecta a dueños de mascotas con cuidadores disponibles.  
Permite registrar usuarios, gestionar mascotas, crear reservas de cuidado y dejar reseñas sobre los cuidadores.  

El proyecto sigue una arquitectura modular y utiliza **pytest** para realizar pruebas automáticas que aseguran el correcto funcionamiento del sistema.

---

## 🚀 Funcionalidades principales

- 👤 **Registro de usuarios** (clientes y cuidadores).  
- 🐶 **Gestión de mascotas** asociadas a cada cliente.  
- 📅 **Creación y seguimiento de reservas** de cuidado.  
- 🌟 **Sistema de reseñas y calificaciones** para los cuidadores.  
- 🧪 **Pruebas unitarias** implementadas con `pytest`.

---
## Requerimientos funcionales

#### 👤 Gestión de usuarios 
- El sistema debe permitir registrar un nuevo usuario como cliente o cuidador
- El sistema debe validar que el email sea único y tenga formato correcto
- El sistema debe enviar un correo de confirmación al completar el registro
- El sistema debe permitir al usuario iniciar sesión con email y contraseña

#### 🐶 Gestión de mascotas(Cliente) 
- El cliente debe poder registrar mascotas, ingresando nombre, especie, raza(si la tiene), edad, peso y características especiales.
- El sistema debe permitir subir una foto de la mascota
- El cliente debe poder editar o eliminar el perfil de una mascota.

#### 👤 Gestión de cuidadores
- El cuidador debe poder crear su perfil, completando descripción, experiencia y servicios ofrecidos
- El sistema debe permitir configurar tarifas por servicio, zona de cobertura y disponibilidad.
- El sistema debe mostrar los perfiles de cuidadores solo si están activos y completos.

#### 🔎 Búsqueda y Filtrado
- El cliente debe poder buscar cuidadores filtrando por: tipo de servicio, fecha, ubicación y tipo de mascota.
- El cliente debe poder ver el perfil completo de un cuidador (reseñas, fotos, tarifas, disponibilidad).

#### 📅 Reservas
- El cliente debe poder crear una reserva seleccionando cuidador, mascota, fechas y servicios.
- El sistema debe notificar al cuidador cuando reciba una solicitud.
- El cuidador debe poder aceptar o rechazar reservas.
- El sistema debe actualizar el estado de la reserva (pendiente, confirmada, rechazada, completada).

#### 🌟 Reseñas
- Tras finalizar el servicio, el cliente debe poder dejar una reseña y puntaje al cuidador.
- El sistema debe mostrar el promedio de calificaciones en los perfiles de cuidadores.


## CASOS DE USO: 
1. Registrar Usuario (Simple)
Actor: Cliente o Cuidador
Flujo Principal:
    1. Usuario selecciona "Registrarse"
    2. Sistema muestra formulario (email, contraseña, tipo: Cliente/Cuidador)
    3. Usuario completa datos y envía
    4. Sistema valida unicidad de email
    5. Sistema crea cuenta y envía email de confirmación
2. Crear Perfil de Mascota (Simple)
Actor: Cliente
Precondición: Usuario registrado como Cliente
Flujo Principal:
    1. Cliente accede a "Mis Mascotas"
    2. Sistema muestra formulario (nombre, especie, raza, edad, peso, características especiales)
    3. Cliente completa información y sube foto
    4. Sistema valida y guarda el perfil
    5. Sistema confirma creación exitosa

3. Crear Perfil de Cuidador (Medio)
Actor: Cuidador
Precondición: Usuario registrado como Cuidador
Flujo Principal:
    1. Cuidador accede a "Completar Mi Perfil"
    2. Sistema muestra secciones:
        * Información personal (descripción, experiencia)
        * Servicios ofrecidos (alimentación, paseos, alojamiento)
        * Tarifas por servicio
        * Zona de cobertura
        * Disponibilidad (calendario)
    3. Cuidador completa cada sección
    4. Sistema valida datos requeridos
    5. Sistema activa perfil para búsquedas

4. Buscar Cuidador (Complejo)
Actor: Cliente
Precondición: Cliente con al menos una mascota registrada
Flujo Principal:
    1. Cliente selecciona "Buscar Cuidadores"
    2. Sistema muestra filtros: servicio, fecha, ubicación, tipo de mascota
    3. Cliente aplica filtros
    4. Sistema consulta API de Google Maps para radio de búsqueda
    5. Sistema muestra resultados en mapa y lista
    6. Cliente puede ver perfiles, reviews y disponibilidad
    
5. Crear Reserva (Complejo)
Actor: Cliente
Precondición: Cliente encontró cuidador deseado
Flujo Principal:
    1. Cliente selecciona "Solicitar Reserva"
    2. Sistema muestra formulario: fechas, servicios, mascota, instrucciones especiales
    3. Cliente completa solicitud
    4. Sistema notifica al cuidador
    5. Cuidador acepta/rechaza reserva
    6. Sistema confirma reserva y envía detalles a ambas partes


## 📚 Librerías Necesarias

Todas las librerías de Python requeridas para el correcto funcionamiento y despliegue de la API se encuentran listadas detalladamente en el archivo **[requerimientos.txt](requerimientos.txt)**.

## Organización del proyecto 
```
app/
├── api/
    ├── main.py
│   └── v1/
│       └── endpoints/
├── core/
├── db/
├── domain/
│   ├── models/
│   └── ...
├── schemas/
├── services/
├── tasks/
├── test/
├── main.py
```

📁 api/

Contiene las rutas expuestas por la aplicación (FastAPI).
Aquí se definen los endpoints que reciben peticiones HTTP y llaman a los servicios correspondientes.

📁 core/

Configuración esencial del sistema:
variables de entorno, autenticación, seguridad, inicialización global.

📁 db/

Manejo de la base de datos:
creación de la sesión, inicialización de conexión, migraciones y funciones auxiliares.

📁 domain/

Contiene la lógica de negocio de la aplicación (independiente del framework).

📁 domain/models/

Modelos ORM que representan entidades en la base de datos.

📁 schemas/

Modelos Pydantic usados para validar y estructurar datos de entrada y salida en la API
(p. ej., UserCreate, TaskRead).

📁 services/

Capa de servicios que implementa la lógica que conecta la API con el dominio.
Se encargan de coordinar acciones entre modelos, reglas de negocio y base de datos.

📁 tasks/

Contiene tareas automatizadas o programadas.

📄 main.py

Inicializa FastAPI, importa rutas, configura eventos y middleware.

## 🚀 Cómo desplegar y probar la API

Esta sección detalla los pasos necesarios para inicializar, ejecutar y validar localmente la PetCare API.

1. Requisitos Previos
Antes de comenzar, asegúrate de tener instalado y configurado lo siguiente en tu sistema:

Python 3.x

Docker y Docker Compose (necesarios para el despliegue de la API y la Base de Datos).

2. Despliegue de la Aplicación (Usando Docker Compose)
Utilizamos Docker para asegurar un entorno de ejecución consistente que incluye la API de FastAPI y su base de datos asociada (sqlalchemy).

* Clonar el Repositorio:

```bash
git clone https://docs.github.com/es/repositories/creating-and-managing-repositories/quickstart-for-repositories
cd [nombre-del-repo]
```


* Configurar Variables de Entorno: Asegúrate de configurar las variables de entorno necesarias (como la URL de la base de datos o claves secretas) en un archivo .env en la raíz del proyecto.

* Ejecutar el Stack: Inicia la API y la base de datos con un solo comando. Docker Compose se encargará de construir la imagen de FastAPI y levantar los servicios.


```bash
docker-compose up --build -d
```
(El flag --build fuerza la reconstrucción de la imagen, y -d ejecuta el proceso en segundo plano).

* Verificación: Una vez que el proceso finalice, la API estará accesible.

    -API Principal: http://localhost:[PUERTO_API] (Usualmente 8000).

    -Documentación Interactiva (Swagger UI): http://localhost:[PUERTO_API]/docs

3. Ejecución de Pruebas
Para validar que toda la funcionalidad de la API funciona correctamente, ejecuta las pruebas unitarias y de integración:

* Acceder al Contenedor de la API:

```bash

docker exec -it [nombre_del_contenedor_api] /bin/bash
```
(Reemplaza [nombre_del_contenedor_api] por el nombre de tu servicio definido en el docker-compose.yml, típicamente api o web).

* Ejecutar Pytest: Una vez dentro del contenedor, ejecuta el siguiente comando:

```bash

pytest
```
* Salir del Contenedor:

```bash

exit
```


