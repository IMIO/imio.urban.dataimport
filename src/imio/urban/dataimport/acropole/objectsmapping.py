# -*- coding: utf-8 -*-

from imio.urban.dataimport.MySQL.mapper import MySQLSimpleMapper as SimpleMapper
from imio.urban.dataimport.MySQL.mapper import MySQLSimpleStringMapper as SimpleStringMapper
from imio.urban.dataimport.acropole.mappers import LicenceFactory, \
    PortalTypeMapper, IdMapper, ParcelsMapper, \
    CompletionStateMapper, ContactFactory, ContactPhoneMapper, StreetAndNumberMapper, \
    ParcelFactory, ParcelDataMapper, UrbanEventFactory, DepositEventMapper, \
    LicenceSubjectMapper, DepositDateMapper, CompleteFolderEventMapper, \
    DecisionEventTypeMapper, ErrorsMapper, DepositEventIdMapper, DecisionEventIdMapper, \
    DecisionEventDateMapper, ContactTitleMapper, ApplicantMapper, ContactIdMapper, \
    CompleteFolderEventIdMapper, CompleteFolderDateMapper, EventDateMapper, \
    LicenceToApplicantEventMapper, LicenceToApplicantEventIdMapper, LicenceToApplicantDateMapper, \
    LicenceToFDEventMapper, LicenceToFDEventIdMapper, LicenceToFDDateMapper, \
    FolderZoneTableMapper, SolicitOpinionsToMapper, FD_SolicitOpinionMapper, Voirie_SolicitOpinionMapper, PCATypeMapper, \
    PCAMapper, InvestigationDateMapper, \
    CollegeReportTransmittedToRWEventTypeMapper, \
    NotaryContactMapper, PcaZoneTableMapper, \
    CollegeReportEventMapper, CollegeReportEventIdMapper, DecisionEventDecisionMapper, CollegeReportEventDateMapper, \
    CollegeReportEventDecisionDateMapper, ArchitectsMapper, EventDecisionMapper, CollegeReportEventDecisionMapper, \
    DecisionEventDecisionDateMapper, \
    EventDecisionAlternativeMapper, CollegeReportBeforeFDDecisionEventMapper, \
    CollegeReportBeforeFDDecisionEventIdMapper, \
    CollegeReportBeforeFDDecisionEventDateMapper, CollegeReportBeforeFDEventDecisionDateMapper, \
    CollegeReportBeforeFDEventDecisionMapper, EventDateCollegeReportMapper, IncompleteFolderEventMapper, \
    IncompleteFolderEventIdMapper, IncompleteFolderDateMapper, CollegeReportTransmittedToRwEventDateMapper, \
    CollegeReportTransmittedToRwDecisionDateMapper, CollegeReportTransmittedToRwDecisionMapper, DepositEventDateMapper, \
    DecisionDecisionEventDateMapper, EventParamDateMapper, CollegeReportDeclarationEventMapper, \
    CollegeReportDeclarationEventIdMapper, EnvClassThreeAcceptabilityEventMapper, \
    EnvClassThreeAcceptabilityEventIdMapper, EventDateEnvClassThreeAcceptabilityMapper, \
    EnvClassThreeAcceptabilityEventDateMapper, EnvClassThreeUnacceptabilityEventMapper, \
    EnvClassThreeUnacceptabilityEventIdMapper, EventDateEnvClassThreeUnacceptabilityMapper, \
    EnvClassThreeUnacceptabilityEventDateMapper, EnvClassThreeCondAcceptabilityEventMapper, \
    EnvClassThreeCondAcceptabilityEventIdMapper, EventDateEnvClassThreeCondAcceptabilityMapper, \
    EnvClassThreeCondAcceptabilityEventDateMapper, DispensationMapper, InvestigationReasonsMapper, \
    RubricsMapper

