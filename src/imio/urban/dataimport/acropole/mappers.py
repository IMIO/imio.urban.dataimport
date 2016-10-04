# -*- coding:utf-8 -*-

from DateTime import DateTime
from Products.CMFPlone.utils import normalizeString
from plone import api
from plone.api.exc import InvalidParameterError
from sqlalchemy import or_, and_
from sqlalchemy.orm import aliased
from plone.i18n.normalizer import idnormalizer

import re
from imio.urban.dataimport.MySQL.mapper import FieldMultiLinesSecondaryTableMapper, SubQueryMapper
from imio.urban.dataimport.MySQL.mapper import MultiLinesSecondaryTableMapper
from imio.urban.dataimport.MySQL.mapper import MySQLFinalMapper as FinalMapper
from imio.urban.dataimport.MySQL.mapper import MySQLMapper as Mapper
from imio.urban.dataimport.MySQL.mapper import MySQLPostCreationMapper as PostCreationMapper
from imio.urban.dataimport.MySQL.mapper import SecondaryTableMapper
from imio.urban.dataimport.exceptions import NoObjectToCreateException
from imio.urban.dataimport.factory import BaseFactory
from imio.urban.dataimport.utils import CadastralReference
from imio.urban.dataimport.utils import cleanAndSplitWord
from imio.urban.dataimport.utils import parse_cadastral_reference


#
# LICENCE
#

# factory


class LicenceFactory(BaseFactory):
    def getCreationPlace(self, factory_args):
        urban_folder = self.site.urban
        portal_type = factory_args.get('portal_type', '')
        if portal_type:
            return getattr(urban_folder, portal_type.lower() + 's')
        return urban_folder


# mappers


class IdMapper(Mapper):

    def mapId(self, line):
        return normalizeString(self.getData('WRKDOSSIER_ID'))


class PortalTypeMapper(Mapper):

    cpt_dossier_from_start_line = 0

    def mapPortal_type(self, line):
        PortalTypeMapper.cpt_dossier_from_start_line += 1
        type_value = self.getData('DOSSIER_TDOSSIERID')
        portal_type = self.getValueMapping('type_map')[type_value]['portal_type']

        #TODO remove this filter zone! Dev mode
        # *** start zone ***

        # with open("sequence_dossier.csv", "a") as file:
        #     file.write(str(PortalTypeMapper.cpt_dossier_from_start_line) + "," + str(self.getData('WRKDOSSIER_ID')) + "\n")
        # import ipdb; ipdb.set_trace()
        # if self.getData('WRKDOSSIER_ID', line=line) == 6112664:
        #     import ipdb; ipdb.set_trace()


        # if portal_type != 'NotaryLetter':
        #     raise NoObjectToCreateException

        # *** end zone ***

        if not portal_type:
            self.logError(self, line, 'No portal type found for this type value', {'TYPE value': type_value})
            raise NoObjectToCreateException
        if portal_type == 'UrbanCertificateOne' and self.getData('DOSSIER_TYPEIDENT') == 'CU2':
            portal_type = 'UrbanCertificateTwo'
        return portal_type

    def mapFoldercategory(self, line):
        type_value = self.getData('DOSSIER_TDOSSIERID')
        foldercategory = self.getValueMapping('type_map')[type_value]['foldercategory']
        return foldercategory


class LicenceSubjectMapper(SecondaryTableMapper):
    """ """


class WorklocationMapper(SubQueryMapper):
    """ """


class ArchitectMapper(PostCreationMapper):

    def mapArchitects(self, line, plone_object):
        archi_name = self.getData('NomArchitecte')
        fullname = cleanAndSplitWord(archi_name)
        if not fullname:
            return []
        noisy_words = ['monsieur', 'madame', 'architecte', '&', ',', '.', 'or', 'mr', 'mme', '/']
        name_keywords = [word.lower() for word in fullname if word.lower() not in noisy_words]
        architects = self.catalog(portal_type='Architect', Title=name_keywords)
        if len(architects) == 1:
            return architects[0].getObject()
        self.logError(self, line, 'No architects found or too much architects found',
                      {
                          'raw_name': archi_name,
                          'name': name_keywords,
                          'search_result': len(architects)
                      })
        return []


class GeometricianMapper(PostCreationMapper):

    def mapGeometricians(self, line, plone_object):
        title_words = [word for word in self.getData('Titre').lower().split()]
        for word in title_words:
            if word not in ['géometre', 'géomètre']:
                return
        name = self.getData('Nom')
        firstname = self.getData('Prenom')
        raw_name = firstname + name
        name = cleanAndSplitWord(name)
        firstname = cleanAndSplitWord(firstname)
        names = name + firstname
        geometrician = self.catalog(portal_type='Geometrician', Title=names)
        if not geometrician:
            geometrician = self.catalog(portal_type='Geometrician', Title=name)
        if len(geometrician) == 1:
            return geometrician[0].getObject()
        self.logError(self, line, 'no geometricians found or too much geometricians found',
                      {
                          'raw_name': raw_name,
                          'title': self.getData('Titre'),
                          'name': name,
                          'firstname': firstname,
                          'search_result': len(geometrician)
                      })
        return []


