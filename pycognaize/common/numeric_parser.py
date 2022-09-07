"""Defines NumericParser for parsing a number string into a float values"""
import re
from typing import Union


class NumericParser:
    """
    Parser for any kind of text input into a corresponding format.
    Numeric data is assumed to be valid and clean.
    Use NumericColumnFormatter for validating your data.
    """
    numeric = (r"(^0+$|^[\\[\\(+-]*(([1-9][0-9]{0,2}([.,][0-9]{3})*)|[0-9]"
               r"|[1-9][0-9]+)([,.][0-9]*)?[\]\)]*$)")
    delimiters = r"[.,]"
    REGEX_NO_ALPHANUM_CHARS = re.compile(r'[^a-zA-Z0-9)\[\](-.,]')

    brackets = r"[\[\]\(\)]"
    # match a pattern with whitespace followed by either a single comma
    #   from the left or whitespace surrounded by numbers
    single_white_space_regex = "(?<=\\d)(,{0,1}) {1,2}(?=\\d)"

    def __init__(self, raw: str):
        """Takes string as an input and create ValueParser object
        :param raw: input raw string representation of the number

        """

        raw = re.sub(self.single_white_space_regex, '', raw)
        raw = raw.replace('$', '').strip()
        self.raw = raw
        self.format = None
        self.parsed = None
        self.value_type = None
        self._separators = None
        self._separated_digits = None
        self.sign = None
        self.removed_sign = False

    def __get_separated_digits_and_separators(self):
        """Assigns the list of separators and separated digits to self.
            Ex. self.raw=12,345.6
            [',','.']->self.separators
            ['12', '345', '6']->self._separated_digits
            Applicable only if type is numeric
        """
        # TODO: check if strip_value is used properly
        val = self.REGEX_NO_ALPHANUM_CHARS.sub('', self.raw)
        val = re.sub(self.brackets, '', val)
        val = self.strip_value(val)
        # strip from multiple zeros. ex: 000 -> 0
        val = val[:-1].lstrip('0') + val[-1]
        self._separators = re.findall(self.delimiters, val)
        self._separated_digits = re.split(self.delimiters, val)

    def infer_sign(self):
        """
        Infer the sign of the number either with brackets
        or a trailing minus sign"""
        self.sign = 1
        if self.raw.startswith('(') and self.raw.endswith(')'):
            self.sign = -1
            self.remove_sign_parentheses()

        elif self.raw.lstrip().startswith('-'):
            self.sign = -1
            self.remove_dash_sign()

    def remove_dash_sign(self):
        self.raw = self.raw.lstrip().lstrip('-')
        self.removed_sign = True

    def remove_sign_parentheses(self):
        self.raw = self.raw.lstrip('(')
        self.raw = self.raw.rstrip(')')
        self.removed_sign = True

    def parse_regular_float(self):
        """Parse Like a regular float number"""
        # noinspection PyBroadException
        try:
            # try parsing like a regular float number
            # if it doesn't work use more complicated logic
            if self.removed_sign:
                self.parsed = float(self.raw.strip()) * self.sign
            else:
                self.parsed = float(self.raw.strip())

            return self.parsed
        except Exception:
            return None

    def parse_regular_float_with_semicolon(self):
        """Parse Like a regular float number with semicolon"""
        # noinspection PyBroadException
        try:
            if self.raw.strip().startswith('0'):
                # try parsing like a regular float number after replacing
                # commas if it doesn't work use more complicated logic
                if self.removed_sign:
                    self.parsed = float(self.raw.strip().replace(',', '.')) \
                                  * self.sign
                else:
                    self.parsed = float(self.raw.strip().replace(',', '.'))

                return self.parsed
        except Exception:
            return None

    def parse_numeric(self) -> Union[int, float]:
        """
        Parse the raw data, and return parsed numeric value
        and get the numeric, separator and value type of the raw data

        :return: Parsed float or int value
        """
        self.infer_sign()

        parse_float = self.parse_regular_float()
        if parse_float is not None:
            return parse_float
        else:
            parse_float_semicolon = self.parse_regular_float_with_semicolon()
            if parse_float_semicolon is not None:
                return parse_float_semicolon

        if '%' in self.raw:
            return float('nan')

        try:
            self.__get_separated_digits_and_separators()

            self.parsed = self.parse_raw_numeric()
            self.parsed = self.parsed * self.sign
        except Exception:
            return float('nan')
        return self.parsed

    def parse_raw_numeric(self) -> Union[int, float]:
        """Used for parsing raw text without getting any context
            from the column
        """
        if len(self._separators) == 0:
            return int(self._separated_digits[0])
        elif len(self._separated_digits[-1]) != 3:
            int_part = int(''.join(self._separated_digits[:-1]))
            dec_part = float('0.' + self._separated_digits[-1])
            return int_part + dec_part
        elif len(self._separators
                 ) > 1 and self._separators[0] != self._separators[-1]:
            int_part = int(''.join(self._separated_digits[:-1]))
            dec_part = float('0.' + self._separated_digits[-1])
            return int_part + dec_part
        else:
            return int(''.join(self._separated_digits))

    @staticmethod
    def strip_value(text: str):
        """Strip non-numeric characters from a string representing a number

        :param str text: Input string representing a number
        :return: String with stripped non-numeric characters
        :rtype str:
        """
        currencies = u'$¢£¤¥֏؋৲৳৻૱௹฿៛₠₡₢₣₤₥₦₧₨₩₪₫€₭₮₯₰₱₲₳₴₵₶₷₸₹₺₻₼₽₾꠸﷼﹩＄￠￡￥￦'
        text = text.strip(
            '\n\r\t ' + currencies + "'+*/%^_:;'\"\\|").rstrip('—-.,')
        text = text.replace(' ', '')
        return text

    def is_numeric(self) -> bool:
        """Determines if the text is a representation of a numeric value

        :return: True if the raw text corresponds to numeric representation
        """
        if re.match(self.numeric,
                    self.strip_value(self.raw)) and '%' not in self.raw:
            return True
        return False
