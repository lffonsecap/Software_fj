"""
main.py
-------
Punto de entrada del Sistema Integral de Gestión de Clientes, Servicios
y Reservas de Software FJ.

Simulamos más de 10 operaciones completas: registros válidos e inválidos de
clientes, creación correcta e incorrecta de servicios, y reservas exitosas
y fallidas. El programa nunca se detiene: cada error se captura, se
registra en logs/software_fj.log y la ejecución continúa.
"""

from datetime import datetime

from gestor import SistemaGestion
from logger_config import ARCHIVO_LOG


def titulo(numero: int, texto: str) -> None:
    """Imprime el encabezado de cada operación simulada."""
    print(f"\n[{numero:02d}] {texto}")


def main() -> None:
    print("=" * 78)
    print("  SOFTWARE FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas")
    print(f"  Ejecución: {datetime.now():%Y-%m-%d %H:%M:%S}")
    print("=" * 78)

    sistema = SistemaGestion()

    # ------------------------- CLIENTES -------------------------
    titulo(1, "Registrar cliente válido")
    ana = sistema.registrar_cliente("ana maría lópez", "1023456789", "ana.lopez@correo.com", "3104567890")

    titulo(2, "Registrar segundo cliente válido")
    sistema.registrar_cliente("Carlos Pérez", "80123456", "carlos.perez@empresa.co", "3209876543")

    titulo(3, "Registrar cliente con correo inválido")
    sistema.registrar_cliente("Luisa Gómez", "52987654", "luisa.gomez@@correo", "3001234567")

    titulo(4, "Registrar cliente sin nombre (parámetro faltante)")
    sistema.registrar_cliente("", "79111222", "sin.nombre@correo.com", "3111111111")

    titulo(5, "Registrar cliente con documento duplicado")
    sistema.registrar_cliente("Ana Duplicada", "1023456789", "otra@correo.com", "3150000000")

    # ------------------------- SERVICIOS ------------------------
    titulo(6, "Crear servicio de sala (válido)")
    sala = sistema.crear_servicio("sala", nombre="Sala Ejecutiva", tarifa_base=80_000, capacidad=40)

    titulo(7, "Crear servicio de alquiler de equipo (válido)")
    equipo = sistema.crear_servicio("equipo", nombre="Portátiles Dell", tarifa_base=45_000,
                                    tipo_equipo="Portátil", cantidad=3)

    titulo(8, "Crear servicio de asesoría (válido)")
    asesoria = sistema.crear_servicio("asesoria", nombre="Asesoría en Ciberseguridad", tarifa_base=120_000,
                                      especialidad="Seguridad informática", nivel="experto")

    titulo(9, "Crear sala con tarifa negativa (inválido)")
    sistema.crear_servicio("sala", nombre="Sala Fantasma", tarifa_base=-5000, capacidad=10)

    titulo(10, "Crear asesoría con nivel inexistente (inválido)")
    sistema.crear_servicio("asesoria", nombre="Asesoría Python", tarifa_base=90_000,
                           especialidad="Programación", nivel="maestro jedi")

    titulo(11, "Crear servicio de un tipo que no existe")
    sistema.crear_servicio("transporte", nombre="Van ejecutiva", tarifa_base=200_000)

    titulo(12, "Crear servicio con un parámetro no reconocido (error inesperado de Python)")
    sistema.crear_servicio("sala", nombre="Sala Azul", tarifa_base=50_000, capacidad=10, color="azul")

    # Obtenemos los IDs de los servicios creados (si alguno falló será None)
    id_sala = sala.id if sala else None
    id_equipo = equipo.id if equipo else None
    id_asesoria = asesoria.id if asesoria else None

    # ------------------------- RESERVAS -------------------------
    titulo(13, "Reserva exitosa: crear, confirmar y procesar (sala 3 horas)")
    r1 = sistema.crear_reserva("1023456789", id_sala, 3)
    if r1:
        sistema.confirmar_reserva(r1.id)
        sistema.procesar_reserva(r1.id)

    titulo(14, "Reserva con descuento del 10 % (asesoría 2 horas)")
    r2 = sistema.crear_reserva("80123456", id_asesoria, 2, impuesto=0.19, descuento=0.10)
    if r2:
        sistema.confirmar_reserva(r2.id)

    titulo(15, "Reserva fallida: duración fuera de rango (sala por 20 horas)")
    sistema.crear_reserva("80123456", id_sala, 20)

    titulo(16, "Reserva fallida: duración con texto en vez de número")
    sistema.crear_reserva("1023456789", id_equipo, "tres")

    titulo(17, "Reserva fallida: cliente inexistente")
    sistema.crear_reserva("99999999", id_sala, 2)

    titulo(18, "Reserva fallida: servicio no disponible")
    sistema.cambiar_disponibilidad(id_equipo, False)
    r3 = sistema.crear_reserva("1023456789", id_equipo, 5)
    if r3:
        sistema.confirmar_reserva(r3.id)   # Aquí salta ServicioNoDisponibleError

    titulo(19, "Reserva con cálculo inconsistente (descuento del 150 %)")
    r4 = sistema.crear_reserva("80123456", id_sala, 2, descuento=1.5)
    if r4:
        sistema.confirmar_reserva(r4.id)   # CalculoInconsistenteError encadenado en ReservaInvalidaError

    titulo(20, "Cancelar reserva confirmada y luego intentar procesarla")
    if r2:
        sistema.cancelar_reserva(r2.id, "")                       # Falla: falta el motivo
        sistema.cancelar_reserva(r2.id, "El cliente reprogramó")  # Éxito
        sistema.procesar_reserva(r2.id)                           # Falla: ya está cancelada

    titulo(21, "Intentar confirmar dos veces la misma reserva")
    if r1:
        sistema.confirmar_reserva(r1.id)

    # ----------------- SOBRECARGA DE MÉTODOS --------------------
    titulo(22, "Sobrecarga: cotizar con número, con diccionario y con tipo no soportado")
    sistema.cambiar_disponibilidad(id_equipo, True)
    sistema.cotizar(id_equipo, 4)                                               # int
    sistema.cotizar(id_equipo, {"duracion": 4, "impuesto": 0.19, "descuento": 0.2})  # dict
    sistema.cotizar(id_equipo, "cuatro días")                                   # str -> no soportado

    titulo(23, "Sobrecarga con parámetros opcionales en calcular_costo()")
    if asesoria:
        print(f"   Sin impuesto ni descuento : ${asesoria.calcular_costo(2):,.2f}")
        print(f"   Con IVA 19 %              : ${asesoria.calcular_costo(2, impuesto=0.19):,.2f}")
        print(f"   Con descuento 15 %        : ${asesoria.calcular_costo(2, descuento=0.15):,.2f}")
        print(f"   Con IVA y descuento       : ${asesoria.calcular_costo(2, 0.19, 0.15):,.2f}")

    # ------------------------- RESUMEN --------------------------
    print("\n" + "=" * 78)
    print("ESTADO FINAL DEL SISTEMA")
    print("-" * 78)
    for coleccion, nombre in ((sistema.clientes, "Clientes"), (sistema.servicios, "Servicios"),
                              (sistema.reservas, "Reservas")):
        print(f"{nombre} ({len(coleccion)}):")
        for elemento in coleccion:
            print(f"   - {elemento}")      # Polimorfismo: cada objeto usa su describir()
    print("-" * 78)
    print(sistema.resumen())
    print(f"Log de eventos y errores: {ARCHIVO_LOG}")
    print("El programa terminó sin interrupciones. ✔")
    print("=" * 78)


if __name__ == "__main__":
    main()
