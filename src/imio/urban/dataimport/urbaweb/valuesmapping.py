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
'header'             : ['decision_event',                       'folder_complete',     'deposit_event',       'implantation_event'],
'BuildLicence'       : ['delivrance-du-permis-octroi-ou-refus', 'accuse-de-reception', 'depot-de-la-demande', 'indication-implantation'],
'ParcelOutLicence'   : ['delivrance-du-permis-octroi-ou-refus', 'accuse-de-reception', 'depot-de-la-demande', ''],
'Declaration'        : ['deliberation-college',                 '',                    'depot-de-la-demande', ''],
'MiscDemand'         : ['deliberation-college',                 '',                    'depot-de-la-demande', ''],
}),

'titre_map': {
    'monsieur': 'mister',
    'messieurs': 'misters',
    'madame': 'madam',
    'mesdames': 'ladies',
    'mademoiselle': 'miss',
    'monsieur et madame': 'madam_and_mister',
},
}