class FolderZoneTableMapper(FieldMultiLinesSecondaryTableMapper):

    def __init__(self, mysql_importer, args):
        super(FolderZoneTableMapper, self).__init__(mysql_importer, args)
        prc_data = self.importer.datasource.get_table('prc_data')
        urbcadastre = self.importer.datasource.get_table('urbcadastre')
        wrkdossier = self.importer.datasource.get_table('wrkdossier')
        self.query = self.query.join(
            urbcadastre,
            prc_data.columns['PRCD_PRC'] == urbcadastre.columns['CAD_NOM']
        ).join(
            wrkdossier,
            wrkdossier.columns['WRKDOSSIER_ID'] == urbcadastre.columns['CAD_DOSSIER_ID']
        )

    def query_secondary_table(self, line):
        licence_id = self.getData('WRKDOSSIER_ID', line)
        lines = self.query.filter_by(WRKDOSSIER_ID=licence_id).all()
        return lines

    def mapFolderzone(self, line):
        raw_folder_zone = self.getData('PRCD_AFFLABEL', line=line)
        raw_folder_zone = raw_folder_zone.lower().strip()
        zoneDictionnary = {
            u"zone d'habitat": "zh",
            u"zone d'habitat à caractère rural": "zhcr",
            u"zone d'habitat à caractère rural sur +/- 50 m et le surplus en zone agricole": "zhcrza",
            u"zone de services publics et d'équipements communautaires": "zspec",
            u"zone de centre d'enfouissement technique": "zcet",
            u"zone de loisirs": "zl",
            u"zones d'activité économique mixte": "zaem",
            u"zones d'activité économique industrielle": "zaei",
            u"zones d'activité économique spécifique agro-économique": "zaesae",
            u"zones d'activité économique spécifique grande distribution": "zaesgd",
            u"zone d'aménagement différé à caractère industriel": "zadci",
            u"zone agricole": "za",
            u"zone forestière": "zf",
            u"zone d'espaces verts": "zev",
            u"zone naturelle": "zn",
            u"zone de parc": "zp",
            u"zone natura 2000": "znatura2000",
            u"zone d'assainissement collectif": "zac",
            u"zone de construction d'habitation fermée": "zchf",
            u"zone de cours et jardins": "zcj",
            u"zone de recul": "zr",
            u"zone forestière d'intérêt paysager": "zfip",
            u"zone faiblement habitée": "zfh",
            u"zone de construction en annexe": "zca",
            u"zone de construction d'habitation semi-ouverte": "zcso",
            u"zone de construction d'habitation ouverte": "zcho",
            u"zone de bâtisses agricoles": "zba",
            u"zone d'habitat dans un périmètre d'intérêt culturel, historique ou esthétique": "zhche",
            u"zone d'habitat à caractère rural sur une profondeur de 50 mètres": "zhcr50",
            u"zone d'habitat à caractère rural sur une profondeur de 40 mètres": "zhcr40",
            u"zone d'extraction": "ze",
            u"zone d'ext. d'habitat": "zeh",
            u"zone d'équipements communautaires et de services publics": "zspec",
            u"zone d'équipement communautaire": "zec",
            u"zone d'assainissement autonome": "zaa",
            u"zone d'aménagement communal concerté mise en oeuvre": "zaccmeo",
            u"zone d'aménagement communal concerté": "zacc",
            u"zone boisée": "zb",
            u"zone artisanale": "zart",
            u"zone agricole pour partie": "zapp",
            u"zone agricole pour le surplus": "zapls",
            u"zone agricole et zone forestière": "zaezf",
            u"zone agricole dans un périmètre d'intérêt paysager pour le surplus": "zapippls",
            u"zone agricole dans un périmètre d'intérêt paysager": "zapip",
            u"voirie": "zv",
            u"sans affectation": "sa",
            u"pv de constat d'infraction": "pvci",
            u"plan d'eau": "pe",
            u"périmètre de réservation sur 75 m de profondeur à partir de l'axe de la voirie": "pr75padlv",
            u"infraction relevée mais sans PV": "pr75irspvpadlv",
            u"aire de faible densité": "afd",
            u"aire de moyenne densité": "amd",
            u"aire de forte densité": "afod",
            u"en partie dans un périmètre de réservation": "eppdr",
            u"déclaré inhabitable": "di",
            u"dans un périmètre d''intérêt culturel, historique ou esthétique": "pche",
            u"dans un périmètre de réservation": "dpdr",
            u"dans un périmètre d'intérêt paysager": "dpip",
            u"faible": "fai",
            u"très faible": "tfai",
            u"eau": "eau",
            u"élevé": "eleve",
            u"éloignée": "eloi",
            u"dossier en cours": "dec",
            u"dans un périmètre d'intérêt culturel, historique ou esthétique": "dupiche",
            u"zone d'habitat sur 50 m de profondeur": "zhas50dp",
        }

        if raw_folder_zone in zoneDictionnary:
            return zoneDictionnary[raw_folder_zone]
        else:
            print (raw_folder_zone)
            return "unknown"


class SolicitOpinionsToMapper(FieldMultiLinesSecondaryTableMapper):

    def mapSolicitopinionsto(self, line):

        if self.getData('AVIS_REQ', line=line) != 1:
            return None

        raw_solicit_opinion_to = self.getData('AVIS_NOM', line=line)
        raw_solicit_opinion_to = raw_solicit_opinion_to.lower()


        solicit_opinion_toDictionnary = {
            u"stp_eau": "stp",
            u"stp": "stp",
            u"stp_voirie": "stp",
            u"base aérienne": "ba",
            u"ddr": "ddr",
            u"sri": "sri",
            u"direction des routes": "spw-dgo1",
            u"x4": "x4",
            u"défense": "defense",
            u"fluxys": "fluxys",
            u"asbl bois du roi": "asblbdr",
            u"cwedd": "cwedd",  # Conseil wallon de l'Environnement pour le Développement durable
            u"elia": "elia",
            u"police": "Police",
            u"tec": "tec",
            u"égouts": "egouts",
            u"ores": "ores",
            u"inasep": "inasep",
            u"dnf": "dnf",
            u"sncb": "sncb",
            u"ccatm": "ccatm",
            u"dgrne": "dgrne",
            u"belgacom": "belgacom",
            u"autres": "autres",
        }

        if raw_solicit_opinion_to in solicit_opinion_toDictionnary:
            print (raw_solicit_opinion_to)
            return solicit_opinion_toDictionnary[raw_solicit_opinion_to]
        else:
            print (raw_solicit_opinion_to)
            return "unknown"

        return solicit_opinion_toDictionnary[raw_solicit_opinion_to]


class PCAInit(SecondaryTableMapper):

    raw_pca_toDictionnary = {
        u"ppa1part": "pca1",
        u"ppa1": "pca1",
        u"ppa1b": "pca1",
        u"ppa1tflo": "pca1",
        u"ppa1tfla": "pca1",
        u"ppa2": "pca2",
        u"ppa2part": "pca2",
        u"ppa2b": "pca2",
        u"ppa3": "pca3",
        u"ppa3part": "pca3",
        u"ppa3mod": "pca3",
    }

    def __init__(self, mysql_importer, args):
        super(PCAInit, self).__init__(mysql_importer, args)
        schema = self.importer.datasource.get_table('schema')
        prc_data = self.importer.datasource.get_table('prc_data')
        urbcadastre = self.importer.datasource.get_table('urbcadastre')
        wrkdossier = self.importer.datasource.get_table('wrkdossier')

        self.query = self.query.join(
            prc_data,
            schema.columns['SCHEMA_ID'] == prc_data.columns['PRCD_SCHID']
        ).join(
            urbcadastre,
            prc_data.columns['PRCD_PRC'] == urbcadastre.columns['CAD_NOM']
        ).join(
            wrkdossier,
            wrkdossier.columns['WRKDOSSIER_ID'] == urbcadastre.columns['CAD_DOSSIER_ID']
        )


class PCATypeMapper(PCAInit):

    def map(self, line, **kwargs):
        objects_args = {}
        lines = self.query.filter_by(WRKDOSSIER_ID=line[0]).all()
        if lines:
            for line in lines:
                mapped_value = self.mapPca(line, **kwargs)
                if mapped_value:
                    objects_args.update({'pca': mapped_value})

        return objects_args

    def mapPca(self, line):
        raw_pca = self.getData('SCH_FUSION', line=line)
        if raw_pca is None:
            return
        raw_pca = raw_pca.lower()

        return self.raw_pca_toDictionnary.get(raw_pca, None)


class PCAMapper(PCAInit):

    def map(self, line, **kwargs):
        objects_args = {}
        lines = self.query.filter_by(WRKDOSSIER_ID=line[0]).all()
        if lines:
            for line in lines:
                mapped_value = self.mapIsinpca(line, **kwargs)
                if mapped_value:
                    objects_args.update({'isInPCA': True})

        return objects_args

    def mapIsinpca(self, line):
        raw_pca = self.getData('SCH_FUSION', line=line)
        if raw_pca is None:
            return
        raw_pca = raw_pca.lower()

        return self.raw_pca_toDictionnary.get(raw_pca, False)


