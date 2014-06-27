"""

Top level generation module

"""

import amf.utils
import amf.parameters
import amf.config
#import amf.webserver.server

import os
import traceback

# needed for py2exe
import amf.chambers
import amf.runs

def get_instance(root, item_name):
  module = __import__(root + '.' + item_name, fromlist=[root])
  return getattr(module, item_name)()

def get_instances(root, item_names):
  l = []
  for name in item_names:
    l.append(get_instance(root, name))
  return l

def names(root, items):
  d = {}
  item_instances = get_instances(root, items)
  for item, instance in zip(items, item_instances):
    d[instance.name] = instance
    d[item] = instance
  return d

def get_chamber(name):
  chambers = names('amf.chambers', amf.config.chambers)
  try:
    return chambers[name]
  except:
    return None

def get_run_mode(mode):
  run_modes = names('amf.runs', amf.config.runs)
  try:
    return run_modes[mode]
  except:
    return None

def generate(p, run, chamber):
  try:
    params = amf.parameters.load_params(p['name'])

    amf.config.dry_run_filename = os.path.join(amf.config.data_dir, p['name'], 'dry_run.txt')
    amf.utils.write_file(amf.config.dry_run_filename, '')

    run.chamber = chamber
    run.init_parameters(params)
    run.generate()
    instructions = run.as_csv()

    path = amf.config.data_dir + '/' + params['name']
    amf.utils.write_file(path + '/instructions.csv', instructions)

    msg = 'Instructions have been generated for LabVIEW in ' + path + '.\n'
    msg += 'Open this file up with LabVIEW.\nHere is the Logfile.'

    last_path = os.path.join(amf.config.data_dir, amf.config.last_generated_filename)
    amf.utils.write_file(last_path, params['name'])
    return True
  except:
    return traceback.format_exc()
