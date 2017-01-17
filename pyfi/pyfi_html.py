#!/usr/bin/env python

from ledger import *
from utilities import *

import sys, os
from utilities import *
# from pyfi_cli import PyFiCLI


##################################
#
# check for
# external libraries
# pip install --upgrade google-api-python-client
##################################

libs=['tabulate','bokeh']

try:
  from tabulate import tabulate
  from BeautifulSoup import BeautifulSoup as bs
  from bokeh.plotting import figure, output_file, show, save, gridplot, vplot
  from bokeh.models import ColumnDataSource, Tool, WheelZoomTool, BoxSelectTool
  from bokeh.models.widgets import DataTable, DateFormatter, TableColumn
  from bokeh.io import vform
except ImportError:
  print "Unmet dependencies were found.  Here are the dependencies:"
  for lib in libs:
    print " * " + lib
  sys.exit(1)

##################################

class PyFiHTML():
  """
    Command line interface to PyFi
  """
  ledger   = None
  accounts = None

  def __init__(self,ledger_file,account_file):
    self.ledger = Ledger(ledger_file,account_file)
    self.accounts = account_file
    sys.path.append('./pyfi')
    print os.getcwd()

  def get_balance_graph_by_account(self,account):
    """
      return a balance over time graph for a given account as a bokeh figure object
    """
    ledger = self.get_register_by_account(account)

    # todo move this whole function to hmtl class

    # create a new plot with a title and axis labels
    p = figure(title=(account + " balance"), x_axis_label='date', y_axis_label='balance',x_axis_type="datetime",width=400, height=400)
    p.add_tools(WheelZoomTool())

    # add a line renderer with legend and line thickness
    p.line(ledger['date'], ledger['balance'], legend="balance", line_width=2)

    return p

  def graph_all_balance(self):
    """
      Create a balance over time graph for all accounts
    """

    # todo move this whole function to hmtl class

    # output to static HTML file
    output_file("output/charts.html")

    max_per_row = 4
    figures = []
    row = []
    for account in self.get_accounts():
      figure = self.get_balance_graph_by_account(account)
      if len(row) >= max_per_row:
        figures.append(row)
        row=[figure]
      else:
        row.append(figure)

    figures.append(row)

    p = gridplot(figures) # todo make grid
    dt = self.get_data_table()

    q = vplot(*[p,dt])

    # save the results
    save(q)

  def get_data_table(self):
    #output_file("data_table.html")

    source = ColumnDataSource(self.ledger)

    columns = [
      TableColumn(field=c, title=c) for c in self.ledger.columns
    ]

    columns[0] = TableColumn(field="date", title="date", formatter=DateFormatter())
    data_table = DataTable(source=source, columns=columns, editable=True, width = 800, height=600)
    #save(data_table)
    return data_table

    #columns = [
    #    TableColumn(field="date", title="Date", formatter=DateFormatter()),
    #    TableColumn(field="debit", title="Downloads"),
    #    TableColumn(field="credit", title="Downloads"),
    #]
    #data_table = DataTable(source=source, width=400, height=280)
    #
    #show(vform(data_table))


  def get_classes(self):
    # todo move this whole function to hmtl class
    return {
      'table': 'table',
      'thead': 'thead',
         'th': 'th',
      'tbody': 'tbody',
         'td': 'td',
         'tr': 'tr',
    }

  def get_html_header(self):
    # todo move this whole function to hmtl class
    static_dir = 'pyfi/site/static/'
    header = ''
    with open(static_dir + 'header.html', 'r') as myfile:
      header=myfile.read().replace('\n', '')
    return header

  # since all the static elements are the same, these functions could be combined
  def get_html_footer(self):
    # todo move this whole function to hmtl class
    static_dir = 'pyfi/site/static/'
    footer = ''
    with open(static_dir + 'footer.html', 'r') as myfile:
      footer=myfile.read().replace('\n', '')
    return footer

  def render_ledger(self):
    # todo move this whole function to hmtl class

    # LEDGER (no processing needed)

    # ACCOUNTS
    accounts = self.ledger.get_balances()
    # remove 'special' accounts
    for account in ['root','init','income']:
      accounts = accounts[accounts.account != account]

    # format balances
    accounts['balance'] = format_currency(accounts['balance'])
    # self.render_html(accounts,"accounts.html")

    site=[
      [self.ledger.ledger,"ledger.html","Legder"],
      [accounts,"accounts.html","Accounts"],
    ]

    # generate menu
    menu = '<div class="menu"><ul>\n'
    for table,filename,linkname in site:
      menu = menu + "<li><a href=\"" + filename + "\">" + linkname + "</a></li>\n"
    menu = menu + '</ul></div>\n'

    # create html pages
    for table,filename,linkname in site:
      self.render_html(table,filename,menu)

  def render_html(self,df,filename,menu):
    # todo move this whole function to hmtl class
    # print "rendering html"

    # get the static elements of the page
    header = self.get_html_header()
    footer = self.get_html_footer()

    # todo format amount
    table = tabulate(df,showindex=False,headers="keys",tablefmt="html",numalign="right",stralign="right")

    # get styles to insert and insert them
    classes = self.get_classes()
    for key in classes:
      class_style = classes[key]
      # todo combine the following to commands into one
      table = re.sub('<'+ key + ' ','<'+ key + ' class="' + class_style + '"' + ' ' + ' ',table,flags=re.MULTILINE|re.IGNORECASE)
      table = re.sub('<'+ key + '>','<'+ key + ' class="' + class_style + '"' + '>' + ' ',table,flags=re.MULTILINE|re.IGNORECASE)

    # combine static and generated elements of page
    raw_html = header + menu + table + footer

    prettyHTML = get_indented_html(raw_html)

    # write the file
    fo = open("pyfi/site/site_root/" + filename, "w+")
    fo.write(prettyHTML)
    fo.close()

  def render(self):
    self.render_ledger()

def main():
  """
    execute this code from the command line
  """

  print "main"
  a = PyFiHTML(
         ledger_file = 'ledger.tsv.csv',
         account_file = 'credit.tsv.csv')
  a.render()
  print "done"

if __name__ == '__main__':
  main()
  # TODO check for --html-only flag and skip menu if just generating html
  # TODO allow run-time passing of how the files are delimited
  sys.exit()

# TODO make readmme

