from amf.chambers.hardware import *
from amf.chambers.abstract_chamber import *

class r_and_d1(abstract_chamber):
  def __init__(self):
    super(r_and_d1, self).__init__()

    self.name = 'R&D1'

    platen = axis(3, 'platen')
    platen.idle_RPM = 3.0
    platen.conversion_factor = 4171.87
    platen.steps_in_rev = 250000
    platen.accel_decel = 500000
    self.platen_axis = platen.index

    mandrel = axis(4, 'mandrel')
    mandrel.idle_RPM = 3.0
    mandrel.conversion_factor = 417.448
    mandrel.steps_in_rev = 25000
    mandrel.accel_decel = 500000
    self.mandrel_axis = mandrel.index

    self.axes = {
      '4': mandrel,
      '3': platen
    }

    self.shutters = {
      '1': shutter(1),
      '2': shutter(2)
    }

    self.cathodes = {
      '1': cathode(1),
      '2': cathode(2)
    }
