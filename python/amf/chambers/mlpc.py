from amf.chambers.hardware import *
from amf.chambers.abstract_chamber import *

class mlpc(abstract_chamber):
  def __init__(self):
    super(mlpc, self).__init__()

    self.name = 'mlpc'

    platen = axis(1, 'platen')
    platen.idle_RPM = 3.0
    platen.conversion_factor = 4171.87
    platen.steps_in_rev = 250000
    platen.accel_decel = 500000
    self.platen_axis = platen.index

    # 2.64 Volts DC @ 5.5 Amps
    # 200 steps / rev on motor
    # 10:1 reduction gearing on transmission

    self.axes = {
      '1': platen
    }

    self.shutters = {
      '1': shutter(1),
      '2': shutter(2)
    }

    self.cathodes = {
      '1': cathode(1),
      '2': cathode(2)
    }