class PcaZoneTableMapper(FieldMultiLinesSecondaryTableMapper):

    def __init__(self, mysql_importer, args):
        super(PcaZoneTableMapper, self).__init__(mysql_importer, args)
        schemaaff = self.importer.datasource.get_table('schemaaff')
        schema = self.importer.datasource.get_table('schema')
        prc_data = self.importer.datasource.get_table('prc_data')
        urbcadastre = self.importer.datasource.get_table('urbcadastre')
        wrkdossier = self.importer.datasource.get_table('wrkdossier')

        self.query = self.query.join(
            schema,
            schemaaff.columns['SCA_SCHEMA_ID'] == schema.columns['SCHEMA_ID']
        ).join(
            prc_data,
            schema.columns['SCHEMA_ID'] == prc_data.columns['PRCD_SCHID']
        ).join(
            urbcadastre,
            prc_data.columns['PRCD_PRC'] == urbcadastre.columns['CAD_NOM']
        ).join(
            wrkdossier,
            wrkdossier.columns['WRKDOSSIER_ID'] == urbcadastre.columns['CAD_DOSSIER_ID']
        ).filter(schema.columns['SCH_FUSION'].like('PPA%'))

    def query_secondary_table(self, line):
        licence_id = self.getData('WRKDOSSIER_ID', line)
        lines = self.query.filter_by(WRKDOSSIER_ID=licence_id).all()
        return lines

    def mapPcazone(self, line):
        raw_pca_zone = self.getData('SCA_LABELFR', line=line)
        raw_pca_zone = raw_pca_zone.lower().strip()
        zoneDictionnary = {
            u"aire de faible densité" : "afad",
            u"aire de forte densité" : "afod",
            u"aire de moyenne densité" : "amd",
            u"dans un périmètre d'intérêt culturel, historique ou esthétique" : "dupiche",
            u"dans un périmètre d'intérêt paysager" : "dupip",
            u"dans un périmètre de réservation" : "dupdr",
            u"déclaré inhabitable" : "di",
            u"dossier en cours" : "dec",
            u"eau" : "eau",
            u"élevé" : "eleve",
            u"éloignée" : "eloi",
            u"en partie dans un périmètre de réservation" : "epdupdr",
            u"faible" : "fai",
            u"infraction relevée mais sans pv" : "irmspv",
            u"moyen" : "moy",
            u"parcs résidentiels" : "pres",
            u"périmètre de réservation sur 75 m de profondeur à partir de l'axe de la voirie" : "pdrs75mdpapdadlv",
            u"périmètre de zones protégées" : "pdzp",
            u"plan d'eau" : "peau",
            u"pv de constat d'infraction" : "pvdci",
            u"rapprochée" : "rapp",
            u"sans affectation" : "saffec",
            u"travaux imposés" : "timp",
            u"très faible" : "tfai",
            u"voirie" : "voirie",
            u"zone agricole" : "za",
            u"zone agricole dans un périmètre d'intérêt paysager" : "zadupip",
            u"zone agricole dans un périmètre d'intérêt paysager pour le surplus" : "zadupippsur",
            u"zone agricole et zone de bâtisses agricoles" : "zaezba",
            u"zone agricole et zone forestière" : "zaezf",
            u"zone agricole pour le surplus" : "zaplsur",
            u"zone agricole pour partie" : "zapp",
            u"zone artisanale" : "zart",
            u"zone boisée" : "zb",
            u"zone d'activité économique industrielle" : "zaei",
            u"zone d'activité économique mixte" : "zaem",
            u"zone d'activités économiques et commerciales" : "zaeec",
            u"zone d'aménagement communal concerté" : "zacc",
            u"zone d'aménagement communal concerté mise en oeuvre" : "zaccmeo",
            u"zone d'assainissement autonome" : "zaa",
            u"zone d'assainissement collectif" : "zac",
            u"zone d'entreprise commerciale de grande dimension" : "zecdgd",
            u"zone d'équipement communautaire" : "zec",
            u"zone d'équipements communautaires et de services publics" : "zecedsp",
            u"zone d'espaces verts" : "zev",
            u"zone d'ext d'industrie" : "zexti",
            u"zone d'ext. d'habitat" : "zexth",
            u"zone d'ext. d'habitat à caractère rural" : "zexthacr",
            u"zone d'ext.. de parcs résidentiels" : "zextdpr",
            u"zone d'extension pour bâtisses  espacées" : "zexpbe",
            u"zone d'extension pour bâtisses espacées" : "zexpbe",
            u"zone d'extraction" : "zextract",
            u"zone d'habitat" : "zha",
            u"zone d'habitat à caractère rural" : "zhaacr",
            u"zone d'habitat à caractère rural sur une profondeur de 40 mètres" : "zhaacrsp40",
            u"zone d'habitat à caractère rural sur une profondeur de 50 mètres" : "zhaacrsp50",
            u"zone d'habitat dans un périmètre d'intérêt culturel, historique ou esthétique" : "zhadupiche",
            u"zone d'habitat sur 50 m de profondeur" : "zhas50dp",
            u"zone d'habitation" : "zhation",
            u"zone d'habitation, annexes, abris" : "zhaaa",
            u"zone de bâtisses agricoles" : "zdba",
            u"zone de construction d'habitation fermée" : "zdchaf",
            u"zone de construction d'habitation ouverte" : "zdchao",
            u"zone de construction d'habitation semi-ouverte" : "zdchaso",
            u"zone de construction en annexe" : "zdcea",
            u"zone de cours et jardins" : "zdcej",
            u"zone de loisirs" : "zdl",
            u"zone de parc" : "zdparc",
            u"zone de parc ou d'espaces verts" : "zdparcev",
            u"zone de prévention en matière de prises d'eau souterraines, zones éloignées." : "zdpemdpeausoutze",
            u"zone de recul" : "zdrec",
            u"zone de recul et de voirie" : "zdrecedv",
            u"zone de recul, zone de construction d'habitation fermée et zone de cours et jardins" : "zdreczdchafeezdcej",
            u"zone de service" : "zdserv",
            u"zone de voirie réservée aux piétons" : "zdvoirap",
            u"zone de voiries et d'espaces publics" : "zdveep",
            u"zone faiblement habitée" : "zfaiha",
            u"zone forestière" : "zforest",
            u"zone forestière d'intérêt paysager" : "zforestip",
            u"zone industrielle" : "zi",
            u"zone réservée aux annexes" : "zresaa",
            u"zone réservée aux constructions à un étage" : "zresacaue",
            u"zone réservée aux constructions principales" : "zresacprinc",
            u"zone réservée aux constructions principales, en zone de cours et jardins et en voirie" : "zresacprincezcejeev",
        }

        if raw_pca_zone in zoneDictionnary:
            return zoneDictionnary[raw_pca_zone]
        else:
            return "unknown"

