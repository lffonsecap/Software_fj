# Software FJ – Sistema Integral de Gestión de Clientes, Servicios y Reservas

Curso Programación (213023) – UNAD – Fase 4: Prácticas simuladas.

Sistema orientado a objetos en Python, **sin base de datos**: todo se maneja con objetos y listas en memoria, y un archivo de logs (`logs/software_fj.log`) registra eventos y errores.

## Cómo ejecutar

```bash
python main.py
```

Requiere Python 3.10 o superior. No usa librerías externas.

## Estructura

| Archivo | Contenido |
|---|---|
| `excepciones.py` | Jerarquía de excepciones personalizadas (`SoftwareFJError` y 8 derivadas) |
| `logger_config.py` | Configuración del archivo de logs |
| `entidad_base.py` | Clase abstracta `EntidadBase` (ID, fecha, `describir()`, `validar()`) |
| `cliente.py` | Clase `Cliente` con encapsulación y validaciones |
| `servicios.py` | Clase abstracta `Servicio` + `ReservaSala`, `AlquilerEquipo`, `Asesoria` |
| `reserva.py` | Clase `Reserva` con estados, confirmación, cancelación y procesamiento |
| `gestor.py` | `SistemaGestion`: listas internas y manejo centralizado de excepciones |
| `main.py` | Simulación de 23 escenarios (más de 30 operaciones) válidos e inválidos |

## Conceptos aplicados

- **Abstracción:** `EntidadBase` y `Servicio` son clases abstractas (`ABC`, `@abstractmethod`).
- **Herencia:** `Cliente`, `Servicio` y `Reserva` heredan de `EntidadBase`; los tres servicios heredan de `Servicio`.
- **Polimorfismo:** cada servicio sobrescribe `_costo_base()`, `validar_parametros()` y `describir()`.
- **Encapsulación:** atributos privados (`__atributo`) con `@property` y setters que validan.
- **Sobrecarga:** `calcular_costo(duracion, impuesto=0, descuento=0)` con parámetros opcionales y `cotizar()` con `@singledispatchmethod` (cambia según el tipo: número o diccionario).
- **Excepciones:** `try/except`, `try/except/else`, `try/except/finally`, `try/finally` y encadenamiento `raise ... from ...`.
