from amf.runs.abstract_run import *
from amf.instructions import *
import sys

class mandrel_mode(abstract_run):
  def __init__(self):
    super(abstract_run, self).__init__()

    self.name = 'Mandrel Mode'

    self.control_sequence = [
      self.slave_offset_back,
      self.offset_back,
      self.slave_start_sweep,
      self.open_shutter,
      self.sweep,
      self.close_shutter,
      self.slave_stop_sweep,
      self.rezero,
      self.slave_rezero,
      self.slave_move_180
    ]

  def post_init(self):
    self.chamber.master_axis = self.chamber.mandrel
    self.chamber.slave_axis = self.chamber.platen
    if int(self.params['sweep_angle']) == 360:
      self.circular_mode = True
      self.dummy_offset = 4.0
    else:
      self.circular_mode = False

  def thickness_func(self, thickness, target_RPM, depositon_rate):
    
    # start out assuming sweeps and RPM is zero
    sweeps = 0.0
    RPM = 0.0

    # rate is in angstroms per rev or sweep if angle is less than 360
    while sweeps == 0.0 or RPM == 0.0:
      scaled_rate = depositon_rate / float(target_RPM)
      raw_sweeps = thickness / scaled_rate
      sweeps = round(raw_sweeps) # sweeps really represents revs
      RPM = (sweeps * target_RPM) / float(raw_sweeps)
      if raw_sweeps <= 0.5:
        sweeps = 1.0
        RPM = target_RPM / raw_sweeps # check this
      if sweeps == 0.0 or RPM == 0.0:
        target_RPM += .5

    if RPM >= 3.5:
      msg = "WARNING: RPM exceeded 3.5 RPM. More info:\n"
      msg += "thickness\t" + str(thickness)
      msg += "\ntarget_RPM\t" + str(target_RPM)
      msg += "\ndepositon_rate\t" + str(depositon_rate)
      raise amf.utils.AMFError(msg)
    return sweeps, RPM
