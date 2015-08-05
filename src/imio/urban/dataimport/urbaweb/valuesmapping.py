# -*- coding: utf-8 -*-

from imio.urban.dataimport.mapping import table

VALUES_MAPS = {

'type_map': table({
'header': ['portal_type',         'foldercategory', 'abreviation'],
'B'     : ['BuildLicence',        'uap',            'uap'],
'U'     : ['BuildLicence',        'uap',            'PU'],
'R'     : ['Declaration',         'dup',            'Decl'],
'L'     : ['ParcelOutLicence',    '',               'PL'],
'Z'     : ['MiscDemand',          'apct',           'DD'],
}),

# type de permis, se baser sur la colonne "Rec":
# B: BuildLicence
# R: Declaration
# E:
# L: ParcelOutLicence
# U: Permis uniques
# Z: MiscDemand


'eventtype_id_map': table({
'header'             : ['decision_event'],
'BuildLicence'       : ['delivrance-du-permis-octroi-ou-refus'],
'ParcelOutLicence'   : ['delivrance-du-permis-octroi-ou-refus'],
'Declaration'        : ['deliberation-college'],
'MiscDemand'         : ['deliberation-college'],
}),

'titre_map': {
    'monsieur': 'mister',
    'messieurs': 'misters',
    'madame': 'madam',
    'mesdames': 'ladies',
    'mademoiselle': 'miss',
    'monsieur et madame': 'madam_and_mister',
},

'externaldecisions_map': {
    'F': 'favorable',
    'FC': 'favorable-conditionnel',
    'D': 'defavorable',
    'RF': 'favorable-defaut',
},
}
