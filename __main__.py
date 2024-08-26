import importlib.resources
import json
from pprint import pprint
import sqlite3
import sxml
import sys
from xml.etree import ElementTree


# `sys.argv[1]` is either a SQLite database file, or a text file containing a
# database schema.
with open(sys.argv[1], 'rb') as db_file:
  db_magic = db_file.read(15)

  if db_magic == b'SQLite format 3':
    # It's a SQLite database file.
    db = sqlite3.connect(f'file:{sys.argv[1]}?mode=ro', uri=True)
  else:
    # Assume it's a SQL script.
    script = (db_magic + db_file.read()).decode()
    db = sqlite3.connect(':memory:')
    db.executescript(script)

query_files = importlib.resources.files('sql')
columns_query = (query_files/'columns.sql').read_text()
edges_query = (query_files/'edges.sql').read_text()

tables = {}
for table, column, type, pk, snowflakes in db.execute(columns_query):
  t = tables.setdefault(table, {})
  cols = t.setdefault('columns', [])
  cols.append({
    'name': column,
    'type': type,
    'pk?': bool(pk),
    'snowflakes': snowflakes
  })
  if snowflakes is not None:
    t.setdefault('snowflakes', set()).add(snowflakes)

edges = []
for from_table, from_column, to_table, to_column in db.execute(edges_query):
  edges.append((from_table, from_column, to_table, to_column))


def to_superscript(text):
  supers = '⁰¹²³⁴⁵⁶⁷⁸⁹'
  zero = ord('0')
  nine = ord('9')
  return ''.join(
      supers[ord(c) - zero] if ord(c) >= zero and ord(c) <= nine else c
      for c in text)


def sxml_from_table(name, columns, num_snowflakes):

  def sxml_from_column(name, type, pk, snowflakes):
    emojis = []
    if pk:
      emojis.append('🔑')
    if snowflakes is not None:
      if num_snowflakes == 1:
        emojis.append('❄️')
      else:
        emojis.append(f'❄️{to_superscript(snowflakes)}')
    return ['TR', ['TD', {'PORT': f'{name}_in'}, name],
            ['TD', {'ALIGN': 'left', 'SIDES': 'LTB'}, ['I', type]],
            ['TD', {'ALIGN': 'left', 'SIDES': 'RTB', 'PORT': f'{name}_out'},
             ''.join(emojis)]]

  return ['TABLE', {'BORDER': '0', 'CELLBORDER': '1', 'CELLSPACING': '0'},
    ['TR', ['TD', {'COLSPAN': '3'}, ['B', name]]],
    *(sxml_from_column(c['name'], c['type'], c['pk?'], c['snowflakes'])
      for c in columns)]


def dot_node(name, markup):
  return f'{json.dumps(name)} [shape=none, label=<{markup}>];'


def dot_edge(from_table, from_column, to_table, to_column):
  from_table = json.dumps(from_table)
  from_column = json.dumps(f'{from_column}_out')
  to_table = json.dumps(to_table)
  to_column = json.dumps(f'{to_column}_in')
  # ":e" means "east", i.e. from the right.
  # ":_" means "automatic", i.e. to whatever side is closest.
  return f'{from_table}:{from_column}:e -> {to_table}:{to_column}:_;'


print('digraph {')
print('rankdir = LR;')
print('node [fontname="Helvetica"];')

for name, table in tables.items():
  table = sxml_from_table(
      name, table['columns'], len(table.get('snowflakes', set())))
  # pprint(table)
  element = sxml.element_from_sexpr(table)
  markup = ElementTree.tostring(
      element,
      encoding='unicode',
      short_empty_elements=False)
  print(dot_node(name, markup))

print()

for from_table, from_column, to_table, to_column in edges:
  print(dot_edge(from_table, from_column, to_table, to_column))

print('}')

