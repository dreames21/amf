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

    # start out assuming everything is zero
    sweeps = 0.0
    RPM = 0.0
    
    # keep going until one of these things are not zero
    # most of the time, this only runs once. It's only when parameters
    # hit an extreme that it runs more than once.
    while sweeps == 0.0 or RPM == 0.0:

      #                           1 minute    60 second   Y angstroms
      # angstroms_per_rotation = ---------- * --------- * -----------
      #                          X rotation   1 minute     1 second
      # where:
      #   X = target RPM
      #   Y = deposition rate in angstroms per second
      #
      angstroms_per_rotation = float(1.0 / target_RPM) * 60.0 * float(depositon_rate)
      
      
      
      # need to scale angstroms_per_rotation down to the percentage of the arc the
      # sweep will travel to get angstroms_per_sweep
      percent_of_arc = self.params['sweep_angle'] / 360.0
      angstroms_per_sweep = percent_of_arc * angstroms_per_rotation
      
      
      
      # raw_sweeps represents how many sweeps the platen has to make if it
      # didn't have to travel an integral number of times
      #
      #              T angstroms     1 sweep
      # raw_sweeps = ----------- * -----------
      #                  1         S angstroms
      # where:
      #   T = desired thickness
      #   S = angstroms per sweep
      #
      raw_sweeps = thickness * float(1.0 / angstroms_per_sweep)
      
      # from here just round to the nearest integer to get the actual number of sweeps
      sweeps = round(raw_sweeps)


      
      # RPM is calculated by the ratio between sweeps and raw_sweeps
      # if sweeps / raw_sweeps is greater than 1.0, it means the chamber is going to
      # therefore it needs to scale the RPM up. The opposite is true when the ratio is less than 1.0.
      #         sweeps
      # RPM = ---------- * target RPM
      #       raw_sweeps
      RPM = (float(sweeps) / float(raw_sweeps)) * float(target_RPM)



      # some heuristics for tweaking values for the next iteration
      if raw_sweeps <= 0.5:
        sweeps = 1.0
        RPM = target_RPM / raw_sweeps # check this
      if sweeps == 0.0 or RPM == 0.0:
        target_RPM += .5
    
    # throw out an error if the RPM is too high
    if RPM >= 5.0:
      msg = "WARNING: RPM exceeded 5.0 RPM. More info:\n"
      msg += "thickness\t" + str(thickness)
      msg += "\ntarget_RPM\t" + str(target_RPM)
      msg += "\ndepositon_rate\t" + str(depositon_rate)
      raise amf.utils.AMFError(msg)
    return sweeps, RPM


