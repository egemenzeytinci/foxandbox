import html
import numpy as np


class Ninja:
    @staticmethod
    def float_range(lower, upper, step):
        """
        Float range function

        :param int lower: lower point
        :param int upper: upper point
        :param float step: step value
        :return: list of values by lower, upper and step values
        :rtype: list
        """
        return list(np.arange(lower, upper, step))

    @staticmethod
    def format_minutes(minutes):
        """
        Format minutes to hour and minutes e.g. 1h 20m

        :param int minutes: minutes
        :return: formatted minutes
        :rtype: str
        """
        h = minutes // 60
        m = minutes - (h * 60)

        return f'{h}h {m}m' if h != 0 else f'{m}m'

    @staticmethod
    def unescape(text):
        """
        Unescape html special characters e.g. &apos; to '

        :param str text: html text
        :return unescaped html text
        :rtype: str
        """
        return html.unescape(text)
