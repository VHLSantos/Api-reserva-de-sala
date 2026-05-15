from dataclasses import dataclass

@dataclass(frozen=True)
class Usuario:
    id: int
    nome: str
    email: str
