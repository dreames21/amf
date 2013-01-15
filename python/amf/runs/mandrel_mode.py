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
    sweeps = 0.0
    RPM = 0.0
    if self.params['sweep_angle'] == 360:
      # rate is in angstroms per rev
      scaled_rate = depositon_rate / float(target_RPM)
      raw_revs = thickness / scaled_rate
      sweeps = float(int(raw_revs)) # really revs
      RPM = (sweeps * target_RPM) / float(raw_revs)
    else:
      # rate is in angstroms per sec
      while sweeps == 0.0 or RPM == 0.0:
        percent_of_arc = self.params['sweep_angle'] / 360.0
        c = percent_of_arc * (60.0 / target_RPM) * float(depositon_rate)
        raw_sweeps = thickness / float(c)
        sweeps = float(int(raw_sweeps))
        RPM = (sweeps * target_RPM) / float(raw_sweeps)
        if raw_sweeps <= 0.5:
          sweeps = 1.0
          RPM = target_RPM / raw_sweeps # check this
        if sweeps == 0.0 or RPM == 0.0:
          target_RPM += .5
        # print thickness, target_RPM, depositon_rate, '\t\t', sweeps, RPM
        # raw_input()
    if RPM >= 5.0:
      msg = "WARNING: RPM exceeded 5.0 RPM. More info:\n"
      msg += "thickness\t" + str(thickness)
      msg += "\ntarget_RPM\t" + str(target_RPM)
      msg += "\ndepositon_rate\t" + str(depositon_rate)
      raise amf.utils.AMFError(msg)
    return sweeps, RPM
