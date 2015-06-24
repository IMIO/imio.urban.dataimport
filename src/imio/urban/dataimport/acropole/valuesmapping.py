# -*- coding: utf-8 -*-

from imio.urban.dataimport.mapping import table

VALUES_MAPS = {

'type_map': table({
'header': ['portal_type',         'foldercategory'],
-67969  : ['',                    'plainte'   ], #  ne pas reprendre ces dossiers
-62737  : ['ParcelOutLicence',    ''          ],
-49306  : ['BuildLicence',        'art127'    ],
-42575  : ['BuildLicence',        'uap'       ],
-40086  : ['ParcelOutLicence',    ''          ], # pour ces 11 dossiers là, il faudra cocher la catégorie RW à la main
-36624  : ['MiscDemand',          'infraction'], # infractions
-34766  : ['UrbanCertificateOne', ''          ],
-15200  : ['Declaration',         ''          ],
-10362  : ['MiscDemand',          'dpr'       ],
-10200  : ['',                    'uap'       ],  # ne pas reprendre ces dossiers
848193  : ['BuildLicence',        'uap'       ],
848999  : ['ParcelOutLicence',    'lap'       ],
850163  : ['ParcelOutLicence',    'lapm'      ],
855825  : ['BuildLicence',        'uap'       ],
855837  : ['BuildLicence',        'uap'       ],
856646  : ['ParcelOutLicence',    'lapm'      ],
857125  : ['ParcelOutLicence',    'lap'       ],
859150  : ['BuildLicence',        'art127'    ],
}),

# pour la reférence, virer le 'RA' ou 'RG'
# pour la référence, reprendre la colonne DOSSIER_REFCOM

# octroi/refus
'state_map': {
    -46: 'refuse',  # -46 = annulé par le FD
    -49: 'accept',  # -49 = octroyé
    -26: 'accept',  # -26 = octroyé
    -19: 'retire',  # -19 = périmé
    -14: 'accept',  # -14 = octroyé
    -11: 'retire',  # -11 = retiré
    -5: 'refuse',  # -5 = refusé
    -4: 'retire',  # -4 = suspendu
    -3: 'accept',  # -3 = octroyé
    -2: 'retire',  # -2 = abandonné
    -1: '',  # -1 = en cours
    0: 'refuse',  # -1 = refusé
    1: 'accept',  # 1 = octroyé
},

'division_map': {
    '01': '64015',
    '02': '64068',
    '03': '64041',
    '04': '64024',
    '05': '64028',
    '06': '64071',
    '07': '64017',
    '08': '64004',
},

'eventtype_id_map': table({
'header'             : ['decision_event',                       'folder_complete',     'deposit_event',       'send_licence_applicant_event', 'send_licence_fd_event'],
'BuildLicence'       : ['delivrance-du-permis-octroi-ou-refus', 'accuse-de-reception', 'depot-de-la-demande', 'envoi-du-permis-au-demandeur', 'envoi-du-permis-au-fd'],
'ParcelOutLicence'   : ['delivrance-du-permis-octroi-ou-refus', 'accuse-de-reception', 'depot-de-la-demande', 'envoi-du-permis-au-demandeur', 'envoi-du-permis-au-fd'],
'Declaration'        : ['deliberation-college',                 '',                    'depot-de-la-demande', '', ''],
'MiscDemand'         : ['deliberation-college',                 '',                    'depot-de-la-demande', '', ''],
'UrbanCertificateOne': ['octroi-cu1',                           '',                    'depot-de-la-demande', '', ''],
'UrbanCertificateTwo': ['octroi-cu2',                           '',                    'depot-de-la-demande', '', ''],
}),

'titre_map': {
    -1000: 'mister',
    21607: 'misters',
    -1001: 'madam',
    171280: 'ladies',
    -1002: 'miss',
    -1003: 'madam_and_mister',
    676263: 'madam_and_mister',
    850199: 'madam_and_mister',
},

}
