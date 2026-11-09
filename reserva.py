"""
reserva.py
----------
Clase Reserva: integra un Cliente, un Servicio, una duración y un estado.


Demuestra:
    * try/except con ENCADENAMIENTO (raise ... from ...)
    * try/except/else  (en confirmar)
    * try/finally      (en procesar)
"""

from datetime import datetime
from enum import Enum

from cliente import Cliente
from entidad_base import EntidadBase
from excepciones import (
    CalculoInconsistenteError,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    ReservaInvalidaError,
    ServicioInvalidoError,
)
from logger_config import obtener_logger
from servicios import Servicio

logger = obtener_logger("reserva")


class EstadoReserva(Enum):
    """Estados posibles de una reserva."""
    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    CANCELADA = "Cancelada"
    PROCESADA = "Procesada"


class Reserva(EntidadBase):
    """Reserva de un servicio por parte de un cliente."""

    def __init__(self, cliente, servicio, duracion, impuesto=0.19, descuento=0.0):
        # 1) Validamos que los objetos recibidos sean del tipo correcto
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un objeto Cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un objeto Servicio válido.")

        # 2) Validamos la duración usando las reglas del servicio (polimorfismo).
        #    Si falla, encadenamos la excepción original con 'from' para no perder la causa.
        try:
            self.__duracion = servicio.validar_parametros(duracion)
        except (ServicioInvalidoError, ParametroFaltanteError) as error:
            raise ReservaInvalidaError(
                f"Duración no válida para '{servicio.nombre}'."
            ) from error

        self.__cliente = cliente
        self.__servicio = servicio
        self.__impuesto = impuesto
        self.__descuento = descuento
        self.__estado = EstadoReserva.PENDIENTE   # Toda reserva inicia pendiente
        self.__costo = None                       # Se calcula al confirmar
        self.__motivo_cancelacion = None
        super().__init__("RES")
        logger.info(f"Reserva {self.id} creada (PENDIENTE) para {cliente.nombre} - {servicio.nombre}")

    # ---------------- Propiedades de solo lectura ----------------
    @property
    def cliente(self) -> Cliente:
        return self.__cliente

    @property
    def servicio(self) -> Servicio:
        return self.__servicio

    @property
    def estado(self) -> EstadoReserva:
        return self.__estado

    @property
    def costo(self):
        return self.__costo

    # ---------------- Operaciones del ciclo de vida ----------------
    def confirmar(self) -> float:
        """Confirma la reserva y calcula su costo final. Usa try/except/else."""
        if self.__estado is not EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"No se puede confirmar la reserva {self.id}: su estado es {self.__estado.value}.")

        try:
            # Puede lanzar ServicioNoDisponibleError (se deja propagar tal cual)
            self.__servicio.verificar_disponibilidad()
            # Puede lanzar CalculoInconsistenteError
            costo = self.__servicio.calcular_costo(self.__duracion, self.__impuesto, self.__descuento)
        except CalculoInconsistenteError as error:
            # Convertimos el error técnico en un error de reserva, conservando la causa
            raise ReservaInvalidaError(f"No se pudo calcular el costo de la reserva {self.id}.") from error
        else:
            # El bloque else SOLO se ejecuta si el try terminó sin errores
            self.__costo = costo
            self.__estado = EstadoReserva.CONFIRMADA
            logger.info(f"Reserva {self.id} CONFIRMADA. Costo total: ${costo:,.2f}")
            return costo

    def cancelar(self, motivo) -> None:
        """Cancela la reserva; exige un motivo y no aplica a reservas ya cerradas."""
        if not motivo or not str(motivo).strip():
            raise ParametroFaltanteError("motivo de cancelación")
        if self.__estado in (EstadoReserva.CANCELADA, EstadoReserva.PROCESADA):
            raise OperacionNoPermitidaError(
                f"No se puede cancelar la reserva {self.id}: ya está {self.__estado.value}.")
        self.__estado = EstadoReserva.CANCELADA
        self.__motivo_cancelacion = str(motivo).strip()
        logger.info(f"Reserva {self.id} CANCELADA. Motivo: {self.__motivo_cancelacion}")

    def procesar(self) -> float:
        """Procesa (cobra/ejecuta) la reserva. Usa try/finally para dejar rastro siempre."""
        try:
            if self.__estado is not EstadoReserva.CONFIRMADA:
                raise OperacionNoPermitidaError(
                    f"Solo se procesan reservas confirmadas; {self.id} está {self.__estado.value}.")
            self.__estado = EstadoReserva.PROCESADA
            logger.info(f"Reserva {self.id} PROCESADA el {datetime.now():%Y-%m-%d %H:%M}.")
            return self.__costo
        finally:
            # finally se ejecuta SIEMPRE, haya error o no
            logger.debug(f"Fin del intento de procesamiento de {self.id} (estado actual: {self.__estado.value}).")

    # ---------------- Métodos abstractos implementados ----------------
    def describir(self) -> str:
        costo = f"${self.__costo:,.2f}" if self.__costo is not None else "sin calcular"
        return (f"Reserva {self.id}: {self.__cliente.nombre} -> {self.__servicio.nombre} | "
                f"{self.__duracion:g} {self.__servicio.unidad} | {self.__estado.value} | {costo}")

    def validar(self) -> bool:
        # La reserva es coherente si su duración sigue siendo válida para el servicio
        self.__servicio.validar_parametros(self.__duracion)
        return True
