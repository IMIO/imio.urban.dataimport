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
    PcaMapper, PcaUIDMapper, IsInPcaMapper, InquiryEventTypeMapper, InquiryDateMapper, InquiryEventIdMapper, \
    ClaimantFactory, ClaimantIdMapper, ClaimantTitleMapper, ClaimantSreetMapper, ClaimantNumberMapper, ClaimantsMapper, \
    PrimoEventTypeMapper, PrimoDateMapper, SecondRWEventTypeMapper, SecondRWEventDateMapper, SecondRWDecisionDateMapper, \
    SecondRWReceiptDateMapper, SecondRWDecisionMapper, WorkTypeMapper, IncompleteFolderEventTypeMapper, \
    IncompleteFolderDateMapper, ComplementReceiptEventTypeMapper, ComplementReceiptDateMapper, OpinionMakersTableMapper, \
    OpinionMakersMapper, DocumentsFactory, DocumentsMapper, AskOpinionsMapper, AskOpinionTableMapper, LinkedInquiryMapper, \
    AdditionalContactMapper, AdditionalContactIdMapper, AdditionalContactTitleMapper, EnvLicenceSubjectMapper, \
    EnvRubricsMapper, DocumentFileMapper, DocumentIdMapper, SuspensionsMapper, SuspensionEventTypeMapper, SuspensionEventReasonMapper, \
    SuspensionEventIdMapper, SuspensionEventFactory

from imio.urban.dataimport.access.mapper import AccessSimpleMapper as SimpleMapper

