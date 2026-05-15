class MemoryDB:
    def __init__(self):
        self.usuarios = {}
        self.salas = {}
        self.reservas = {}
        self.next_usuario_id = 1
        self.next_sala_id = 1
        self.next_reserva_id = 1

    def reset(self):
        self.__init__()


db = MemoryDB()
