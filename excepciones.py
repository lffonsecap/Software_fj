"""
excepciones.py
--------------
Jerarquía de excepciones personalizadas del sistema Software FJ.

Todas heredan de SoftwareFJError, de modo que el gestor puede capturar
cualquier error del negocio con un solo except, y distinguirlo
de los errores inesperados de Python (TypeError, KeyError, etc.).
"""


class SoftwareFJError(Exception):
    """Excepción base de todo el sistema (clase padre de las demás)."""

    def __init__(self, mensaje: str, codigo: str = "SFJ-000"):
        # Llamamos al constructor de Exception para conservar el mensaje estándar
        super().__init__(mensaje)
        # Guardamos el mensaje para mostrarlo de forma amigable
        self.mensaje = mensaje
        # Código interno que facilita buscar el error en el archivo de logs
        self.codigo = codigo

    def __str__(self) -> str:
        # Representación en texto: "[CODIGO] mensaje"
        return f"[{self.codigo}] {self.mensaje}"


class ParametroFaltanteError(SoftwareFJError):
    """Se lanza cuando un dato obligatorio llega vacío o como None."""

    def __init__(self, parametro: str):
        # Construimos el mensaje indicando qué parámetro falta
        super().__init__(f"Falta el parámetro obligatorio '{parametro}'.", "SFJ-001")


class ClienteInvalidoError(SoftwareFJError):
    """Datos de cliente con formato incorrecto (correo, documento, etc.)."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "SFJ-100")


class ServicioInvalidoError(SoftwareFJError):
    """Servicio mal configurado o parámetros de servicio fuera de rango."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "SFJ-200")


class ServicioNoDisponibleError(SoftwareFJError):
    """Se intenta usar un servicio marcado como no disponible."""

    def __init__(self, nombre_servicio: str):
        super().__init__(f"El servicio '{nombre_servicio}' no está disponible en este momento.", "SFJ-201")


class CalculoInconsistenteError(SoftwareFJError):
    """El cálculo de costos produce un valor imposible (negativo, infinito...)."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "SFJ-300")


class ReservaInvalidaError(SoftwareFJError):
    """La reserva no se puede crear o confirmar por datos incorrectos."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "SFJ-400")


class OperacionNoPermitidaError(SoftwareFJError):
    """Acción no válida para el estado actual (ej. procesar una reserva cancelada)."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "SFJ-500")


class RecursoNoEncontradoError(SoftwareFJError):
    """Se busca un cliente, servicio o reserva que no existe en las listas."""

    def __init__(self, tipo: str, identificador: str):
        super().__init__(f"No existe {tipo} con identificador '{identificador}'.", "SFJ-404")
