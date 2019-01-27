import csv2bib
import pytest

def test_guess_refs_type_from_headers():
  assert csv2bib.guess_refs_type_from_headers({0:' key', 1: 'title', 5: 'year'}) == 'book'
  assert csv2bib.guess_refs_type_from_headers({0:' key', 1: 'title', 5: 'year', 6: 'pages'}) == 'incollection'
  assert csv2bib.guess_refs_type_from_headers({0:' key', 1: 'title', 5: 'year', 6: 'pages', 15: 'journal'}) == 'article'
  assert csv2bib.guess_refs_type_from_headers({0:' key', 1: 'howpublished', 5: 'year', 6: 'pages', 15: 'journal'}) == 'misc'


def test_parse_headers():
  h = csv2bib.parse_headers(['', 'key', 'invalid', 'invalid', 'title'])
  assert h.valid == {1: 'key', 4: 'title'}
  assert h.invalid == {0: '', 2: 'invalid', 3: 'invalid'}
  with pytest.raises(csv2bib.CSVParseError):
    csv2bib.parse_headers(['pages', 'title', 'year']) == {0: 'pages', 1: 'title', 2: 'year'}


def test_strip_disallowed_headers():
  attrs = {0:'key', 1: 'title', 5: 'year'}
  assert csv2bib.strip_disallowed_headers(attrs, 'book') == attrs

  attrs = {0:'key', 1: 'title', 5: 'year', 7: 'invalid' }
  want = {0:'key', 1: 'title', 5: 'year' }
  assert csv2bib.strip_disallowed_headers(attrs, 'book') == want

def test_to_bib():
  ref = {'key': '123', 'title': 'Book name', 'year': 2019}
  want = """@book{123, 
  title = "Book name",
  year = "2019",
}
"""
  assert csv2bib.to_bib(ref, 'book') == want


  ref = {'key': '123', 'title': 'Book name', 'year': 2019, 'howpublished': 'http://url'}
  want = """@misc{123, 
  title = "Book name",
  year = "2019",
  howpublished = "\\url{http://url}",
}
"""
  assert csv2bib.to_bib(ref, 'misc') == want