class StreetAndNumberMapper(SubQueryMapper):

    def __init__(self, mysql_importer, args):
        super(StreetAndNumberMapper, self).__init__(mysql_importer, args)
        k2adr = self.importer.datasource.get_table('k2adr')
        adr = self.importer.datasource.get_table('adr')
        wrkdossier = self.importer.datasource.get_table('wrkdossier')

        self.query = self.query.join(
            k2adr,
            k2adr.columns['K_ID2'] == adr.columns['ADR_ID']
        ).join(
            wrkdossier,
            wrkdossier.columns['WRKDOSSIER_ID'] == k2adr.columns['K_ID1']
        ).add_column(adr.columns['ADR_ID']
        ).add_column(wrkdossier.columns['WRKDOSSIER_ID'])

    def mapWorklocations(self, line, **kwargs):
        objects_args = ()

        lines = self.query.filter_by(WRKDOSSIER_ID=line[0]).all()
        if lines :
            street = Utils.convertToUnicode(lines[0][1] if lines[0][1] is not None else "")
            street_uid = ''
            if street:
                street_uid = Utils.searchByStreet(street)
                if not street_uid:
                    self.logError(self, line, 'Work Locations : Pas de rue trouvée pour cette valeur : ', {'TYPE value': street})

            objects_args = ({'street': street_uid, 'number': lines[0][4] if lines[0][4] is not None else "" },)

        return objects_args


class InvestigationDateMapper(SecondaryTableMapper):

    def __init__(self, mysql_importer, args):
        super(InvestigationDateMapper, self).__init__(mysql_importer, args)
        wrkparam = self.importer.datasource.get_table('wrkparam')
        k2 = self.importer.datasource.get_table('k2')
        wrkdossier = self.importer.datasource.get_table('wrkdossier')

        self.query = self.query.join(
            k2,
            wrkparam.columns['WRKPARAM_ID'] == k2.columns['K_ID2']
        ).join(
            wrkdossier,
            wrkdossier.columns['WRKDOSSIER_ID'] == k2.columns['K_ID1']
        ).filter(or_(wrkparam.columns['PARAM_IDENT'] == 'EnqDatDeb',
                     wrkparam.columns['PARAM_IDENT'] == 'EnqDatFin', ))

    def map(self, line, **kwargs):
        objects_args = {}
        lines = self.query.filter_by(WRKDOSSIER_ID=line[0]).all()
        if lines:
            for line in lines:
                if (self.getData('PARAM_IDENT', line=line) == 'EnqDatDeb'):
                    if (self.getData('PARAM_VALUE', line=line)):
                        objects_args.update({'investigationStart': self.inverseDateDayMonth(self.getData('PARAM_VALUE', line=line))})
                elif (self.getData('PARAM_IDENT', line=line) == 'EnqDatFin'):
                    if (self.getData('PARAM_VALUE', line=line)):
                        objects_args.update({'investigationEnd': self.inverseDateDayMonth(self.getData('PARAM_VALUE', line=line))})
                else:
                    return

        return objects_args

    def inverseDateDayMonth(self,date):

        # TODO this is a W.A, change zope/plone config to avoid this ?
        if date and (len(date) == 10):
            month = date[0:2]
            day = date[3:5]
            year = date[6:10]
            inverseDate = u"" + day + '-' + month + '-' + year
            return inverseDate

        return date


class FD_SolicitOpinionMapper(SecondaryTableMapper):

    def __init__(self, mysql_importer, args):
        super(FD_SolicitOpinionMapper, self).__init__(mysql_importer, args)
        wrkparam = self.importer.datasource.get_table('wrkparam')
        k2 = self.importer.datasource.get_table('k2')
        wrkdossier = self.importer.datasource.get_table('wrkdossier')

        self.query = self.query.join(
            k2,
            wrkparam.columns['WRKPARAM_ID'] == k2.columns['K_ID2']
        ).join(
            wrkdossier,
            wrkdossier.columns['WRKDOSSIER_ID'] == k2.columns['K_ID1']
        ).filter(and_(wrkparam.columns['PARAM_VALUE'] == '1',
                     wrkparam.columns['PARAM_NOMFUSION'].like(u'%avis préalable du FD%')))

    def map(self, line, **kwargs):
        objects_args = {}
        lines = self.query.filter_by(WRKDOSSIER_ID=line[0]).all()
        if lines:
            objects_args.update({'procedureChoice': 'FD'})
            # objects_args.update({'roadAdaptation': 'create'}) # Removed after customer demand

        return objects_args

class Voirie_SolicitOpinionMapper(SubQueryMapper):

    def __init__(self, mysql_importer, args):
        super(Voirie_SolicitOpinionMapper, self).__init__(mysql_importer, args)
        wrkparam = self.importer.datasource.get_table('wrkparam')
        k2 = self.importer.datasource.get_table('k2')
        wrkdossier = self.importer.datasource.get_table('wrkdossier')

        self.query = self.query.join(
            k2,
            wrkparam.columns['WRKPARAM_ID'] == k2.columns['K_ID2']
        ).join(
            wrkdossier,
            wrkdossier.columns['WRKDOSSIER_ID'] == k2.columns['K_ID1']
        ).filter(and_(wrkparam.columns['PARAM_VALUE'] == '1',or_(wrkparam.columns['PARAM_NOMFUSION'].like(u"%accordable à l'égout%"),
                                                                 wrkparam.columns['PARAM_NOMFUSION'].like(u"%voirie équipée%"),
                                                                 wrkparam.columns['PARAM_NOMFUSION'].like(u"%épuration individuelle%"))
                      ,or_(wrkdossier.columns['DOSSIER_TDOSSIERID'] == -34766,wrkdossier.columns['DOSSIER_TDOSSIERID'] == -5753))
                     )

    def mapRoadspecificfeatures(self, line, **kwargs):
        objects_response = {}
        lines = self.query.filter_by(WRKDOSSIER_ID=line[0]).all()
        if lines:
            raccordable_egout = ''
            raccordable_egout_prevision = ''
            zone_faiblement_habitee = ''
            voirie_suffisamment_equipee = ''
            for line in lines:
                voirie_eq = self.getData('PARAM_NOMFUSION', line=line)
                if  voirie_eq == u"accordable \xe0 l'\xe9gout":
                    raccordable_egout = '1'
                elif voirie_eq == u"sera accordable \xe0 l'\xe9gout":
                    raccordable_egout_prevision = '1'
                elif voirie_eq == u"Epuration individuelle":
                    zone_faiblement_habitee = '1'
                elif voirie_eq == u"acc\xe8s voirie \xe9quip\xe9e" or voirie_eq == u"Voirie \xe9quip\xe9e":
                    voirie_suffisamment_equipee = '1'

            objects_response = (
            {'check': raccordable_egout,
              'id': 'raccordable-egout',
              'text': "<p>est actuellement raccordable \xc3\xa0 l'\xc3\xa9gout selon les normes fix\xc3\xa9es par le Service Technique Communal;</p>",
              'value': "Raccordable \xc3\xa0 l'\xc3\xa9gout"
             },
             {'check': raccordable_egout_prevision,
              'id': 'raccordable-egout-prevision',
              'text': "<p>sera raccordable \xc3\xa0l'\xc3\xa9gout selon les pr\xc3\xa9visions actuelles;</p>",
              'value': "Raccordable \xc3\xa0 l'\xc3\xa9gout (pr\xc3\xa9vision),"
              },
             {'check': zone_faiblement_habitee,
              'id': 'zone-faiblement-habitee',
              'text': "<p>est situ\xc3\xa9 dans une des zones faiblement habit\xc3\xa9e qui ne seront pas pourvue d'\xc3\xa9gout et qui feront l'objet d'une \xc3\xa9puration individuelle;</p>",
              'value': 'Zone faiblement habit\xc3\xa9e (\xc3\xa9puration individuelle),'
              },
             {'check': voirie_suffisamment_equipee,
              'id': 'voirie-suffisamment-equipee',
              'text': "<p>b\xc3\xa9n\xc3\xa9ficie d'un acc\xc3\xa8s \xc3\xa0 une voirie suffisamment \xc3\xa9quip\xc3\xa9e en eau, \xc3\xa9lectricit\xc3\xa9, pourvue d'un rev\xc3\xaatement solide et d'une largeur suffisante compte tenu de la situation des lieux;</p>",
              'value': 'Voirie suffisamment \xc3\xa9quip\xc3\xa9e'
              })

        return objects_response


