# -*- coding: utf-8 -*-

from imio.urban.dataimport.errormessage import ImportErrorMessage
from imio.urban.dataimport.importer import UrbanDataImporter
from imio.urban.dataimport.importsource import DataExtractor
from imio.urban.dataimport.importsource import UrbanImportSource
from imio.urban.dataimport.MySQL.interfaces import IMySQLImporter
from imio.urban.dataimport.MySQL.interfaces import IMySQLImportSource

from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy.orm import sessionmaker

from zope.interface import implements


class MySQLImportSource(UrbanImportSource):

    implements(IMySQLImportSource)

    def __init__(self, importer):
        super(MySQLImportSource, self).__init__(importer)

        session, metadata = self.init_session_and_metadata()

        self.metadata = metadata
        self.session = session
        self.main_table = self.get_table(self.importer.table_name)

    def iterdata(self):

        result = self.session.query(self.main_table)
        records = result.all()

        return records

    def init_session_and_metadata(self):
        importer = self.importer

        engine = create_engine(
            'mysql://{username}:{password}@{host}/{db_name}'.format(
                username=importer.username,
                password=importer.password,
                host=importer.host,
                db_name=importer.db_name,
            ),
            echo=True
        )

        metadata = MetaData(engine)
        Session = sessionmaker(bind=engine)

        return Session(), metadata

    def get_table(self, table_name):
        table = Table(table_name, self.metadata, autoload=True)
        return table


class MySQLDataExtractor(DataExtractor):

    def extractData(self, valuename, line):
        return getattr(line, valuename)


class MySQLErrorMessage(ImportErrorMessage):

    def __str__(self):
        key_column = getattr(self.error_location, 'key_column', self.importer.key_column)
        key = self.importer.getData(key_column, self.line)
        migration_step = self.error_location.__class__.__name__
        factory_stack = self.importer.current_containers_stack
        stack_display = '\n'.join(
            ['%sid: %s Title: %s' % (''.join(['    ' for i in range(factory_stack.index(obj))]), obj.id, obj.Title()) for obj in factory_stack]
        )

        message = [
            'line %s (key %s)' % (self.importer.current_line, key),
            'migration substep: %s' % migration_step,
            'error message: %s' % self.message,
            'data: %s' % self.data,
            'plone containers stack:\n  %s' % stack_display,
        ]
        message = '\n'.join(message)

        return message


class MySQLDataImporter(UrbanDataImporter):
    """
    expect:
        db_name: the mysql db filename to query
        table_name: the main table in the data base (the one that will be used as 'central node' to recover licences)
    """

    implements(IMySQLImporter)

    def __init__(self, db_name, table_name, key_column, **kwargs):
        super(MySQLDataImporter, self).__init__(**kwargs)
        self.db_name = db_name
        self.table_name = table_name
        self.key_column = key_column
        self.username = 'root'
        self.password = 'root'
        self.host = 'localhost'

    def getData(self, valuename, line):
        return getattr(line, valuename)
