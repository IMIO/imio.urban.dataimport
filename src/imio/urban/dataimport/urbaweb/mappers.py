# -*- coding: utf-8 -*-

from imio.urban.dataimport.access.mapper import AccessMapper as Mapper
from imio.urban.dataimport.access.mapper import AccessPostCreationMapper as PostCreationMapper
from imio.urban.dataimport.access.mapper import AccessFinalMapper as FinalMapper

from imio.urban.dataimport.factory import BaseFactory, MultiObjectsFactory
from imio.urban.dataimport.utils import cleanAndSplitWord
from DateTime import DateTime
from Products.CMFPlone.utils import normalizeString
from Products.CMFCore.utils import getToolByName
import re

#
# LICENCE
#

# factory


class LicenceFactory(BaseFactory):
    def getCreationPlace(self, **kwargs):
        path = '%s/urban/%ss' % (self.site.absolute_url_path(), kwargs['portal_type'].lower())
        return self.site.restrictedTraverse(path)

# mappers


class IdMapper(Mapper):
    def mapId(self, line):
        return normalizeString(self.getData('Cle_Urba'))


class PortalTypeMapper(Mapper):
    def mapPortal_type(self, line):
        type_value = self.getData('TypeNat')
        portal_type = self.getValueMapping('type_map')[type_value]['portal_type']
        if not portal_type:
            self.logError(self, line, 'No portal type found for this type value', {'TYPE value': type_value})
        return portal_type

    def mapFoldercategory(self, line):
        type_value = self.getData('TypeNat')
        foldercategory = self.getValueMapping('type_map')[type_value]['foldercategory']
        return foldercategory


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


class ObservationsMapper(Mapper):
    def mapDescription(self, line):
        obs_urban = '<p>%s</p>' % self.getData('Memo_Urba')
        obs_decision1 = '<p>%s</p>' % self.getData('memo_Autorisation')
        obs_decision2 = '<p>%s</p>' % self.getData('memo_Autorisation2')
        return '%s%s%s' % (obs_urban, obs_decision1, obs_decision2)


class ReferenceMapper(PostCreationMapper):
    def mapReference(self, line, plone_object):
        ref = plone_object.getLicenceTypeAcronym()
        ref = '%s/%s' % (ref, self.getData('Numero'))
        return ref


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
        return
        self.line = line
        state = ''
        if bool(int(self.getData('DossierIncomplet'))):
            state = 'incomplete'
        elif self.getData('Refus') == 'O':
            state = 'accepted'
        elif self.getData('Refus') == 'N':
            state = 'refused'
        elif plone_object.portal_type in ['MiscDemand']:
            state = 'accepted'
        else:
            return
        workflow_tool = getToolByName(plone_object, 'portal_workflow')
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
        error_trace = ''.join(error_trace)

        return '%s%s' % (error_trace, description)

#
# CONTACT
#

# factory


class ContactFactory(BaseFactory):
    def getPortalType(self, place, **kwargs):
        if place.portal_type in ['UrbanCertificateOne', 'UrbanCertificateTwo', 'NotaryLetter']:
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
        title = self.getData('Civi2').lower()
        if title1:
            title = title1
        title_mapping = self.getValueMapping('titre_map')
        if title in title_mapping.keys():
            return title_mapping[title]
        return 'notitle'


class ContactNameMapper(Mapper):
    def mapName1(self, line):
        title = self.getData('Civi2')
        name = self.getData('D_Nom')
        if '.' in title:
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

#
# PARCEL
#

#factory


class ParcelFactory(MultiObjectsFactory):
    def create(self, place=None, line=None, **kwargs):
        parcels = {}
        searchview = self.site.restrictedTraverse('searchparcels')
        for index, args in kwargs.iteritems():
            #need to trick the search browser view about the args in its request
            for k, v in args.iteritems():
                searchview.context.REQUEST[k] = v
            #check if we can find a parcel in the db cadastre with these infos
            found = searchview.findParcel(**args)
            if not found:
                found = searchview.findParcel(browseoldparcels=True, **args)
            if len(found) == 1:
                args['divisionCode'] = args['division']
                args['division'] = args['division']
                parcels[index] = args
            else:
                parcels[index] = args
                self.logError(self, line, 'Too much parcels found or not enough parcels found', {'args': args, 'search result': len(found)})
        return super(ParcelFactory, self).create(place=place, **parcels)

# mappers


class ParcelDataMapper(Mapper):
    def map(self, line, **kwargs):
        parcel_args = []

        section = self.getSection(line)
        division = self.getDivision(line)
        import ipdb; ipdb.set_trace()

        return parcel_args

    def getSection(self, line):
        return self.getData('Section', line=line).upper()

    def getDivision(self, line):
        divisions = {
            '1': '63020',
            '2': '63002',
        }
        raw_div = self.getData('Division', line=line)
        return divisions[raw_div]


#
# UrbanEvent deposit
#

# factory
class UrbanEventFactory(BaseFactory):
    def getPortalType(self, **kwargs):
        return 'UrbanEvent'

    def create(self, place, **kwargs):
        if not kwargs['eventtype']:
            return []
        urban_tool = getToolByName(place, 'portal_urban')
        edit_url = urban_tool.createUrbanEvent(place.UID(), kwargs['eventtype'])
        return [getattr(place, edit_url.split('/')[-2])]

#mappers


class DepositEventTypeMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = getToolByName(licence, 'portal_urban')
        eventtype_id = self.getValueMapping('eventtype_id_map')[licence.portal_type]['deposit_event']
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class DepositDateMapper(PostCreationMapper):
    def mapEventdate(self, line, plone_object):
        date = self.getData('DateRecDem')
        date = date and DateTime(date) or None
        if not date:
            self.logError(self, line, 'No deposit date found')
        return date

#
# UrbanEvent complete folder
#

#mappers


class CompleteFolderEventTypeMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = getToolByName(licence, 'portal_urban')
        eventtype_id = self.getValueMapping('eventtype_id_map')[licence.portal_type]['folder_complete']
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class CompleteFolderDateMapper(PostCreationMapper):
    def mapEventdate(self, line, plone_object):
        date = self.getData('AvisDossierComplet')
        date = date and DateTime(date) or None
        if not date:
            self.logError(self, line, "No 'folder complete' date found")
        return date

#
# UrbanEvent decision
#

#mappers


class DecisionEventTypeMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = getToolByName(licence, 'portal_urban')
        eventtype_id = self.getValueMapping('eventtype_id_map')[licence.portal_type]['decision_event']
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class DecisionDateMapper(PostCreationMapper):
    def mapDecisiondate(self, line, plone_object):
        date = self.getData('DateDecisionCollege')
        date = date and DateTime(date) or None
        if not date:
            self.logError(self, line, 'No decision date found')
        return date


class NotificationDateMapper(PostCreationMapper):
    def mapEventdate(self, line, plone_object):
        date = self.getData('DateNotif')
        date = date and DateTime(date) or None
        if not date:
            self.logError(self, line, 'No notification date found')
        return date


class DecisionMapper(PostCreationMapper):
    def mapDecision(self, line, plone_object):
        decision = self.getData('Refus')
        if decision == 'O':
            return 'favorable'
        elif decision == 'N':
            return 'defavorable'
        #error
        return []