class ParcelsMapper(MultiLinesSecondaryTableMapper):
    """ """


class CompletionStateMapper(PostCreationMapper):

    def map(self, line, plone_object):
        state = self.getData('DOSSIER_OCTROI', line)
        transition = self.getValueMapping('state_map')[state]
        if transition:
            try:
                api.content.transition(plone_object, transition)
            except InvalidParameterError:
                # TODO check valid transition for Division (type -14179, id 6294300)
                # if plone_object.getId() == '6294300l':
                api.content.transition(plone_object, 'nonapplicable')


class ErrorsMapper(FinalMapper):

    def mapDescription(self, line, plone_object):

        line_number = self.importer.current_line
        errors = self.importer.errors.get(line_number, None)
        description = plone_object.Description()

        error_trace = []

        if errors:
            for error in errors:
                data = error.data
                if 'streets' in error.message:
                    error_trace.append('<p>adresse : %s</p>' % data['address'])
                elif 'notaries' in error.message:
                    error_trace.append('<p>notaire : %s %s %s</p>' % (data['title'], data['firstname'], data['name']))
                elif 'architects' in error.message:
                    error_trace.append('<p>architecte : %s</p>' % data['raw_name'])
                elif 'geometricians' in error.message:
                    error_trace.append('<p>géomètre : %s</p>' % data['raw_name'])
                elif 'parcelling' in error.message:
                    error_trace.append('<p>lotissement : %s %s, autorisé le %s</p>' % (
                    data['approval date'], data['city'], data['auth_date']))
                elif 'article' in error.message.lower():
                    error_trace.append('<p>Articles de l\'enquête : %s</p>' % (data['articles']))
        error_trace = ''.join(error_trace)

        return '%s%s' % (error_trace, description)


#
# CONTACT
#

# factory


class ContactFactory(BaseFactory):

    def getPortalType(self, container, **kwargs):
        if container.portal_type in ['UrbanCertificateOne', 'UrbanCertificateTwo', 'NotaryLetter', 'Division']:
            return 'Proprietary'
        return 'Applicant'


# mappers


class ApplicantMapper(SecondaryTableMapper):

    def __init__(self, mysql_importer, args):
        super(ApplicantMapper, self).__init__(mysql_importer, args)
        cpsn = self.importer.datasource.get_table('cpsn')
        wrkdossier = self.importer.datasource.get_table('wrkdossier')
        cloc = self.importer.datasource.get_table('cloc')
        k2 = self.importer.datasource.get_table('k2')
        k2cloctmp = self.importer.datasource.get_table('k2')
        k2cloc = k2cloctmp.alias('k2cloc')

        self.query = self.init_query(self.table)
        self.query = self.query.join(
            k2, wrkdossier.columns['WRKDOSSIER_ID'] == k2.columns['K_ID2'])

        self.query = self.query.join(
            cpsn, cpsn.columns['CPSN_ID'] == k2.columns['K_ID1']
        )

        self.query = self.query.join(
            k2cloc, cpsn.columns['CPSN_ID'] == k2cloc.columns['K_ID2']
        ).join(
            cloc, cloc.columns['CLOC_ID'] == k2cloc.columns['K_ID1']
        ).add_column(wrkdossier.columns['WRKDOSSIER_ID']
        ).add_column(cpsn.columns['CPSN_NOM']
        ).add_column(cpsn.columns['CPSN_PRENOM']
        ).add_column(cpsn.columns['CPSN_EMAIL']
        ).add_column(cpsn.columns['CPSN_FAX']
        ).add_column(cpsn.columns['CPSN_TYPE']
        ).add_column(cpsn.columns['CPSN_TEL1']
        ).add_column(cpsn.columns['CPSN_GSM']
        ).add_column(cloc.columns['CLOC_ADRESSE']
        ).add_column(cloc.columns['CLOC_ZIP']
        ).add_column(cloc.columns['CLOC_LOCALITE']
        ).add_column(wrkdossier.columns['WRKDOSSIER_ID']
        ).add_column(wrkdossier.columns['DOSSIER_TDOSSIERID'])

        # cpsn type id 89801 = notaries
        linesNotaries = self.query.filter(k2.columns['K2KND_ID']==-204, cpsn.columns['CPSN_TYPE']==89801).all()
        if linesNotaries:
            Utils.createNotaries(linesNotaries)

        # cpsn type id 353506 = architects
        linesArchitects = self.query.filter(k2.columns['K2KND_ID'] == -204, cpsn.columns['CPSN_TYPE'] == 353506).all()
        if linesArchitects:
            Utils.createArchitects(linesArchitects)

    def query_secondary_table(self, line):
        licence_id = self.getData('WRKDOSSIER_ID', line)
        applicant_type = -204
        k2 = self.importer.datasource.get_table('k2')
        lines = self.query.filter(k2.columns['K_ID2']==licence_id, k2.columns['K2KND_ID']==applicant_type).all()

        return lines


class ContactIdMapper(Mapper):

    def mapId(self, line):

        name = '%s%s' % (self.getData('CPSN_NOM'), self.getData('CPSN_PRENOM'))
        name = name.replace(' ', '').replace('-', '')
        contact_id = normalizeString(self.site.portal_urban.generateUniqueId(name))
        return contact_id


class ContactTitleMapper(Mapper):

    def mapPersontitle(self, line):

        title = self.getData('CPSN_TYPE')
        title_mapping = self.getValueMapping('titre_map')
        return title_mapping.get(title, 'notitle')


class ContactPhoneMapper(Mapper):

    def mapPhone(self, line):

        phone_numbers = []

        phone = self.getData('CPSN_TEL1')
        if phone:
            phone_numbers.append(phone)

        gsm = self.getData('CPSN_GSM')
        if gsm:
            phone_numbers.append(gsm)

        return ', '.join(phone_numbers)


