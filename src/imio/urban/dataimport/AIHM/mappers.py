# -*- coding: utf-8 -*-

from imio.urban.dataimport.access.mapper import AccessMapper as Mapper
from imio.urban.dataimport.access.mapper import MultiLinesSecondaryTableMapper
from imio.urban.dataimport.access.mapper import AccessPostCreationMapper as PostCreationMapper
from imio.urban.dataimport.access.mapper import AccessFinalMapper as FinalMapper

from imio.urban.dataimport.factory import BaseFactory
from imio.urban.dataimport.utils import cleanAndSplitWord, normalizeDate
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
        path = '%s/urban/%ss' % (self.site.absolute_url_path(), factory_args['portal_type'].lower())
        return self.site.restrictedTraverse(path)

# mappers


class IdMapper(Mapper):
    def mapId(self, line):
        return normalizeString(self.getData('CLEF')).strip('_')


class PortalTypeMapper(Mapper):
    def mapPortal_type(self, line):
        type_value = self.getData('TYPE')
        portal_type = self.getValueMapping('type_map')[type_value]['portal_type']
        if not portal_type:
            self.logError(self, line, 'No portal type found for this type value', {'TYPE value': type_value})
        return portal_type

    def mapFoldercategory(self, line):
        type_value = self.getData('TYPE')
        foldercategory = self.getValueMapping('type_map')[type_value]['foldercategory']
        return foldercategory


class WorklocationMapper(Mapper):
    def mapWorklocations(self, line):
        num = self.getData('NumPolParcelle')
        noisy_words = set(('d', 'du', 'de', 'des', 'le', 'la', 'les', 'à', ',', 'rues', 'terrain', 'terrains', 'garage', 'magasin', 'entrepôt'))
        raw_street = self.getData('AdresseDuBien')
        street = cleanAndSplitWord(raw_street)
        street_keywords = [word for word in street if word not in noisy_words and len(word) > 1]
        if len(street_keywords) and street_keywords[-1] == 'or':
            street_keywords = street_keywords[:-1]
        locality = self.getData('AncCommune')
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


class PcaMapper(Mapper):
    def mapIsinpca(self, line):
        return bool(self.getData('DatePPA'))

    def mapPca(self, line):
        if not self.mapIsinpca(line):
            return []
        pca_date = normalizeDate(self.getData('DatePPA'))
        pcas = self.catalog(Title=pca_date)
        if len(pcas) != 1:
            self.logError(self, line, 'Couldnt find pca or found too much pca', {'date': pca_date})
            return []
        return pcas[0].id


class ParcellingsMapper(Mapper):
    def mapIsinsubdivision(self, line):
        return any([self.getData('NumLot'), self.getData('DateLot'), self.getData('DateLotUrbanisme')])

    def mapParcellings(self, line):
        if not self.mapIsinsubdivision(line):
            return []
        auth_date = normalizeDate(self.getData('DateLot'))
        approval_date = normalizeDate(self.getData('DateLotUrbanisme'))
        raw_city = self.getData('AncCommune')
        city = raw_city.split('-')
        keywords = [approval_date] + city
        if raw_city or approval_date:
            parcellings = self.catalog(Title=keywords)
            if len(parcellings) == 1:
                return parcellings[0].getObject().UID()
            keywords = [auth_date] + city
            parcellings = self.catalog(Title=keywords)
            if len(parcellings) == 1:
                return parcellings[0].getObject().UID()
            self.logError(self, line, 'Couldnt find parcelling or found too much parcelling', {'approval date': approval_date, 'auth_date': auth_date, 'city': raw_city})
        return []


class ParcellingRemarksMapper(Mapper):
    def mapLocationtechnicalremarks(self, line):
        return '<p>%s</p>' % self.getData('PPAObservations')


class ObservationsMapper(Mapper):
    def mapDescription(self, line):
        return '<p>%s</p>' % self.getData('Observations')


class ReferenceMapper(PostCreationMapper):
    def mapReference(self, line, plone_object):
        ref = self.getData('CLEF')
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


class NotaryMapper(PostCreationMapper):
    def mapNotarycontact(self, line, plone_object):
        title = self.getData('Titre').lower()
        titre_mapping = self.getValueMapping('titre_map')
        if title not in titre_mapping or titre_mapping[title] not in ['master', 'masters']:
            return
        name = self.getData('Nom')
        firstname = self.getData('Prenom')
        notary = self.catalog(portal_type='Notary', Title=[name, firstname])
        if not notary:
            notary = self.catalog(portal_type='Notary', Title=name)
        if len(notary) == 1:
            return notary[0].getObject()
        self.logError(self, line, 'no notaries found or too much notaries found',
                      {'title': self.getData('Titre'), 'name': name, 'firstname': firstname, 'search_result': len(notary)})
        return []


class CompletionStateMapper(PostCreationMapper):
    def map(self, line, plone_object):
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
        error_trace = ''.join(error_trace)

        return '%s%s' % (error_trace, description)

#
# CONTACT
#

# factory


class ContactFactory(BaseFactory):
    def create(self, kwargs, container, line=None):
        if self.getPortalType(container) == 'Applicant' or kwargs['personTitle'] not in ['master', 'masters']:
            return super(ContactFactory, self).create(kwargs, container)
        else:
            #notaries are bound  with a reference
            return None

    def getPortalType(self, place, **kwargs):
        if place.portal_type in ['UrbanCertificateOne', 'UrbanCertificateTwo', 'NotaryLetter']:
            return 'Proprietary'
        return 'Applicant'

