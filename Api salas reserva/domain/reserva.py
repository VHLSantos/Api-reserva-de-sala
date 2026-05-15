from __future__ import annotations

from datetime import datetime, time, date, timedelta


class Reserva:
    def __init__(
        self,
        id: int,
        usuario_id: int,
        sala_id: int,
        data: str,
        hora_inicio: str,
        hora_fim: str,
        status: str = "active",
    ):
        self.id = id
        self.usuario_id = usuario_id
        self.sala_id = sala_id
        self.data = data
        self.hora_inicio = hora_inicio
        self.hora_fim = hora_fim
        self.status = status

    @staticmethod
    def _parse_date(value: str) -> date:
        return datetime.strptime(value, "%Y-%m-%d").date()

    @staticmethod
    def _parse_time(value: str) -> time:
        return datetime.strptime(value, "%H:%M").time()

    def _start_end_datetimes(self) -> tuple[datetime, datetime]:
        d = self._parse_date(self.data)
        inicio = self._parse_time(self.hora_inicio)
        fim = self._parse_time(self.hora_fim)
        return datetime.combine(d, inicio), datetime.combine(d, fim)

    def cancelar(self):
        if self.status == "canceled":
            raise ValueError("Reserva já está cancelada.")
        if self.status == "finished":
            raise ValueError("Reserva finalizada não pode ser cancelada.")
        if self.status != "active":
            raise ValueError("Apenas reservas ativas podem ser canceladas.")
        self.status = "canceled"

    def finalizar(self, hora_atual: str):
        if self.status != "active":
            raise ValueError("Apenas reservas ativas podem ser finalizadas.")
        agora = datetime.combine(self._parse_date(self.data), self._parse_time(hora_atual))
        _, fim = self._start_end_datetimes()
        if agora < fim:
            raise ValueError("A reserva só pode ser finalizada após o horário de término.")
        self.status = "finished"

    def duracao_em_horas(self) -> float:
        inicio, fim = self._start_end_datetimes()
        return (fim - inicio).total_seconds() / 3600

    def conflita_com(self, outra_reserva) -> bool:
        if self.data != outra_reserva.data:
            return False
        inicio_a, fim_a = self._start_end_datetimes()
        inicio_b = datetime.combine(self._parse_date(outra_reserva.data), self._parse_time(outra_reserva.hora_inicio))
        fim_b = datetime.combine(self._parse_date(outra_reserva.data), self._parse_time(outra_reserva.hora_fim))
        return inicio_a < fim_b and fim_a > inicio_b

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "sala_id": self.sala_id,
            "data": self.data,
            "hora_inicio": self.hora_inicio,
            "hora_fim": self.hora_fim,
            "status": self.status,
        }
