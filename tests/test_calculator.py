"""Tests para el módulo de calculadora."""

import pytest
import sys
sys.path.insert(0, '/home/fernando/ai-ecosystem/src')

from calculator import sumar, restar, multiplicar, dividir


class TestSumar:
    def test_sumar_numeros_positivos(self):
        assert sumar(3, 5) == 8

    def test_sumar_numeros_negativos(self):
        assert sumar(-3, -5) == -8

    def test_sumar_positivo_y_negativo(self):
        assert sumar(10, -3) == 7

    def test_sumar_cero(self):
        assert sumar(5, 0) == 5


class TestRestar:
    def test_restar_numeros_positivos(self):
        assert restar(10, 3) == 7

    def test_restar_numeros_negativos(self):
        assert restar(-5, -3) == -2

    def test_restar_resultado_negativo(self):
        assert restar(3, 10) == -7

    def test_restar_cero(self):
        assert restar(5, 0) == 5


class TestMultiplicar:
    def test_multiplicar_numeros_positivos(self):
        assert multiplicar(4, 5) == 20

    def test_multiplicar_por_cero(self):
        assert multiplicar(5, 0) == 0

    def test_multiplicar_numeros_negativos(self):
        assert multiplicar(-3, -4) == 12

    def test_multiplicar_positivo_y_negativo(self):
        assert multiplicar(3, -4) == -12


class TestDividir:
    def test_dividir_numeros_positivos(self):
        assert dividir(10, 2) == 5

    def test_dividir_no_entero(self):
        assert dividir(7, 2) == 3.5

    def test_dividir_negativo(self):
        assert dividir(-10, 2) == -5

    def test_dividir_por_cero_raises(self):
        with pytest.raises(ValueError, match="No se puede dividir por cero"):
            dividir(10, 0)