from amf.runs.abstract_run import *
from amf.instructions import *
import amf.utils

class linear_mode(abstract_run):
  def __init__(self):
    super(abstract_run, self).__init__()

    self.name = 'Linear Mode'

    self.control_sequence = [
      self.stage_offset_back,
      self.open_shutter,
      self.stage_sweep,
      self.close_shutter,
      self.stage_rezero,
      self.move_180
    ]

  def thickness_func(self, thickness, target_velocity, depositon_rate, pass_length):

    #~ thickness algorithm for linear stage:
    
    #~ target_velocity = desired linear stage velocity (mm/sec) 
    #~ depositon_rate = current rate as measured at the calibration velocity (angstoms/second)
    #~ thickness = desired thickness of deposition on the substrate (angstroms)
    #~ pass_length = length of the pass to go from one end of the substrate to the other (mm)
    
    #~ first need to scale the rate up or down depending on desired velocity and calibration velocity
    
    scaled_rate = float(self.chamber.linear_stage_calibration_velocity) / float(target_velocity) * depositon_rate
    
    #                    X mm       1 second
    # time_per_pass = ---------- * ---------
    #                      1         Y mm 
    # where:
    #   X = path length in mm
    #   Y = scaled rate
    #   C = 10 mm/sec stage velocity
    #
    time_per_pass = float(pass_length) / float(target_velocity)
    
    angstoms_per_pass = float(time_per_pass) * float(scaled_rate)
    
    raw_passes = float(thickness) / float(angstoms_per_pass)
    
    passes = round(raw_passes)
    
    velocity = float(passes) / float(raw_passes) * target_velocity
    
    return passes, velocity
    
    def offset_back(self, axis='master'):
      if axis == 'master':
        axis = self.chamber.master_axis()

        if self.circular_mode:
          angle = -self.dummy_offset
        else:
          angle = -1.0 * self.params['sweep_angle'] / 2.0
      elif axis == 'slave':
        axis = self.chamber.slave_axis()
        angle = -1.0 * self.params['slave_sweep_angle'] / 2.0
      i = []
      if True or angle != 0:
        i.append(amf.instructions.log('ofsetting ' + axis.name + ' back ' + str(angle) + ' degrees'))
        i.append(amf.instructions.move_angle(axis, angle))
      return i
