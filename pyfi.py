#!/usr/bin/env python

import sys

# external libraries
libs=['pandas','tabulate','bokeh']
try:
  import pandas as pd
  from tabulate import tabulate
  from bokeh.plotting import figure, output_file, show, save, gridplot, vplot
  from bokeh.models import ColumnDataSource, Tool, WheelZoomTool, BoxSelectTool
except ImportError:
  print "Unmet dependencies were found.  Here are the dependencies:"
  for lib in libs:
    print " * " + lib
  sys.exit(1)

class finance():

  def __init__(self,ledger_file,account_file):
    self.ledger = pd.read_csv('ledger.tsv.csv',sep='\t')
    self.ledger['date'] = pd.to_datetime(self.ledger['date'],infer_datetime_format=True)
    self.accounts = account_file

  def print_balances(self):
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
      #print "********************************************************"
      #print account,':',balance
      #print "********************************************************"
      #print account_ledger
      #print 'exchange',exchange
    self.print_table(pd.DataFrame({
     'account': accounts,
     'balance': balances}).sort_values(by='account'))

  def get_ledger_by_account(self,account):
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

  def print_ledger_by_account(self,account):

    account_ledger = self.get_ledger_by_account(account)

    # change format of currency columns
    cur_columns = ['amount','balance']
    for col in cur_columns:
      account_ledger[col] = account_ledger[col].map('{:,.2f}'.format)

    # print account header
    print "+------------+-----------------+\n| ",account
    self.print_table(account_ledger)

  def get_accounts(self):
    accounts = pd.unique(self.ledger[['debit', 'credit']].values.ravel())
    return sorted(accounts)

  def print_ledger_all_accounts(self):
    accounts = self.get_accounts()

    for account in accounts:
      self.print_ledger_by_account(account)

  def print_table(self,data):
    print tabulate(data,showindex=False,headers="keys",tablefmt="grid",numalign="right",stralign="right")

  def get_number_transactions(self):
    return len(self.ledger.index)

  def all(self):
    print "transactions:",self.get_number_transactions()
    self.print_ledger_all_accounts()
    self.print_balances()

  def graph_balance(self,account):
    ledger = self.get_ledger_by_account(account)

    # create a new plot with a title and axis labels
    p = figure(title=(account + " balance"), x_axis_label='date', y_axis_label='balance',x_axis_type="datetime",width=400, height=400)
    p.add_tools(WheelZoomTool())

    # add a line renderer with legend and line thickness
    p.line(ledger['date'], ledger['balance'], legend="balance", line_width=2)

    return p

  def graph_all_balance(self):

    # output to static HTML file
    output_file("output/charts.html")

    max_per_row = 4
    figures = []
    row = []
    for account in self.get_accounts():
      figure = self.graph_balance(account)
      if len(row) >= max_per_row:
        figures.append(row)
        row=[figure]
      else:
        row.append(figure)

    figures.append(row)

    p = gridplot(figures) # todo make grid

    # save the results
    save(p)


def main():
  print "main"
  a = finance(
         ledger_file = 'ledger.tsv.csv',
         account_file = 'credit.tsv.csv')
  a.all()
  #a.print_ledger_by_account('td-checking')
  #a.print_ledger_by_account('vu-checking')
  # a.graph_balance('vu-checking')
  a.graph_all_balance()
  print "done"

if __name__ == '__main__':
  main()
  sys.exit()
