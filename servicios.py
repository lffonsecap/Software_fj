"""
servicios.py
------------
Clase abstracta Servicio y sus tres servicios especializados:
    - ReservaSala      (se cobra por hora)
    - AlquilerEquipo   (se cobra por día y por unidad)
    - Asesoria         (se cobra por hora según el nivel del asesor)

Aquí se demuestran:
    * Herencia: las tres clases heredan de Servicio (y esta de EntidadBase).
    * Polimorfismo: cada una sobrescribe _costo_base(), validar_parametros()
      y describir(); el sistema las usa igual sin saber de qué tipo son.
    * Sobrecargfa: calcular_costo() admite parámetros opcionales (impuesto,
      descuento) y cotizar() cambia de comportamiento según el TIPO del
      argumento (int/float o dict) usando functools.singledispatchmethod.
"""

import math                                  # Para detectar valores infinitos o NaN
from abc import abstractmethod               # Métodos que las hijas DEBEN implementar
from functools import singledispatchmethod   # Sobrecarga por tipo de dato en Python

from entidad_base import EntidadBase
from excepciones import (
    CalculoInconsistenteError,
    ParametroFaltanteError,
    ServicioInvalidoError,
    ServicioNoDisponibleError,
)


def validar_numero(valor, campo: str, minimo: float, maximo: float) -> float:
    """Valida que 'valor' sea un número (no booleano) dentro de [minimo, maximo]."""
    if valor is None:
        raise ParametroFaltanteError(campo)
    # bool es subclase de int en Python, por eso lo excluimos explícitamente
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ServicioInvalidoError(f"'{campo}' debe ser numérico, se recibió '{valor}' ({type(valor).__name__}).")
    if not (minimo <= valor <= maximo):
        raise ServicioInvalidoError(f"'{campo}' = {valor} fuera de rango permitido [{minimo}, {maximo}].")
    return float(valor)


class Servicio(EntidadBase):
    """Clase abstracta: representa cualquier servicio que ofrece Software FJ."""

    TASA_IMPUESTO_MAXIMA = 0.5   # 50 %: ningún impuesto válido supera esto
    DESCUENTO_MAXIMO = 0.9       # 90 %: un descuento mayor sería inconsistente

    def __init__(self, nombre, tarifa_base, unidad: str):
        # Validamos y guardamos los datos comunes a todos los servicios
        if nombre is None or (isinstance(nombre, str) and not nombre.strip()):
            raise ParametroFaltanteError("nombre")
        if not isinstance(nombre, str):
            raise ServicioInvalidoError("El nombre del servicio debe ser texto.")
        self.__nombre = nombre.strip()
        self.__tarifa_base = validar_numero(tarifa_base, "tarifa_base", 1, 10_000_000)
        self.__unidad = unidad          # "horas" o "días"
        self.__disponible = True        # Todo servicio nace disponible
        super().__init__("SRV")         # Genera el ID solo si todo lo anterior fue válido

    # ---------------- Propiedades ----------------
    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def tarifa_base(self) -> float:
        return self.__tarifa_base

    @property
    def unidad(self) -> str:
        return self.__unidad

    @property
    def disponible(self) -> bool:
        return self.__disponible

    @disponible.setter
    def disponible(self, valor):
        if not isinstance(valor, bool):
            raise ServicioInvalidoError("La disponibilidad debe ser True o False.")
        self.__disponible = valor

    def verificar_disponibilidad(self) -> None:
        """Lanza ServicioNoDisponibleError si el servicio está deshabilitado."""
        if not self.__disponible:
            raise ServicioNoDisponibleError(self.__nombre)

    # ---------------- Métodos abstractos (polimorfismo) ----------------
    @abstractmethod
    def _costo_base(self, duracion: float) -> float:
        """Costo sin impuestos ni descuentos. Cada servicio lo calcula distinto."""

    @abstractmethod
    def validar_parametros(self, duracion) -> float:
        """Verifica que la duración sea válida para ESTE tipo de servicio."""

    # ---------------- Sobrecarga 1: parámetros opcionales ----------------
    def calcular_costo(self, duracion, impuesto: float = 0.0, descuento: float = 0.0) -> float:
        """
        Variantes de uso (sobrecarga mediante parámetros opcionales):
            calcular_costo(3)                         -> solo costo base
            calcular_costo(3, impuesto=0.19)          -> con IVA
            calcular_costo(3, descuento=0.10)         -> con descuento
            calcular_costo(3, impuesto=0.19, descuento=0.10) -> ambos
        """
        duracion = self.validar_parametros(duracion)   # Polimórfico: cada hija valida a su manera

        # Validamos impuesto y descuento; si son absurdos el cálculo es inconsistente
        for valor, campo, maximo in ((impuesto, "impuesto", self.TASA_IMPUESTO_MAXIMA),
                                     (descuento, "descuento", self.DESCUENTO_MAXIMO)):
            if isinstance(valor, bool) or not isinstance(valor, (int, float)):
                raise CalculoInconsistenteError(f"El {campo} debe ser numérico, se recibió '{valor}'.")
            if not (0 <= valor <= maximo):
                raise CalculoInconsistenteError(f"El {campo} {valor:.0%} está fuera del rango 0% - {maximo:.0%}.")

        base = self._costo_base(duracion)          # Polimórfico: cada hija calcula su costo
        subtotal = base * (1 - descuento)          # Primero se aplica el descuento
        total = subtotal * (1 + impuesto)          # Luego el impuesto sobre el subtotal

        # Verificación final de consistencia del resultado
        if not math.isfinite(total) or total <= 0:
            raise CalculoInconsistenteError(f"Costo calculado inválido ({total}) para '{self.nombre}'.")
        return round(total, 2)

    # ---------------- Sobrecarga 2: según el tipo del argumento ----------------
    @singledispatchmethod
    def cotizar(self, parametro):
        """Versión genérica: se ejecuta si el tipo de 'parametro' no está registrado."""
        raise ServicioInvalidoError(f"No se puede cotizar con un parámetro de tipo {type(parametro).__name__}.")

    @cotizar.register(int)
    @cotizar.register(float)
    def _(self, duracion):
        """cotizar(3) -> cotización rápida con IVA del 19 %."""
        return self.calcular_costo(duracion, impuesto=0.19)

    @cotizar.register(dict)
    def _(self, opciones):
        """cotizar({'duracion': 3, 'impuesto': 0.19, 'descuento': 0.1}) -> cotización detallada."""
        if "duracion" not in opciones:
            raise ParametroFaltanteError("duracion")
        return self.calcular_costo(opciones["duracion"],
                                   opciones.get("impuesto", 0.0),
                                   opciones.get("descuento", 0.0))

    def validar(self) -> bool:
        # Un servicio es válido si su tarifa sigue siendo positiva
        validar_numero(self.__tarifa_base, "tarifa_base", 1, 10_000_000)
        return True


