#!/usr/bin/python
"""
Superblame

Because

Eugen Sawin <esawin@me73.com>
"""


import argparse
import os
import subprocess
import math

from collections import defaultdict


class HeatMap:

  def __init__(self, add_lambda=0.8, remove_lambda=0.8, epsilon=0.001):
    self.users = {}
    self.heat = []
    self.add_lambda = add_lambda
    self.remove_lambda = remove_lambda
    self.epsilon = epsilon
    self.author = -1

  def user_id(self, name):
    idx = self.users.setdefault(name, len(self.users))
    self.users[name] = idx
    if len(self.users) > len(self.heat):
      self.heat.append([0.0, name])
    return idx

  def calc_heat(self, dist, l):
    """ Probability density function based on distance. """
    dist = min(0.1, dist)
    return l * math.exp(-l * dist)

  def register_radius(self, line, blames, l):
    dist = 0
    h = self.calc_heat(dist, l)
    cur_line = int(line)
    while cur_line > 0 and h > self.epsilon:
      if blames[cur_line] == self.author:
        cur_line -= 1
        continue
      self.heat[blames[cur_line]][0] += h
      cur_line -= 1
      dist += 1
      h = self.calc_heat(dist, l)

    dist = 0
    h = self.calc_heat(dist, l)
    cur_line = int(line)
    while cur_line < len(blames) and h > self.epsilon:
      if blames[cur_line] == self.author:
        cur_line += 1
        continue
      self.heat[blames[cur_line]][0] += h
      cur_line += 1
      dist += 1
      h = self.calc_heat(dist, l)

  def register_add(self, line, blames):
    self.author = blames[line]
    self.register_radius(line, blames, self.add_lambda)

  def register_remove(self, line, blames):
    self.register_radius(line, blames, self.remove_lambda)

  def top(self, n):
    n = min(n, len(self.heat))
    if n == 0:
      return []
    s = sorted(self.heat, reverse=True)[:n]
    while s[-1][0] < self.epsilon:
      s = s[:-1]
    return s

  def top_str(self, n):
    s = self.top(n)
    if len(s) == 0:
      return 'no results'
    max_heat = s[0][0]
    s = ['{:>30} {}'.format(n[:30], '#' * int(30 * v / max_heat)) for (v, n) in s]
    return '\n'.join(s)


  def __str__(self):
    return self.top_str(len(self.heat))


class Mod:

  def __init__(self):
    self.reset(None)

  def reset(self, path):
    self.path = path
    self.adds = []
    self.removes = []
    self.blames = [-1]
    self.line = 1

  def append_blame(self, name):
    self.blames.append(name)

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
    return "{{{},\n  {},\n  {},\n  {},\n  {},\n}}".format(
            self.path, self.adds, self.removes, self.blames, self.line)


# Mapping of firs split to handler, populated at the end of file.
handler = {}

args = None


def main():
  global args

  args = parse_args()
  with open(args.patch) as patch_file:
    heat = HeatMap()
    a = Mod()
    b = Mod()
    for line in patch_file:
      if len(line) and line[0] in handlers:
        handlers[line[0]](line, a, b, heat)
    # print 'a = ', a
    # print 'b = ', b
    print heat.top_str(args.top)


def handle_mod(line, a, b, heat):
  if line[0] == '+':
    heat.register_add(b.line, b.blames)
    a.append_add(a.line)
    b.line += 1
  elif line[0] == '-':
    heat.register_remove(b.line, b.blames)
    a.append_remove(a.line)
    a.line += 1
  else:
    assert False


def handle_nonmod(line, a, b, heat):
  a.line += 1
  b.line += 1
  
 
def handle_header(line, a, b, heat):
  splits = line.split()
  path = splits[1]
  if len(path) > 1 and (path[0:2] == 'a/' or path[0:2] == 'b/'):
    path = path[2:]
  if splits[0] == '---':
    a.reset(path)
  elif splits[0] == '+++':
    b.reset(path)
    load_blames(b, path, heat)
  else:
    assert False


def handle_header_or_mod(line, a, b, heat):
  if line[0] == line[1] and line[1] == line[2]:
    return handle_header(line, a, b, heat)
  return handle_mod(line, a, b, heat);


def handle_hunk(line, a, b, heat):
  splits = line.split()
  assert splits[0] == '@@'
  a_splits = splits[1].split(',')
  b_splits = splits[2].split(',')
  a.line = int(a_splits[0][1:])
  b.line = int(b_splits[0][1:])


def handle_index_or_imported(line, a, b, heat):
  splits = line.split()
  assert splits[0] == 'index' or splits[0] == 'imported'


def handle_diff(line, a, b, heat):
  splits = line.split()
  assert splits[0] == 'diff'
  assert splits[1] == '--git'
  assert splits[2][0] == 'a'
  assert splits[3][0] == 'b'


def handle_comment(line, a, b, heat):
  pass


def load_git_blame(x, path, heat):
  content = subprocess.check_output(['git', 'blame', path])
  for line in content.split('\n'):
    start = line.find('(')
    if start == -1:
      break
    end = line.find(')')
    assert end != -1
    splits = line[start+1:end].split()
    user = heat.user_id(' '.join(splits[:-4]))
    x.append_blame(user)


def load_hg_blame(x, path, heat):
  content = subprocess.check_output(['hg', 'annotate', '-u', path])
  for line in content.split('\n'):
    end = line.find(':')
    if end == -1:
      break
    user = heat.user_id(line[:end].strip())
    x.append_blame(user)


handlers = {
  '#': handle_comment,
  'd': handle_diff,
  'i': handle_index_or_imported,
  '@': handle_hunk,
  '-': handle_header_or_mod,
  '+': handle_header_or_mod,
  ' ': handle_nonmod,
}


blame_loaders = {
  'git': load_git_blame,
  'hg': load_hg_blame,
}


def load_blames(x, path, heat):
  vcs = identify_vcs()
  assert vcs in blame_loaders
  blame_loaders[vcs](x, path, heat)


def identify_vcs():
  global args

  if os.path.exists(args.src + '/.git'):
    return 'git'
  if os.path.exists(args.src + '/.hg'):
    return 'hg'


def parse_args():
  parser = argparse.ArgumentParser(description='Superblame')
  parser.add_argument('patch', help='patch')
  parser.add_argument('--src', default=os.getcwd(), help='source directory')
  parser.add_argument('--top', type=int, default=10, help='top n reviewers output')
  return parser.parse_args()


if __name__ == '__main__':
  main()