OBJECTS_NESTING = [
    (
        'LICENCE', [
            ('CONTACT', []),
            ('PARCEL', []),
            ('DEPOSIT EVENT', []),
            ('INCOMPLETE FOLDER EVENT', []),
            ('COMPLETE FOLDER EVENT', []),
            ('COLLEGE REPORT TRANSMITTED TO RW EVENT', []),
            ('SEND LICENCE TO APPLICANT EVENT', []),
            ('SEND LICENCE TO FD EVENT', []),
            ('COLLEGE REPORT BEFORE FD DECISION EVENT', []),
            ('COLLEGE REPORT DECLARATION EVENT', []),
            ('COLLEGE REPORT EVENT', []),
            ('ACCEPTABLE DECLARATION EVENT', []),
            ('UNACCEPTABLE DECLARATION EVENT', []),
            ('ACCEPTABLE CONDITIONAL DECLARATION EVENT', []),
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
                    'from': ('PARAM_NOMFUSION', 'PARAM_VALUE',),
                    'to': ('investigationStart', 'investigationEnd',),
                },

                InvestigationReasonsMapper: {
                    'table': 'wrkparam',
                    'KEYS': ('WRKDOSSIER_ID', 'WRKPARAM_ID', 'CREMARQ_ID'),
                    'from': ('PARAM_NOMFUSION', 'PARAM_VALUE', 'REMARQ_LIB'),
                    'to': ('investigationReasons', ),
                },

                DispensationMapper: {
                    'table': 'wrkparam',
                    'KEYS': ('WRKDOSSIER_ID', 'WRKPARAM_ID'),
                    'from': ('PARAM_NOMFUSION', 'PARAM_VALUE',),
                    'to': ('derogation',),
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

                RubricsMapper: {
                    'table': 'urblistecat',
                    'KEYS': ('WRKDOSSIER_ID', 'CAT_ID'),
                    'from': ('CAT_CLE', ),
                    'to': 'rubrics'
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
            # 'allowed_containers': ['BuildLicence', 'ParcelOutLicence', 'Article127', 'Declaration','Division', 'MiscDemand', 'Division', 'UrbanCertificateOne', 'Division', 'UrbanCertificateTwo'],

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

                DepositEventDateMapper: {
                    'allowed_containers': ['BuildLicence', 'ParcelOutLicence', 'Article127', 'NotaryLetters'],
                    'table': 'wrketape',
                    'KEYS': ('WRKDOSSIER_ID', 'WRKETAPE_ID'),
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

                DecisionDecisionEventDateMapper: {
                    'from': ('DOSSIER_DATEDELIV'),
                    'to': 'eventDate',
                },

                DecisionEventDateMapper: {
                    'table': 'wrketape',
                    'KEYS': ('WRKDOSSIER_ID', 'WRKETAPE_ID'),
                    'mappers': {
                        DecisionEventDecisionDateMapper: {
                            'from': ('ETAPE_DATEDEPART',),
                            'to': ('decisionDate'),
                        },
                    },
                },

                EventDecisionMapper: {
                    'table': 'wrkparam',
                    'KEYS': ('WRKDOSSIER_ID', 'WRKPARAM_ID'),
                    'mappers': {
                        DecisionEventDecisionMapper: {
                            'from': ('PARAM_NOMFUSION', 'PARAM_VALUE',),
                            'to': ('decision'),
                        },
                    },
                },

            },
        },

    'COLLEGE REPORT TRANSMITTED TO RW EVENT':
        {
            'factory': [UrbanEventFactory],
            'allowed_containers': ['BuildLicence'],

            'mappers': {
                CollegeReportTransmittedToRWEventTypeMapper: {
                    'from': (),
                    'to': 'eventtype',
                },

                EventDateMapper: {
                    'table': 'wrketape',
                    'KEYS': ('WRKDOSSIER_ID', 'WRKETAPE_ID'),
                    'event_name': u'envoi du dossier et rapport au FD',
                    'mappers': {
                        CollegeReportTransmittedToRwEventDateMapper: {
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
                        CollegeReportTransmittedToRwDecisionDateMapper: {
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
                        CollegeReportTransmittedToRwDecisionMapper: {
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
            'allowed_containers': ['BuildLicence'],

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

                EventDateCollegeReportMapper: {
                    'table': 'wrketape',
                    'KEYS': ('WRKDOSSIER_ID', 'WRKETAPE_ID'),
                    'mappers': {
                        CollegeReportEventDateMapper: {
                            'from': ('ETAPE_DATEDEPART',),
                            'to': ('eventDate'),
                        },
                    },
                },

                EventParamDateMapper: {
                    'table': 'wrkparam',
                    'KEYS': ('WRKDOSSIER_ID', 'WRKPARAM_ID'),
                    'event_name': u'Date décision finale du Collège',
                    'mappers': {
                        CollegeReportEventDecisionDateMapper: {
                            'from': ('PARAM_NOMFUSION', 'PARAM_VALUE',),
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

    'COLLEGE REPORT DECLARATION EVENT':
        {
            'factory': [UrbanEventFactory],
            'allowed_containers': ['MiscDemand'],

            'mappers': {
                CollegeReportDeclarationEventMapper: {
                    'from': (),
                    'to': 'eventtype',
                },

                CollegeReportDeclarationEventIdMapper: {
                    'from': (),
                    'to': 'id',
                },

                EventDateCollegeReportMapper: {
                    'table': 'wrketape',
                    'KEYS': ('WRKDOSSIER_ID', 'WRKETAPE_ID'),
                    'mappers': {
                        CollegeReportEventDateMapper: {
                            'from': ('ETAPE_DATEDEPART',),
                            'to': ('eventDate'),
                        },
                    },
                },

                # EventParamDateMapper: {
                #     'table': 'wrkparam',
                #     'KEYS': ('WRKDOSSIER_ID', 'WRKPARAM_ID'),
                #     'event_name': u'Date décision finale du Collège',
                #     'mappers': {
                #         CollegeReportEventDecisionDateMapper: {
                #             'from': ('PARAM_NOMFUSION', 'PARAM_VALUE',),
                #             'to': ('decisionDate'),
                #         },
                #     },
                # },
                #
                # EventDecisionMapper: {
                #     'table': 'wrkparam',
                #     'KEYS': ('WRKDOSSIER_ID', 'WRKPARAM_ID'),
                #     'event_name': u'décision finale du Collège',
                #     'mappers': {
                #         CollegeReportEventDecisionMapper: {
                #             'from': ('PARAM_NOMFUSION', 'PARAM_VALUE',),
                #             'to': ('decision'),
                #         },
                #     },
                # },
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

                EventDateCollegeReportMapper: {
                    'table': 'wrketape',
                    'KEYS': ('WRKDOSSIER_ID', 'WRKETAPE_ID'),
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

        'ACCEPTABLE DECLARATION EVENT':
        {
            'factory': [UrbanEventFactory],
            'allowed_containers': ['EnvClassThree'],

            'mappers': {
                EnvClassThreeAcceptabilityEventMapper: {
                    'from': (),
                    'to': 'eventtype',
                },

                EnvClassThreeAcceptabilityEventIdMapper: {
                    'from': (),
                    'to': 'id',
                },

                EventDateEnvClassThreeAcceptabilityMapper: {
                    'table': 'urbmessagestatus',
                    'KEYS': ('WRKDOSSIER_ID', 'DOSSIER_OCTROI', 'STAT_NUM'),
                    'mappers': {
                        EnvClassThreeAcceptabilityEventDateMapper: {
                            'from': ('DOSSIER_DATEDELIV',),
                            'to': ('eventDate'),
                        },
                    },
                },

            },
        },

        'UNACCEPTABLE DECLARATION EVENT':
        {
            'factory': [UrbanEventFactory],
            'allowed_containers': ['EnvClassThree'],

            'mappers': {
                EnvClassThreeUnacceptabilityEventMapper: {
                    'from': (),
                    'to': 'eventtype',
                },

                EnvClassThreeUnacceptabilityEventIdMapper: {
                    'from': (),
                    'to': 'id',
                },

                EventDateEnvClassThreeUnacceptabilityMapper: {
                    'table': 'urbmessagestatus',
                    'KEYS': ('WRKDOSSIER_ID', 'DOSSIER_OCTROI', 'STAT_NUM'),
                    'mappers': {
                        EnvClassThreeUnacceptabilityEventDateMapper: {
                            'from': ('DOSSIER_DATEDELIV',),
                            'to': ('eventDate'),
                        },
                    },
                },

            },
        },

        'ACCEPTABLE CONDITIONAL DECLARATION EVENT':
        {
            'factory': [UrbanEventFactory],
            'allowed_containers': ['EnvClassThree'],

            'mappers': {
                EnvClassThreeCondAcceptabilityEventMapper: {
                    'from': (),
                    'to': 'eventtype',
                },

                EnvClassThreeCondAcceptabilityEventIdMapper: {
                    'from': (),
                    'to': 'id',
                },

                EventDateEnvClassThreeCondAcceptabilityMapper: {
                    'table': 'urbmessagestatus',
                    'KEYS': ('WRKDOSSIER_ID', 'DOSSIER_OCTROI', 'STAT_NUM'),
                    'mappers': {
                        EnvClassThreeCondAcceptabilityEventDateMapper: {
                            'from': ('DOSSIER_DATEDELIV',),
                            'to': ('eventDate'),
                        },
                    },
                },

            },
        },

}
