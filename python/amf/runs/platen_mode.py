from amf.runs.abstract_run import *
from amf.instructions import *
import amf.utils

class platen_mode(abstract_run):
  def __init__(self):
    super(abstract_run, self).__init__()
    
    self.name = 'Platen Mode'
    
    self.control_sequence = [
      self.offset_back,
      self.open_shutter,
      self.sweep,
      self.close_shutter,
      self.rezero,
      self.move_180
    ]

  def thickness_func(self, thickness, target_RPM, depositon_rate):
    sweeps = 0.0
    RPM = 0.0
    while sweeps == 0.0 or RPM == 0.0:
      percent_of_arc = self.params['sweep_angle'] / 360.0
      c = percent_of_arc * (60.0 / target_RPM) * float(depositon_rate)
      raw_sweeps = thickness / float(c)
      sweeps = round(raw_sweeps)
      RPM = (sweeps * target_RPM) / float(raw_sweeps)
      if raw_sweeps <= 0.5:
        sweeps = 1.0
        RPM = target_RPM / raw_sweeps # check this
      if sweeps == 0.0 or RPM == 0.0:
        target_RPM += .5
      #print thickness, target_RPM, depositon_rate, '\t\t', sweeps, RPM
      #raw_input()
    if RPM >= 5.0:
      msg = "WARNING: RPM exceeded 5.0 RPM. More info:\n"
      msg += "thickness\t" + str(thickness)
      msg += "\ntarget_RPM\t" + str(target_RPM)
      msg += "\ndepositon_rate\t" + str(depositon_rate)
      raise amf.utils.AMFError(msg)
    return sweeps, RPM
