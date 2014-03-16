"""
Superblame

Because

Eugen Sawin <esawin@me73.com>
"""


import argparse
import os


class Mod:

  def __init__(self):
    self.paths = []
    self.adds = []
    self.removes = []
    self.blames = []
    self.line = 1

  def append_add(self, line):
    if len(self.adds) and self.adds[-1][0] == line:
      self.adds[-1][1] += 1
    else:
      self.adds.append([line, 1])

  def append_remove(self, line):
    if len(self.removes) and self.removes[-1][0] == line:
      self.removes[-1][1] += 1
    else:
      self.removes.append([line, 1])

  def __str__(self):
    return "{{{}\n  {}\n  {}\n  {}\n  {}\n}}".format(self.paths, self.adds,\
        self.removes, self.blames, self.line)



# Mapping of firs split to handler, populated at the end of file.
handler = {}


def main():
  args = parse_args()
  with open(args.patch) as patch_file:
    a = Mod()
    b = Mod()
    for line in patch_file:
      if len(line) and line[0] in handlers:
        handlers[line[0]](line, a, b)
    print a
    print
    print b


def handle_mod(line, a, b):
  if line[0] == '+':
    a.append_add(a.line)
    b.line += 1
  elif line[0] == '-':
    a.append_remove(a.line)
    a.line += 1
  else:
    assert False


def handle_unmod(line, a, b):
  a.line += 1
  b.line += 1
  
 
def handle_header(line, a, b):
  splits = line.split()
  path = splits[1]
  if len(path) > 1 and (path[0:2] == 'a/' or path[0:2] == 'b/'):
    path = path[2:]
  if splits[0] == '---':
    x = a
  elif splits[0] == '+++':
    x = b
  else:
    assert False
  x.paths.append(path)


def handle_header_or_mod(line, a, b):
  if line[0] == line[1] and line[1] == line[2]:
    return handle_header(line, a, b)
  return handle_mod(line, a, b);


def handle_hunk(line, a, b):
  splits = line.split()
  assert splits[0] == '@@'
  a_splits = splits[1].split(',')
  b_splits = splits[2].split(',')
  a.line = int(a_splits[0][1:])
  b.line = int(b_splits[0][1:])



def handle_index(line, a, b):
  splits = line.split()
  assert splits[0] == 'index'


def handle_diff(line, a, b):
  splits = line.split()
  assert splits[0] == 'diff'
  assert splits[1] == '--git'
  assert splits[2][0] == 'a'
  assert splits[3][0] == 'b'


def handle_comment(line, a, b):
  pass


handlers = {
  '#': handle_comment,
  'd': handle_diff,
  'i': handle_index,
  '@': handle_hunk,
  '-': handle_header_or_mod,
  '+': handle_header_or_mod,
  ' ': handle_unmod,
}

def parse_args():
  parser = argparse.ArgumentParser(description='Superblame')
  parser.add_argument('patch', help='patch')
  parser.add_argument('--src', default=os.getcwd(), help='source directory')
  return parser.parse_args()


if __name__ == '__main__':
  main()
