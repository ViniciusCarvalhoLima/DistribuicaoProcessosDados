import random
import sys
from sensores.Sensor_base import SensorBase
from shared.Constants import PORTA_SENSOR_AR


class SensorQualidadeAr(SensorBase):
    def __init__(self, porta=PORTA_SENSOR_AR, id_sensor=None):
        super().__init__(
            tipo_sensor="AR",
            intervalo=5,
            porta_comando=porta
        )
        if id_sensor:
            self.id_sensor = id_sensor

    def gerar_dados(self):
        co2 = random.randint(300, 700)
        covs = random.randint(0, 500)
        return {
            "CO2": f"{co2} ppm",
            "COVs": f"{covs} ppb",
            "Estado": "ATIVO" if self.ativo else "INATIVO"
        }


if __name__ == "__main__":
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else PORTA_SENSOR_AR
    id_sensor = sys.argv[2] if len(sys.argv) > 2 else None
    sensor = SensorQualidadeAr(porta=porta, id_sensor=id_sensor)
    sensor.executar_base()