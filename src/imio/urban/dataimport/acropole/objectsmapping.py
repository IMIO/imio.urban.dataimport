# -*- coding: utf-8 -*-

from imio.urban.dataimport.acropole.mappers import LicenceFactory, \
    PortalTypeMapper, IdMapper, WorklocationMapper, ParcelsMapper, \
    CompletionStateMapper, ContactFactory, ContactPhoneMapper, StreetAndNumberMapper, \
    ParcelFactory, ParcelDataMapper, UrbanEventFactory, DepositEventMapper, \
    LicenceSubjectMapper, CompleteFolderEventTypeMapper, CompleteFolderDateMapper, DepositDateMapper, \
    DecisionEventTypeMapper, ErrorsMapper, DepositEventIdMapper, DecisionEventIdMapper, \
    DecisionEventDateMapper, ImplantationEventTypeMapper, ImplantationEventIdMapper, \
    ImplantationEventControlDateMapper, ImplantationEventDecisionDateMapper, \
    ImplantationEventDecisionMapper, ContactTitleMapper, ApplicantMapper, ContactIdMapper

from imio.urban.dataimport.MySQL.mapper import MySQLSimpleMapper as SimpleMapper

OBJECTS_NESTING = [
    (
        'LICENCE', [
            ('CONTACT', []),
            ('PARCEL', []),
            ('DEPOSIT EVENT', []),
#            ('COMPLETE FOLDER EVENT', []),
            ('DECISION EVENT', []),
#            ('IMPLANTATION EVENT', []),
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
                    'from': 'DOSSIER_REFCOM',
                    'to': 'reference',
                },
                {
                    'from': 'DOSSIER_REFURB',
                    'to': 'referenceDGATLP',
                },
            ),

            IdMapper: {
                'from': ('WRKDOSSIER_ID',),
                'to': ('id',)
            },

            PortalTypeMapper: {
                'from': ('DOSSIER_TDOSSIERID', 'DOSSIER_TYPEIDENT'),
                'to': ('portal_type', 'folderCategory',)
            },

            LicenceSubjectMapper: {
                'table': 'finddoss_index',
                'KEYS': ('WRKDOSSIER_ID', 'ID'),
                'mappers': {
                    SimpleMapper: (
                        {
                            'from': 'OBJET_KEY',
                            'to': 'licenceSubject',
                        },
                    ),
                },
            },

            WorklocationMapper: {
                'table': 'finddoss_index',
                'KEYS': ('WRKDOSSIER_ID', 'ID'),
                'mappers': {
                    StreetAndNumberMapper: {
                        'from': ('SITUATION_DES',),
                        'to': ('workLocations',)
                    },
                },
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
                'from': 'DOSSIER_OCTROI',
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
            ApplicantMapper: {
                'table': 'cpsn',
                'KEYS': ('WRKDOSSIER_ID', 'CPSN_ID'),
                'mappers': {
                    SimpleMapper: (
                        {
                            'from': 'CPSN_NOM',
                            'to': 'name1',
                        },
                        {
                            'from': 'CPSN_PRENOM',
                            'to': 'name2',
                        },
                        {
                            'from': 'CPSN_FAX',
                            'to': 'fax',
                        },
                        {
                            'from': 'CPSN_EMAIL',
                            'to': 'email',
                        },
                    ),

                    ContactIdMapper: {
                        'from': ('CPSN_NOM', 'CPSN_PRENOM'),
                        'to': 'id',
                    },

                    ContactTitleMapper: {
                        'from': 'CPSN_TYPE',
                        'to': 'personTitle',
                    },

                    ContactPhoneMapper: {
                        'from': ('CPSN_TEL1', 'CPSN_GSM'),
                        'to': 'phone',
                    },

                },
            },
        },
    },

    'PARCEL':
    {
        'factory': [ParcelFactory, {'portal_type': 'PortionOut'}],

        'mappers': {
            ParcelsMapper: {
                'table': 'urbcadastre',
                'KEYS': ('WRKDOSSIER_ID', 'CAD_DOSSIER_ID'),
                'mappers': {
                    ParcelDataMapper: {
                        'from': ('CAD_NOM',),
                        'to': (),
                    },
                },
            },
        },
    },

    'DEPOSIT EVENT':
    {
        'factory': [UrbanEventFactory],

        'mappers': {
            DepositEventMapper: {
                'from': (),
                'to': 'eventtype',
            },

            DepositDateMapper: {
                'from': 'DOSSIER_DATEDEPOT',
                'to': 'eventDate',
            },

            DepositEventIdMapper: {
                'from': (),
                'to': 'id',
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
                'from': (),
                'to': 'eventtype',
            },

            DecisionEventIdMapper: {
                'from': (),
                'to': 'id',
            },

            DecisionEventDateMapper: {
                'from': ('DOSSIER_DATEDELIV'),
                'to': 'decisionDate',
            },
        },
    },

    'IMPLANTATION EVENT':
    {
        'factory': [UrbanEventFactory],

        'allowed_containers': ['BuildLicence'],

        'mappers': {
            ImplantationEventTypeMapper: {
                'from': (),
                'to': 'eventtype',
            },

            ImplantationEventIdMapper: {
                'from': (),
                'to': 'id',
            },

            ImplantationEventControlDateMapper: {
                'from': 'Visite_DateDemande',
                'to': 'eventDate',
            },

            ImplantationEventDecisionDateMapper: {
                'from': 'Visite_DateCollege',
                'to': 'eventDate',
            },

            ImplantationEventDecisionMapper: {
                'from': 'Visite_Resultat',
                'to': 'decisionText',
            },
        },
    },
}
