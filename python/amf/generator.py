"""

Top level generation module

"""

import amf.utils
import amf.parameters
import amf.config
import amf.gui
#import amf.webserver.server

import os
import json
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

def setup_chamber():
  chambers = names('amf.chambers', amf.config.chambers)
  this_chamber_name = amf.gui.gui_choice('Please choose a chamber', chambers.keys())
  if this_chamber_name == False:
    return False
  else:
    this_chamber = chambers[this_chamber_name]
    return this_chamber

def setup_run():
  run_modes = names('amf.runs', amf.config.runs)
  this_run_name = amf.gui.gui_choice('Please choose a run mode', run_modes.keys())
  if this_run_name == False:
    return False
  else:
    this_run = run_modes[this_run_name]
    return this_run

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

def setup():
  runs = os.listdir(amf.config.data_dir)
  runs.append('NEW')
  msg = 'Please choose a run to generate or choose \'NEW\' to make a new one.'
  run_params = amf.gui.gui_choice(msg, runs)
  if run_params == False:
    return False
  elif run_params == 'NEW':
    run_params = create_new_params()['name']
  params = amf.parameters.load_params(run_params)

  chambers = names('amf.chambers', amf.config.chambers)
  try:
    chamber = chambers[params['chamber']]
  except:
    chamber = setup_chamber()

  run_modes = names('amf.runs', amf.config.runs)
  try:
    run = run_modes[params['run_mode']]
  except:
    run = setup_run()
  return chamber, run, params

def create_new_params():
  params = amf.parameters.build_params()
  amf.parameters.save_params(params)
  return params


def generate(p, run, chamber):
  try:
    params = amf.parameters.load_params(p['name'])

    amf.config.dry_run_filename = amf.config.data_dir + '/' + p['name'] + '/dry_run.txt'
    amf.utils.write_file(amf.config.dry_run_filename, '')

    run.chamber = chamber
    run.init_parameters(params)
    run.generate()
    instructions = run.as_csv()

    path = amf.config.data_dir + '/' + params['name']
    amf.utils.write_file(path + '/instructions.csv', instructions)

    msg = 'Instructions have been generated for LabVIEW in ' + path + '.\n'
    msg += 'Open this file up with LabVIEW.\nHere is the Logfile.'

    last_path = amf.config.data_dir + '/' + amf.config.last_generated_filename
    amf.utils.write_file(last_path, params['name'])
    return True
  except:
    return traceback.format_exc()

def welcome():
  msg = amf.config.welcome
  welcome = amf.gui.gui_continue(msg)

def confirm(chamber, run, param):
  msg = 'You are about to do a '
  msg += run.name + ' run on chamber ' + chamber.name + '\n\n'
  msg += 'Run Parameters:\n'
  msg += json.dumps(param, sort_keys=True, indent=4) + '\n'
  return amf.gui.gui_yn(msg)

def _main():
  amf.webserver.server.run_server()

def main():
  this_chamber = None
  this_run = None
  run_param = None

  step_index = 0
  res = True

  while True:
    if step_index <= 0:
      welcome()
      res = True
    elif step_index == 1:
      this_chamber, this_run, run_param = setup()
      amf.config.dry_run_filename = amf.config.data_dir + '/' + run_param['name'] + '/dry_run.txt'
      amf.utils.write_file(amf.config.dry_run_filename, '')
      res = run_param
    elif step_index == 2:
      res = confirm(this_chamber, this_run, run_param)
    elif step_index == 3:
      generate(this_chamber, this_run, run_param)
    else:
      break
    if res == False:
      step_index -= 1
    else:
      step_index += 1

if __name__ == '__main__':
  main()
