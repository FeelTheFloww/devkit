"""Fichier d'exemple pour démontrer `devkit ai docstring` et `devkit ai test-gen`.

Volontairement sans docstrings ni tests, pour que la démo soit visible.
"""

from __future__ import annotations


def add(a, b):
    return a + b


def divide(a, b):
    if b == 0:
        raise ValueError("Division by zero")
    return a / b


def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def fibonacci(n):
    if n < 0:
        raise ValueError("n must be non-negative")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


class Counter:

    def __init__(self, start=0):
        self.value = start

    def increment(self, amount=1):
        self.value += amount
        return self.value

    def reset(self):
        self.value = 0
        return self.value
