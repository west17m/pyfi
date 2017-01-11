#!/usr/bin/env python

import pandas as pd
class account():
  start_balance = 0
  limit = 0

  def __init__(self,starting_balance,limit):
    self.start_balance = starting_balance
    self.limit = limit

def main():
  print "main"
  ledger = pd.read_csv('ledger.tsv.csv',sep='\t')
  # print ledger

  balances = []
  accounts = pd.unique(ledger[['debit', 'credit']].values.ravel())
  for account in accounts:
    account_ledger = pd.concat([ledger.loc[ledger['debit'] == account],ledger.loc[ledger['credit'] == account]])
    debit  = -1 * (account_ledger.loc[account_ledger['debit']  == account])['amount'].sum()
    credit = (account_ledger.loc[account_ledger['credit'] == account])['amount'].sum()
    balance = debit + credit
    balances.append(balance)
    print account,balance
    print account_ledger
    print "********************************************************"

  print balances
  print accounts
  print pd.DataFrame({'account': accounts,
     'balance': balances}).sort_index(by='account')
  print "done"

if __name__ == '__main__':
  main()
