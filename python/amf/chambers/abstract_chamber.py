"""

Chamber settings module

Used to store and retreive settings for different chambers in the lab
Everything is stored in JSON

"""

class abstract_chamber(object):
  def __init__(self):
    self.name = ''
    self.shutters = {}
    self.axes = {}
    self.cathodes = {}
    self.master_axis = self.platen
    self.slave_axis = self.mandrel

  def platen(self):
    return self.axes[str(self.platen_axis)]

  def mandrel(self):
    return self.axes[str(self.mandrel_axis)]

  def cathode(self, i):
    return self.cathodes[str(i)]

  def shutter(self, i):
    return self.shutters[str(i)]

  def num_cathodes(self):
    return len(self.cathodes.keys())

  def header_items(self):
    d = {}
    d['chamber_name'] = self.name
    d['platen_axis'] = self.platen_axis
    try:
      d['mandrel_axis'] = self.mandrel_axis
    except:
      pass
    try:
      d['linear_stage_axis'] = self.linear_stage_axis
    except:
      pass
    for item in [self.axes, self.cathodes]:
      for subitem in item.itervalues():
        print subitem
        subitem.add_header_item(d)

    return d
