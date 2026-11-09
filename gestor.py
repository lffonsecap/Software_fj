"""
gestor.py
---------
SistemaGestion: administra las LISTAS INTERNAS de clientes, servicios y
reservas (no hay base de datos; todo vive en memoria).

Todas las operaciones pasan por el método _ejecutar(), que aplica el
bloque completo try / except / else / finally. Así, cualquier error se
registra en el log y la aplicación sigue funcionando.
"""

from cliente import Cliente
from excepciones import (
    OperacionNoPermitidaError,
    RecursoNoEncontradoError,
    ServicioInvalidoError,
    SoftwareFJError,
)
from logger_config import obtener_logger
from reserva import Reserva
from servicios import AlquilerEquipo, Asesoria, ReservaSala

logger = obtener_logger("gestor")


class SistemaGestion:
    """Fachada principal del sistema Software FJ."""

    # Mapa de tipos de servicio disponibles -> clase que los implementa
    TIPOS_SERVICIO = {"sala": ReservaSala, "equipo": AlquilerEquipo, "asesoria": Asesoria}

    def __init__(self):
        self.__clientes: list[Cliente] = []    # Lista interna de clientes
        self.__servicios: list = []            # Lista interna de servicios
        self.__reservas: list[Reserva] = []    # Lista interna de reservas
        self.__operaciones = 0                 # Contadores para el resumen final
        self.__exitosas = 0
        self.__fallidas = 0
        logger.info("=== Sistema Software FJ iniciado ===")

    # -----------------------------------------------------------------
    # Núcleo de manejo de excepciones
    # -----------------------------------------------------------------
    def _ejecutar(self, descripcion: str, accion):
        """Ejecuta 'accion' protegiéndola con try/except/else/finally."""
        self.__operaciones += 1
        numero = self.__operaciones
        try:
            resultado = accion()                      # Intentamos la operación
        except SoftwareFJError as error:              # Errores de negocio previstos
            self.__fallidas += 1
            causa = ""
            if error.__cause__ is not None:           # ¿Hubo encadenamiento?
                causa = f" | Causa original: {type(error.__cause__).__name__}: {error.__cause__}"
            logger.error(f"Op #{numero} '{descripcion}' falló -> {type(error).__name__}: {error}{causa}")
            print(f"   ✘ ERROR: {error}{causa}")
            return None
        except Exception as error:                    # Cualquier error inesperado de Python
            self.__fallidas += 1
            logger.exception(f"Op #{numero} '{descripcion}' error INESPERADO -> {error!r}")
            print(f"   ✘ ERROR INESPERADO ({type(error).__name__}): {error}. El sistema continúa.")
            return None
        else:                                         # Solo si no hubo error
            self.__exitosas += 1
            logger.info(f"Op #{numero} '{descripcion}' completada con éxito.")
            print(f"   ✔ OK: {resultado}")
            return resultado
        finally:                                      # Siempre se ejecuta
            logger.debug(f"Op #{numero} finalizada.")

    # -----------------------------------------------------------------
    # Búsquedas (lanzan RecursoNoEncontradoError si no existe)
    # -----------------------------------------------------------------
    def _buscar_cliente(self, documento) -> Cliente:
        for cliente in self.__clientes:
            if cliente.documento == str(documento):
                return cliente
        raise RecursoNoEncontradoError("cliente", documento)

    def _buscar_servicio(self, id_servicio):
        for servicio in self.__servicios:
            if servicio.id == id_servicio:
                return servicio
        raise RecursoNoEncontradoError("servicio", id_servicio)

    def _buscar_reserva(self, id_reserva) -> Reserva:
        for reserva in self.__reservas:
            if reserva.id == id_reserva:
                return reserva
        raise RecursoNoEncontradoError("reserva", id_reserva)

    # -----------------------------------------------------------------
    # Operaciones públicas
    # -----------------------------------------------------------------
    def registrar_cliente(self, nombre, documento, correo, telefono):
        def accion():
            # Regla de negocio: no se permiten documentos duplicados
            if any(c.documento == str(documento).strip() for c in self.__clientes):
                raise OperacionNoPermitidaError(f"Ya existe un cliente con documento {documento}.")
            cliente = Cliente(nombre, documento, correo, telefono)
            self.__clientes.append(cliente)
            return cliente
        return self._ejecutar(f"Registrar cliente {nombre}", accion)

    def crear_servicio(self, tipo, **datos):
        def accion():
            clase = self.TIPOS_SERVICIO.get(tipo)
            if clase is None:
                raise ServicioInvalidoError(
                    f"Tipo de servicio '{tipo}' no existe. Tipos válidos: {', '.join(self.TIPOS_SERVICIO)}.")
            servicio = clase(**datos)      # Polimorfismo: cada clase se construye a su modo
            self.__servicios.append(servicio)
            return servicio
        return self._ejecutar(f"Crear servicio '{tipo}'", accion)

    def cambiar_disponibilidad(self, id_servicio, disponible):
        def accion():
            servicio = self._buscar_servicio(id_servicio)
            servicio.disponible = disponible
            return f"{servicio.nombre} ahora está {'disponible' if disponible else 'NO disponible'}"
        return self._ejecutar(f"Cambiar disponibilidad de {id_servicio}", accion)

    def crear_reserva(self, documento_cliente, id_servicio, duracion, impuesto=0.19, descuento=0.0):
        def accion():
            cliente = self._buscar_cliente(documento_cliente)
            servicio = self._buscar_servicio(id_servicio)
            reserva = Reserva(cliente, servicio, duracion, impuesto, descuento)
            self.__reservas.append(reserva)
            return reserva
        return self._ejecutar(f"Crear reserva ({documento_cliente} -> {id_servicio})", accion)

    def confirmar_reserva(self, id_reserva):
        def accion():
            reserva = self._buscar_reserva(id_reserva)
            costo = reserva.confirmar()
            return f"{reserva.id} confirmada por ${costo:,.2f}"
        return self._ejecutar(f"Confirmar reserva {id_reserva}", accion)

    def cancelar_reserva(self, id_reserva, motivo):
        def accion():
            reserva = self._buscar_reserva(id_reserva)
            reserva.cancelar(motivo)
            return f"{reserva.id} cancelada ({motivo})"
        return self._ejecutar(f"Cancelar reserva {id_reserva}", accion)

    def procesar_reserva(self, id_reserva):
        def accion():
            reserva = self._buscar_reserva(id_reserva)
            costo = reserva.procesar()
            return f"{reserva.id} procesada. Cobrado: ${costo:,.2f}"
        return self._ejecutar(f"Procesar reserva {id_reserva}", accion)

    def cotizar(self, id_servicio, parametro):
        def accion():
            servicio = self._buscar_servicio(id_servicio)
            valor = servicio.cotizar(parametro)   # Sobrecarga por tipo (int/float o dict)
            return f"Cotización de {servicio.nombre} con {parametro!r}: ${valor:,.2f}"
        return self._ejecutar(f"Cotizar {id_servicio}", accion)

    # -----------------------------------------------------------------
    # Consultas (devuelven tuplas para no exponer las listas internas)
    # -----------------------------------------------------------------
    @property
    def clientes(self):
        return tuple(self.__clientes)

    @property
    def servicios(self):
        return tuple(self.__servicios)

    @property
    def reservas(self):
        return tuple(self.__reservas)

    def resumen(self) -> str:
        texto = (f"Operaciones: {self.__operaciones} | Exitosas: {self.__exitosas} | "
                 f"Fallidas (controladas): {self.__fallidas}")
        logger.info(f"Resumen final -> {texto}")
        return texto
