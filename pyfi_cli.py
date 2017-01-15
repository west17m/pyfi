#!/usr/bin/env python

from ledger import *
from utilities import *
from pyfi_html import *

class PyFiCLI():
  """
    Command line interface to PyFi
  """
  ledger   = None
  accounts = None

  ledger_file =   None
  accounts_file = None

  def __init__(self,ledger_file,account_file):

    self.ledger_file   = ledger_file
    self.accounts_file = account_file

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
        a = PyFiHTML(
          self.ledger_file,
          self.accounts_file)
        a.render()

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

