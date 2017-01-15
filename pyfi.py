#!/usr/bin/env python

import sys, os, re
import pyfi_cli

##################################
#
# check for
# external libraries
# pip install --upgrade google-api-python-client
##################################

libs=['pandas','tabulate','bokeh']

try:
  import pandas as pd
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

# Utility Functions
# todo move to other file

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

##################################

class Ledger():

  def __init__(self,ledger_file,account_file):
    self.ledger = pd.read_csv('ledger.tsv.csv',sep=',')
    self.ledger['date'] = pd.to_datetime(self.ledger['date'],infer_datetime_format=True)
    self.ledger.sort_values('date',inplace=True)
    self.accounts = account_file

  def get_balances(self):
    """
      get a dataframe with columns account and balance
    """
    balances = []
    accounts = pd.unique(self.ledger[['debit', 'credit']].values.ravel())
    for account in accounts:
      account_ledger = pd.concat([self.ledger.loc[self.ledger['debit'] == account],self.ledger.loc[self.ledger['credit'] == account]])
      debit  = -1 * (account_ledger.loc[account_ledger['debit']  == account])['amount'].sum()
      credit = (account_ledger.loc[account_ledger['credit'] == account])['amount']
      exchange = (account_ledger.loc[account_ledger['credit'] == account])['exchange']
      credit = credit.multiply(exchange).sum()
      balance = debit + credit
      balances.append(balance)
    return pd.DataFrame({
     'account': accounts,
     'balance': balances}).sort_values(by='account')

  def get_register_by_account(self,account):
    """
      return a register for the given account consisting of columns:
      date,account,category,description,amount,balance
      where amount and balance correct for credit vs debit and currency exchange
    """

    # just transactions for this account
    account_ledger = pd.concat([self.ledger.loc[self.ledger['debit'] == account],self.ledger.loc[self.ledger['credit'] == account]])

    # separate credits and debits
    credits = account_ledger.loc[account_ledger.loc[:,'credit'] == account].copy()
    debits  = account_ledger.loc[account_ledger.loc[:,'debit']  == account].copy()

    # when crediting an account multiply by the exhange rate
    # when debiting an account, change the sign of the transaction

    new_credit_amounts = credits['amount'].multiply(account_ledger.loc[account_ledger['credit'] == account]['exchange'])
    new_debits_amounts =  debits['amount'].multiply(-1)

    # replace the amount column for each frame
    credits.loc[:,'amount'] = new_credit_amounts
    debits.loc[:,'amount']  = new_debits_amounts

    # replace two column ledger with single column since it is for a specific account
    credits['account'] = credits.loc[:,'debit']
    debits['account']  = debits.loc[:,'credit']

    # drop columns we no longer care about
    drop = ['debit','credit','exchange']
    credits = credits.drop(drop, 1)
    debits  =  debits.drop(drop,1)

    # bring frames together and order by date
    account_ledger = pd.concat([credits,debits]).sort_values('date')

    # create a running balance
    account_ledger['balance'] = account_ledger['amount'].cumsum()

    # reorder the columns
    account_ledger = account_ledger[['date','account','category','description','amount','balance']]

    return account_ledger

  def get_root_account(self):
    account_ledger = self.get_register_by_account('root')
    account_ledger = account_ledger.drop('balance',1)

    account_ledger = account_ledger.loc[account_ledger.loc[:,'category'] != 'init']
    # from our perspective, all these values are negated
    account_ledger['amount'] = account_ledger['amount'].multiply(-1)

    # recreate a running balance
    account_ledger['balance'] = account_ledger['amount'].cumsum()

    return account_ledger

  def get_accounts(self):
    """
      a list of unique accounts
    """
    accounts = pd.unique(self.ledger[['debit', 'credit']].values.ravel())
    return sorted(accounts)

  def get_number_transactions(self):
    return len(self.ledger.index)

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

  def get_category_rates(self):
    """
      return a Series of user-defined categories and occurences
    """

    return self.ledger['category'].value_counts()

  def get_category_list(self):
    return self.get_category_rates().index.tolist()

  def get_category_count_list(self):
    return self.get_category_rates().values

  def all(self):
    """
      run several pre-defined methods
    """

    # todo refactor

    self.print_all_transactions()
    self.print_register_all_accounts()
    self.print_balances()
    self.graph_all_balance()
    print_table_cli(pd.DataFrame({'category':self.get_category_list(),'count':self.get_category_count_list()}))
    self.print_root_account()

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
    static_dir = 'site/static/'
    header = ''
    with open(static_dir + 'header.html', 'r') as myfile:
      header=myfile.read().replace('\n', '')
    return header

  # since all the static elements are the same, these functions could be combined
  def get_html_footer(self):
    # todo move this whole function to hmtl class
    static_dir = 'site/static/'
    footer = ''
    with open(static_dir + 'footer.html', 'r') as myfile:
      footer=myfile.read().replace('\n', '')
    return footer

  def render_ledger(self):
    # todo move this whole function to hmtl class

    # LEDGER (no processing needed)

    # ACCOUNTS
    accounts = self.get_balances()
    # remove 'special' accounts
    for account in ['root','init','income']:
      accounts = accounts[accounts.account != account]
    # format balances
    accounts['balance'] = format_currency(accounts['balance'])
    # self.render_html(accounts,"accounts.html")

    site=[
      [self.ledger,"ledger.html","Legder"],
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
    fo = open("site/site_root/" + filename, "w+")
    fo.write(prettyHTML)
    fo.close()

class PyFiCLI():
  """
    Command line interface to PyFi
  """
  ledger   = None
  accounts = None

  def __init__(self,ledger_file,account_file):
    self.ledger = Ledger(ledger_file,account_file)
    self.accounts = account_file

  #
  # printing
  #

  def print_balances(self):
    """
      print accounts and balances to the screen
    """
    # todo replace this with a call to a central currency format function
    balances = self.ledger.get_balances()
    total = balances['balance'].sum()
    balances['balance'] = format_currency(balances['balance'])
    print_table_cli(balances)
    print total

  def print_root_account(self):

    register = self.ledger.get_root_account()
    header = 'root'

    cur_columns = ['amount','balance']
    for col in cur_columns:
      register[col] = format_currency(register[col])

    print_table_cli(register,header)

  def print_register_by_account(self,account):

    account_ledger = self.ledger.get_register_by_account(account)

    # change format of currency columns
    cur_columns = ['amount','balance']
    for col in cur_columns:
      account_ledger[col] = format_currency(account_ledger[col])

    print_table_cli(account_ledger,account)

  def print_register_all_accounts(self):
    """
       print a register to the screen for each account found
    """

    for account in self.ledger.get_accounts():
      self.print_register_by_account(account)

  def print_all_transactions(self):
    # print self.ledger.ledger
    # todo replace with get_all_transactions()
    print_table_cli(self.ledger.ledger,"All Transactions")

  def menu(self):

    _=os.system("clear")
    while True:
      accounts = self.ledger.get_balances()

      # remove 'special' accounts
      for account in ['root','init','income']:
        accounts = accounts[accounts.account != account]

      # add numeric choices for menu
      accounts['num'] = range(1, len(accounts.index)+1,1)

      # format balances
      accounts['balance'] = format_currency(accounts['balance'])

      print "1: accounts\n" + \
            "2: income summary\n" + \
            "3: net debit/credit\n" + \
            "4: full ledger\n" + \
            "5: enter a new transaction\n" + \
            "6: print expense\n" + \
            "7: write html\n" + \
            "q: quit"
      choice = raw_input('Enter your input: ')
      if choice == "q":
        break
      elif choice == "1":
        print_table_cli(accounts[['num','account','balance']])
        choice = raw_input('Enter your input: ')
        if choice == "q":
          break
        elif choice == "p":
          break
        else:
          account = accounts.loc[accounts.loc[:,'num'] == int(choice)]['account'].values[0]
          # print account
          self.print_register_by_account(account)
          raw_input("Press Enter to continue...")
      elif choice == "2":
        self.print_register_by_account('income')
        raw_input("Press Enter to continue...")
      elif choice == "3":
        self.print_root_account()
        raw_input("Press Enter to continue...")
      elif choice == "4":
        self.print_all_transactions()
        raw_input("Press Enter to continue...")
      elif choice == "5":
        print_table_cli(accounts[['num','account','balance']])
        debit  = raw_input('  From: ')
        credit = raw_input('   To: ')
        amount = raw_input('Amount: ')
        print self.ledger.get_category_rates()
        category = raw_input('Category: ')
        description = raw_input('Description: ')
        exchange = raw_input('Exchange: ')
        print debit,credit,amount,category,description,exchange
      elif choice == "6":
        a = self.ledger.get_root_account()
        a = a.drop('balance',1)
        a = a.loc[a['amount'] < 0]
        a['balance'] = a['amount'].cumsum()
        # format balances
        a['balance'] = format_currency(a['balance'])
        a['amount']  = format_currency(a['amount'])
        print_table_cli(a)
      elif choice == "7":
        self.ledger.render_ledger()

def main():
  """
    execute this code from the command line
  """

  print "main"
  a = PyFiCLI(
         ledger_file = 'ledger.tsv.csv',
         account_file = 'credit.tsv.csv')
  a.menu()
  print "done"

if __name__ == '__main__':
  main()
  # TODO create tableFormatter
  # TODO check for --html-only flag and skip menu if just generating html
  # TODO allow run-time passing of how the files are delimited
  sys.exit()

# TODO make readmme



