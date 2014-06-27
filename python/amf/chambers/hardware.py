class axis(object):
  def __init__(self, index, name):
    self.index = index
    
    # what does it control
    self.name = name
    
    # steps to RPM CF
    self.conversion_factor = None
    
    # steps in rev
    self.steps_in_rev = None
    
    self.idle_RPM = 1.0
    
    self.accel_decel = 50000

  def angle_to_steps(self, angle):
    return int(angle * self.steps_in_rev / 360)

  # needs to be in mm
  def distance_to_steps(self, distance):
    return int(distance * self.steps_in_mm)

  def RPM_to_steps_per_sec(self, RPM):
    return RPM * self.conversion_factor
  
  def velocity_to_steps_per_sec(self, velocity):
    return velocity * self.conversion_factor
  
  def add_header_item(self, d):
    key_prefix = 'axis ' + str(self.index) + ' '
    properties = {
      'name' : self.name,
      'conversion_factor' : self.conversion_factor,
      'steps_in_rev': self.steps_in_rev,
      'accel_decel': self.accel_decel	  
    }
    for k, v in properties.iteritems():
      d[key_prefix + k] = str(v)
  
class shutter(object):
  def __init__(self, index):
    self.index = index

  def add_header_item(self, d):
    #key_prefix = 'shutter ' + str(self.index) + ' '
    #d[key_prefix + 'index'] = self.index
    return

class cathode(object):
  def __init__(self, index):
    self.name = ''
    self.index = index
    self.deposition_rate = None
    
  def add_header_item(self, d):
    if self.deposition_rate is None:
      return
    else:
      key_prefix = 'cathode ' + str(self.index) + ' '
      properties = {
        'name' : self.name,
        'deposition_rate' : self.deposition_rate
      }
      for k, v in properties.iteritems():
        d[key_prefix + k] = str(v)
