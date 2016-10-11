# -*- coding: utf-8 -*-

from imio.urban.dataimport.acropole.mappers import LicenceFactory, \
    PortalTypeMapper, IdMapper, WorklocationMapper, ParcelsMapper, \
    CompletionStateMapper, ContactFactory, ContactPhoneMapper, StreetAndNumberMapper, \
    ParcelFactory, ParcelDataMapper, UrbanEventFactory, DepositEventMapper, \
    LicenceSubjectMapper, DepositDateMapper, CompleteFolderEventMapper, \
    DecisionEventTypeMapper, ErrorsMapper, DepositEventIdMapper, DecisionEventIdMapper, \
    DecisionEventDateMapper,   ContactTitleMapper, ApplicantMapper, ContactIdMapper, \
    CompleteFolderEventIdMapper, CompleteFolderDateMapper, EventDateMapper, \
    LicenceToApplicantEventMapper, LicenceToApplicantEventIdMapper, LicenceToApplicantDateMapper, \
    LicenceToFDEventMapper, LicenceToFDEventIdMapper, LicenceToFDDateMapper, \
    FolderZoneTableMapper, SolicitOpinionsToMapper, FD_SolicitOpinionMapper, Voirie_SolicitOpinionMapper, PCATypeMapper, PCAMapper, InvestigationDateMapper, \
    FirstFolderTransmittedToRwEventIdMapper, FirstFolderTransmittedToRwEventTypeMapper, \
    NotaryContactMapper, PcaZoneTableMapper, \
    CollegeReportEventMapper, CollegeReportEventIdMapper, DecisionEventDecisionMapper, CollegeReportEventDateMapper, \
    CollegeReportEventDecisionDateMapper, ArchitectsMapper, EventDecisionMapper, CollegeReportEventDecisionMapper, \
    DecisionEventDecisionDateMapper, FirstFolderTransmmittedToRwDecisionMapper, \
    FirstFolderTransmmittedToRwDecisionDateMapper, FirstFolderTransmmittedToRwEventDateMapper, \
    EventDecisionAlternativeMapper, CollegeReportBeforeFDDecisionEventMapper, CollegeReportBeforeFDDecisionEventIdMapper, \
    CollegeReportBeforeFDDecisionEventDateMapper, CollegeReportBeforeFDEventDecisionDateMapper, \
    CollegeReportBeforeFDEventDecisionMapper, EventDateAlternativeMapper, IncompleteFolderEventMapper, \
    IncompleteFolderEventIdMapper, IncompleteFolderDateMapper

from imio.urban.dataimport.MySQL.mapper import MySQLSimpleMapper as SimpleMapper
from imio.urban.dataimport.MySQL.mapper import MySQLSimpleStringMapper as SimpleStringMapper

