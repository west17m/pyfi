#!/usr/bin/env python

class PyFiCLI():
  """
    Command line interface to PyFi
  """
  ledger   = None
  accounts = None

  def __init__(self,ledger_file,account_file):
    self.ledger = Ledger(ledger_file,account_file)
    self.accounts = account_file

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
      accounts['balance'] = accounts['balance'].map('{:,.2f}'.format)

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
        self.ledger.print_table(accounts[['num','account','balance']])
        choice = raw_input('Enter your input: ')
        if choice == "q":
          break
        elif choice == "p":
          break
        else:
          account = accounts.loc[accounts.loc[:,'num'] == int(choice)]['account'].values[0]
          # print account
          self.ledger.print_register_by_account(account)
          raw_input("Press Enter to continue...")
      elif choice == "2":
        self.ledger.print_register_by_account('income')
        raw_input("Press Enter to continue...")
      elif choice == "3":
        self.ledger.print_root_account()
        raw_input("Press Enter to continue...")
      elif choice == "4":
        self.ledger.print_all_transactions()
        raw_input("Press Enter to continue...")
      elif choice == "5":
        self.ledger.print_table(accounts[['num','account','balance']])
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
        a['balance'] = a['balance'].map('{:,.2f}'.format)
        a['amount']  = a['amount'].map('{:,.2f}'.format)
        self.ledger.print_table(a)
      elif choice == "7":
        self.ledger.render_ledger()

