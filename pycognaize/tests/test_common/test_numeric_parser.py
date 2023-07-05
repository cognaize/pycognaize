import unittest
import pandas as pd
import math

from pycognaize.common.numeric_parser import NumericParser

class TestNumericParser(unittest.TestCase):
    CONVERT_TO_NUMBER = {
        '$ 458': '458',
        '$458': '458',
        '-$458': '-458',
        '$-458': '-458',
        '(125)': -125,
        '(1.25)': -1.25,
        '(0.01)': -0.01,
        '0.01': 0.01,
        '0.00': 0.0,
        '0,0': 0.0,
        '0,01': 0.01,
      # "12,345'67": 12345.67,
        '0.75%': float('nan'),
        '10, 000': 10000,
        '10,009 ': 10009,
        '10,009.0 ': 10009.0,
        '10,009.01 ': 10009.01,
        '10.009,01 ': 10009.01,
        '10  000': 10000,
        '4,174,352': 4174352,
        '10%': float('nan'),
        '10q 15': float('nan'),
        '-140,753.24': -140753.24,
        '-140,753,100.24': -140753100.24,
        '-140,753,100,100.24': -140753100100.24,
        '-140.753.100.100,24': -140753100100.24,
        '-140.753,24': -140753.24,
        '(125.04)': -125.04,
        '(125.0404)': -1250404,
        '(125.040)': -125040,
        '(1250.40)': -1250.4,
        '(1.250.404.987,65)': -1250404987.65,
        '(1.250.404.98765)': -125040498765,
        '1.250.404.987': 1250404987,
        '-140.753.154,24': -140753154.24,
        '30,456 .67': 30456.67,
        '3,08,520.01': 308520.01,
        '23.096': 23096,
        '234.096,01': 234096.01,
        '234,096.096,096': 234096096096,
        '2,13': 2.13,
        'A 13': float('nan'),
        'A13': float('nan'),
        'A,13': float('nan'),
        'A, 13': float('nan'),
        '^, 13': float('nan'),
        '., 13': float('nan'),
    }

    PARSED_TO_NUMBER = {
        "$458": True,
        "(125)": True,
        "(1.25)": True,
        "0, 01": True,
        "0.75 %": False,
        "10, 000%": False,
        "10 %": False,
        "A13": False
    }
    INFER_SIGN_NUMBER = {
        "(0.01)": -1,
        "-5": -1,
        "944": 1,
        "6.456": 1,
        "(895.5)": -1,
        "-9.045": -1
    }

    PARSE_TO_NUMBER_RAW = {
        "123": 123,
        "3.14": 3.14,
        "1,234": 1234,
        "1,234.56": 1234.56,
        "123.00": 123,
        "3.1400": 3.14,
        "-42": -42,
        "-3.14": -3.14,
        "": ValueError,  # Empty input
        "12a3.45": ValueError,  # Invalid characters
    }
    def test_parse_numeric(self):
        for actual, expected in self.CONVERT_TO_NUMBER.items():
            if expected is not None:
                expected = float(expected)

            if not pd.isna(expected):
                self.assertEqual(
                   expected, NumericParser(actual).parse_numeric()
                )
            else:
                self.assertTrue(pd.isna(NumericParser(actual).parse_numeric()))

    def test_is_numeric(self):
        for actual, expected in self.PARSED_TO_NUMBER.items():
            if expected is not None:
                self.assertEqual(expected, NumericParser(actual).is_numeric())

    def test_infer_sign(self):
        for actual, expected in self.INFER_SIGN_NUMBER.items():
            parser = NumericParser(actual)
            parser.infer_sign()
            self.assertEqual(expected, parser.sign)

if __name__ == '__main__':
    unittest.main()
