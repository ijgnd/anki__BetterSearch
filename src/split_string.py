"""
Copyright (c): 2018  Rene Schallner
               2020- ijgnd

This file (split_string.py) is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This file is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this file.  If not, see <http://www.gnu.org/licenses/>.


adapted from https://github.com/renerocksai/sublimeless_zk/tree/6738375c0e371f0c2fde0aa9e539242cfd2b4777/src
mainly from utils.py
"""


def remove_leading_whitespace_on_lines(arg):
    search_string = ""
    split = arg.split("\n")
    for l in split:
        search_string += l.lstrip(" ")
    return search_string


def line_list_to_indented_string_basic(list_):
    r = "\n".join(list_)
    r = r.replace("(","(\n").replace(")","\n)").replace("\n\n","\n")
    return r


def line_list_to_indented_string(list_):
    pass
    # TODO


def to_list__quoted_on_same_line(search_string):
    in_quotes = False
    pos = 0
    str_len = len(search_string)
    results = []
    current_snippet = ''
    while pos < str_len:
        if search_string[pos:].startswith('"'):
            in_quotes = not in_quotes
            if not in_quotes:
                # finish this snippet
                if current_snippet:
                    results.append(current_snippet)
                current_snippet = ''
            pos += 1
        elif search_string[pos] in (' ') and not in_quotes:
            # push current snippet
            if current_snippet:
                results.append(current_snippet)
            current_snippet = ''
            pos += 1
        else:
            current_snippet += search_string[pos]
            pos += 1
    if current_snippet:
        results.append(current_snippet)
    return results


def split_to_multiline(string_):
    search_string = remove_leading_whitespace_on_lines(string_)
    results = to_list__quoted_on_same_line(search_string)
    # results_string = line_list_to_indented_string(results)
    results_string = line_list_to_indented_string_basic(results)
    return results_string