OBJECTS_NESTING = [
    (
        'LICENCE', [
            ('CONTACT', []),
            ('ADDITIONAL CONTACTS', []),
            ('PARCEL', []),
            ('DEPOSIT EVENT 1', []),
            ('DEPOSIT EVENT 2', []),
            ('INCOMPLETE FOLDER EVENT', []),
            ('COMPLEMENT RECEIPT EVENT', []),
            ('COMPLETE FOLDER EVENT', []),
            ('PRIMO RW EVENT', []),
            ('INQUIRY EVENT', [
                ('CLAIMANT', []),
            ]),
            ('ASK OPINION EVENTS', []),
            ('SECOND RW EVENT', []),
            ('DECISION EVENT', []),
            ('IMPLANTATION EVENT', []),
            ('SUSPENSION EVENT', []),
            ('DOCUMENTS', []),
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
                'from': 'Cle_Urba',
                'to': 'id',
            },

            PortalTypeMapper: {
                'from': ('Rec', 'Art127'),
                'to': ('portal_type', 'folderCategory',)
            },

            EnvLicenceSubjectMapper: {
                'allowed_containers': ['EnvClassOne', 'EnvClassTwo', 'EnvClassThree'],
                'table': 'ENVIRONNEMENT',
                'KEYS': ('Cle_Urba', 'Cle_Env'),
                'mappers': {
                    SimpleMapper: (
                        {
                            'from': 'NatureEtablissement',
                            'to': 'licenceSubject',
                        },
                    ),
                }
            },

            ReferenceMapper: {
                'from': 'Numero',
                'to': 'reference',
            },

            WorklocationMapper: {
                'from': ('C_Adres', 'C_Num', 'C_Code', 'C_Loc'),
                'to': 'workLocations',
            },

            WorkTypeMapper: {
                'allowed_containers': ['BuildLicence', 'ParcelOutLicence'],
                'from': 'Code_220+',
                'to': 'workType',
            },

            InquiryStartDateMapper: {
                'allowed_containers': ['BuildLicence', 'ParcelOutLicence', 'UrbanCertificateTwo'],
                'from': 'E_Datdeb',
                'to': 'investigationStart',
            },

            InquiryEndDateMapper: {
                'allowed_containers': ['BuildLicence', 'ParcelOutLicence', 'UrbanCertificateTwo'],
                'from': 'E_Datfin',
                'to': 'investigationEnd',
            },

            InquiryReclamationNumbersMapper: {
                'allowed_containers': ['BuildLicence', 'ParcelOutLicence', 'UrbanCertificateTwo'],
                'from': 'NBRec',
                'to': 'investigationWriteReclamationNumber',
            },

            InquiryArticlesMapper: {
                'allowed_containers': ['BuildLicence', 'ParcelOutLicence', 'UrbanCertificateTwo'],
                'from': 'Enquete',
                'to': 'investigationArticles',
            },

            AskOpinionTableMapper: {
                'allowed_containers': ['BuildLicence', 'ParcelOutLicence', 'UrbanCertificateTwo', 'MiscDemand'],
                'table': 'SERVICES',
                'KEYS': ('Cle_Urba', 'Cle_Serv'),
                'mappers': {
                    AskOpinionsMapper: {
                        'from': ('Org1', 'Org3', 'Org4', 'Org5', 'Org6', 'Org7', 'Org8', 'Org9', 'Org10'),
                        'to': 'solicitOpinionsTo',
                    }
                }
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

            EnvRubricsMapper: {
                'allowed_containers': ['EnvClassOne', 'EnvClassTwo', 'EnvClassThree'],
                'from': 'LibNat',
                'to': 'description',
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

    'ADDITIONAL CONTACTS':
    {
        'factory': [ContactFactory],

        'mappers': {
            AdditionalContactMapper: {
                'table': 'COHABITANT',
                'KEYS': ('Cle_Urba', 'Cle_Co'),
                'mappers': {
                    SimpleMapper: (
                        {
                            'from': 'CONom',
                            'to': 'name1',
                        },
                        {
                            'from': 'COPrenom',
                            'to': 'name2',
                        },
                        {
                            'from': 'COCode',
                            'to': 'zipcode',
                        },
                        {
                            'from': 'COLoc',
                            'to': 'city',
                        },
                        {
                            'from': 'COTel',
                            'to': 'phone',
                        },

                    ),

                    AdditionalContactTitleMapper: {
                        'from': 'CiviC',
                        'to': 'personTitle',
                    },

                    AdditionalContactIdMapper: {
                        'from': ('CONom', 'COPrenom'),
                        'to': 'id',
                    },
                },
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

    'INCOMPLETE FOLDER EVENT':
    {
        'factory': [UrbanEventFactory],

        'allowed_containers': ['BuildLicence', 'ParcelOutLicence', 'UrbanCertificateTwo'],

        'mappers': {
            IncompleteFolderEventTypeMapper: {
                'from': (),
                'to': 'eventtype',
            },

            IncompleteFolderDateMapper: {
                'from': 'P_Datdem',
                'to': 'eventDate',
            },
        },
    },

    'COMPLEMENT RECEIPT EVENT':
    {
        'factory': [UrbanEventFactory],

        'allowed_containers': ['BuildLicence', 'ParcelOutLicence'],

        'mappers': {
            ComplementReceiptEventTypeMapper: {
                'from': (),
                'to': 'eventtype',
            },

            ComplementReceiptDateMapper: {
                'from': 'P_Datrec',
                'to': 'eventDate',
            },
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

    'PRIMO RW EVENT':
    {
        'factory': [UrbanEventFactory],

        'allowed_containers': ['BuildLicence', 'ParcelOutLicence'],

        'mappers': {
            PrimoEventTypeMapper: {
                'from': (),
                'to': 'eventtype',
            },

            PrimoDateMapper: {
                'from': 'UR_Datenv',
                'to': 'eventDate',
            },
        },
    },

    'INQUIRY EVENT':
    {
        'factory': [UrbanEventFactory],

        'allowed_containers': ['BuildLicence', 'ParcelOutLicence', 'UrbanCertificateTwo'],

        'mappers': {
            InquiryEventTypeMapper: {
                'from': (),
                'to': 'eventtype',
            },

            InquiryEventIdMapper: {
                'from': (),
                'to': 'id',
            },

            InquiryDateMapper: {
                'from': 'E_Datdeb',
                'to': 'eventDate',
            },
        },
    },

    'ASK OPINION EVENTS':
    {
        'factory': [UrbanEventFactory],

        'allowed_containers': ['BuildLicence', 'ParcelOutLicence', 'UrbanCertificateTwo', 'MiscDemand'],

        'mappers': {
            OpinionMakersTableMapper: {
                'table': 'SERVICES',
                'KEYS': ('Cle_Urba', 'Cle_Serv'),
                'mappers': {
                    OpinionMakersMapper: {
                        'from': (
                            'Org1', 'Cont1', 'Rec1', 'Ref1',
                            'Org2', 'Cont2', 'Rec2', 'Ref2',
                            'Org3', 'Cont3', 'Rec3', 'Ref3',
                            'Org4', 'Cont4', 'Rec4', 'Ref4',
                            'Org5', 'Cont5', 'Rec5', 'Ref5',
                            'Org6', 'Cont6', 'Rec6', 'Ref6',
                            'Org7', 'Cont7', 'Rec7', 'Ref7',
                            'Org8', 'Cont8', 'Rec8', 'Ref8',
                            'Org9', 'Cont9', 'Rec9', 'Ref9',
                            'Org10', 'Cont10', 'Rec10', 'Ref10',
                        ),
                        'to': (),
                    },
                },
            },
            LinkedInquiryMapper: {
                'from': (),
                'to': 'linkedInquiry',
            }
        },
    },

    'CLAIMANT':
    {
        'factory': [ClaimantFactory],

        'mappers': {
            ClaimantsMapper: {
                'table': 'RECLAMANTS',
                'KEYS': ('Cle_Urba', 'Cle_Rec'),
                'mappers': {
                    SimpleMapper: (
                        {
                            'from': 'RECNom',
                            'to': 'name1',
                        },
                        {
                            'from': 'RECPrenom',
                            'to': 'name2',
                        },
                        {
                            'from': 'RECCode',
                            'to': 'zipcode',
                        },
                        {
                            'from': 'RELoc',
                            'to': 'city',
                        },
                        {
                            'from': 'RECTel',
                            'to': 'phone',
                        },
                        {
                            'from': 'RecRemarque',
                            'to': 'claimingText',
                        },
                    ),

                    ClaimantTitleMapper: {
                        'from': 'Civi_Rec',
                        'to': 'personTitle',
                    },

                    ClaimantSreetMapper: {
                        'from': 'RECAdres',
                        'to': 'street',
                    },

                    ClaimantNumberMapper: {
                        'from': 'RECAdres',
                        'to': 'number',
                    },

                    ClaimantIdMapper: {
                        'from': ('RECNom', 'RECPrenom'),
                        'to': 'id',
                    },
                },
            },
        },
    },

    'SECOND RW EVENT':
    {
        'factory': [UrbanEventFactory],

        'allowed_containers': ['BuildLicence', 'ParcelOutLicence'],

        'mappers': {
            SecondRWEventTypeMapper: {
                'from': (),
                'to': 'eventtype',
            },

            SecondRWEventDateMapper: {
                'from': 'UR_Datenv2',
                'to': 'eventDate',
            },

            SecondRWDecisionMapper: {
                'from': 'UR_Avis',
                'to': 'externalDecision',
            },

            SecondRWDecisionDateMapper: {
                'from': 'UR_Datpre',
                'to': 'decisionDate',
            },

            SecondRWReceiptDateMapper: {
                'from': 'UR_Datret',
                'to': 'receiptDate',
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

    'SUSPENSION EVENT':
    {
        'factory': [SuspensionEventFactory],

        'allowed_containers': ['BuildLicence', 'Article127', 'ParcelOutLicence'],

        'mappers': {
            SuspensionsMapper: {
                'table': 'SUSPENSIONS',
                'KEYS': ('Cle_Urba', 'Cle_Susp'),
                'mappers': {
                    SimpleMapper: (
                        {
                            'from': 'Date_Deb',
                            'to': 'eventDate',
                        },
                        {
                            'from': 'Date_Fin',
                            'to': 'suspensionEndDate',
                        },
                    ),
                    SuspensionEventTypeMapper: {
                        'from': (),
                        'to': 'eventtype',
                    },

                    SuspensionEventIdMapper: {
                        'from': (),
                        'to': 'id',
                    },

                    SuspensionEventReasonMapper: {
                        'from': 'Motif',
                        'to': 'suspensionReason',
                    },
                },
            },
        },
    },

    'DOCUMENTS':
    {
        'factory': [DocumentsFactory],

        'mappers': {
            DocumentsMapper: {
                'table': 'EMAESTRO-DOC',
                'KEYS': ('Cle_Urba', 'Cle_eMaestro'),
                'mappers': {
                    SimpleMapper: (
                        {
                            'from': 'Libelle',
                            'to': 'title',
                        },
                    ),
                    DocumentIdMapper: {
                        'from': 'Fichier',
                        'to': 'id',
                    },
                    DocumentFileMapper: {
                        'from': 'Fichier',
                        'to': 'file',
                    },
                }
            }
        },
    },
}
