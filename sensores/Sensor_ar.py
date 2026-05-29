import random
import os
import time
import threading

from sensores.Sensor_base import SensorBase


class SensorQualidadeAr(SensorBase):
    def __init__(self):
        super().__init__(
            tipo_sensor="AR",
            intervalo=5
        )

    def gerar_dados(self):
        co2 = random.randint(300, 700)
        covs = random.randint(0, 500)

        return {
            "CO2": f"{co2} ppm",
            "COVs": f"{covs} ppb",
            "Estado": "ATIVO" if self.ativo else "INATIVO"
        }

    def ouvir_comandos(self):
        while True:
            comando = input(
                "\nComando (ligar/desligar/sair): "
            ).lower()

            if comando == "desligar":
                self.desligar()

            elif comando == "ligar":
                if not self.ativo:
                    self.ativo = True

                    threading.Thread(
                        target=self.iniciar,
                        daemon=True
                    ).start()

            elif comando == "sair":
                self.desligar()

                print(f"\n[{self.id_sensor}] Encerrando processo...\n")

                os._exit(0)

            else:
                print("\nComando inválido.")

    def executar(self):
        threading.Thread(
            target=self.ouvir_comandos,
            daemon=True
        ).start()

        threading.Thread(
            target=self.ouvir_descoberta,
            daemon=True
        ).start()

        threading.Thread(
            target=self.iniciar,
            daemon=True
        ).start()

        while True:
            time.sleep(1)


if __name__ == "__main__":
    sensor = SensorQualidadeAr()
    sensor.executar()