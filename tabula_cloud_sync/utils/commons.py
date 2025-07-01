# Funcionalidades comunes del sistema


def get_dv(numero: str):
    """
    Obtener Digito Verificador del documento
    """
    basemax = 11
    v_numero_al = ""
    k = 2
    v_total = 0
    for x in range(
        len(numero)
    ):  # Cambia la ultima letra por ascii en caso que la cedula termine en letra
        v_caracter = str(numero[x]).upper()
        if not (ord(v_caracter) >= 48 and ord(v_caracter) <= 57):
            v_numero_al = v_numero_al + str(ord(v_caracter))
        else:
            v_numero_al = v_numero_al + v_caracter
    for x in reversed(v_numero_al):
        if k > basemax:
            k = 2
        v_numero_aux = int(x)
        v_total += v_numero_aux * k
        k += 1
    v_resto = v_total % 11
    if v_resto > 1:
        v_digit = 11 - v_resto
    else:
        v_digit = 0
    return v_digit


def validar_gtin(gtin) -> bool:
    """Valida códigos GTIN-8, GTIN-12, GTIN-13 y GTIN-14."""
    # Verificar si el GTIN contiene solo dígitos y tiene una longitud válida
    if not gtin.isdigit() or len(gtin) not in [8, 12, 13, 14]:
        return False

    # Convertir el GTIN en una lista de enteros para facilitar el manejo
    digitos = [int(d) for d in gtin]

    # Inicializar la suma total
    suma_total = 0

    # La lógica de ponderación varía según la longitud del GTIN
    # Para GTIN-8, la ponderación comienza con 3 en la posición más a la izquierda
    # Para GTIN-12, GTIN-13, y GTIN-14, comienza con 1
    ponderacion = 3 if len(gtin) == 8 else 1

    # Recorrer todos los dígitos excepto el último (dígito de control)
    for i in range(len(digitos) - 1):
        suma_total += digitos[i] * ponderacion
        # Alternar la ponderación
        ponderacion = 4 - ponderacion  # Esto alternará entre 3 y 1

    # Calcular el dígito de control
    digito_control_calculado = (10 - suma_total % 10) % 10

    # Verificar si el dígito de control calculado coincide con el último dígito del GTIN
    return digito_control_calculado == digitos[-1]


# Funcion de redondeo
def round_ext(num, decimales=0):
    factor = 10**decimales
    entero = int(num * factor)
    decimal = num * factor - entero
    if decimal >= 0.5:
        redondeado = (entero + 1) / factor
    else:
        redondeado = entero / factor
    return redondeado