# =====================================================================
#                     SERVICIOS ESPECIALIZADOS
# =====================================================================

class ReservaSala(Servicio):
    """Reserva de salas de reuniones. Se cobra por hora."""

    RECARGO_SALA_GRANDE = 0.15   # 15 % extra si la sala es para más de 30 personas

    def __init__(self, nombre, tarifa_base, capacidad):
        # Validamos el atributo propio ANTES de llamar al constructor padre
        self.__capacidad = int(validar_numero(capacidad, "capacidad", 1, 200))
        super().__init__(nombre, tarifa_base, "horas")

    @property
    def capacidad(self) -> int:
        return self.__capacidad

    def validar_parametros(self, duracion) -> float:
        # Una sala se reserva entre 1 y 12 horas
        return validar_numero(duracion, "duración (horas)", 1, 12)

    def _costo_base(self, duracion: float) -> float:
        costo = self.tarifa_base * duracion
        if self.__capacidad > 30:                     # Regla propia de las salas
            costo *= 1 + self.RECARGO_SALA_GRANDE
        return costo

    def describir(self) -> str:
        return (f"Sala {self.id}: {self.nombre} | capacidad {self.__capacidad} personas | "
                f"${self.tarifa_base:,.0f}/hora | {'Disponible' if self.disponible else 'NO disponible'}")


class AlquilerEquipo(Servicio):
    """Alquiler de equipos (portátiles, proyectores...). Se cobra por día y unidad."""

    SEGURO = 0.05   # 5 % de seguro obligatorio sobre el alquiler

    def __init__(self, nombre, tarifa_base, tipo_equipo, cantidad):
        if not tipo_equipo or not isinstance(tipo_equipo, str):
            raise ParametroFaltanteError("tipo_equipo")
        self.__tipo_equipo = tipo_equipo.strip()
        self.__cantidad = int(validar_numero(cantidad, "cantidad", 1, 50))
        super().__init__(nombre, tarifa_base, "días")

    def validar_parametros(self, duracion) -> float:
        # Un equipo se alquila entre 1 y 30 días
        return validar_numero(duracion, "duración (días)", 1, 30)

    def _costo_base(self, duracion: float) -> float:
        alquiler = self.tarifa_base * duracion * self.__cantidad
        return alquiler * (1 + self.SEGURO)

    def describir(self) -> str:
        return (f"Equipo {self.id}: {self.nombre} | {self.__cantidad} x {self.__tipo_equipo} | "
                f"${self.tarifa_base:,.0f}/día | {'Disponible' if self.disponible else 'NO disponible'}")


class Asesoria(Servicio):
    """Asesoría especializada. La tarifa se multiplica según el nivel del asesor."""

    MULTIPLICADORES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    def __init__(self, nombre, tarifa_base, especialidad, nivel):
        if not especialidad or not isinstance(especialidad, str):
            raise ParametroFaltanteError("especialidad")
        if nivel not in self.MULTIPLICADORES:
            raise ServicioInvalidoError(f"Nivel '{nivel}' no válido. Use: {', '.join(self.MULTIPLICADORES)}.")
        self.__especialidad = especialidad.strip()
        self.__nivel = nivel
        super().__init__(nombre, tarifa_base, "horas")

    def validar_parametros(self, duracion) -> float:
        # Una asesoría dura entre 1 y 8 horas
        return validar_numero(duracion, "duración (horas)", 1, 8)

    def _costo_base(self, duracion: float) -> float:
        return self.tarifa_base * duracion * self.MULTIPLICADORES[self.__nivel]

    def describir(self) -> str:
        return (f"Asesoría {self.id}: {self.nombre} | {self.__especialidad} ({self.__nivel}) | "
                f"${self.tarifa_base:,.0f}/hora | {'Disponible' if self.disponible else 'NO disponible'}")
