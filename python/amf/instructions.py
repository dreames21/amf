"""

Instructions

"""

import amf.utils
import amf.config

class instruction():
  def __init__(self, function, params=[]):
    self.function = function
    self.params = params

  def as_array(self):
    param_strings = []
    for param in self.params:
      param_strings.append(str(param))
    return [self.function] + param_strings

def move_angle(axis, angle, RPM=None):
  steps = axis.angle_to_steps(angle)
  if RPM is None:
    RPM = axis.idle_RPM
  velocity = axis.RPM_to_steps_per_sec(RPM)
  accel_decel = axis.accel_decel
  return instruction('move_angle', [axis.index, steps, velocity, accel_decel])

def shutter_control(shutter, open=True):
  if open:
    state = 'open'
  else:
    state = 'close'
  return instruction('shutter', [shutter.index, state])

def slave_sweep(axis, angle, RPM, start=True):
  steps = axis.angle_to_steps(angle)
  velocity = axis.RPM_to_steps_per_sec(RPM)
  accel_decel = axis.accel_decel
  if start:
    state = 'start'
  else:
    state = 'stop'
  return instruction('slave_sweep', [axis.index, state, steps, velocity, accel_decel])

def slave_rezero(axis):
  velocity = axis.RPM_to_steps_per_sec(axis.idle_RPM)
  accel_decel = axis.accel_decel
  return instruction('slave_rezero', [axis.index, velocity, accel_decel])

def sweep(axis, angle, RPM, times):
  steps = axis.angle_to_steps(angle)
  accel_decel = axis.accel_decel
  velocity = axis.RPM_to_steps_per_sec(RPM)
  return instruction('sweep', [axis.index, times, steps, velocity, accel_decel])

def check_pause():
  return instruction('check_pause')

def open_shutter(shutter):
  return shutter_control(shutter, True)

def close_shutter(shutter):
  return shutter_control(shutter, False)

def slave_start_sweep(axis, angle, RPM):
  return slave_sweep(axis, angle, RPM, True)

def slave_stop_sweep(axis, angle, RPM):
  return slave_sweep(axis, angle, RPM, False)

def log(message, timestamp=False):
  #print message
  fn = amf.config.dry_run_filename
  text = amf.utils.read_file(fn)
  text += message
  amf.utils.write_file(fn, text + '\n')
  return instruction('log', [message, 'true' if timestamp else 'false'])

def set(key, value):
  return instruction('set', [key, value])
