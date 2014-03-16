"""
Superblame

Because

Eugen Sawin <esawin@me73.com>
"""


import argparse
import os


# Mapping of firs split to handler, populated at the end of file.
handler = {}


def main():
  args = parse_args()
  with open(args.patch) as patch_file:
    a = {'paths': [], 'adds': [], 'deletes': [], 'blames': []}
    b = {'paths': [], 'adds': [], 'deletes': [], 'blames': []}
    for line in patch_file:
      splits = line.split()
      if len(splits) and splits[0] in handlers:
        handlers[splits[0]](splits, a, b)
    print a
    print
    print b
  

def handle_header(splits, a, b):
  path = splits[1]
  if len(path) > 1 and (path[0:2] == 'a/' or path[0:2] == 'b/'):
    path = path[2:]
  if splits[0] == '---': x = a
  elif splits[0] == '+++': x = b
  else: assert False
  x['paths'].append(path)



def handle_hunk(splits, a, b):
  pass


def handle_diff(splits, a, b):
  assert splits[0] == 'diff'
  assert splits[1] == '--git'
  assert splits[2][0] == 'a'
  assert splits[3][0] == 'b'


def handle_comment(splits, a, b):
  pass


handlers = {
  '#': handle_comment,
  'diff': handle_diff,
  '@@': handle_hunk,
  '---': handle_header,
  '+++': handle_header,
}

def parse_args():
  parser = argparse.ArgumentParser(description='Superblame')
  parser.add_argument('patch', help='patch')
  parser.add_argument('--src', default=os.getcwd(), help='source directory')
  return parser.parse_args()


if __name__ == '__main__':
  main()
