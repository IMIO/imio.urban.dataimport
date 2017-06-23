# -*- coding: utf-8 -*-

from imio.urban.dataimport.access.mapper import AccessFinalMapper as FinalMapper
from imio.urban.dataimport.access.mapper import AccessMapper as Mapper
from imio.urban.dataimport.access.mapper import AccessPostCreationMapper as PostCreationMapper
from imio.urban.dataimport.access.mapper import MultiLinesSecondaryTableMapper
from imio.urban.dataimport.access.mapper import SecondaryTableMapper
from imio.urban.dataimport.access.mapper import SubQueryMapper

from imio.urban.dataimport.config import IMPORT_FOLDER_PATH

from imio.urban.dataimport.exceptions import NoObjectToCreateException

from imio.urban.dataimport.factory import BaseFactory
from imio.urban.dataimport.utils import CadastralReference
from imio.urban.dataimport.utils import cleanAndSplitWord
from imio.urban.dataimport.utils import guess_cadastral_reference
from imio.urban.dataimport.utils import identify_parcel_abbreviations
from imio.urban.dataimport.utils import parse_cadastral_reference

from DateTime import DateTime
from Products.CMFPlone.utils import normalizeString
from Products.CMFPlone.utils import safe_unicode

from plone import api
from plone.i18n.normalizer import idnormalizer

import re

import os

#
# LICENCE
#

# factory


class LicenceFactory(BaseFactory):
    def getCreationPlace(self, factory_args):
        path = '%s/urban/%ss' % (self.site.absolute_url_path(), factory_args['portal_type'].lower())
        return self.site.restrictedTraverse(path)

# mappers


class IdMapper(Mapper):
    def mapId(self, line):
        return normalizeString(self.getData('Cle_Urba'))


class PortalTypeMapper(SubQueryMapper):
    def mapPortal_type(self, line):
        type_value = self.getData('Rec').upper()
        if type_value == 'E':
            # special case for environnement licences to determine if its class
            # 1, 2 or 3
            db_query = "Select * from ENVIRONNEMENT Where Cle_Env = '%s'" % self.getData('Cle_Urba')
            lines = [l for l in self._query(db_query)]
            self.table_name = 'ENVIRONNEMENT'
            type_value = self.getData('Classe', line=lines[0])
            if 'Classe 1' in type_value:
                type_value = 'Classe 1'
            if 'Classe 2' in type_value:
                type_value = 'Classe 2'
            if 'Classe 3' in type_value:
                type_value = 'Classe 3'
            else:
                type_value = 'Autre'
            delattr(self, 'table_name')
        portal_type = self.getValueMapping('type_map')[type_value]['portal_type']
        if not portal_type:
            self.logError(self, line, 'No portal type found for this type value', {'TYPE value': type_value})
            raise NoObjectToCreateException
        return portal_type

    def mapFoldercategory(self, line):
        art127 = self.getData('Art127')
        if bool(int(art127)):
            return 'art127'
        type_value = self.getData('Rec').upper()
        if type_value == 'E':
            # special case for environnement licences to determine if its class
            # 1, 2 or 3
            db_query = "Select * from ENVIRONNEMENT Where Cle_Env = '%s'" % self.getData('Cle_Urba')
            lines = [l for l in self._query(db_query)]
            self.table_name = 'ENVIRONNEMENT'
            type_value = self.getData('Classe', line=lines[0])
            if 'Classe 1' in type_value:
                type_value = 'Classe 1'
            if 'Classe 2' in type_value:
                type_value = 'Classe 2'
            if 'Classe 3' in type_value:
                type_value = 'Classe 3'
            else:
                type_value = 'Autre'
            delattr(self, 'table_name')
        foldercategory = self.getValueMapping('type_map')[type_value]['foldercategory']
        return foldercategory


class EnvLicenceSubjectMapper(SecondaryTableMapper):
    """ """


