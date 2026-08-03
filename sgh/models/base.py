from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarativa de todos os models do SGH.

    Fica sozinha neste módulo para que qualquer módulo de model possa importá-la
    sem criar ciclo de import.
    """
