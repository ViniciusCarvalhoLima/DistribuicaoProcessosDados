import random

from sensores.Sensor_base import SensorBase
from shared.Constants import PORTA_SENSOR_AR


class SensorQualidadeAr(SensorBase):
    def __init__(self):
        super().__init__(
            tipo_sensor="AR",
            intervalo=5,
            porta_comando=PORTA_SENSOR_AR
        )

    def gerar_dados(self):
        co2 = random.randint(300, 700)
        covs = random.randint(0, 500)

        return {
            "CO2": f"{co2} ppm",
            "COVs": f"{covs} ppb",
            "Estado": "ATIVO" if self.ativo else "INATIVO"
        }


if __name__ == "__main__":
    sensor = SensorQualidadeAr()
    sensor.executar_base()