class WorklocationMapper(Mapper):
    def mapWorklocations(self, line):
        num = self.getData('C_Num')
        noisy_words = set(('d', 'du', 'de', 'des', 'le', 'la', 'les', 'à', ',', 'rues', 'terrain', 'terrains', 'garage', 'magasin', 'entrepôt'))
        raw_street = self.getData('C_Adres')
        if raw_street.endswith(')'):
            raw_street = raw_street[:-5]
        street = cleanAndSplitWord(raw_street)
        street_keywords = [word for word in street if word not in noisy_words and len(word) > 1]
        if len(street_keywords) and street_keywords[-1] == 'or':
            street_keywords = street_keywords[:-1]

        locality = '%s %s' % (self.getData('C_Code'), self.getData('C_Loc'))
        street_keywords.extend(cleanAndSplitWord(locality))
        brains = self.catalog(portal_type='Street', Title=street_keywords)
        if len(brains) == 1:
            return ({'street': brains[0].UID, 'number': num},)
        if street:
            self.logError(self, line, 'Couldnt find street or found too much streets', {
                'address': '%s, %s %s' % (num, raw_street, locality),
                'street': street_keywords,
                'search result': len(brains)
            })
        return {}


class WorkTypeMapper(Mapper):
    def mapWorktype(self, line):
        worktype = self.getData('Code_220+')
        return [worktype]


class InquiryStartDateMapper(Mapper):
    def mapInvestigationstart(self, line):
        date = self.getData('E_Datdeb')
        date = date and DateTime(date) or None
        return date


class InquiryEndDateMapper(Mapper):
    def mapInvestigationend(self, line):
        date = self.getData('E_Datfin')
        date = date and DateTime(date) or None
        return date


class InquiryReclamationNumbersMapper(Mapper):
    def mapInvestigationwritereclamationnumber(self, line):
        reclamation = self.getData('NBRec')
        return reclamation


class InquiryArticlesMapper(PostCreationMapper):
    def mapInvestigationarticles(self, line, plone_object):
        raw_articles = self.getData('Enquete')

        articles = []

        if raw_articles:
            article_regex = '(\d+ ?, ?\d+)°'
            found_articles = re.findall(article_regex, raw_articles)

            if not found_articles:
                self.logError(self, line, 'No investigation article found.', {'articles': raw_articles})

            for art in found_articles:
                article_id = re.sub(' ?, ?', '-', art)
                if not self.article_exists(article_id, licence=plone_object):
                    self.logError(
                        self, line, 'Article %s does not exist in the config',
                        {'article id': article_id, 'articles': raw_articles}
                    )
                else:
                    articles.append(article_id)

        return articles

    def article_exists(self, article_id, licence):
        return article_id in licence.getLicenceConfig().investigationarticles.objectIds()


class AskOpinionTableMapper(SecondaryTableMapper):
    """ """


class AskOpinionsMapper(Mapper):
    def mapSolicitopinionsto(self, line):
        ask_opinions = []
        for i in range(1, 11):
            opinionmakers = self.getData('Org{}'.format(i), line)
            if opinionmakers:
                ask_opinions.append(opinionmakers)
        return ask_opinions


class ObservationsMapper(Mapper):
    def mapDescription(self, line):
        description = '<p>%s</p>' % self.getData('Memo_Urba')
        return description


class TechnicalConditionsMapper(Mapper):
    def mapLocationtechnicalconditions(self, line):
        obs_decision1 = '<p>%s</p>' % self.getData('memo_Autorisation')
        obs_decision2 = '<p>%s</p>' % self.getData('memo_Autorisation2')
        return '%s%s' % (obs_decision1, obs_decision2)


class ReferenceMapper(PostCreationMapper, SubQueryMapper):
    def mapReference(self, line, plone_object):
        type_value = self.getData('Rec').upper()
        if type_value == 'E':
            # special case for environnement licences to determine if its class
            # 1, 2 or 3
            db_query = "Select * from ENVIRONNEMENT Where Cle_Env = '%s'" % self.getData('Cle_Urba')
            lines = [l for l in self._query(db_query)]
            self.table_name = 'ENVIRONNEMENT'
            type_value = self.getData('Classe', line=lines[0])
            if 'Classe 1' in type_value:
                type_value = 'Classe 1'
            if 'Classe 2' in type_value:
                type_value = 'Classe 2'
            if 'Classe 3' in type_value:
                type_value = 'Classe 3'
            else:
                type_value = 'Autre'
            delattr(self, 'table_name')
        ref = self.getValueMapping('type_map')[type_value]['abreviation']
        ref = '%s/%s' % (ref, self.getData('Numero'))
        return ref


