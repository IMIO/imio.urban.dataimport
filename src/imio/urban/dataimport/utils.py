# -*- coding: utf-8 -*-


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
