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

    separators = (',', 'et', ';')

    regex = '{separators}'.format(separators='|'.join(separators))
    raw_parcels = re.sub(regex, ',', string)

    abbreviations = raw_parcels.split(',')
    abbreviations = [re.findall('pie|\d+|[a-zA-Z]+', abbr) for abbr in abbreviations]

    return abbreviations


def guess_cadastral_ref(base_reference, abbreviation):
    """
    """
    cadastral_ref = {
        'division': base_reference.get('division'),
        'section': base_reference.get('section')
    }
    return cadastral_ref


class CadastralReference(object):
    """
    """

    def __init__(self, division='', section='', radical='', bis='', exposant='', power='', partie=''):
        """
        """
        self.division = division
        self.section = section
        self.radical = radical
        self.bis = bis
        self.exposant = exposant
        self.power = power
        self.partie = partie
