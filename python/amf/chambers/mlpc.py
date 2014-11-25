from amf.chambers.hardware import *
from amf.chambers.abstract_chamber import *

class mlpc(abstract_chamber):
  def __init__(self):
    super(mlpc, self).__init__()

    self.name = 'mlpc'

    # specs on motor casing:
    #   2.64 Volts DC @ 5.5 Amps
    #   200 steps / rev on motor

    # 7:1 reduction gearing on transmission
    # 125000 steps / motor rev with micro stepping
    # ...means 875000 steps for one revolution of platen

    platen = axis(1, 'platen')
    platen.idle_RPM = 2.0

    platen.conversion_factor = 14612.5
    platen.steps_in_rev = 875000
    platen.accel_decel = 500000

    self.platen_axis = platen.index
    
    self.mandrel_axis = 2
    
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
