# -*- coding: utf-8 -*-

from imio.urban.dataimport.mapping import table

VALUES_MAPS = {

'type_map': table({
'header'  : ['portal_type',         'foldercategory', 'abreviation'],
'B'       : ['BuildLicence',        'uap',            ''],
'U'       : ['',                    '',               'PU'],  # permis uniques, pas encore dans urban
'Autre'   : ['MiscDemand',          'env',            'E'],  # ancien dossier environnement
'Classe 1': ['EnvClassOne',         '',               'E1'],
'Classe 2': ['EnvClassTwo',         '',               'E2'],
'Classe 3': ['EnvClassThree',       '',               'E3'],
'R'       : ['Declaration',         'dup',            'Decl'],
'L'       : ['ParcelOutLicence',    '',               'PL'],
'1'       : ['UrbanCertificateOne', '',               'CU2'],
'2'       : ['UrbanCertificateTwo', '',               'CU1'],
'A'       : ['MiscDemand',          'apct',           'DD'],
'Z'       : ['MiscDemand',          'apct',           'DD'],
}),

# type de permis, se baser sur la colonne "Rec":
# B: BuildLicence
# R: Declaration
# E: Environnement
# L: ParcelOutLicence
# U: Permis uniques
# 1: Certificats d'urbanisme 1
# 2: Certificats d'urbanisme 2
# Z: MiscDemand


'eventtype_id_map': table({
'header'             : ['decision_event'],
'BuildLicence'       : ['delivrance-du-permis-octroi-ou-refus'],
'ParcelOutLicence'   : ['delivrance-du-permis-octroi-ou-refus'],
'Declaration'        : ['deliberation-college'],
'UrbanCertificateOne': ['octroi-cu1'],
'UrbanCertificateTwo': ['octroi-cu2'],
'MiscDemand'         : ['deliberation-college'],
'EnvClassOne'        : ['decision'],
'EnvClassTwo'        : ['desision'],
'EnvClassThree'      : ['acceptation-de-la-demande'],
}),

'documents_map': {
    'BuildLicence': 'URBA',
    'UniqueLicence': 'PERMIS-UNIQUE',
    'ParcelOutLicence': 'LOTISSEMENT',
    'Declaration': 'REGISTRE-PU',
    'UrbanCertificateOne': 'CU/1',
    'UrbanCertificateTwo': 'CU/2',
    'MiscDemand': 'AUTRE DOSSIER',
    'EnvClassOne': 'ENVIRONNEMENT',
    'EnvClassTwo': 'ENVIRONNEMENT',
    'EnvClassThree': 'ENVIRONNEMENT',
},

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
