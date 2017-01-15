#!/usr/bin/env python

import re

##################################
#
# check for
# external libraries
# pip install --upgrade google-api-python-client
#
##################################

libs=['BeautifulSoup','tabulate']

try:
  from tabulate import tabulate
  from BeautifulSoup import BeautifulSoup as bs
except ImportError:
  print "Unmet dependencies were found.  Here are the dependencies:"
  for lib in libs:
    print " * " + lib
  sys.exit(1)


# Utility Functions

def print_table_cli(data,header=None):
  """
    Use a standard method to display tabular data on screen
  """

  if header != None:
    # todo should run tabulate first, then calculat the width of the table and maek the header span
    #   and possible center the full rowspan
    # print account header
    print "+------------+-----------------+\n| ",header

  print tabulate(data,showindex=False,headers="keys",tablefmt="grid",numalign="right",stralign="right")


def format_currency(series):
  return series.map('{:,.2f}'.format)

def get_indented_html(html):

  # make BeautifulSoup with 2 spaces instead of 1
  r = re.compile(r'^(\s*)', re.MULTILINE)
  return r.sub(r'\1\1', bs(html).prettify())

