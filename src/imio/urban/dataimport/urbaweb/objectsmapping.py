# -*- coding: utf-8 -*-

from imio.urban.dataimport.urbaweb.mappers import LicenceFactory, \
    PortalTypeMapper, IdMapper, ReferenceMapper, WorklocationMapper, ObservationsMapper, \
    ArchitectMapper, GeometricianMapper, CompletionStateMapper, ContactFactory, ContactNameMapper, \
    ContactTitleMapper, ContactSreetMapper, ContactNumberMapper, ContactPhoneMapper, \
    ContactIdMapper, ParcelFactory, ParcelDataMapper, UrbanEventFactory, DepositEventTypeMapper, \
    DepositDateMapper, CompleteFolderEventTypeMapper, CompleteFolderDateMapper, \
    DecisionEventTypeMapper, DecisionDateMapper, NotificationDateMapper, DecisionMapper, \
    ErrorsMapper

from imio.urban.dataimport.access.mapper import AccessSimpleMapper as SimpleMapper

OBJECTS_NESTING = [
    (
        'LICENCE', [
            ('CONTACT', []),
            ('PARCEL', []),
#            ('DEPOSIT EVENT', []),
#            ('COMPLETE FOLDER EVENT', []),
#            ('DECISION EVENT', []),
        ],
    ),
]

FIELDS_MAPPINGS = {
    'LICENCE':
    {
        'factory': [LicenceFactory],

        'mappers': {
            SimpleMapper: (
                {
                    'from': 'LibNat',
                    'to': 'licenceSubject',
                },
            ),

            IdMapper: {
                'from': ('Cle_Urba',),
                'to': ('id',)
            },

            PortalTypeMapper: {
                'from': ('TypeNat',),
                'to': ('portal_type', 'folderCategory',)
            },

            ReferenceMapper: {
                'from': ('Numero'),
                'to': ('reference',)
            },

            WorklocationMapper: {
                'from': ('C_Adres', 'C_Num', 'C_Code', 'C_Loc'),
                'to': ('workLocations',)
            },

            ObservationsMapper: {
                'from': ('Memo_Urba', 'memo_Autorisation', 'memo_Autorisation2'),
                'to': ('description',),
            },

#            ArchitectMapper: {
#                'allowed_containers': ['BuildLicence'],
#                'from': ('NomArchitecte',),
#                'to': ('architects',)
#            },

#            GeometricianMapper: {
#                'allowed_containers': ['ParcelOutLicence'],
#                'from': ('Titre', 'Nom', 'Prenom'),
#                'to': ('geometricians',)
#            },

            CompletionStateMapper: {
                'from': ('Autorisa', 'Refus', 'TutAutorisa', 'TutRefus'),
                'to': (),  # <- no field to fill, its the workflow state that has to be changed
            },

            ErrorsMapper: {
                'from': (),
                'to': ('description',),  # log all the errors in the description field
            }
        },
    },

    'CONTACT':
    {
        'factory': [ContactFactory],

        'mappers': {
            SimpleMapper: (
                {
                    'from': 'D_Prenom',
                    'to': 'name2',
                },
                {
                    'from': 'D_Code',
                    'to': 'zipcode',
                },
                {
                    'from': 'D_Loc',
                    'to': 'city',
                },
            ),

            ContactTitleMapper: {
                'from': ('Civi', 'Civi2'),
                'to': 'personTitle',
            },

            ContactNameMapper: {
                'from': ('D_Nom', 'Civi2'),
                'to': 'name1',
            },

            ContactSreetMapper: {
                'from': ('D_Adres'),
                'to': 'street',
            },

            ContactNumberMapper: {
                'from': ('D_Adres'),
                'to': 'number',
            },

            ContactPhoneMapper: {
                'from': ('D_Tel', 'D_GSM'),
                'to': 'phone',
            },

            ContactIdMapper: {
                'from': ('D_Nom', 'D_Prenom'),
                'to': 'id',
            },
        },
    },

    'PARCEL':
    {
        'factory': [ParcelFactory, {'portal_type': 'PortionOut'}],

        'mappers': {
            ParcelDataMapper: {
                'from': ('Cadastre', 'Cadastre_2', 'Section', 'Division'),
                'to': (),
            },
        },
    },

    'DEPOSIT EVENT':
    {
        'factory': [UrbanEventFactory],

        'mappers': {
            DepositEventTypeMapper: {
                'from': (),
                'to': 'eventtype',
            },

            DepositDateMapper: {
                'from': 'DateRecDem',
                'to': 'eventDate',
            }
        },
    },

    'COMPLETE FOLDER EVENT':
    {
        'factory': [UrbanEventFactory],

        'allowed_containers': ['BuildLicence', 'ParcelOutLicence'],

        'mappers': {
            CompleteFolderEventTypeMapper: {
                'from': (),
                'to': 'eventtype',
            },

            CompleteFolderDateMapper: {
                'from': 'AvisDossierComplet',
                'to': 'eventDate',
            },
        },
    },

    'DECISION EVENT':
    {
        'factory': [UrbanEventFactory],

        'mappers': {
            DecisionEventTypeMapper: {
                'from': 'Refus',
                'to': 'eventtype',
            },

            DecisionDateMapper: {
                'from': 'DateDecisionCollege',
                'to': 'decisionDate',
            },

            NotificationDateMapper: {
                'from': 'DateNotif',
                'to': 'eventDate',
            },

            DecisionMapper: {
                'from': 'Refus',
                'to': 'decision',
            },
        },
    },
}