class ArchitectMapper(PostCreationMapper):
    def mapArchitects(self, line, plone_object):
        archi_name = self.getData('A_Nom')
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


class ParcellingsMapper(SecondaryTableMapper):
    """ """


class ParcellingUIDMapper(Mapper):

    def mapParcellings(self, line):
        title = self.getData('Lotis')
        parcelling_id = normalizeString(title)
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(id=parcelling_id)
        parcelling_uids = [brain.getObject().UID() for brain in brains]
        return parcelling_uids


class IsInSubdivisionMapper(Mapper):

    def mapIsinsubdivision(self, line):
        title = self.getData('Lotis')
        return bool(title)


class PcaMapper(SecondaryTableMapper):
    """ """


class PcaUIDMapper(Mapper):

    def mapPca(self, line):
        title = self.getData('PPA')
        if title:
            catalog = api.portal.get_tool('portal_catalog')
            if catalog(portal_type='PcaTerm', Title=title):
                pca_id = catalog(portal_type='PcaTerm', Title=title)[0].id
                if pca_id and pca_id[0].id:
                    return pca_id[0].id
        return []


class IsInPcaMapper(Mapper):

    def mapIsinpca(self, line):
        title = self.getData('PPA')
        return bool(title)


class EnvRubricsMapper(Mapper):

    def mapDescription(self, line):
        rubric = self.getData('LibNat')
        return rubric


class CompletionStateMapper(PostCreationMapper):
    def map(self, line, plone_object):
        self.line = line
        state = ''
        if self.getData('Autorisa') or self.getData('TutAutorisa'):
            state = 'accepted'
        elif self.getData('Refus') or self.getData('TutRefus'):
            state = 'refused'
        else:
            return
        workflow_tool = api.portal.get_tool('portal_workflow')
        workflow_def = workflow_tool.getWorkflowsFor(plone_object)[0]
        workflow_id = workflow_def.getId()
        workflow_state = workflow_tool.getStatusOf(workflow_id, plone_object)
        workflow_state['review_state'] = state
        workflow_tool.setStatusOf(workflow_id, plone_object, workflow_state.copy())


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
                    error_trace.append('<p>lotissement : %s %s, autorisé le %s</p>' % (data['approval date'], data['city'], data['auth_date']))
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
        if container.portal_type in ['UrbanCertificateOne', 'UrbanCertificateTwo', 'NotaryLetter']:
            return 'Proprietary'
        return 'Applicant'

# mappers


class ContactIdMapper(Mapper):
    def mapId(self, line):
        name = '%s%s' % (self.getData('D_Nom'), self.getData('D_Prenom'))
        name = name.replace(' ', '').replace('-', '')
        return normalizeString(self.site.portal_urban.generateUniqueId(name))


class ContactTitleMapper(Mapper):
    def mapPersontitle(self, line):
        title1 = self.getData('Civi').lower()
        title = title1 or self.getData('Civi2').lower()
        title_mapping = self.getValueMapping('titre_map')
        return title_mapping.get(title, 'notitle')


class ContactNameMapper(Mapper):
    def mapName1(self, line):
        title = self.getData('Civi2')
        name = self.getData('D_Nom')
        regular_titles = [
            'M.',
            'M et Mlle',
            'M et Mme',
            'M. et Mme',
            'M. l\'Architecte',
            'M. le président',
            'Madame',
            'Madame Vve',
            'Mademoiselle',
            'Maître',
            'Mlle et Monsieur',
            'Mesdames',
            'Mesdemoiselles',
            'Messieurs',
            'Mlle',
            'MM',
            'Mme',
            'Mme et M',
            'Monsieur',
            'Monsieur,',
            'Monsieur et Madame',
            'Monsieur l\'Architecte',
        ]
        if title not in regular_titles:
            name = '%s %s' % (title, name)
        return name


class ContactSreetMapper(Mapper):
    def mapStreet(self, line):
        regex = '((?:[^\d,]+\s*)+),?'
        raw_street = self.getData('D_Adres')
        match = re.match(regex, raw_street)
        if match:
            street = match.group(1)
        else:
            street = raw_street
        return street


