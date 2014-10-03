# -*- coding: utf-8 -*-

from imio.urban.dataimport.mapping import table

VALUES_MAPS = {

'type_map': table({
'header': ['portal_type',         'foldercategory', 'abreviation'],
'NC'    : ['BuildLicence',        'uap',            'PU'],
'PP'    : ['BuildLicence',        'upp',            'PU'],
'NH'    : ['BuildLicence',        '',               'PU'],
'LO'    : ['ParcelOutLicence',    '',               'PL'],
'DI'    : ['MiscDemand',          'apct',           'DD'],
'TC'    : ['BuildLicence',        'pu',             'PU'],
'DU'    : ['Declaration',         'dup',            'Decl'],
}),


'eventtype_id_map': table({
'header'             : ['decision_event',                       'folder_complete',     'deposit_event'],
'BuildLicence'       : ['delivrance-du-permis-octroi-ou-refus', 'accuse-de-reception', 'depot-de-la-demande'],
'ParcelOutLicence'   : ['delivrance-du-permis-octroi-ou-refus', 'accuse-de-reception', 'depot-de-la-demande'],
'Declaration'        : ['deliberation-college',                 '',                    'depot-de-la-demande'],
'MiscDemand'         : ['deliberation-college',                 '',                    'depot-de-la-demande'],
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
