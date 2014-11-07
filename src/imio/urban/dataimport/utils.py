# -*- coding: utf-8 -*-

import re


def normalizeDate(date):
    if not date:
        return ''
    parts = date.split()[0].split('/')
    century = parts[2] > '40' and '19' or '20'
    return '%s/%s/%s%s' % (parts[1], parts[0], century, parts[2])


def cleanAndSplitWord(word):
    clean_word = word.replace('\'', ' ').replace(',', ' ').replace('-', ' ').replace('.', ' ')\
        .replace(';', ' ').replace('(', ' ').replace(')', ' ').replace(':', ' ').lower().split()
    return clean_word


def identify_parcel_abbreviation(string):
    """
    """

    separators = (',', 'et')

    regex = '(.+?(?:{separators})|.+)'.format(separators='|'.join(separators))

    abbreviations = re.findall(regex, string)

    split_regex = '(\d+|[a-zA-Z]+|/\s*\d)'
    abbreviations = [re.findall(split_regex, abbr) for abbr in abbreviations]

    return parcels


def create_cadastral_ref(base_reference, abbreviation):
    """
    """
    cadastral_ref = {
        'division': base_reference.get('division')
        'section': base_reference.get('section')
    }
