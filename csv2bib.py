#!/usr/bin/env python3

import sys, getopt, csv

SCRIPT_NAME = 'csv2bib' 
BIB_ATTRIBUTE_MAP = {
  'address':      ['address'],
  'author':       ['author', 'authors'],
  'chapter':      ['chapter'],
  'edition':      ['edition'],
  'editor':       ['editor'],
  'howpublished': ['url', 'howpublished'],
  'journal':      ['journal', 'journal name'],
  'key':          ['key'],
  'month':        ['month'],
  'note':         ['note'],
  'pages':        ['pages'],
  'publisher':    ['publisher'],
  'series':       ['series'],
  'title':        ['title', 'book title', 'volume title'],
  'volume':       ['volume'],
  'year':         ['year', 'date'],
}

ALLOWED_ATTRIBUTES_BY_TYPE = {
  'article': [ 'author', 'title', 'journal', 'year', 'volume', 'number',
               'pages', 'month', 'doi', 'note', 'key'],
  'book': [ 'author', 'editor', 'title', 'publisher', 'year', 'volume',
            'series', 'address', 'edition', 'month', 'note', 'key'],
  'inbook': [ 'author', 'editor', 'title', 'publisher', 'year', 'volume',
            'series', 'address', 'edition', 'month', 'note', 'pages', 'key' ],
  'misc': [ 'author', 'title', 'howpublished', 'month', 'year', 'note', 'key']
}

class CSVParseError(Exception):
    pass

# [0 => 'author', 1 => 'title', ...]
def parse_headers(headers, bib_attribute_map = BIB_ATTRIBUTE_MAP):
  attributes_order = {}

  for i, header in enumerate(headers):
    for bib_attribute, bib_attribute_variants in bib_attribute_map.items():
      # The reference attribute is recognised, and allowed for that reference type
      if header.lower() in bib_attribute_variants:
        attributes_order[i] = bib_attribute

  if 'key' not in attributes_order.values():
    raise CSVParseError('no "key" column found')

  return attributes_order

def parse_reference(row, attributes_order):
  ref = {}
  for i, col in enumerate(row):
    # Skip columns for which we did not recognise the header
    if i not in attributes_order:
      continue

    col = col.strip()

    if len(col) == 0:
      continue

    ref[attributes_order[i]] = col

  return ref


# we guess the reference from the headers... eg if it has a 'pages' column,
# it might be an inbook reference rather than a book
def guess_refs_type_from_headers(headers):
  if 'howpublished' in headers.values():
    return 'misc'

  if 'journal' in headers.values() and 'pages' in headers.values():
    return 'article'

  if 'pages' in headers.values():
    return 'inbook'

  return 'book'

def to_bib(ref, ref_type):
  bib_ref = "@%s{%s, \n" % (ref_type, ref['key'])
  for attr, attr_value in ref.items():
    if attr == 'key':
      continue

    if attr == 'howpublished' and attr_value.startswith('http'):
      attr_value = "\\url{%s}" % attr_value

    bib_ref += '  %s = "%s",\n' %(attr, attr_value)
  bib_ref += "}\n"
  return bib_ref


def strip_disallowed_headers(attributes_order, refs_type, allowed_attributes_by_type=ALLOWED_ATTRIBUTES_BY_TYPE):
  clean_attributes_order = {}
  for idx, header in attributes_order.items():
    if header in allowed_attributes_by_type[refs_type]:
      clean_attributes_order[idx] = header

  return clean_attributes_order

def csv_to_bib(csv_file):
  attributes_order = {}
  bib_refs = []

  with open(csv_file, 'r') as f:
    refs_type = ''
    csv_reader = csv.reader(f, delimiter=',', quotechar='"')

    for row in csv_reader:
      if len(''.join(row)) == 0: # skip leading empty lines
        continue
      
      if len(attributes_order) == 0:
        # We assume all refs in a CSV are the same type (book, article, ...)
        attributes_order = parse_headers(row)
        refs_type = guess_refs_type_from_headers(attributes_order)
        attributes_order = strip_disallowed_headers(attributes_order, refs_type)
        continue

      reference = parse_reference(row, attributes_order)
      bib_refs.append(to_bib(reference, refs_type))

  return "\n".join(bib_refs)


def main(argv):
  failure = 0

  try:
    opts, csv_files = getopt.getopt(argv,"-d:")
  except getopt.GetoptError:
    print('Error parsing command line. Usage:\n')
    print("    %s -d <delimiter> file1 file2 ...\n" % SCRIPT_NAME)
    return 2
  for csv_file in csv_files:
    try:
      print (csv_to_bib(csv_file))
    except CSVParseError as e:
        print ('Error: Failed to parse %s: %s' % (csv_file, str(e)), file=sys.stderr)
        failure = 1
    except FileNotFoundError as e:
        print ('Error: Failed to parse %s: file not found' % csv_file, file=sys.stderr)
        failure = 1

  return failure


if __name__ == "__main__":
   sys.exit(main(sys.argv[1:]))

