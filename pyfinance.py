#!/usr/bin/env python

import pandas as pd
from tabulate import tabulate

class finance():

  def __init__(self,ledger_file,account_file):
    self.ledger = pd.read_csv('ledger.tsv.csv',sep='\t')
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

  def print_ledger_by_account(self,account):
    account_ledger = pd.concat([self.ledger.loc[self.ledger['debit'] == account],self.ledger.loc[self.ledger['credit'] == account]])
    credit = (account_ledger.loc[account_ledger['credit'] == account])['amount']
    exchange = (account_ledger.loc[account_ledger['credit'] == account])['exchange']
    # account_ledger['amount'] = credit = credit.multiply(exchange)
    # todo fix this
    self.print_table(account_ledger)

  def print_ledger_all_accounts(self):
    accounts = pd.unique(self.ledger[['debit', 'credit']].values.ravel())
    for account in accounts:
      print "\n[[",account,"]]"
      self.print_ledger_by_account(account)

  def print_table(self,data):
    print tabulate(data,showindex=False,headers="keys",tablefmt="grid")

  def get_number_transactions(self):
    return len(self.ledger.index)

  def all(self):
    print "transactions:",self.get_number_transactions()
    self.print_ledger_all_accounts()
    self.print_balances()

def main():
  print "main"
  a = finance(
         ledger_file = 'ledger.tsv.csv',
         account_file = 'credit.tsv.csv')
  a.all()
  print "done"

if __name__ == '__main__':
  main()
