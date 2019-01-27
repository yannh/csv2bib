# CSV2BIB

Converts CSV files to BIBtex file.

Assumptions:
 * A single CSV file contains a single type of BIB reference (book, article, inbook reference..)
 * The first non-empty line of the CSV file is a Title that can be mapped to a BIB attribute
 * One of the columns contains a "key", a unique identifier for the reference.

 Usage:

   ./csv2bib.py bibliography.csv > bibliography.bib
