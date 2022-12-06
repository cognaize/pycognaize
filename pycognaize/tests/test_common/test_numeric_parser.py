import unittest
import pandas as pd
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

    def test_parse_numeric(self):
        for actual, expected in self.CONVERT_TO_NUMBER.items():
            if expected is not None:
                expected = float(expected)

            if not pd.isna(expected):
                self.assertEqual(
                    NumericParser(actual).parse_numeric(), expected
                )
            else:
                self.assertTrue(pd.isna(NumericParser(actual).parse_numeric()))


if __name__ == '__main__':
    unittest.main()