class NotaryContactMapper(PostCreationMapper, SubQueryMapper):

    def __init__(self, mysql_importer, args):
        super(NotaryContactMapper, self).__init__(mysql_importer, args)
        cpsn = self.importer.datasource.get_table('cpsn')
        wrkdossier = self.importer.datasource.get_table(self.table)
        cloc = self.importer.datasource.get_table('cloc')
        k2 = self.importer.datasource.get_table('k2')
        k2cloctmp = self.importer.datasource.get_table('k2')
        k2cloc = k2cloctmp.alias('k2cloc')
        self.query = self.init_query(self.table)
        self.query = self.query.join(
            k2, wrkdossier.columns['WRKDOSSIER_ID'] == k2.columns['K_ID2'])

        self.query = self.query.join(
            cpsn, cpsn.columns['CPSN_ID'] == k2.columns['K_ID1']
        )

        self.query = self.query.join(
            k2cloc, cpsn.columns['CPSN_ID'] == k2cloc.columns['K_ID2']
        ).join(
            cloc, cloc.columns['CLOC_ID'] == k2cloc.columns['K_ID1']
        ).filter(or_(wrkdossier.columns['DOSSIER_TDOSSIERID'] == -5753,
                     wrkdossier.columns['DOSSIER_TDOSSIERID'] == -34766, )
        ).add_column(wrkdossier.columns['WRKDOSSIER_ID']
        ).add_column(wrkdossier.columns['DOSSIER_TDOSSIERID']
        ).add_column(wrkdossier.columns['WRKDOSSIER_ID']
        ).add_column(cpsn.columns['CPSN_NOM']
        ).add_column(cpsn.columns['CPSN_PRENOM']
        ).add_column(cpsn.columns['CPSN_TEL1']
        ).add_column(cpsn.columns['CPSN_GSM']
        ).add_column(cpsn.columns['CPSN_EMAIL']
        ).add_column(cpsn.columns['CPSN_TYPE']
        ).add_column(cloc.columns['CLOC_ADRESSE']
        ).add_column(cloc.columns['CLOC_ZIP']
        ).add_column(cloc.columns['CLOC_LOCALITE']
        )


    def init_query(self, table):
        datasource = self.importer.datasource
        query = datasource.session.query(datasource.get_table(table))
        return query

    def mapNotarycontact(self,line, plone_object):

        wrkdossier = self.importer.datasource.get_table(self.table)

        lines = self.query.filter(wrkdossier.columns['WRKDOSSIER_ID'] == line[0]).all()
        if lines:

            firstPart = Utils.convertToUnicode(lines[0][36])
            secondPart = Utils.convertToUnicode(lines[0][37])
            idNotary = idnormalizer.normalize(Utils.createId(firstPart, secondPart, 'Notary').replace(" ",""))
            containerNotaries = api.content.get(path='/Plone/urban/notaries')

            if idNotary not in containerNotaries.objectIds():
                self.createNotary(lines[0])

            item = api.content.get(path='/Plone/urban/notaries/' + idNotary)
            return item.UID()

    def createNotary(self, notary_infos):

        firstPart = Utils.convertToUnicode(notary_infos[36])
        secondPart = Utils.convertToUnicode(notary_infos[37])

        new_id = idnormalizer.normalize(Utils.createId(firstPart,secondPart, 'Notary').replace(" ",""))
        new_name1 = firstPart if firstPart else ""
        new_name2 = secondPart if secondPart else ""

        telfixe = str(notary_infos[38]) if notary_infos[38] else ""
        telgsm = str(notary_infos[39]) if notary_infos[39] else ""
        email = str(notary_infos[40]) if notary_infos[40] else ""
        street = Utils.convertToUnicode(str(notary_infos[42])) if notary_infos[42] else ""
        zipcode = str(notary_infos[43]) if notary_infos[43] else ""
        city = Utils.convertToUnicode(str(notary_infos[44])) if notary_infos[44] else ""

        notarytitle = notary_infos[41]
        title_mapping = self.getValueMapping('titre_map')
        title = title_mapping.get(notarytitle, '')

        container = api.content.get(path='/Plone/urban/notaries')

        if not (new_id in container.objectIds()):
            object_id = container.invokeFactory('Notary', id=new_id,
                                                name1=new_name1,
                                                name2=new_name2,
                                                phone=telfixe,
                                                gsm=telgsm,
                                                email=email,
                                                personTitle=title,
                                                street=street,
                                                zipcode=zipcode,
                                                city=city)

class ArchitectsMapper(PostCreationMapper, SubQueryMapper):

    def __init__(self, mysql_importer, args):
        super(ArchitectsMapper, self).__init__(mysql_importer, args)
        cpsn = self.importer.datasource.get_table('cpsn')
        wrkdossier = self.importer.datasource.get_table(self.table)
        cloc = self.importer.datasource.get_table('cloc')
        k2 = self.importer.datasource.get_table('k2')
        k2cloctmp = self.importer.datasource.get_table('k2')
        k2cloc = k2cloctmp.alias('k2cloc')
        self.query = self.init_query(self.table)
        self.query = self.query.join(
            k2, wrkdossier.columns['WRKDOSSIER_ID'] == k2.columns['K_ID2'])

        self.query = self.query.join(
            cpsn, cpsn.columns['CPSN_ID'] == k2.columns['K_ID1']
        )

        self.query = self.query.join(
            k2cloc, cpsn.columns['CPSN_ID'] == k2cloc.columns['K_ID2']
        ).join(
            cloc, cloc.columns['CLOC_ID'] == k2cloc.columns['K_ID1']
        ).filter(or_(cpsn.columns['CPSN_TYPE'] == 353506,
                     cpsn.columns['CPSN_TYPE'] == 4314287, )
        ).add_column(wrkdossier.columns['WRKDOSSIER_ID']
        ).add_column(cpsn.columns['CPSN_NOM']
        ).add_column(cpsn.columns['CPSN_PRENOM']
        ).add_column(cpsn.columns['CPSN_EMAIL']
        ).add_column(cpsn.columns['CPSN_FAX']
        ).add_column(cpsn.columns['CPSN_TYPE']
        ).add_column(cpsn.columns['CPSN_TEL1']
        ).add_column(cpsn.columns['CPSN_GSM']
        ).add_column(cloc.columns['CLOC_ADRESSE']
        ).add_column(cloc.columns['CLOC_ZIP']
        ).add_column(cloc.columns['CLOC_LOCALITE'])

    def init_query(self, table):
        datasource = self.importer.datasource
        query = datasource.session.query(datasource.get_table(table))
        return query

    def mapArchitects(self, line, plone_object):

        wrkdossier = self.importer.datasource.get_table(self.table)

        lines = self.query.filter(wrkdossier.columns['WRKDOSSIER_ID'] == line[0]).all()
        if not lines:
            return None
        firstPart = Utils.convertToUnicode(lines[0][34])
        secondPart = Utils.convertToUnicode(lines[0][35])
        idArchitect = idnormalizer.normalize(Utils.createId(firstPart, secondPart,'Architect').replace(" ", ""))
        containerArchitects = api.content.get(path='/Plone/urban/architects')

        if idArchitect not in containerArchitects.objectIds():
            Utils.createArchitects([lines[0]])

        item = api.content.get(path='/Plone/urban/architects/' + idArchitect)
        if item:
            return item.UID()
#
# PARCEL
#

# factory


