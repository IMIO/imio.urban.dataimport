# -*- coding: utf-8 -*-

import copy

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


def identify_parcel_abbreviations(string):
    """
    """

    separators = (',', 'et', ';')

    regex = '{separators}'.format(separators='|'.join(separators))
    raw_parcels = re.sub(regex, ',', string)

    abbreviations = raw_parcels.split(',')

    return abbreviations


def parse_cadastral_reference(string):
    cadastral_regex = '\W*(?P<division>\d+)?\W*(?P<section>[A-Z])?\W*(?P<radical>\d+)?\W*/?\s*(?P<bis>\d+)?\W*(?P<exposant>[a-zA-Z])?\W*(?P<puissance>\d+)?\W*(?P<partie>pie)?.*'

    abbreviations = re.match(cadastral_regex, string)

    if abbreviations:
        return abbreviations.groups()


def guess_cadastral_reference(base_reference, abbreviation):
    """
    """
    regex = '\W*(?P<radical>\d+)?\s*(?P<bis>/\s*\d+)?\W*(?P<exposant>[a-zA-Z](?![a-zA-Z]))?\W*(?P<puissance>\d+)?\W*(?P<partie>pie)?\W*'

    parsed_abbr = re.match(regex, abbreviation).groups()

    cadastral_ref = copy.deepcopy(base_reference)

    update = False

    for i, attribute in enumerate(['radical', 'bis', 'exposant', 'puissance', 'partie']):
        value = parsed_abbr[i]

        if value:
            update = True
            if i == 1:  # for the 'bis', only keep the number
                value = value[-1]
            elif i == 4:  # 'partie' should be boolean
                value = bool(value[4])

        if update:
            setattr(cadastral_ref, attribute, value)

    return cadastral_ref


class CadastralReference(object):
    """
    """

    def __init__(self, division='', section='', radical='', bis='', exposant='', puissance='', partie=''):
        """
        """
        self.division = division or ''
        self.section = section and section.upper() or ''
        self.radical = radical or ''
        self.bis = bis or ''
        self.exposant = exposant and exposant.upper() or ''
        self.puissance = puissance and puissance.upper() or ''
        self.partie = bool(partie)

    def __str__(self):
        ref_parts = [
            self.division, self.section, self.radical, self.bis and '/%s' % self.bis,
            self.exposant, self.puissance, self.partie and 'pie'
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
            self.puissance,
            self.partie,
        )
        return ref + '( ' + detail + ' ) '

    def to_dict(self):
        return self.__dict__.copy()

    @property
    def id(self):
        return str(self).replace(' ', '').lower()

    def has_same_attribute_values(self, ref_dict):
        common_keys = set(ref_dict.keys()).intersection(set(self.__dict__.keys()))

        for key in common_keys:
            if ref_dict[key] != self.__dict__[key]:
                return False

        return True
