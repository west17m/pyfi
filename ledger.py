#!/usr/bin/env python

import sys, os
from utilities import *
# from pyfi_cli import PyFiCLI

##################################
#
# check for
# external libraries
# pip install --upgrade google-api-python-client
##################################

libs=['pandas']

try:
  import pandas as pd
except ImportError:
  print "Unmet dependencies were found.  Here are the dependencies:"
  for lib in libs:
    print " * " + lib
  sys.exit(1)

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

if __name__ == '__main__':
  print "please call pyfi_cli.py or pyfi_html.py instead"
  sys.exit()

