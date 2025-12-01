# blockchain.py
import hashlib
from datetime import datetime
import json
import os


class Bloque:
    def __init__(self, id, datos, prev_hash=""):
        self.id = id
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.datos = datos          # texto con info clave de la obra
        self.prev_hash = prev_hash
        self.hash_actual = self.calcular_hash()

    def calcular_hash(self):
        """
        Hash SHA-256 del bloque: H(ID || timestamp || datos || prev_hash)
        """
        contenido = f"{self.id}{self.timestamp}{self.datos}{self.prev_hash}"
        return hashlib.sha256(contenido.encode("utf-8")).hexdigest()

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "datos": self.datos,
            "prev_hash": self.prev_hash,
            "hash_actual": self.hash_actual
        }

    @staticmethod
    def from_dict(data):
        # reconstruir bloque desde dict
        bloque = Bloque(data["id"], data["datos"], data["prev_hash"])
        bloque.timestamp = data["timestamp"]
        bloque.hash_actual = data["hash_actual"]
        return bloque


class Blockchain:
    def __init__(self, ruta_archivo="blockchain.json"):
        self.ruta_archivo = ruta_archivo
        self.cadena = []
        self.cargar_cadena()
        if not self.cadena:
            # Crear bloque génesis si no existe nada
            genesis = Bloque(1, "Bloque génesis - Inicio de la cadena", "0")
            self.cadena.append(genesis)
            self.guardar_cadena()

    # ---------- Persistencia ----------

    def guardar_cadena(self):
        with open(self.ruta_archivo, "w", encoding="utf-8") as f:
            json.dump([b.to_dict() for b in self.cadena], f, ensure_ascii=False, indent=4)

    def cargar_cadena(self):
        if not os.path.exists(self.ruta_archivo):
            self.cadena = []
            return
        with open(self.ruta_archivo, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.cadena = [Bloque.from_dict(b) for b in data]

    # ---------- Operaciones ----------
    def agregar_bloque(self, datos):
        """
        datos: string con info relevante de la obra (autor, título, hash_archivo, etc.)
        Devuelve el nuevo bloque.
        """
        self.cargar_cadena()
        prev_hash = self.cadena[-1].hash_actual if self.cadena else "0"
        nuevo_id = self.cadena[-1].id + 1 if self.cadena else 1
        nuevo_bloque = Bloque(nuevo_id, datos, prev_hash)
        self.cadena.append(nuevo_bloque)
        self.guardar_cadena()
        return nuevo_bloque

    def mostrar_cadena(self):
        return [b.to_dict() for b in self.cadena]

    def obtener_bloque_por_id(self, id_bloque):
        for b in self.cadena:
            if b.id == id_bloque:
                return b
        return None

    def verificar_cadena(self):
        """
        Recorre toda la cadena:
        - Recalcula hash de cada bloque y lo compara con hash_actual.
        - Verifica prev_hash vs hash_actual anterior.
        Devuelve: (es_valida(bool), lista_errores)
        """
        self.cargar_cadena()
        errores = []

        for i, bloque in enumerate(self.cadena):
            hash_recalc = bloque.calcular_hash()
            if hash_recalc != bloque.hash_actual:
                errores.append(
                    f"Bloque {bloque.id}: hash_actual NO coincide con el hash recalculado."
                )
            if i > 0:
                anterior = self.cadena[i-1]
                if bloque.prev_hash != anterior.hash_actual:
                    errores.append(
                        f"Bloque {bloque.id}: prev_hash NO coincide con hash_actual del bloque anterior ({anterior.id})."
                    )

        return len(errores) == 0, errores

    def simular_ataque_modificando_bloque(self, id_bloque):
        """
        Modifica los datos de un bloque sin actualizar hashes, para romper la cadena.
        """
        self.cargar_cadena()
        bloque = self.obtener_bloque_por_id(id_bloque)
        if not bloque:
            return False
        bloque.datos = bloque.datos + " [DATOS ALTERADOS]"
        # No recalculamos hash_actual -> la cadena queda corrupta
        self.guardar_cadena()
        return True
