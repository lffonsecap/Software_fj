"""
cliente.py
----------
Clase Cliente: hereda de EntidadBase y encapsula los datos personales.

Los atributos son privados (__nombre, __documento, ...) y solo se acceden
mediante propiedades (@property). Los setters validan cada dato y lanzan
excepciones personalizadas si algo está mal.
"""

import re  # Expresiones regulares para validar formatos

from entidad_base import EntidadBase
from excepciones import ClienteInvalidoError, ParametroFaltanteError

# Patrones de validación (se compilan una vez para mayor eficiencia)
PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]{3,60}$")      # Solo letras y espacios
PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)*\.[A-Za-z]{2,}$")  # usuario@dominio.ext
PATRON_DOCUMENTO = re.compile(r"^\d{6,10}$")                         # 6 a 10 dígitos
PATRON_TELEFONO = re.compile(r"^\d{7,10}$")                          # 7 a 10 dígitos


def _texto_obligatorio(valor, nombre_campo: str) -> str:
    """Verifica que el valor exista y sea texto; devuelve el texto sin espacios extra."""
    # None o cadena vacía => falta el parámetro
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        raise ParametroFaltanteError(nombre_campo)
    # Si no es texto, el tipo de dato es inválido
    if not isinstance(valor, str):
        raise ClienteInvalidoError(f"El campo '{nombre_campo}' debe ser texto, se recibió {type(valor).__name__}.")
    return valor.strip()


class Cliente(EntidadBase):
    """Cliente de Software FJ con validaciones robustas."""

    def __init__(self, nombre, documento, correo, telefono):
        # Cada asignación pasa por su setter, que valida el dato
        self.nombre = nombre
        self.__documento = self.__validar_documento(documento)  # El documento no se puede cambiar luego
        self.correo = correo
        self.telefono = telefono
        # Solo si todo es válido se genera el ID (así no se "gastan" IDs con clientes inválidos)
        super().__init__("CLI")

    # ---------------- Propiedades encapsuladas ----------------
    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        texto = _texto_obligatorio(valor, "nombre")
        if not PATRON_NOMBRE.match(texto):
            raise ClienteInvalidoError(f"Nombre inválido '{texto}': solo letras y espacios (3 a 60 caracteres).")
        self.__nombre = texto.title()  # Guardamos con mayúscula inicial

    @property
    def documento(self) -> str:
        # Solo lectura: no existe setter para el documento
        return self.__documento

    @staticmethod
    def __validar_documento(valor) -> str:
        texto = _texto_obligatorio(valor, "documento")
        if not PATRON_DOCUMENTO.match(texto):
            raise ClienteInvalidoError(f"Documento inválido '{texto}': debe tener entre 6 y 10 dígitos.")
        return texto

    @property
    def correo(self) -> str:
        return self.__correo

    @correo.setter
    def correo(self, valor):
        texto = _texto_obligatorio(valor, "correo").lower()
        if not PATRON_CORREO.match(texto):
            raise ClienteInvalidoError(f"Correo electrónico inválido: '{texto}'.")
        self.__correo = texto

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        texto = _texto_obligatorio(valor, "telefono")
        if not PATRON_TELEFONO.match(texto):
            raise ClienteInvalidoError(f"Teléfono inválido '{texto}': debe tener entre 7 y 10 dígitos.")
        self.__telefono = texto

    # ---------------- Métodos abstractos implementados ----------------
    def documento_enmascarado(self) -> str:
        """Protege el dato personal mostrando solo los últimos 4 dígitos."""
        return "*" * (len(self.__documento) - 4) + self.__documento[-4:]

    def describir(self) -> str:
        return f"Cliente {self.id}: {self.nombre} | Doc: {self.documento_enmascarado()} | {self.correo}"

    def validar(self) -> bool:
        # Reverifica todos los campos; si alguno falla se lanza la excepción correspondiente
        self.nombre = self.__nombre
        self.correo = self.__correo
        self.telefono = self.__telefono
        return True