class ContactNumberMapper(Mapper):
    def mapNumber(self, line):
        regex = '(?:[^\d,]+\s*)+,?\s*(.*)'
        raw_street = self.getData('D_Adres')
        number = ''

        match = re.match(regex, raw_street)
        if match:
            number = match.group(1)
        return number


class ContactPhoneMapper(Mapper):
    def mapPhone(self, line):
        raw_phone = self.getData('D_Tel')
        gsm = self.getData('D_GSM')
        phone = ''
        if raw_phone:
            phone = raw_phone
        if gsm:
            phone = phone and '%s %s' % (phone, gsm) or gsm
        return phone


class AdditionalContactMapper(MultiLinesSecondaryTableMapper):
    """
    Additional contacts mapper
    """


class AdditionalContactIdMapper(Mapper):
    def mapId(self, line):
        name = '%s%s' % (self.getData('CONom'), self.getData('COPrenom'))
        name = name.replace(' ', '').replace('-', '')
        return normalizeString(self.site.portal_urban.generateUniqueId(name))


class AdditionalContactTitleMapper(Mapper):
    def mapPersontitle(self, line):
        title = self.getData('CiviC').lower()
        title_mapping = self.getValueMapping('titre_map')
        return title_mapping.get(title, 'notitle')

#
# PARCEL
#

#factory


class ParcelFactory(BaseFactory):
    def create(self, parcel, container=None, line=None):
        searchview = self.site.restrictedTraverse('searchparcels')
        #need to trick the search browser view about the args in its request
        parcel_args = parcel.to_dict()
        parcel_args.pop('partie')

        for k, v in parcel_args.iteritems():
            searchview.context.REQUEST[k] = v
        #check if we can find a parcel in the db cadastre with these infos
        found = searchview.search_parcels_custom(**parcel_args)
        if not found:
            found = searchview.search_parcels_custom(old=True, **parcel_args)

        if len(found) == 1 and parcel.has_same_attribute_values(found[0]):
            parcel_args['divisionCode'] = parcel_args['division']
            parcel_args['isOfficialParcel'] = True
        else:
            self.logError(self, line, 'Too much parcels found or not enough parcels found', {'args': parcel_args, 'search result': len(found)})
            parcel_args['isOfficialParcel'] = False

        parcel_args['id'] = parcel.id
        parcel_args['partie'] = parcel.partie

        return super(ParcelFactory, self).create(parcel_args, container=container)

    def objectAlreadyExists(self, parcel, container):
        existing_object = getattr(container, parcel.id, None)
        return existing_object

# mappers


class ParcelDataMapper(SubQueryMapper):
    def map(self, line, **kwargs):

        section = self.getSection(line)
        division = self.getDivision(line)

        remaining_reference = self.getData('Cadastre', line)
        remaining_reference_2 = self.getData('Cadastre_2', line)
        if remaining_reference_2:
            remaining_reference = remaining_reference + ',' + remaining_reference_2
        chars_to_remove = ['.', ',', '?', ';', ':', '#']
        for char in chars_to_remove:
            remaining_reference = remaining_reference.replace(char, '')

        if not remaining_reference:
            return []
        if not division:
            division = ''
        if not section:
            section = ''
        abbreviations = identify_parcel_abbreviations(remaining_reference)
        base_reference = parse_cadastral_reference(division + section + abbreviations[0])

        base_reference = CadastralReference(*base_reference)

        parcels = [base_reference]
        for abbreviation in abbreviations[1:]:
            new_parcel = guess_cadastral_reference(base_reference, abbreviation)
            parcels.append(new_parcel)

        return parcels

    def getSection(self, line):
        return self.getData('Section', line=line).upper()

    def getDivision(self, line):
        key_value = self.getData('Division', line)
        db_query = "Select Num_D from DIVISIONS Where CLEF = '%s'" % key_value
        try:
            division = self._query(db_query).next()[0]
            return division
        except StopIteration:
            return

#
# UrbanEvent deposit
#

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

#mappers


class DepositEventMapper(Mapper):

    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = 'depot-de-la-demande'
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class DepositDate_1_Mapper(Mapper):

    def mapEventdate(self, line):
        date = self.getData('Recepisse')
        if not date:
            raise NoObjectToCreateException
        date = date and DateTime(date) or None
        return date


