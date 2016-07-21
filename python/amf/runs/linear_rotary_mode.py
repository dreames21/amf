from amf.runs.abstract_run import *
from amf.instructions import *
import amf.utils

class linear_mode(abstract_run):
  def __init__(self):
    super(abstract_run, self).__init__()

    self.name = 'Linear-Rotary Mode'

    self.control_sequence = [
      self.stage_offset_back,
      self.open_shutter,
      self.stage_sweep,
      self.close_shutter,
      self.stage_rezero,
      self.slave_move_180  #slave is rotary stage
    ]

  def thickness_func(self, thickness, target_velocity, depositon_rate, pass_length):

    # thickness algorithm for linear stage:
    
    # thickness = desired thickness of deposition on the substrate (angstroms)
    # target_velocity = desired linear stage velocity (mm/sec) 
    # depositon_rate = current rate as measured at the calibration velocity (angstoms/second)
    # pass_length = length of the pass to go from one end of the substrate to the other (mm)

    angstoms_per_pass = float(depositon_rate) / float(target_velocity) * float(pass_length)

    raw_passes = float(thickness) / float(angstoms_per_pass)
    
    passes = round(raw_passes)
    
    velocity = float(passes) / float(raw_passes) * target_velocity
    
    return passes, velocity
