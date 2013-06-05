# -*- coding: utf-8 -*-

from zope.interface import Interface, Attribute


class IUrbanDataImporter(Interface):
    """  """

    site = Attribute('Site portal')
    datasource = Attribute('data source object, see IUrbanImportSource for more details')
    values_mappings = Attribute('Nested dicts giving mapping between static values (eg: BE -> Belgium)')

    def importData(self):
        """ run the data import, mainly loop over data fragments and call importDataLine """

    def importDataLine(self, dataline):
        """ intermediate method which call every other method needed to process one data line """

    def createPloneObject(self):
        """ receive a data fragment and create its coresponding(s) object(s) """

    def setupImport(self):
        """ should parse the mapping and instanciate mappers and factories """

    def setupFactory(self, object_name, mapping):
        """ instanciate factories """

    def setupObjectMappers(self, object_name, mapping):
        """ instanciate fields mappers for one specific content type """

    def setupAllowedContainer(self, object_name, mapping):
        """ list allowed containers for each object """

    def getFactoryArgument(self):
        """ extract all the values from a data fragment that will be used as factory arguments """

    def getAfterCreationValues(self):
        """ extract all the values that will be set on the object after its creation """

    def logError(self):
        """ log an error occuring during the import """

    def log(self):
        """ log anything you want to trace during the import """


class IUrbanImportSource(Interface):
    """ object wrapper for raw source data """

    rawsource = Attribute('raw import source data')

    def iterdata(self):
        """
         Return an iterator over the source data.
         Each iterated item should represent an object or logical group of objects to import.
        """


class IObjectsMapping(Interface):
    """ Object representing an import mapping between data source and destinations objects """

    def getObjectsNesting(self):
        """ return nested lists representing how destination objects contain each others """

    def getFieldsMapping(self):
        """ return nested dicts giving objects class factory and their fields mapping """


class IValuesMapping(Interface):
    """ Object representing a mapping between static values (eg: BE -- map to --> Belgium) """


class IPostCreationMapper(Interface):
    """ marker interface for post creation mapper """


class IAihmDataImporter(Interface):
    """ marker interface for AIHM migrator """
