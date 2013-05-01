from amf.chambers.hardware import *
from amf.chambers.abstract_chamber import *

class r_and_d2(abstract_chamber):
  def __init__(self):
    super(r_and_d2, self).__init__()

    self.name = 'R&D2'

    platen = axis(1, 'platen')
    platen.idle_RPM = 3.0
    platen.conversion_factor = 6897.92
    platen.steps_in_rev = 412500
    platen.accel_decel = 500000
    self.platen_axis = platen.index

    rotary_stage = axis(2, 'rotary stage')
    rotary_stage.idle_RPM = 3.0
    rotary_stage.conversion_factor = 600.521
    rotary_stage.steps_in_rev = 36000
    rotary_stage.accel_decel = 50000
    self.mandrel_axis = rotary_stage.index

    # total travel = 8 inches * 25.4 mm / inch = 203.2 mm
    # 53304 steps / 203.2 mm = 262.322834646 steps / mm

    linear_stage = axis(3, 'linear stage')
    linear_stage.conversion_factor = 262.322834646 # steps per mm
    linear_stage.idle_velocity = 10.0 * linear_stage.conversion_factor
    linear_stage.steps_in_mm = linear_stage.steps_in_rev = 53304
    linear_stage.accel_decel = 50000
    self.linear_stage_axis = linear_stage.index
    self.linear_stage_calibration_velocity = 10.0 # mm/sec
    
    #~ set linear stage as the master axis
    self.master_axis = self.linear_stage

    self.axes = {
      '1': platen,
      '2': rotary_stage,
      '3': linear_stage
    }

    self.shutters = {
      '1': shutter(1),
      '2': shutter(2),
    }

    self.cathodes = {
      '1': cathode(1),
      '2': cathode(2),
    }

  def linear_stage(self):
    return self.axes[str(self.linear_stage_axis)]
