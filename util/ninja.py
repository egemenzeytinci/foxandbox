import html


class Ninja:
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
