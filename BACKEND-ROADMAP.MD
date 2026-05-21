# Especificación Técnica del Backend
## Sistema de Gestión de Eventos y Entradas

Este documento detalla la arquitectura, el diseño de datos, la lógica de negocio y las fases de desarrollo correspondientes a la capa del servidor (Backend) para el Sistema de Gestión de Eventos y Entradas, utilizando el framework Django.

---

## 1. Arquitectura y Estructura del Backend

La aplicación se estructurará bajo el patrón **MVT (Modelo-Vista-Template)** nativo de Django, pero aplicando un enfoque modular y desacoplado para asegurar la escalabilidad, mantenibilidad y el cumplimiento de las buenas prácticas de ingeniería de software. 

### Organización por Capas Internas:
* **Capa de Modelos (Datos):** Representación de las entidades de la base de datos relacional, encargada de la integridad y las restricciones estructurales.
* **Capa de Formularios (Validación):** Encargada de la captura, limpieza y validación estricta de los datos entrantes antes de interactuar con los modelos.
* **Capa de Servicios (Lógica de Negocio):** Módulos independientes para procesos complejos (como la generación de códigos QR, exportación de reportes y procesamiento de pagos simulados), evitando saturar las vistas.
* **Capa de Vistas (Controladores):** Coordinadores del flujo de la aplicación que gestionan las peticiones HTTP, aplican filtros de seguridad por roles y retornan el contexto necesario.

---

## 2. Modelado de Datos Relacional

El sistema se fundamenta en un esquema relacional compuesto por cuatro modelos principales interconectados mediante llaves foráneas y relaciones lógicas robustas:

1.  **Usuario / Perfil Personalizado (`CustomUser`):** Extensión del sistema de autenticación de Django para soportar múltiples roles (Administrador, Organizador, Asistente) mediante campos de selección estrictos.
2.  **Ubicación (`Location`):** Almacena la información de los recintos o espacios donde se llevarán a cabo los eventos (Nombre, Capacidad Máxima, Dirección, Ciudad).
3.  **Evento (`Event`):** Entidad central del sistema. Contiene los detalles del espectáculo (Título, Descripción, Fecha, Hora, Estado). Mantiene una relación de clave foránea con `Location` (un evento pertenece a una ubicación) y con `CustomUser` (para identificar al Organizador dueño del evento).
4.  **Entrada / Ticket (`Ticket`):** Registra la adquisición de accesos. Relaciona un `CustomUser` (Asistente) con un `Event`. Contiene campos críticos como el precio de compra, un código UUID único para el control de acceso, un estado de validación (Activa, Utilizada, Cancelada) y la fecha de compra.

---

## 3. Lógica de Negocio y Funcionalidades Clave

El backend procesará de forma automatizada los siguientes requerimientos del sistema:
* **Sistema de Roles:** Implementación de decoradores y Mixins personalizados basados en los atributos del usuario para restringir el acceso a vistas específicas (por ejemplo, solo Organizadores pueden ejecutar el CRUD de eventos).
* **Generador de Códigos QR:** Servicio interno que toma el identificador único (UUID) de la `Entrada` y genera una matriz de puntos empaquetada, asociándola al registro para su posterior verificación en puerta.
* **Módulo de Reportes:** Utilización de herramientas de análisis de datos para procesar el inventario de entradas vendidas y estructurar archivos de descarga en formatos Excel y PDF con filtros temporales.
* **Pasarela de Pagos Simulada:** Componente de servicio que recibe los datos de transacción, ejecuta una validación de fondos y estados lógicos de forma asíncrona, y retorna una confirmación de éxito o rechazo.

---

## 4. Fases de Desarrollo del Backend

El desarrollo del backend se dividirá en cinco fases secuenciales y progresivas:

### Fase 1: Configuración del Entorno y Estrategia GitFlow
* Configuración del entorno virtual, inicialización del proyecto Django y estructuración de la base de datos inicial.
* Establecimiento de la arquitectura GitFlow. **Regla Estricta de Integración:** Todo el desarrollo se realizará en ramas de características (`feature/backend-*`). Al finalizar una característica, se subirá la rama al repositorio remoto y se abrirá un **Pull Request (PR) exclusivamente desde la interfaz web de GitHub** hacia la rama `develop`. Queda estrictamente prohibido realizar fusiones (`merge`) de forma local desde la terminal hacia las ramas protegidas (`develop` o `main`).

### Fase 2: Autenticación, Roles y Modelado Base
* Implementación del modelo de usuario personalizado.
* Creación de las migraciones para los modelos `Location`, `Event` y `Ticket`, definiendo campos de auditoría (fechas de creación y modificación) e integridad referencial (`on_delete=models.PROTECT` para evitar pérdidas accidentales de datos históricos).

### Fase 3: Capa de Controladores (CRUD) y Validación
* Construcción de formularios basados en modelos (`ModelForms`) con validaciones personalizadas (por ejemplo, evitar que un evento se agende en una ubicación que ya tiene un evento asignado en la misma fecha y hora).
* Desarrollo de las vistas para el flujo CRUD de eventos, ubicaciones y precios, asegurando el manejo seguro de excepciones y errores HTTP (404, 403).

### Fase 4: Servicios Avanzados y API Simulada
* Desarrollo del servicio de generación de códigos QR y lógica de negocio para cambiar el estado de la entrada durante la validación de acceso.
* Integración de las librerías de reportes para procesar los datos transaccionales, permitiendo la segmentación y filtrado por categorías de eventos o rangos de fechas.

### Fase 5: Preparación para el Despliegue y Pruebas
* Configuración de variables de entorno seguras para la base de datos de producción (PostgreSQL) y claves del sistema.
* Ajuste de configuraciones de producción para el despliegue en la nube.

---

## 5. Documentación y Control de Calidad
Cada endpoint y función de la lógica de negocio contará con docstrings descriptivos bajo el estándar de Django. La verificación de la consistencia de los datos relacionales garantizará que no existan duplicados ni registros huérfanos en el flujo de ventas de entradas.