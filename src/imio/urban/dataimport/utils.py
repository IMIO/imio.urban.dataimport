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
    cadastral_regex = '\W*(?P<radical>\d+)?\W*/?\s*(?P<bis>\d+)?\W*(?P<exposant>[a-zA-Z])?\W*(?P<puissance>\d+)?\W*(?P<partie>pie)?.*'
    abbreviations = [re.match(cadastral_regex, abbr).groups() for abbr in abbreviations]

    return abbreviations


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
        self.partie = bool(partie)

    def __str__(self):
        ref_parts = [
            self.division, self.section, self.radical, self.bis and '/%s' % self.bis,
            self.exposant, self.power, self.partie and 'pie'
        ]
        ref_parts = [part for part in ref_parts if part]

        return ' '.join(ref_parts)

    def __repr__(self):
        ref = self.__str__()
        detail = "div: %s, sec: %s, rad: %s, bis: %s, exp: %s, pow: %s, pie: %s" % (
            self.division,
            self.section,
            self.radical,
            self.bis,
            self.exposant,
            self.power,
            self.partie,
        )
        return ref + '( ' + detail + ' ) '

    def guess_cadastral_reference(self, abbreviation):
        """
        """
