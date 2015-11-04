# -*- coding: utf-8 -*-

from imio.urban.dataimport.mapping import table

VALUES_MAPS = {

'type_map': table({
'header': ['portal_type',         'foldercategory', 'abreviation'],
'B'     : ['BuildLicence',        'uap',            ''],
'U'     : ['',                    '',               'PU'],  # permis uniques, pas encore dans urban
'E'     : ['',                    '',               'E'],  # permis d'environnement, comment les distinguer??
'R'     : ['Declaration',         'dup',            'Decl'],
'L'     : ['ParcelOutLicence',    '',               'PL'],
'1'     : ['UrbanCertificateOne', '',               'CU2'],
'2'     : ['UrbanCertificateTwo', '',               'CU1'],
'A'     : ['MiscDemand',          'apct',           'DD'],
'Z'     : ['MiscDemand',          'apct',           'DD'],
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
'UrbanCertificateTwo': ['decision-octroi-refus'],
'MiscDemand'         : ['deliberation-college'],
}),

'documents_map': {
    'BuildLicence': 'URBA',
    'ParcelOutLicence': 'LOTISSEMENT',
    'Declaration': 'REGISTRE-PU',
    'UrbanCertificateOne': 'CU/1',
    'UrbanCertificateTwo': 'CU/2',
    'MiscDemand': 'AUTRE DOSSIER',
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
