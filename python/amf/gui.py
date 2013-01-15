import amf.config

import sys
from easygui import *

def gui_choice(msg, choices):
  title = amf.config.app_name
  choice = choicebox(msg, title, choices)
  if not choice:
    return False
  else:
    return choice

def gui_continue(msg):
  title = amf.config.app_name
  if ccbox(msg, title, choices=('Continue', 'Cancel')):     # show a Continue/Cancel dialog
    return True
  else:  # user chose Cancel
    sys.exit(0)

def gui_yn(msg):
  title = amf.config.app_name
  if ynbox(msg, title):
    return True
  else:
    return False

def gui_q(msg):
  title = amf.config.app_name
  s = enterbox(msg, title)
  if s:
    return s
  else:
    return False

def gui_edit(msg, filename):
  title = amf.config.app_name
  text = amf.utils.read_file(filename)
  s = codebox(msg, title, text)
  if s != text:
    return amf.utils.write_file(filename, s)
  else:
    return False

def gui_codebox(msg, contents):
  title = amf.config.app_name
  s = codebox(msg, title, contents)