class DepositEvent_1_IdMapper(Mapper):

    def mapId(self, line):
        return 'deposit-1'


class DepositDate_2_Mapper(Mapper):

    def mapEventdate(self, line):
        date = self.getData('Recepisse2')
        if not date:
            raise NoObjectToCreateException
        date = date and DateTime(date) or None
        return date


class DepositEvent_2_IdMapper(Mapper):

    def mapId(self, line):
        return 'deposit-2'

#
# UrbanEvent incomplete folder
#

#mappers


class IncompleteFolderEventTypeMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = 'dossier-incomplet'
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class IncompleteFolderDateMapper(Mapper):
    def mapEventdate(self, line):
        date = self.getData('P_Datdem')
        date = date and DateTime(date) or None
        if not date:
            raise NoObjectToCreateException
        return date

#
# UrbanEvent complement receipt
#

#mappers


class ComplementReceiptEventTypeMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = 'recepisse-art15-complement'
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class ComplementReceiptDateMapper(Mapper):
    def mapEventdate(self, line):
        date = self.getData('P_Datrec')
        date = date and DateTime(date) or None
        if not date:
            raise NoObjectToCreateException
        return date

#
# UrbanEvent complete folder
#

#mappers


class CompleteFolderEventTypeMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = 'accuse-de-reception'
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class CompleteFolderDateMapper(Mapper):
    def mapEventdate(self, line):
        date = self.getData('Date_Rec')
        date = date and DateTime(date) or None
        if not date:
            raise NoObjectToCreateException
        return date

#
# UrbanEvent primo RW
#

#mappers


class PrimoEventTypeMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = 'transmis-1er-dossier-rw'
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class PrimoDateMapper(Mapper):
    def mapEventdate(self, line):
        date = self.getData('UR_Datenv')
        date = date and DateTime(date) or None
        if not date:
            raise NoObjectToCreateException
        return date

#
# UrbanEvent inquiry
#

#mappers


class InquiryEventTypeMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = 'enquete-publique'
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class InquiryEventIdMapper(Mapper):
    def mapId(self, line):
        return 'inquiry-event'


class InquiryDateMapper(Mapper):
    def mapEventdate(self, line):
        date = self.getData('E_Datdeb')
        if not date:
            raise NoObjectToCreateException
        return date


#
# UrbanEvent inquiry
#

#mappers


class InquiryEventTypeMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = 'enquete-publique'
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class InquiryEventIdMapper(Mapper):
    def mapId(self, line):
        return 'inquiry-event'


class InquiryDateMapper(Mapper):
    def mapEventdate(self, line):
        date = self.getData('E_Datdeb')
        if not date:
            raise NoObjectToCreateException
        return date

#
# UrbanEvent ask opinions
#

# factory


class OpinionMakersFactory(BaseFactory):
    """ """

#mappers


class OpinionMakersTableMapper(SecondaryTableMapper):
    """ """
    def map(self, line, **kwargs):
        lines = self.query_secondary_table(line)
        for secondary_line in lines:
            for mapper in self.mappers:
                return mapper.map(secondary_line, **kwargs)
            break
        return []


class OpinionMakersMapper(Mapper):

    def map(self, line):
        opinionmakers_args = []
        for i in range(1, 11):
            opinionmakers_id = self.getData('Org{}'.format(i), line)
            if not opinionmakers_id:
                return opinionmakers_args
            event_date = self.getData('Cont{}'.format(i), line)
            receipt_date = self.getData('Rec{}'.format(i), line)
            args = {
                'id': opinionmakers_id,
                'eventtype': opinionmakers_id,
                'eventDate': event_date and DateTime(event_date) or None,
                'transmitDate': event_date and DateTime(event_date) or None,
                'receiptDate': receipt_date and DateTime(receipt_date) or None,
                'receivedDocumentReference': self.getData('Ref{}'.format(i), line),
            }
            opinionmakers_args.append(args)
        if not opinionmakers_args:
            raise NoObjectToCreateException
        return opinionmakers_args


