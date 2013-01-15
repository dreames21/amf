import sys, os
#sys.stdout = sys.stderr # mod_wsgi flips out if this isn't here
#abspath = os.path.dirname(__file__)
#sys.path.append(abspath)
#os.chdir(abspath)

import amf.config
import amf.generator
import time
import web
import shutil

import pprint
pp = pprint.PrettyPrinter(indent=4)
import subprocess

urls = (
  '/', 'index',
  '/new', 'new',
  '/browse', 'browse',
  '/start_lv', 'start_lv',
  '/editcreate', 'editcreate',
  '/(static)/(.*)', 'static',
  '/del/(\d+)', 'delete'
)

render = web.template.render('templates', base='base')

class index:
  def GET(self):
    return render.index()

class start_lv:
  def GET(self):
    cmd = ["C:\Program Files\National Instruments\LabVIEW 8.6\LabVIEW.exe", "..\dashboard.vi"]
    #cmd = ["\"C:\\Program Files\\National Instruments\\LabVIEW 2012\\LabVIEW.exe\""]
    print cmd
    subprocess.Popen(cmd, shell=False, stdin=None, stdout=None, stderr=None, close_fds=True)
    return render.index('Labview Started!')
  def POST(self):
    return self.GET()

class new:
  def GET(self):
    web.header("Content-Type","text/html; charset=utf-8")
    return render.form("New Run")

class editcreate:
  def GET(self):
    web.header("Content-Type","text/html; charset=utf-8")
    i = web.input(c1_file={}, c2_file={})
    #print web.webapi.rawinput().get("c1_file").filename
    #print web.webapi.rawinput().get("c1_file").value
    try:
      print i['c1_file'].file
    except:
      i['c1_file'] = None
    try:
      print i['c2_file'].file
    except:
      i['c2_file'] = None

    global pp
    pp.pprint(dict(i))
    if i == {}:
      return render.form("New Run")
    else:
      #return render.form("New Run")
      p = {}
      errors = []

      def map_input(root_input, errmsg='', dest=None, _type=str):
        if dest == None:
          dest = root_input
        if i[root_input] == '':
          errors.append(' '.join(root_input.split('_')) + ' can\'t be blank!')
          return
        else:
          try:
            p[dest] = _type(i[root_input].strip())
          except:
            if errmsg == '':
              errmsg = 'Input ' + root_input + ' is invalid, can\'t be converted into ' + str(_type)
            p[dest] = i[root_input].strip()
            errors.append(errmsg)

      def map_input2(thing, thing_name, errmsg='', _type=str):
        thing = thing.strip()
        if i[thing] == '':
          errors.append(thing_name + ' can\'t be blank!')
          return ''
        else:
          try:
            ret = _type(i[thing])
          except:
            if errmsg == '':
              errmsg = '"' + i[thing] + '"' + ' is not valid for ' + thing_name
            errors.append(errmsg)
            ret = i[thing]
          return ret

      map_input('run_name', dest='name')
      map_input('chamber')
      map_input('run_mode')

      chamber = amf.generator.get_chamber(i['chamber'])
      if chamber == None:
        errors.append('The selected vacuum chamber could not be found')

      run = amf.generator.get_run_mode(i['run_mode'])
      if run == None:
        errors.append('The selected run mode could not be found')

      msg = '"' + i['N'] + '" is not a valid integer value for N'
      map_input('N', errmsg=msg, _type=int)

      if i['mandrel_use'] == "Yes":

        msg = '"' + i['slave_sweep_angle'] + '" is not a valid float value for platen sweep angle'
        map_input('slave_sweep_angle', errmsg=msg, _type=float)

        msg = '"' + i['slave_RPM'] + '" is not a valid float value for platen RPM'
        map_input('slave_RPM', errmsg=msg, _type=float)

        msg = '"' + i['sweep_angle'] + '" is not a valid float value for mandrel sweep angle'
        map_input('sweep_angle', errmsg=msg, _type=float)
      else:
        msg = '"' + i['sweep_angle'] + '" is not a valid float value for platen sweep angle'
        map_input('sweep_angle', errmsg=msg, _type=float)

      p['generate_files'] = i['generate_files'] == 'Yes'
      p['single_cathode'] = i['single_cathode'] == 'Yes'

      msg = '"' + i['initial_cathode'] + '" is not a valid integer value for initial cathode'
      map_input('initial_cathode', errmsg=msg, _type=int)

      cathodes = []
      prefixes = []
      if p['single_cathode']:
        first_cathode_index = str(p['initial_cathode'])
        cathodes = ['cathode ' + first_cathode_index]
        prefixes = ['c' + first_cathode_index + '_']
      else:
        other_cathode = ''
        if p['initial_cathode'] == 1:
          other_cathode = 'cathode 2'
          other_prefix = 'c2_'
        else:
          other_cathode = 'cathode 1'
          other_prefix = 'c1_'
        cathodes = ['cathode ' + str(p['initial_cathode']), other_cathode]
        prefixes = ['c' + str(p['initial_cathode']) + '_', other_prefix]

      p['cathodes'] = cathodes

      for prefix, cathode in zip(prefixes, cathodes):
        this_cathode = {}
        this_cathode['name'] = map_input2(prefix + 'name', cathode + ' name')
        this_cathode['RPM'] = map_input2(prefix + 'RPM', cathode + ' RPM', _type=float)
        this_cathode['rate'] = map_input2(prefix + 'rate', cathode + ' rate', _type=float)
        if p['generate_files']:
          this_cathode['thickness'] = map_input2(prefix + 'thickness', cathode + ' thickness', _type=float)
        else:
          dirname = os.path.join(amf.config.data_dir, p['name'])
          if not os.path.exists(dirname):
            os.makedirs(dirname)
          try:
            filename = i[prefix + 'file'].filename
            filename = os.path.join(dirname, filename)
            contents = i[prefix + 'file'].value
            amf.utils.write_file(filename, contents)
          except:
            filename = os.path.basename(i[prefix + 'oldfile'])
            filename = os.path.join(dirname, filename)
            try:
              shutil.copy(i[prefix + 'oldfile'], filename)
            except shutil.Error:
              pass
          this_cathode['file'] = filename
        p[cathode] = this_cathode

      if errors != []:
        msg = "There were some problems processing your request. Please fix the following errors:"
        return render.form("New Run", msg, errors, p)

      amf.parameters.save_params(p)

      params = amf.parameters.load_params(p['name'])

      result = amf.generator.generate(p, run, chamber)
      if result != True:
        msg = "There was an error with the run<br><br><br>"
        msg += '<pre>' + result + '</pre>'
        return render.form("Edit Run - " + p['name'], msg, None, p, get_ext(p))
      else:
        log_txt = amf.utils.read_file(amf.config.dry_run_filename)
        return render.post_new(log_txt)

  def POST(self):
    return self.GET()

