from dataclasses import dataclass

@dataclass(frozen=True)
class Sala:
    id: int
    nome: str
    capacidade: int
    bloco: str
