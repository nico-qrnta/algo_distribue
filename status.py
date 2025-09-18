from enum import Enum

class Status(Enum):
    """
    Représente les différents états d'un processus dans la gestion de la section critique
    """
    NULL = 0
    REQUEST = 1
    SECTION_CRITIQUE = 2
    RELEASE = 3