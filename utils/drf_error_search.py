def find_error_message(d, key_target):
    """
    Busca recursivamente un mensaje de error en el diccionario anidado.

    Args:
    d (dict): El diccionario en el que buscar.
    key_target (str): La clave que contiene el mensaje de error.

    Returns:
    str: El mensaje de error si se encuentra, 'None' si no se encuentra.
    """
    if isinstance(d, dict):
        for key, value in d.items():
            if key == key_target:
                # Asumiendo que el valor asociado con 'non_field_errors' es una lista.
                return value[0] if value else "Error sin mensaje específico"
            if isinstance(value, (dict, list)):
                # Si el valor es otro diccionario o lista, busca recursivamente dentro de él.
                result = find_error_message(value, key_target)
                if result:
                    return result
    elif isinstance(d, list):
        for item in d:
            result = find_error_message(item, key_target)
            if result:
                return result
    return None  # Si no se encuentra el mensaje de error