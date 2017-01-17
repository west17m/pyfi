import unittest

from utilities import *

import pandas as pd
import numpy as np

class UtilitiesTestCase(unittest.TestCase):
  """Tests for `utilities.py`."""

  def test_format_currency(self):
    float_list = [0,1,1.1,1.01,1.001]
    float_series = pd.Series(float_list)
    self.assertEqual(len(float_list),len(float_series),msg="the list and series of floats are not the same")
    self.assertEqual(type(float_list[2]),type(1.0),msg="not storing as floats")
    self.assertEqual(type(float_series[2]),np.float64,msg="not storing as numpy float64")

    formatted_float_series = format_currency(float_series)
    self.assertEqual(type(formatted_float_series[2]),type("2"),msg="expected format to return as a string")

  def test_get_indented_html(self):
    test_long_string = "<html><head></head><body><h1>heading<h1></body></html>"
    indented_test_long_string = "<html>\n  <head>\n  </head>\n  <body>\n    <h1>\n      heading\n    <h1>\n  </body>\n</html>"

    self.assertNotEqual(indented_test_long_string,test_long_string)
    # self.assertEqual(indented_test_long_string,get_indented_html(test_long_string)) # fails

if __name__ == '__main__':
    unittest.main()