# mappers


class ContactIdMapper(Mapper):
    def mapId(self, line):
        m = self.getData('MandantNom') and 'Mandant' or ''
        name = '%s%s' % (self.getData('%sNom' % m), self.getData('%sPrenom' % m))
        name = name.replace(' ', '').replace('-', '')
        return normalizeString(self.site.portal_urban.generateUniqueId(name))


class ContactTitleMapper(Mapper):
    def mapPersontitle(self, line):
        m = self.getData('MandantNom') and 'Mandant' or ''
        titre = self.getData('%sTitre' % m).lower()
        titre_mapping = self.getValueMapping('titre_map')
        if titre in titre_mapping.keys():
            return titre_mapping[titre]
        return 'notitle'


class ContactNameMapper(Mapper):
    def mapName1(self, line):
        m = self.getData('MandantNom') and 'Mandant' or ''
        return self.getData('%sNom' % m)


class ContactFirstnameMapper(Mapper):
    def mapName2(self, line):
        m = self.getData('MandantNom') and 'Mandant' or ''
        return self.getData('%sPrenom' % m)


class ContactSreetMapper(Mapper):
    def mapStreet(self, line):
        m = self.getData('MandantNom') and 'Mandant' or ''
        return self.getData('%sAdresse' % m)


class ContactNumberMapper(Mapper):
    def mapNumber(self, line):
        m = self.getData('MandantNom') and 'Mandant' or ''
        number = self.getData('%sNumPolice' % m)
        box = self.getData('%sBtePost' % m)
        return "%s%s" % (number, box and '/%s' % box or '')


class ContactZipcodeMapper(Mapper):
    def mapZipcode(self, line):
        m = self.getData('MandantNom') and 'Mandant' or ''
        return self.getData('%sCP' % m)


class ContactCityMapper(Mapper):
    def mapCity(self, line):
        m = self.getData('MandantNom') and 'Mandant' or ''
        return self.getData('%sLocalite' % m)


class ContactCountryMapper(Mapper):
    def mapCountry(self, line):
        m = self.getData('MandantNom') and 'Mandant' or ''
        try:
            return self.getValueMapping('country_map')[self.getData('%sPays' % m).lower()]
        except:
            self.logError(self, line, 'Unknown country', {'country': self.getData('Pays')})


class ContactPhoneMapper(Mapper):
    def mapPhone(self, line):
        m = self.getData('MandantNom') and 'Mandant' or ''
        return self.getData('%sTelephone' % m)


class ContactRepresentedByMapper(Mapper):
    def mapRepresentedby(self, line):
        container = self.importer.current_containers_stack[-1]
        if not self.getData('MandantNom'):
            return ''
        if container.portal_type == 'BuildLicence':
            return container.getArchitects() and container.getArchitects()[0].UID() or ''
        elif container.portal_type in ['UrbanCertificateOne', 'UrbanCertificateTwo']:
            return container.getNotaryContact() and container.getNotaryContact()[0].UID() or ''
        return ''

#
# PARCEL
#

#factory


class ParcelFactory(BaseFactory):
    def create(self, kwargs, container, line=None):
        searchview = self.site.restrictedTraverse('searchparcels')
        # need to trick the search browser view about the args in its request
        for k, v in kwargs.iteritems():
            searchview.context.REQUEST[k] = v
        # check if we can find a parcel in the db cadastre with these infos
        found = searchview.findParcel(**kwargs)
        if not found:
            found = searchview.findParcel(browseoldparcels=True, **kwargs)
        if len(found) == 1:
            kwargs['divisionCode'] = kwargs['division']
            kwargs['division'] = kwargs['division']
        else:
            self.logError(self, line, 'Too much parcels found or not enough parcels found', {'kwargs': kwargs, 'search result': len(found)})
        kwargs['id'] = ''.join([''.join(cleanAndSplitWord(ref)) for ref in kwargs.values()])
        kwargs['id'] = kwargs['id'].replace('/', '')
        if kwargs['id'] in container.objectIds():
            return None
        return super(ParcelFactory, self).create(kwargs, container=container)

# mappers


class ParcelDataMapper(MultiLinesSecondaryTableMapper):
    pass


class RadicalMapper(Mapper):
    def mapRadical(self, line):
        radical = self.getData('RADICAL')
        if not radical:
            return radical
        return str(int(float(radical)))


class ExposantMapper(Mapper):
    def mapExposant(self, line):
        raw_val = self.getData('EXPOSANT')
        result = re.search('[a-z]', raw_val, re.I)
        exposant = result and result.group().capitalize() or ''
        return exposant

    def mapPuissance(self, line):
        raw_val = self.getData('EXPOSANT')
        result = re.search('\d+', raw_val)
        puissance = result and result.group() or ''
        return puissance


class BisMapper(Mapper):
    def mapBis(self, line):
        bis = self.getData('BIS')
        if not bis:
            return bis
        return str(int(float(bis)))


#
# UrbanEvent deposit
#

# factory
class UrbanEventFactory(BaseFactory):
    def getPortalType(self, **kwargs):
        return 'UrbanEvent'

    def create(self, kwargs, container, line=None):
        if not kwargs['eventtype']:
            return []
        event = container.createUrbanEvent(kwargs['eventtype'])
        return event

#mappers


class DepositEventTypeMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
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
        urban_tool = api.portal.get_tool('portal_urban')
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
        urban_tool = api.portal.get_tool('portal_urban')
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