def get_ext(param):
  ext = {}
  try:
    ext['c1_basename'] = os.path.basename(param['cathode 1']['file'])
    #ext['c1_oldfile'] = param['cathode 1']['file']
  except:
    pass
  try:
    ext['c2_basename'] = os.path.basename(param['cathode 2']['file'])
    #ext['c2_oldfile'] = param['cathode 2']['file']
  except:
    pass
  return ext

class browse:
  def GET(self):
    web.header("Content-Type","text/html; charset=utf-8")
    def get_runs():
      runs = []
      for obj in os.listdir(amf.config.data_dir):
        if os.path.isdir(os.path.join(amf.config.data_dir, obj)):
          runs_id = ('_'.join(obj.split(' ')))
          runs.append((obj, runs_id))
      return render.browse(runs)

    if 'p' in dict(web.input()).keys():
      p = web.input()['p']
      try:
        param =  amf.parameters.load_params(p)
        ext = get_ext(param)
      except:
        pass
      if 'duplicate' in dict(web.input()).keys():
        title = "Duplicate Run - " + p
        param['name'] += '_duplicate'
        msg = 'Run ' + p + ' has been duplicated. '
        msg += 'You can modify any parameters below without changing '
        msg += p + '.'
        return render.form(title, msg, None, param, ext)
      elif 'delete' in dict(web.input()).keys():
        path = os.path.join(amf.config.data_dir, p)
        shutil.rmtree(path)
        return get_runs()
      elif 'log' in dict(web.input()).keys():
        path = os.path.join(amf.config.data_dir, p)
        path = os.path.join(path, 'dry_run.txt')
        log = amf.utils.read_file(path)
        return render.logviewer(p, log)
      else:
        title = "Edit Run - " + p
        return render.form(title, None, None, param, ext)
    else:
      return get_runs()

def main():
  print "starting webserver on localhost on port", amf.config.local_server_port

  # annoying hack to make webpy start on the right port locally
  sys.argv.append(str(amf.config.local_server_port))

  app = web.application(urls, globals(), autoreload=True)
  app.internalerror = web.debugerror
  amf.utils.run_process('start http://localhost:' + str(amf.config.local_server_port))
  app.run()

#app = web.application(urls, globals(), autoreload=False)
#application = app.wsgifunc()
