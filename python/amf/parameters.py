import amf.utils
import amf.config

import os

def build_params():
  params = {}
  params['name'] = amf.utils.q('What do you want to call this run? \n')
  params['N'] = amf.utils.q('How many layers are you doing? (N=??)\n', int)
  if amf.utils.y_or_n('Are you using the mandrel for this run? \n'):
    params['slave_sweep_angle'] = amf.utils.q('What is the sweep angle for the platen? \n', float)
    params['slave_RPM'] = amf.utils.q('What is the sweep RPM for the platen? \n', float)
    params['sweep_angle'] = amf.utils.q('What is the mandrel sweep angle? \n', float)
  else:
    params['sweep_angle'] = amf.utils.q('What is the platen sweep angle? \n', float)

  params['generate_files'] = amf.utils.y_or_n('Do you want to generate thickness files? \n')
  params['single_cathode'] = amf.utils.y_or_n('Is this a single layer run? \n')
  params['initial_cathode'] = amf.utils.q('What cathode is the run starting on? \n', int)
  
  cathodes = []
  if params['single_cathode']:
    cathodes = ['cathode ' + str(params['initial_cathode'])]
  else:
    other_cathode = '0'
    if params['initial_cathode'] == 1:
      other_cathode = 'cathode 2'
    else:
      other_cathode = 'cathode 1'
    cathodes = ['cathode ' + str(params['initial_cathode']), other_cathode]
  
  params['cathodes'] = cathodes
  
  for cathode in cathodes:
    this_cathode = {}
    
    this_cathode['name'] = amf.utils.q('Enter a descriptive name for ' + cathode + '. \n')

    if params['generate_files']:
      this_cathode['thickness'] = amf.utils.q('What is the thickness for ' + cathode + '? (angstroms)\n', float)
      this_cathode['RPM'] = amf.utils.q('What is the target RPM for ' + cathode + '? \n', float)
    else:
      this_cathode['file'] = choose_file(params, this_cathode['name'])
      this_cathode['RPM'] = amf.utils.q('What is the target RPM for ' + cathode + '? \n', float)
    this_cathode['rate'] = amf.utils.q('What is the rate for ' + cathode + '? \n', float)
    params[cathode] = this_cathode
    
  return params

def save_params(params):
  folder = os.path.join(amf.config.data_dir, params['name'])
  if not os.path.exists(folder):
    os.makedirs(folder)
  path = os.path.join(folder, 'params.json')
  amf.utils.dict_to_file(params, path)

def load_params(name):
  path = os.path.join(amf.config.data_dir, name)
  path = os.path.join(path, 'params.json')
  return amf.utils.file_to_dict(path)
