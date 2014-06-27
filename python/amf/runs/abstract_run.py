"""

Run types module

Definitions for the types of runs that chambers can do

"""

import amf.instructions
import amf.utils
import amf.config

class abstract_run(object):
  def __init___(self):
    self.name = ''
    self.chamber = None
    self.control_sequence = []
    self.run = []
    self.run_data = {}
    self.params = {}
    self.circular_mode = False

  def post_init(self):
    self.circular_mode = False
    pass

  def init_parameters(self, params):
    self.params = params
    self.run_data = {}

    # runtime variables
    self.current_cathode_index = str(params['initial_cathode'])
    self.this_bilayer = []
    self.current_N = 0
    self.bilayer_index = 0

    for cathode in params['cathodes']:
      this_cathode = params[cathode]
      index = int(cathode.split(' ')[-1])

      self.chamber.cathode(index).name = cathode

      thickness_RPM = []
      if self.params['generate_files']:
        for _ in range(int(self.params['N'])):
          thickness = float(this_cathode['thickness'])
          RPM = float(this_cathode['RPM'])
          thickness_RPM.append((thickness, RPM))
      else:
        lines = amf.utils.read_file(this_cathode['file']).split('\n')
        for line in lines:
          if line == '':
            continue
          thickness = float(line)
          RPM = float(this_cathode['RPM'])
          thickness_RPM.append((thickness, RPM))

      self.chamber.cathode(index).deposition_rate = this_cathode['rate']

      self.run_data[cathode] = []
      j = 0
      for thickness, RPM in thickness_RPM:
        j += 1
        print cathode, j
        if params['run_mode'] == 'linear_mode':
          
          # rpm here is actually a linear velocity -- we just reuse the input
          layer_data = self.thickness_func(thickness, RPM, this_cathode['rate'], params['linear_stage_pass_length'])
        else:
          layer_data = self.thickness_func(thickness, RPM, this_cathode['rate'])
        self.run_data[cathode].append(layer_data)
    self.post_init()

  def generate(self):
    self.run = []
    self.sequence_number = 0
    self.gen_header()

    layer_indexes = range(2*self.params['N'])
    if self.params['single_cathode']:
      layer_indexes = [0]

    for i in layer_indexes:
      self.this_bilayer = []
      self.pre_bilayer()
      for instruction_container in self.control_sequence:
        these_instructions = instruction_container()
        for instruction in these_instructions:
          if instruction is not None:
            self.add_instruction(instruction)
      self.post_bilayer()
      self.run.append(self.this_bilayer)
    print "done run"

  def add_instruction(self, instruction):
    self.this_bilayer.append([str(self.sequence_number)] + instruction.as_array())
    self.sequence_number += 1

  def gen_header(self):
    header = {}

    for k, v in self.chamber.header_items().iteritems():
      header[k] = v

    header['run_name'] = self.params['name']
    header['N'] = self.params['N']
    header['current_N'] = 0
    header['current_bilayer'] = 0
    header['current_sweep_iterations'] = 0

    header_list = []
    header_list.append(['-1'] + amf.instructions.log('begin header for ' + self.params['name'], True).as_array())
    header_label_list = []
    for k, v, in header.iteritems():
      header_list.append(['-1'] + amf.instructions.set(k, v).as_array())
      header_label_list.append(str(k) + ' = ' + str(v))
    
    for label in sorted(header_label_list):
      header_list.append(['-1'] + amf.instructions.log(label).as_array())
    self.run.append(header_list)

  def pre_bilayer(self):
    if self.bilayer_index == 0:
      self.add_instruction(amf.instructions.log(''))
      self.add_instruction(amf.instructions.log('starting layer ' + str(self.current_N + 1)))
      self.add_instruction(amf.instructions.log('starting bilayer 1'))
    else:
      self.add_instruction(amf.instructions.log('starting bilayer 2'))
      self.bilayer_index = 1
    self.add_instruction(amf.instructions.set('current_N', self.current_N + 1))
    self.add_instruction(amf.instructions.set('current_bilayer', self.bilayer_index + 1))
    data = self.run_data['cathode ' + self.current_cathode_index][self.current_N]
    self.current_sweep_iterations, self.current_sweep_RPM = data
    self.add_instruction(amf.instructions.set('current_sweep_iterations', self.current_sweep_iterations))

  def post_bilayer(self):
    self.current_cathode_index = str((int(self.current_cathode_index) % self.chamber.num_cathodes()) + 1)
    if self.bilayer_index == 0:
      self.bilayer_index = 1
    else:
      self.bilayer_index = 0
      self.current_N += 1

  def as_csv(self):
    s = ''
    for bilayer in self.run:
      for instruction in bilayer:
        try:
          s += amf.config.delimiter.join(instruction) + '\n'
        except:
          print instruction
    return s

  def offset_back(self, axis='master'):
    if axis == 'master':
      axis = self.chamber.master_axis()

      if self.circular_mode:
        angle = -self.dummy_offset
      else:
        angle = -self.params['sweep_angle'] / 2.0
    elif axis == 'slave':
      axis = self.chamber.slave_axis()
      angle = -self.params['slave_sweep_angle'] / 2.0
    i = []
    if True or angle != 0:
      i.append(amf.instructions.log('ofsetting ' + axis.name + ' back ' + str(angle) + ' degrees'))
      i.append(amf.instructions.move_angle(axis, angle))
    return i

  def sweep(self):
    RPM = self.current_sweep_RPM
    times = self.current_sweep_iterations
    axis = self.chamber.master_axis()
    angle = self.params['sweep_angle']
    i = []
    if True or (angle != 0 and times != 0 and RPM != 0):
      if not self.circular_mode:
        i.append(amf.instructions.log('sweeping ' + axis.name + ' back and forth ' + str(times) + ' times at ' + str(RPM) + ' RPM'))
        i.append(amf.instructions.sweep(axis, angle, RPM, times))
      else:
        i.append(amf.instructions.log('rotating ' + axis.name + ' ' + str(times) + ' times at ' + str(RPM) + ' RPM'))
        for j in range(int(times)):
          i.append(amf.instructions.set('current_sweep', j + 1))
          i.append(amf.instructions.move_angle(axis, angle, RPM))
    return i

  def rezero(self, axis='master'):
    if axis == 'master':
      axis = self.chamber.master_axis()
      angle = self.params['sweep_angle']
    elif axis == 'slave':
      axis = self.chamber.slave_axis()
      angle = self.params['slave_sweep_angle']
    if self.circular_mode:
      angle = self.dummy_offset
    else:
      times = int(self.current_sweep_iterations)
      if times % 2 == 0:
        direction = 1.0
      else:
        direction = -1.0
      angle = direction * angle / 2.0
    i = []
    if True or angle != 0:
      i.append(amf.instructions.log('rezeroing ' + axis.name + ' by moving ' + str(angle) + ' degrees'))
      i.append(amf.instructions.move_angle(axis, angle))
    return i
  
  def move_180(self, axis='master'):
    if self.params['single_cathode']:
      return []
    if axis == 'master':
      axis = self.chamber.master_axis()
    elif axis == 'slave':
      axis = self.chamber.slave_axis()
    if self.params['initial_cathode'] == 2:
      if self.bilayer_index == 0:
        direction = 1.0
      else:
        direction = -1.0
    else:
      if self.bilayer_index == 0:
        direction = -1.0
      else:
        direction = 1.0
    angle = direction * 180.0
    i = []
    i.append(amf.instructions.check_pause())
    i.append(amf.instructions.log('moving ' + axis.name + ' ' + str(angle) + ' degrees'))
    i.append(amf.instructions.move_angle(axis, angle))
    i.append(amf.instructions.check_pause())
    return i

  def open_shutter(self):
    i = []
    shutter = self.chamber.shutter(self.current_cathode_index)
    i.append(amf.instructions.log('opening shutter ' + self.current_cathode_index, True))
    i.append(amf.instructions.open_shutter(shutter))
    return i

  def close_shutter(self):
    i = []
    shutter = self.chamber.shutter(self.current_cathode_index)
    i.append(amf.instructions.log('closing shutter ' + self.current_cathode_index, True))
    i.append(amf.instructions.close_shutter(shutter))
    return i

  def slave_start_sweep(self):
    axis = self.chamber.slave_axis()
    angle = self.params['slave_sweep_angle']
    RPM = self.params['slave_RPM']
    
    i = []
    if True or (angle != 0 and RPM != 0):
      i.append(amf.instructions.log('sweeping slave axis ' + axis.name + ' at ' + str(angle) + ' angle at ' + str(RPM) + ' RPM'))
      i.append(amf.instructions.slave_start_sweep(axis, angle, RPM))
    return i

  def slave_stop_sweep(self):
    axis = self.chamber.slave_axis()
    angle = self.params['slave_sweep_angle']
    RPM = self.params['slave_RPM']
    i = []
    if True or (angle != 0 and RPM != 0):
      i.append(amf.instructions.log('stopping slave sweep for ' + axis.name))
      i.append(amf.instructions.slave_stop_sweep(axis, angle, RPM))
    return i

  def slave_rezero(self):
    i = []
    axis = self.chamber.slave_axis()
    i.append(amf.instructions.log('rezero slave axis ' + axis.name))
    i.append(amf.instructions.slave_rezero(axis))
    return i

  def slave_move_180(self):
    return self.move_180('slave')

  def slave_offset_back(self):
    return self.offset_back('slave')

  def stage_offset_back(self):
    axis = self.chamber.linear_stage()
    distance = -self.params['linear_stage_pass_length'] / 2.0
    i = []
    i.append(amf.instructions.log('ofsetting ' + axis.name + ' back ' + str(distance) + ' mm'))
    i.append(amf.instructions.move_linear_stage(axis, distance))
    return i

  def stage_sweep(self):
    # this is actually velocity, not RPM but need to take it from RPM
    velocity = self.current_sweep_RPM
    times = self.current_sweep_iterations
    axis = self.chamber.linear_stage()
    distance = self.params['linear_stage_pass_length']
    i = []
    if True or (angle != 0 and times != 0 and velocity != 0):
      i.append(amf.instructions.log('sweeping ' + axis.name + ' ' + str(times) + ' times at ' + str(velocity) + ' mm/sec'))
      i.append(amf.instructions.linear_sweep(axis, distance, velocity, times))
    return i

  def stage_rezero(self):
    axis = self.chamber.linear_stage()
    distance = self.params['linear_stage_pass_length']
    times = int(self.current_sweep_iterations)
    if times % 2 == 0:
      direction = 1.0
    else:
      direction = -1.0
    distance = direction * distance / 2.0
    i = []
    if True or angle != 0:
      i.append(amf.instructions.log('rezeroing ' + axis.name + ' by moving ' + str(distance) + ' degrees'))
      i.append(amf.instructions.move_linear_stage(axis, distance))
    return i
