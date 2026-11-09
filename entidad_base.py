"""
entidad_base.py
---------------
Clase abstracta que representa cualquier entidad general del sistema
(clientes, servicios y reservas heredan de ella).

Aplica abstracción: define que debe saber hacer toda entidad
(describirse y validarse) sin decir como; cada clase hija lo implementa.
"""

from abc import ABC, abstractmethod  # Herramientas para clases abstractas
from datetime import datetime         # Para guardar la fecha de creación


class EntidadBase(ABC):
    """Entidad general: tiene un identificador único y una fecha de creación."""

    # Diccionario de clase que lleva un contador por prefijo (CLI, SRV, RES)
    _contadores: dict[str, int] = {}

    def __init__(self, prefijo: str):
        # Generamos el siguiente número para este prefijo
        numero = EntidadBase._contadores.get(prefijo, 0) + 1
        EntidadBase._contadores[prefijo] = numero
        # Identificador encapsulado (atributo "privado" con doble guion bajo)
        self.__id = f"{prefijo}-{numero:03d}"
        # Fecha y hora en que se creó el objeto
        self.__fecha_creacion = datetime.now()

    @property
    def id(self) -> str:
        """Identificador de solo lectura (no tiene setter)."""
        return self.__id

    @property
    def fecha_creacion(self) -> datetime:
        """Fecha de creación de solo lectura."""
        return self.__fecha_creacion

    @abstractmethod
    def describir(self) -> str:
        """Cada entidad debe devolver una descripción legible de sí misma."""

    @abstractmethod
    def validar(self) -> bool:
        """Cada entidad debe poder verificar que su estado es coherente."""

    def __str__(self) -> str:
        # Al imprimir cualquier entidad se usa su propia descripción (polimorfismo)
        return self.describir()
