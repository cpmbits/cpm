import argparse
from collections import defaultdict
import textwrap


class LineWrapRawTextHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def __init__(self, *args, options=[], **kwargs):
        self.options = options
        super(LineWrapRawTextHelpFormatter, self).__init__(*args, **kwargs)

    def _split_lines(self, text, width):
        text = self._whitespace_matcher.sub(' ', text).strip()
        return textwrap.wrap(text, width)

    def _get_default_metavar_for_optional(self, action):
        for option in self.options:
            if action.option_strings == option['flags'] and option['arg_format'] is not None:
                return option['arg_format']
        return action.dest

    def _get_default_metavar_for_positional(self, action):
        for option in self.options:
            if action.dest == option['flags'][0] and option['arg_format'] is not None:
                return option['arg_format']
        return action.dest


class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        self.program = {
            key: kwargs[key] for key in kwargs
        }
        self.options = []
        super(ArgumentParser, self).__init__(*args, **kwargs)

    def add_argument(self, *args, arg_format=None, **kwargs):
        super(argparse.ArgumentParser, self).add_argument(*args, **kwargs)
        option = defaultdict(str)
        option['flags'] = [item for item in args]
        for key in kwargs:
            option['arg_format'] = arg_format
            option[key] = kwargs[key]
        self.options.append(option)

    def _get_formatter(self):
        return LineWrapRawTextHelpFormatter(prog=self.prog, options=self.options)
