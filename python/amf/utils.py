"""

General utilities

"""

import json
from json import encoder
encoder.FLOAT_REPR = lambda o: format(o, '.4f')
import re
import subprocess

class AMFError(BaseException):
  pass

def paths_equal(p1, p2):
  def strip_dirs(s):
    s = ''.join(s.split('/'))
    s = ''.join(s.split('\\'))
  return strip_dirs(p1) == strip_dirs(p2)

def run_process(cmd):
  subprocess.Popen(cmd.split(), shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

def dict_to_file(d, filename):
  write_file(filename, json.dumps(d, sort_keys=True, indent=4) + '\n')

def file_to_dict(filename):
  file_text = read_file(filename)
  file_text = filter_comments(file_text)
  return json.loads(file_text)

def write_file(name, contents):
  f = open(name, 'w')
  f.write(contents)
  f.close()

def read_file(name):
  f = open(name, 'r')
  s = f.read()
  f.close()
  return s

def filter_comments(text):
  comment_re0 = re.compile(' \/\/.*\\n')
  comment_re1 = re.compile('\\n\/\/.*\\n')
  comment_re2 = re.compile('[^:]\/\/.*\\n')
  comment_re3 = re.compile('\/\*.*\*\/')
  
  re_list = [comment_re0, comment_re1, comment_re2, comment_re3]
  for _re in re_list:
    for comment in _re.findall(text):
      text = text.replace(comment, '')
  print text
  return text