class ParcelFactory(BaseFactory):

    def create(self, parcel, container=None, line=None):
        searchview = self.site.restrictedTraverse('searchparcels')

        if parcel is None:
            return None

        # need to trick the search browser view about the args in its request
        parcel_args = parcel.to_dict()
        parcel_args.pop('partie')

        for k, v in parcel_args.iteritems():
            searchview.context.REQUEST[k] = v
        # check if we can find a parcel in the db cadastre with these infos
        found = searchview.findParcel(**parcel_args)
        if not found:
            found = searchview.findParcel(browseoldparcels=True, **parcel_args)

        if len(found) == 1 and parcel.has_same_attribute_values(found[0]):
            parcel_args['divisionCode'] = parcel_args['division']
            parcel_args['isOfficialParcel'] = True
        else:
            self.logError(self, line, 'Too much parcels found or not enough parcels found',
                          {'args': parcel_args, 'search result': len(found)})
            parcel_args['isOfficialParcel'] = False

        parcel_args['id'] = parcel.id
        parcel_args['partie'] = parcel.partie

        return super(ParcelFactory, self).create(parcel_args, container=container)

    def objectAlreadyExists(self, parcel, container):
        if not parcel:
            return
        existing_object = getattr(container, parcel.id, None)
        return existing_object


# mappers


class ParcelDataMapper(Mapper):

    def map(self, line, **kwargs):
        raw_reference = self.getData('CAD_NOM')
        reference = parse_cadastral_reference(raw_reference)
        cadastral_ref = CadastralReference(*reference)
        division_map = self.getValueMapping('division_map')
        if cadastral_ref.division:
            cadastral_ref.division = division_map[cadastral_ref.division]
        else:
            cadastral_ref = None
        return cadastral_ref


#
# UrbanEvent deposit
#

class EventDateMapper(SecondaryTableMapper):

    def __init__(self, mysql_importer, args):
        super(EventDateMapper, self).__init__(mysql_importer, args)
        wrketape = self.importer.datasource.get_table('wrketape')
        k2 = self.importer.datasource.get_table('k2')
        self.query = self.query.filter_by(
            ETAPE_NOMFR=args['event_name'],
        ).join(
            k2, wrketape.columns['WRKETAPE_ID'] == k2.columns['K_ID2']
        )

    def query_secondary_table(self, line):
        licence_id = self.getData('WRKDOSSIER_ID', line)
        event_type = -207 # etape
        lines = self.query.filter_by(K_ID1=licence_id, K2KND_ID=event_type).all()
        if not lines:
            raise NoObjectToCreateException

        return lines


class EventDecisionMapper(SecondaryTableMapper):

    def __init__(self, mysql_importer, args):
        super(EventDecisionMapper, self).__init__(mysql_importer, args)
        wrkparam = self.importer.datasource.get_table('wrkparam')
        k2 = self.importer.datasource.get_table('k2')
        self.query = self.query.filter_by(
            PARAM_NOMFUSION=args['event_name'],
        ).join(
            k2, wrkparam.columns['WRKPARAM_ID'] == k2.columns['K_ID2']
        )

    def query_secondary_table(self, line):
        licence_id = self.getData('WRKDOSSIER_ID', line)
        event_type = -208 # param
        lines = self.query.filter_by(K_ID1=licence_id, K2KND_ID=event_type).all()
        if not lines:
            raise NoObjectToCreateException

        return lines

class EventDecisionAlternativeMapper(SecondaryTableMapper):

    def __init__(self, mysql_importer, args):
        super(EventDecisionAlternativeMapper, self).__init__(mysql_importer, args)
        wrkparam = self.importer.datasource.get_table('wrkparam')
        k2 = self.importer.datasource.get_table('k2')
        self.query = self.query.filter_by(
            PARAM_NOMFUSION=args['event_name'],
        ).join(
            k2, wrkparam.columns['WRKPARAM_ID'] == k2.columns['K_ID2']
        )

    def query_secondary_table(self, line):
        licence_id = self.getData('WRKDOSSIER_ID', line)
        event_type = -208 # param
        lines = self.query.filter_by(K_ID1=licence_id, K2KND_ID=event_type).all()
        if not lines:
            raise NoObjectToCreateException

        return lines

# factory
class UrbanEventFactory(BaseFactory):

    def getPortalType(self, **kwargs):
        return 'UrbanEvent'

    def create(self, kwargs, container, line):
        if not kwargs['eventtype']:
            return []
        eventtype_uid = kwargs.pop('eventtype')
        urban_event = container.createUrbanEvent(eventtype_uid, **kwargs)
        return urban_event


# mappers


class DepositEventMapper(Mapper):

    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = self.getValueMapping('eventtype_id_map')[licence.portal_type]['deposit_event']
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class DepositDateMapper(Mapper):

    def mapEventdate(self, line):

        date = self.getData('DOSSIER_DATEDEPOT')
        if not date:
            raise NoObjectToCreateException
        date = date and DateTime(date) or None
        return date


class DepositEventIdMapper(Mapper):

    def mapId(self, line):
        return 'deposit'


#
# UrbanEvent complete Folder
#

# mappers


class CompleteFolderEventMapper(Mapper):

    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = self.getValueMapping('eventtype_id_map')[licence.portal_type]['folder_complete']
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class CompleteFolderDateMapper(Mapper):

    def mapEventdate(self, line):
        date = self.getData('ETAPE_DATEDEPART')
        if not date:
            raise NoObjectToCreateException
        date = date and DateTime(date) or None
        return date


class CompleteFolderEventIdMapper(Mapper):

    def mapId(self, line):
        return 'complete_folder'


#
# UrbanEvent decision
#

# mappers


class DecisionEventTypeMapper(Mapper):

    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = self.getValueMapping('eventtype_id_map')[licence.portal_type]['decision_event']
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class DecisionEventIdMapper(Mapper):

    def mapId(self, line):
        return 'decision-event'


class DecisionEventDateMapper(Mapper):

    def mapEventdate(self, line):

        date = self.getData('DOSSIER_DATEDELIV')
        if not date:
            self.logError(self, line, 'No decision date found')
        return str(date)

class DecisionEventDecisionMapper(Mapper):

    def mapDecision(self, line):
        decision = self.getData('PARAM_VALUE')

        if decision and decision == u'1':
            return u'Octroyé'
        else:
            return u'Refusé'

class DecisionEventDecisionDateMapper(Mapper):

    def mapDecisiondate(self, line):
        date = self.getData('ETAPE_DATEDEPART')
        if not date:
            raise NoObjectToCreateException
        date = date and DateTime(date) or None
        return date
#
# UrbanEvent send licence to applicant
#

# mappers


class LicenceToApplicantEventMapper(Mapper):

    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = self.getValueMapping('eventtype_id_map')[licence.portal_type]['send_licence_applicant_event']
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class LicenceToApplicantDateMapper(Mapper):

    def mapEventdate(self, line):
        date = self.getData('ETAPE_DATEDEPART')
        if not date:
            raise NoObjectToCreateException
        date = date and DateTime(date) or None
        return date


class LicenceToApplicantEventIdMapper(Mapper):

    def mapId(self, line):
        return 'licence_to_applicant'


#
# UrbanEvent send licence to FD
#

# mappers


