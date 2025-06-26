from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal

class Comunicador(QWidget):
    # Definimos una señal personalizada con un argumento de tipo str
    # 1 - Limpiar, 2 - ReadOnly
    fields_estado = Signal(int)
    field_data = Signal(object)
    field_read_only = Signal(bool)