OBJECTS_NESTING = [
    (
        'LICENCE', [
            ('CONTACT', []),
            ('PARCEL', []),
            ('DEPOSIT EVENT', []),
            ('INCOMPLETE FOLDER EVENT', []),
            ('COMPLETE FOLDER EVENT', []),
            ('FIRST FOLDER TRANSMITTED TO RW EVENT', []),
            ('SEND LICENCE TO APPLICANT EVENT', []),
            ('SEND LICENCE TO FD EVENT', []),
            ('COLLEGE REPORT BEFORE FD DECISION EVENT', []),
            ('COLLEGE REPORT EVENT', []),
            ('DECISION EVENT', []),
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

            # WorklocationMapper: {
            #     'table': 'finddoss_index',
            #     'KEYS': ('WRKDOSSIER_ID', 'ID'),
            #     'mappers': {
            #         StreetAndNumberMapper: {
            #             'from': ('SITUATION_DES',),
            #             'to': ('workLocations',)
            #         },
            #     },
            # },

            FolderZoneTableMapper: {
                'table': 'prc_data',
                'KEYS': ('WRKDOSSIER_ID', 'PRCD_ID'),
                'from': 'PRCD_AFFLABEL',
                'to': 'folderZone',
            },

            PcaZoneTableMapper: {
                'table': 'schemaaff',
                'KEYS': ('WRKDOSSIER_ID', 'SCA_SCHEMA_ID'),
                'from': 'SCA_LABELFR',
                'to': 'pcaZone',
            },

            NotaryContactMapper: {
                'table': 'wrkdossier',
                'KEYS': ('ID', 'K_ID1',),
                'from': ('DOSSIER_TDOSSIERID',),
                'to': 'notaryContact',
            },

            ArchitectsMapper: {
                'table': 'wrkdossier',
                'KEYS': ('ID', 'K_ID1',),
                'from': ('DOSSIER_TDOSSIERID',),
                'to': 'architects',
            },

            SolicitOpinionsToMapper: {
                'table': 'wrkavis',
                'KEYS': ('WRKDOSSIER_ID', 'AVIS_DOSSIERID'),
                'from': 'AVIS_NOM',
                'to': 'solicitOpinionsTo',
            },

            PCATypeMapper: {
                'table': 'schema',
                'KEYS': ('WRKDOSSIER_ID', 'SCHEMA_ID'),
                'from': 'SCH_FUSION',
                'to': 'pca',
            },

            PCAMapper: {
                'table': 'schema',
                'KEYS': ('WRKDOSSIER_ID', 'SCHEMA_ID'),
                'from': 'SCH_FUSION',
                'to': 'isInPca',
            },

            InvestigationDateMapper: {
                'table': 'wrkparam',
                'KEYS': ('WRKDOSSIER_ID', 'WRKPARAM_ID'),
                'from': ('PARAM_VALUE', 'PARAM_VALUE',),
                'to': ('investigationStart', 'investigationEnd',),
            },

            FD_SolicitOpinionMapper: {
                'table': 'wrkparam',
                'KEYS': ('WRKDOSSIER_ID', 'WRKPARAM_ID'),
                'from': ('PARAM_VALUE', 'PARAM_NOMFUSION',),
                'to': ('procedureChoice',),
            },

            Voirie_SolicitOpinionMapper: {
                'table': 'wrkparam',
                'KEYS': ('WRKDOSSIER_ID', 'WRKPARAM_ID'),
                'from': ('PARAM_VALUE', 'PARAM_NOMFUSION',),
                'to': ('roadSpecificFeatures'),
            },
            StreetAndNumberMapper: {
                'table': 'adr',
                'KEYS': ('WRKDOSSIER_ID', 'ADR_ID'),
                'from': ('ADR_ADRESSE', 'ADR_ZIP', 'ADR_LOCALITE', 'ADR_NUM',),
                'to': 'workLocations'
            },

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
                'table': 'wrkdossier',
                'KEYS': ('WRKDOSSIER_ID', 'CPSN_ID',),
                'mappers': {
                    SimpleStringMapper: (
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
                        {
                            'from': 'CLOC_ADRESSE',
                            'to': 'street',
                        },
                        {
                            'from': 'CLOC_ZIP',
                            'to': 'zipcode',
                        },
                        {
                            'from': 'CLOC_LOCALITE',
                            'to': 'city',
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

            DepositEventIdMapper: {
                'from': (),
                'to': 'id',
            },

            EventDateMapper: {
                'allowed_containers': ['BuildLicence', 'ParcelOutLicence'],
                'table': 'wrketape',
                'KEYS': ('WRKDOSSIER_ID', 'WRKETAPE_ID'),
                'event_name': u'récépissé',
                'mappers': {
                    DepositDateMapper: {
                        'from': ('ETAPE_DATEDEPART',),
                        'to': ('eventDate'),
                    },
                },
            },

            # issue with basic eventDate
            # EventDateAlternativeMapper: {
            #     'allowed_containers': ['UrbanCertificateOne', 'UrbanCertificateTwo'],
            #     'table': 'wrketape',
            #     'KEYS': ('WRKDOSSIER_ID', 'WRKETAPE_ID'),
            #     'event_name': u'réception demande',
            #     'mappers': {
            #         DepositDateMapper: {
            #             'from': ('ETAPE_DATEDEPART',),
            #             'to': ('eventDate'),
            #         },
            #     },
            # },
        },
    },

    'COMPLETE FOLDER EVENT':
    {
        'factory': [UrbanEventFactory],
        'allowed_containers': ['BuildLicence', 'ParcelOutLicence'],

        'mappers': {
            CompleteFolderEventMapper: {
                'from': (),
                'to': 'eventtype',
            },

            CompleteFolderEventIdMapper: {
                'from': (),
                'to': 'id',
            },

            EventDateMapper: {
                'table': 'wrketape',
                'KEYS': ('WRKDOSSIER_ID', 'WRKETAPE_ID'),
                'event_name': u'accusé de réception',
                'mappers': {
                    CompleteFolderDateMapper: {
                        'from': ('ETAPE_DATEDEPART',),
                        'to': ('eventDate'),
                    },
                },
            },
        },
    },

    'INCOMPLETE FOLDER EVENT':
    {
        'factory': [UrbanEventFactory],
        'allowed_containers': ['BuildLicence', 'ParcelOutLicence'],

        'mappers': {
            IncompleteFolderEventMapper: {
                'from': (),
                'to': 'eventtype',
            },

            IncompleteFolderEventIdMapper: {
                'from': (),
                'to': 'id',
            },

            EventDateMapper: {
                'table': 'wrketape',
                'KEYS': ('WRKDOSSIER_ID', 'WRKETAPE_ID'),
                'event_name': u'dossier incomplet',
                'mappers': {
                    IncompleteFolderDateMapper: {
                        'from': ('ETAPE_DATEDEPART',),
                        'to': ('eventDate'),
                    },
                },
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
                'to': 'eventDate',
            },

            EventDateMapper: {
                'table': 'wrketape',
                'KEYS': ('WRKDOSSIER_ID', 'WRKETAPE_ID'),
                'event_name': u'délivrance permis',
                'mappers': {
                    DecisionEventDecisionDateMapper: { # get ETAPE_DATEDEPART
                        'from': ('ETAPE_DATEDEPART',),
                        'to': ('decisionDate'),
                    },
                },
            },

            EventDecisionMapper: {
                'table': 'wrkparam',
                'KEYS': ('WRKDOSSIER_ID', 'WRKPARAM_ID'),
                'event_name': u'Octroi du permis',
                'mappers': {
                    DecisionEventDecisionMapper: {
                        'from': ('PARAM_NOMFUSION', 'PARAM_VALUE',),
                        'to': ('decision'),
                    },
                },
            },

        },
    },

    'FIRST FOLDER TRANSMITTED TO RW EVENT':
    {
        'factory': [UrbanEventFactory],
        'allowed_containers': ['BuildLicence', 'ParcelOutLicence'],

        'mappers': {
            FirstFolderTransmittedToRwEventTypeMapper: {
                'from': (),
                'to': 'eventtype',
            },

            FirstFolderTransmittedToRwEventIdMapper: {
                'from': (),
                'to': 'id',
            },

            EventDateMapper: {
                'table': 'wrketape',
                'KEYS': ('WRKDOSSIER_ID', 'WRKETAPE_ID'),
                'event_name': 'envoi du primo dossier au FD',
                'mappers': {
                    FirstFolderTransmmittedToRwEventDateMapper: {
                        'from': ('ETAPE_DATEDEPART',),
                        'to': ('eventDate'),
                    },
                },
            },

            EventDecisionAlternativeMapper: {
                'table': 'wrkparam',
                'KEYS': ('WRKDOSSIER_ID', 'WRKPARAM_ID'),
                'event_name': u'Date décision urbanisme',
                'mappers': {
                    FirstFolderTransmmittedToRwDecisionDateMapper: {
                        'from': ('PARAM_NOMFUSION', 'PARAM_VALUE',),
                        'to': ('decisionDate'),
                    },
                },
            },

            EventDecisionMapper: {
                'table': 'wrkparam',
                'KEYS': ('WRKDOSSIER_ID', 'WRKPARAM_ID'),
                'event_name': u'avis FD',
                'mappers': {
                    FirstFolderTransmmittedToRwDecisionMapper: {
                        'from': ('PARAM_NOMFUSION', 'PARAM_VALUE',),
                        'to': ('externalDecision'),
                    },
                },
            },

        },
    },

    'SEND LICENCE TO APPLICANT EVENT':
    {
        'factory': [UrbanEventFactory],
        'allowed_containers': ['BuildLicence', 'ParcelOutLicence'],

        'mappers': {
            LicenceToApplicantEventMapper: {
                'from': (),
                'to': 'eventtype',
            },

            LicenceToApplicantEventIdMapper: {
                'from': (),
                'to': 'id',
            },

            EventDateMapper: {
                'table': 'wrketape',
                'KEYS': ('WRKDOSSIER_ID', 'WRKETAPE_ID'),
                'event_name': 'envoi du permis au demandeur',
                'mappers': {
                    LicenceToApplicantDateMapper: {
                        'from': ('ETAPE_DATEDEPART',),
                        'to': ('eventDate'),
                    },
                },
            },
        },
    },

    'SEND LICENCE TO FD EVENT':
    {
        'factory': [UrbanEventFactory],
        'allowed_containers': ['BuildLicence', 'ParcelOutLicence'],

        'mappers': {
            LicenceToFDEventMapper: {
                'from': (),
                'to': 'eventtype',
            },

            LicenceToFDEventIdMapper: {
                'from': (),
                'to': 'id',
            },

            EventDateMapper: {
                'table': 'wrketape',
                'KEYS': ('WRKDOSSIER_ID', 'WRKETAPE_ID'),
                'event_name': 'envoi du permis au fd',
                'mappers': {
                    LicenceToFDDateMapper: {
                        'from': ('ETAPE_DATEDEPART',),
                        'to': ('eventDate'),
                    },
                },
            },
        },
    },

    'COLLEGE REPORT EVENT':
    {
        'factory': [UrbanEventFactory],
        'allowed_containers': ['Article127'],

        'mappers': {
            CollegeReportEventMapper: {
                'from': (),
                'to': 'eventtype',
            },

            CollegeReportEventIdMapper: {
                'from': (),
                'to': 'id',
            },

            EventDateAlternativeMapper: {
                'table': 'wrketape',
                'KEYS': ('WRKDOSSIER_ID', 'WRKETAPE_ID'),
                'event_name': u'Rapport du collège',
                'mappers': {
                    CollegeReportEventDateMapper: {
                        'from': ('ETAPE_DATEDEPART',),
                        'to': ('eventDate'),
                    },
                },
            },

            EventDateMapper: {
                'table': 'wrketape',
                'KEYS': ('WRKDOSSIER_ID', 'WRKETAPE_ID'),
                'event_name': u'décision finale du Collège',
                'mappers': {
                    CollegeReportEventDecisionDateMapper: {
                        'from': ('ETAPE_DATEDEPART',),
                        'to': ('decisionDate'),
                    },
                },
            },

            EventDecisionMapper: {
                'table': 'wrkparam',
                'KEYS': ('WRKDOSSIER_ID', 'WRKPARAM_ID'),
                'event_name': u'décision finale du Collège',
                'mappers': {
                    CollegeReportEventDecisionMapper: {
                        'from': ('PARAM_NOMFUSION', 'PARAM_VALUE',),
                        'to': ('decision'),
                    },
                },
            },
        },
    },

    'COLLEGE REPORT BEFORE FD DECISION EVENT':
        {
            'factory': [UrbanEventFactory],
            'allowed_containers': ['BuildLicence'],

            'mappers': {
                CollegeReportBeforeFDDecisionEventMapper: {
                    'from': (),
                    'to': 'eventtype',
                },

                CollegeReportBeforeFDDecisionEventIdMapper: {
                    'from': (),
                    'to': 'id',
                },

                EventDateAlternativeMapper: {
                    'table': 'wrketape',
                    'KEYS': ('WRKDOSSIER_ID', 'WRKETAPE_ID'),
                    'event_name': u'rapport Collège avant décision du FD',
                    'mappers': {
                        CollegeReportBeforeFDDecisionEventDateMapper: {
                            'from': ('ETAPE_DATEDEPART',),
                            'to': ('eventDate'),
                        },
                    },
                },

                EventDateMapper: {
                    'table': 'wrketape',
                    'KEYS': ('WRKDOSSIER_ID', 'WRKETAPE_ID'),
                    'event_name': u'décision finale du Collège',
                    'mappers': {
                        CollegeReportBeforeFDEventDecisionDateMapper: {
                            'from': ('ETAPE_DATEDEPART',),
                            'to': ('decisionDate'),
                        },
                    },
                },

                EventDecisionMapper: {
                    'table': 'wrkparam',
                    'KEYS': ('WRKDOSSIER_ID', 'WRKPARAM_ID'),
                    'event_name': u'décision finale du Collège',
                    'mappers': {
                        CollegeReportBeforeFDEventDecisionMapper: {
                            'from': ('PARAM_NOMFUSION', 'PARAM_VALUE',),
                            'to': ('decision'),
                        },
                    },
                },
            },
        },

}
