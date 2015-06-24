# -*- coding: utf-8 -*-

from imio.urban.dataimport.MySQL.mapper import MultiLinesSecondaryTableMapper
from imio.urban.dataimport.MySQL.mapper import MySQLMapper as Mapper
from imio.urban.dataimport.MySQL.mapper import MySQLPostCreationMapper as PostCreationMapper
from imio.urban.dataimport.MySQL.mapper import MySQLFinalMapper as FinalMapper
from imio.urban.dataimport.MySQL.mapper import SecondaryTableMapper

from imio.urban.dataimport.exceptions import NoObjectToCreateException

from imio.urban.dataimport.factory import BaseFactory
from imio.urban.dataimport.utils import CadastralReference
from imio.urban.dataimport.utils import cleanAndSplitWord
from imio.urban.dataimport.utils import parse_cadastral_reference

from DateTime import DateTime
from Products.CMFPlone.utils import normalizeString

from plone import api

import re

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
    def mapPortal_type(self, line):
        type_value = self.getData('DOSSIER_TDOSSIERID')
        portal_type = self.getValueMapping('type_map')[type_value]['portal_type']
        if not portal_type:
            self.logError(self, line, 'No portal type found for this type value', {'TYPE value': type_value})
        if portal_type == 'UrbanCertificateOne' and self.getData('DOSSIER_TYPEIDENT') == 'CU2':
            portal_type = 'UrbanCertificateTwo'
        return portal_type

    def mapFoldercategory(self, line):
        type_value = self.getData('DOSSIER_TDOSSIERID')
        foldercategory = self.getValueMapping('type_map')[type_value]['foldercategory']
        return foldercategory


class LicenceSubjectMapper(SecondaryTableMapper):
    """ """


class WorklocationMapper(SecondaryTableMapper):
    """ """


class StreetAndNumberMapper(Mapper):
    def mapWorklocations(self, line):
        raw_street = self.getData('SITUATION_DES') or u''
        parsed_street = re.search('(.*?)(\d+.*)?\( (?:(?:426\d)|(?:0 BRAIVES))', raw_street)
        if parsed_street:
            street, num = parsed_street.groups()
            street_keywords = cleanAndSplitWord(street)
            brains = self.catalog(portal_type='Street', Title=street_keywords)
            if len(brains) == 1:
                return ({'street': brains[0].UID, 'number': num or ''},)
            if street:
                self.logError(self, line, 'Couldnt find street or found too much streets', {
                    'address': '%s' % raw_street,
                    'street': street_keywords,
                    'search result': len(brains)
                })
        else:
            self.logError(self, line, 'Couldnt parse street and number', {
                'address': '%s' % raw_street,
            })
        return []


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


class CompletionStateMapper(PostCreationMapper):
    def map(self, line, plone_object):
        state = self.getData('DOSSIER_OCTROI', line)
        transition = self.getValueMapping('state_map')[state]
        if transition:
            api.content.transition(plone_object, transition)


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


class ApplicantMapper(SecondaryTableMapper):

    def __init__(self, mysql_importer, args):
        super(ApplicantMapper, self).__init__(mysql_importer, args)
        cpsn = self.importer.datasource.get_table('cpsn')
        k2 = self.importer.datasource.get_table('k2')
        self.query = self.query.join(
            k2, cpsn.columns['CPSN_ID'] == k2.columns['K_ID1']
        )

    def query_secondary_table(self, line):
        licence_id = self.getData('WRKDOSSIER_ID', line)
        applicant_type = -204

        lines = self.query.filter_by(K_ID2=licence_id, K2KND_ID=applicant_type).all()

        return lines


class ContactIdMapper(Mapper):
    def mapId(self, line):
        name = '%s%s' % (self.getData('CPSN_NOM'), self.getData('CPSN_PRENOM'))
        name = name.replace(' ', '').replace('-', '')
        return normalizeString(self.site.portal_urban.generateUniqueId(name))


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

#
# PARCEL
#

#factory


class ParcelFactory(BaseFactory):
    def create(self, parcel, container=None, line=None):
        searchview = self.site.restrictedTraverse('searchparcels')

        if parcel is None:
            return None

        #need to trick the search browser view about the args in its request
        parcel_args = parcel.to_dict()
        parcel_args.pop('partie')

        for k, v in parcel_args.iteritems():
            searchview.context.REQUEST[k] = v
        #check if we can find a parcel in the db cadastre with these infos
        found = searchview.findParcel(**parcel_args)
        if not found:
            found = searchview.findParcel(browseoldparcels=True, **parcel_args)

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
        if not parcel:
            return
        existing_object = getattr(container, parcel.id, None)
        return existing_object

# mappers


class ParcelsMapper(MultiLinesSecondaryTableMapper):
    """ """


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
        event_type = -207

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

#mappers


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

#mappers


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
    def mapEventdate(self, line):
        date = self.getData('DOSSIER_DATEDELIV')
        if not date:
            self.logError(self, line, 'No decision date found')
        return str(date)

#
# UrbanEvent send licence to applicant
#

#mappers


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

#mappers


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