class LinkedInquiryMapper(PostCreationMapper):

    def map(self, line, plone_object):
        opinion_event = plone_object
        licence = opinion_event.aq_inner.aq_parent
        inquiry = licence.getInquiries() and licence.getInquiries()[-1] or licence
        opinion_event.setLinkedInquiry(inquiry)


#
# Claimant
#

# factory


class ClaimantFactory(BaseFactory):
    def getPortalType(self, container, **kwargs):
        return 'Claimant'

#mappers


class ClaimantsMapper(MultiLinesSecondaryTableMapper):
    """ """


class ClaimantIdMapper(Mapper):
    def mapId(self, line):
        name = '%s%s' % (self.getData('RECNom'), self.getData('RECPrenom'))
        name = name.replace(' ', '').replace('-', '')
        if not name:
            raise NoObjectToCreateException
        return normalizeString(self.site.portal_urban.generateUniqueId(name))


class ClaimantTitleMapper(Mapper):
    def mapPersontitle(self, line):
        title = self.getData('Civi_Rec').lower()
        title_mapping = self.getValueMapping('titre_map')
        return title_mapping.get(title, 'notitle')


class ClaimantSreetMapper(Mapper):
    def mapStreet(self, line):
        regex = '((?:[^\d,]+\s*)+),?'
        raw_street = self.getData('RECAdres')
        match = re.match(regex, raw_street)
        if match:
            street = match.group(1)
        else:
            street = raw_street
        return street


class ClaimantNumberMapper(Mapper):
    def mapNumber(self, line):
        regex = '(?:[^\d,]+\s*)+,?\s*(.*)'
        raw_street = self.getData('RECAdres')
        number = ''

        match = re.match(regex, raw_street)
        if match:
            number = match.group(1)
        return number

#
# UrbanEvent second RW
#

#mappers


class SecondRWEventTypeMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = 'transmis-2eme-dossier-rw'
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class SecondRWEventDateMapper(Mapper):
    def mapEventdate(self, line):
        date = self.getData('UR_Datenv2')
        date = date and DateTime(date) or None
        if not date:
            raise NoObjectToCreateException
        return date


class SecondRWDecisionMapper(Mapper):
    def mapExternaldecision(self, line):
        raw_decision = self.getData('UR_Avis')
        decision = self.getValueMapping('externaldecisions_map').get(raw_decision, [])
        return decision


class SecondRWDecisionDateMapper(Mapper):
    def mapDecisiondate(self, line):
        date = self.getData('UR_Datpre')
        date = date and DateTime(date) or None
        return date


class SecondRWReceiptDateMapper(Mapper):
    def mapReceiptdate(self, line):
        date = self.getData('UR_Datret')
        date = date and DateTime(date) or None
        return date

#
# UrbanEvent decision
#

#mappers


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
    def mapDecisiondate(self, line):
        autorisa = self.getData('Autorisa')
        refus = self.getData('Refus')
        tutAutorisa = self.getData('TutAutorisa')
        tutRefus = self.getData('TutRefus')
        date = autorisa or refus or tutAutorisa or tutRefus
        if not date:
            self.logError(self, line, 'No decision date found')
            raise NoObjectToCreateException
        return date


class DecisionEventDecisionMapper(Mapper):
    def mapDecision(self, line):
        autorisa = self.getData('Autorisa')
        refus = self.getData('Refus')
        tutAutorisa = self.getData('TutAutorisa')
        tutRefus = self.getData('TutRefus')
        if autorisa or tutAutorisa:
            return 'favorable'
        elif refus or tutRefus:
            return 'defavorable'
        #error
        raise NoObjectToCreateException


class DecisionEventTitleMapper(Mapper):
    def mapTitle(self, line):
        tutAutorisa = self.getData('TutAutorisa')
        tutRefus = self.getData('TutRefus')

        if tutAutorisa or tutRefus:
            return u'Délivrance du permis par la tutelle (octroi ou refus)'

        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = self.getValueMapping('eventtype_id_map')[licence.portal_type]['decision_event']
        config = urban_tool.getUrbanConfig(licence)
        event_type = getattr(config.urbaneventtypes, eventtype_id)
        return event_type.Title()


