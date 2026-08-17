"""Módulo de calculadora con operaciones aritméticas básicas."""


def sumar(a: float, b: float) -> float:
    """Suma dos números."""
    return a + b


def restar(a: float, b: float) -> float:
    """Resta el segundo número del primero."""
    return a - b


def multiplicar(a: float, b: float) -> float:
    """Multiplica dos números."""
    return a * b


def dividir(a: float, b: float) -> float:
    """Divide el primer número por el segundo.

    Raises:
        ValueError: Si el divisor es cero.
    """
    if b == 0:
        raise ValueError("No se puede dividir por cero")
    return a / b