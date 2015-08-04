# -*- coding: utf-8 -*-

from imio.urban.dataimport.urbaweb.mappers import LicenceFactory, \
    PortalTypeMapper, IdMapper, ReferenceMapper, WorklocationMapper, ObservationsMapper, \
    CompletionStateMapper, ContactFactory, ContactNameMapper, \
    ContactTitleMapper, ContactSreetMapper, ContactNumberMapper, ContactPhoneMapper, \
    ContactIdMapper, ParcelFactory, ParcelDataMapper, UrbanEventFactory, DepositEventMapper, \
    CompleteFolderEventTypeMapper, CompleteFolderDateMapper, DepositDate_1_Mapper, DepositDate_2_Mapper, \
    DecisionEventTypeMapper, ErrorsMapper, DepositEvent_1_IdMapper, DepositEvent_2_IdMapper, InquiryStartDateMapper, \
    InquiryEndDateMapper, InquiryReclamationNumbersMapper, InquiryArticlesMapper, DecisionEventIdMapper, \
    DecisionEventDateMapper, DecisionEventDecisionMapper, DecisionEventTitleMapper, DecisionEventNotificationDateMapper, \
    ImplantationEventTypeMapper, ImplantationEventIdMapper, ImplantationEventControlDateMapper, ImplantationEventDecisionDateMapper, \
    ImplantationEventDecisionMapper, TechnicalConditionsMapper, ParcellingsMapper, ParcellingUIDMapper, IsInSubdivisionMapper, \
    PcaMapper, PcaUIDMapper, IsInPcaMapper

from imio.urban.dataimport.access.mapper import AccessSimpleMapper as SimpleMapper

OBJECTS_NESTING = [
    (
        'LICENCE', [
            ('CONTACT', []),
            ('PARCEL', []),
            ('DEPOSIT EVENT 1', []),
            ('DEPOSIT EVENT 2', []),
            ('COMPLETE FOLDER EVENT', []),
            ('DECISION EVENT', []),
            ('IMPLANTATION EVENT', []),
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
                    'from': 'Urbanisme',
                    'to': 'referenceDGATLP',
                },
                {
                    'from': 'LibNat',
                    'to': 'licenceSubject',
                },
                {
                    'from': 'Zon',
                    'to': 'folderZone',
                },
            ),

            IdMapper: {
                'from': ('Cle_Urba',),
                'to': ('id',)
            },

            PortalTypeMapper: {
                'from': ('Rec', 'Art127'),
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

            InquiryStartDateMapper: {
                'allowed_containers': ['BuildLicence', 'ParcelOutLicence'],
                'from': 'E_Datdeb',
                'to': 'investigationStart',
            },

            InquiryEndDateMapper: {
                'allowed_containers': ['BuildLicence', 'ParcelOutLicence'],
                'from': 'E_Datfin',
                'to': 'investigationEnd',
            },

            InquiryReclamationNumbersMapper: {
                'allowed_containers': ['BuildLicence', 'ParcelOutLicence'],
                'from': 'NBRec',
                'to': 'investigationWriteReclamationNumber',
            },

            InquiryArticlesMapper: {
                'allowed_containers': ['BuildLicence', 'ParcelOutLicence'],
                'from': 'Enquete',
                'to': 'investigationArticles',
            },

            ObservationsMapper: {
                'from': 'Memo_Urba',
                'to': 'description',
            },

            TechnicalConditionsMapper: {
                'from': ('memo_Autorisation', 'memo_Autorisation2'),
                'to': 'locationTechnicalConditions',
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

            ParcellingsMapper: {
                'table': 'LOTISSEM',
                'KEYS': ('Cle_Urba', 'Cle_Lot'),
                'mappers': {
                    SimpleMapper: (
                        {
                            'from': 'Lot',
                            'to': 'subdivisionDetails',
                        },
                    ),
                    ParcellingUIDMapper: {
                        'from': 'Lotis',
                        'to': 'parcellings',
                    },

                    IsInSubdivisionMapper: {
                        'from': 'Lotis',
                        'to': 'isInSubdivision',
                    }
                },
            },

            PcaMapper: {
                'table': 'PPA',
                'KEYS': ('Cle_Urba', 'Cle_PPA'),
                'mappers': {
                    SimpleMapper: (
                        {
                            'from': 'PPA_Affectation',
                            'to': 'pcaDetails',
                        },
                    ),
                    PcaUIDMapper: {
                        'from': 'PPA',
                        'to': 'pca',
                    },

                    IsInPcaMapper: {
                        'from': 'PPA',
                        'to': 'isInPCA',
                    }
                },
            },

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

    'DEPOSIT EVENT 1':
    {
        'factory': [UrbanEventFactory],

        'mappers': {
            DepositEventMapper: {
                'from': (),
                'to': 'eventtype',
            },

            DepositDate_1_Mapper: {
                'from': 'Recepisse',
                'to': 'eventDate',
            },

            DepositEvent_1_IdMapper: {
                'from': (),
                'to': 'id',
            }
        },
    },

    'DEPOSIT EVENT 2':
    {
        'factory': [UrbanEventFactory],

        'mappers': {
            DepositEventMapper: {
                'from': (),
                'to': 'eventtype',
            },

            DepositDate_2_Mapper: {
                'from': 'Recepisse2',
                'to': 'eventDate',
            },

            DepositEvent_2_IdMapper: {
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
                'from': 'Date_Rec',
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
                'from': ('Autorisa', 'Refus', 'TutAutorisa', 'TutRefus'),
                'to': 'decisionDate',
            },

            DecisionEventDecisionMapper: {
                'from': ('Autorisa', 'Refus', 'TutAutorisa', 'TutRefus'),
                'to': 'decision',
            },

            DecisionEventTitleMapper: {
                'from': ('TutAutorisa', 'TutRefus'),
                'to': 'Title',
            },

            DecisionEventNotificationDateMapper: {
                'from': 'Notifica',
                'to': 'eventDate',
            }
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