class DecisionEventNotificationDateMapper(Mapper):
    def mapEventdate(self, line):
        eventDate = self.getData('Notifica')
        # if no Notifica/eventDate, get decisionDate otherwise no created decision event
        if not eventDate:
            autorisa = self.getData('Autorisa')
            refus = self.getData('Refus')
            tutAutorisa = self.getData('TutAutorisa')
            tutRefus = self.getData('TutRefus')
            eventDate = autorisa or refus or tutAutorisa or tutRefus

        return eventDate

#
# UrbanEvent implantation
#

#mappers


class ImplantationEventTypeMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        eventtype_id = 'indication-implantation'
        if not eventtype_id:
            return

        urban_tool = api.portal.get_tool('portal_urban')
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class ImplantationEventIdMapper(Mapper):
    def mapId(self, line):
        return 'implantation-event'


class ImplantationEventControlDateMapper(Mapper):
    def mapEventdate(self, line):
        date = self.getData('Visite_DateDemande')
        if not date:
            raise NoObjectToCreateException
        return date


class ImplantationEventDecisionDateMapper(Mapper):
    def mapDecisiondate(self, line):
        eventDate = self.getData('Visite_DateCollege')
        return eventDate


class ImplantationEventDecisionMapper(Mapper):
    def mapDecisiontext(self, line):
        return self.getData('Visite_Resultat')

#
# UrbanEvent suspension
#


# factory
class SuspensionEventFactory(UrbanEventFactory):

    def create(self, kwargs, container, line):
        if not kwargs['eventtype']:
            return []
        eventtype_uid = kwargs.pop('eventtype')
        suspension_reason = kwargs.pop('suspensionReason')
        urban_event = container.createUrbanEvent(eventtype_uid, **kwargs)
        urban_event.setSuspensionReason(suspension_reason)
        return urban_event

#mappers


class SuspensionsMapper(MultiLinesSecondaryTableMapper):
    """ """


class SuspensionEventTypeMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        eventtype_id = 'suspension-du-permis'
        if not eventtype_id:
            return

        urban_tool = api.portal.get_tool('portal_urban')
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class SuspensionEventIdMapper(Mapper):
    def mapId(self, line):
        return self.site.portal_urban.generateUniqueId('suspension')


class SuspensionEventReasonMapper(Mapper):
    def mapSuspensionreason(self, line):
        reason = '<p>{}</p>'.format(self.getData('Motif'))
        return reason

#
# Documents
#

# factory


class DocumentsFactory(BaseFactory):
    """ """
    def getPortalType(self, container, **kwargs):
        return 'File'

#mappers


class DocumentsMapper(MultiLinesSecondaryTableMapper):
    """ """


class DocumentIdMapper(Mapper):
    def mapId(self, line):
        document_path = self.getData('Fichier')
        doc_id = document_path.split('\\')[-1]
        doc_id = idnormalizer.normalize(doc_id)
        return doc_id


class DocumentFileMapper(Mapper):
    def mapFile(self, line):
        document_path = self.getData('Fichier')
        document_path = '{base}/documents/{rel_path}'.format(
            base=IMPORT_FOLDER_PATH,
            rel_path=document_path[12:].replace('\\', '/')
        )
        try:
            doc = open(document_path, 'rb')
        except:
            print "COULD NOT FIND DOCUMENT {}".format(document_path)
            raise NoObjectToCreateException
        doc_content = doc.read()
        doc.close()
        return doc_content


class DocumentsMapper2(Mapper):
    def map(self, line):
        licence = self.importer.current_containers_stack[-1]
        path_mapping = self.getValueMapping('documents_map')
        documents_path = '{base}/documents/{folder}/DOSSIERS/{id}/'.format(
            base=IMPORT_FOLDER_PATH,
            folder=path_mapping.get(licence.portal_type),
            id=licence.id[1:]
        )

        documents_args = []
        try:
            doc_names = os.listdir(documents_path)
        except:
            return documents_args

        for doc_name in doc_names:
            doc = open(documents_path + doc_name, 'rb')
            doc_content = doc.read()
            doc.close()

            doc_args = {
                'portal_type': 'File',
                'id': normalizeString(safe_unicode(doc_name)),
                'title': doc_name,
                'file': doc_content,
            }
            documents_args.append(doc_args)
        return documents_args