class LicenceToFDEventMapper(Mapper):

    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = self.getValueMapping('eventtype_id_map')[licence.portal_type]['send_licence_fd_event']
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class LicenceToFDDateMapper(Mapper):

    def mapEventdate(self, line):
        date = self.getData('ETAPE_DATEDEPART')
        if not date:
            raise NoObjectToCreateException
        date = date and DateTime(date) or None
        return date


class LicenceToFDEventIdMapper(Mapper):
    def mapId(self, line):
        return 'licence_to_fd'


#
# UrbanEvent college report
#

# mappers


class CollegeReportEventMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = 'rapport-du-college'
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class CollegeReportEventDateMapper(Mapper):

    def mapEventdate(self, line):
        date = self.getData('ETAPE_DATEDEPART')
        if not date:
            raise NoObjectToCreateException
        date = date and DateTime(date) or None
        return date


class CollegeReportEventDecisionDateMapper(Mapper):

    def mapDecisiondate(self, line):
        date = self.getData('ETAPE_DATEDEPART')
        if not date:
            raise NoObjectToCreateException
        date = date and DateTime(date) or None
        return date


class CollegeReportEventDecisionMapper(Mapper):

    def mapDecision(self, line):
        decision = self.getData('PARAM_VALUE')
        if not decision:
            return None

        return decision


class CollegeReportEventIdMapper(Mapper):
    def mapId(self, line):
        return 'rapport-du-college'


#
# UrbanEvent complete Folder
#

# mappers


class FirstFolderTransmittedToRwEventTypeMapper(Mapper):

    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = self.getValueMapping('eventtype_id_map')[licence.portal_type][
            'first_folder_transmitted_to_rw_event']
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class FirstFolderTransmittedToRwEventIdMapper(Mapper):

    def mapId(self, line):
        return 'transmis-1er-dossier-rw'

class FirstFolderTransmmittedToRwEventDateMapper(Mapper):

    def mapEventdate(self, line):
        date = self.getData('ETAPE_DATEDEPART')
        if not date:
            return None
        return date

class FirstFolderTransmmittedToRwDecisionDateMapper(Mapper):

    def mapDecisiondate(self, line):
        decisionDate = self.getData('PARAM_VALUE')
        if not decisionDate:
            return None
        return decisionDate

class FirstFolderTransmmittedToRwDecisionMapper(Mapper):

    def mapExternaldecision(self, line):
        decision = self.getData('PARAM_VALUE')
        if not decision:
            return None
        return decision


    def query_secondary_table(self, line):
        licence_id = self.getData('WRKDOSSIER_ID', line)
        lines = self.query.filter_by(WRKDOSSIER_ID=licence_id).all()

        if not lines:
            raise NoObjectToCreateException

        return lines


# *** Utils ***

class Utils():

    @staticmethod
    def convertToUnicode(string):

        # convert to unicode if necessary, against iso-8859-1 : iso-8859-15 add € and oe characters
        data = ""
        if string and type(string) is str:
            data = unicode(string, "iso-8859-15")
        return data


    @staticmethod
    def searchByStreet(street):

        catalog = api.portal.get_tool('portal_catalog')
        street = street.replace('(', ' ').replace(')', ' ').strip()
        street_uids = [brain.UID for brain in catalog(portal_type='Street', Title=street)]
        if not street_uids:
            # second chance without street number
            strwithoutdigits = ''.join([letter for letter in street if not letter.isdigit()]).strip()
            street_uids = [brain.UID for brain in catalog(portal_type='Street', Title=strwithoutdigits)]
            if not street_uids and len(strwithoutdigits.strip()) > 1:
                # last chance : try to remove last char, for example : 1a or 36C
                strwithoutlastchar = strwithoutdigits.strip()[:-1]
                street_uids = [brain.UID for brain in catalog(portal_type='Street', Title=strwithoutlastchar)]
                if not street_uids:
                    # log the address issue infos
                    with open("matchBestAddressError.csv", "a") as file:
                        file.write(Utils.convertToUnicode(strwithoutlastchar) + "\n")

        return street_uids

    @staticmethod
    def createId(name, firstName, type):
        idToNormalize = u"" + type

        if name:
            idToNormalize += name
        if firstName:
            idToNormalize += firstName

        return idToNormalize

    @staticmethod
    def createNotaries(notaryInfos):

        for notaryInfo in notaryInfos:

            firstPart = Utils.convertToUnicode(notaryInfo[34])
            secondPart = Utils.convertToUnicode(notaryInfo[35])

            idNotary = idnormalizer.normalize(Utils.createId(firstPart, secondPart, 'Notary').replace(" ", ""))
            containerNotaries = api.content.get(path='/Plone/urban/notaries')

            if idNotary not in containerNotaries.objectIds():

                new_id = idNotary
                new_name1 = firstPart if firstPart else ""
                new_name2 = secondPart if secondPart else ""

                telfixe = str(notaryInfo[39]) if notaryInfo[39] else ""
                telgsm = str(notaryInfo[40]) if notaryInfo[40] else ""
                email = str(notaryInfo[36]) if notaryInfo[36] else ""
                street = Utils.convertToUnicode(str(notaryInfo[41])) if notaryInfo[41] else ""
                zipcode = str(notaryInfo[42]) if notaryInfo[42] else ""
                city = Utils.convertToUnicode(str(notaryInfo[43])) if notaryInfo[43] else ""

                title = 'master'

                container = api.content.get(path='/Plone/urban/notaries')

                if not (new_id in container.objectIds()):
                    object_id = container.invokeFactory('Notary', id=new_id,
                                                        name1=new_name1,
                                                        name2=new_name2,
                                                        phone=telfixe,
                                                        gsm=telgsm,
                                                        email=email,
                                                        personTitle=title,
                                                        street=street,
                                                        zipcode=zipcode,
                                                        city=city)

    @staticmethod
    def createArchitects(architectsInfos):

        for architectsInfo in architectsInfos:

            firstPart = Utils.convertToUnicode(architectsInfo[34])
            secondPart = Utils.convertToUnicode(architectsInfo[35])

            idArchitect = idnormalizer.normalize(Utils.createId(firstPart, secondPart, 'Architect').replace(" ", ""))
            containerArchitects = api.content.get(path='/Plone/urban/architects')

            if idArchitect not in containerArchitects.objectIds():

                new_id = idArchitect
                new_name1 = firstPart if firstPart else ""
                new_name2 = secondPart if secondPart else ""

                telfixe = str(architectsInfo[39]) if architectsInfo[39] else ""
                telgsm = str(architectsInfo[40]) if architectsInfo[40] else ""
                email = str(architectsInfo[36]) if architectsInfo[36] else ""
                street = Utils.convertToUnicode(str(architectsInfo[41])) if architectsInfo[41] else ""
                zipcode = str(architectsInfo[42]) if architectsInfo[42] else ""
                city = Utils.convertToUnicode(str(architectsInfo[43])) if architectsInfo[43] else ""

                container = api.content.get(path='/Plone/urban/architects')

                if not (new_id in container.objectIds()):
                    object_id = container.invokeFactory('Architect', id=new_id,
                                                        name1=new_name1,
                                                        name2=new_name2,
                                                        phone=telfixe,
                                                        gsm=telgsm,
                                                        email=email,
                                                        street=street,
                                                        zipcode=zipcode,
                                                        city=city)
