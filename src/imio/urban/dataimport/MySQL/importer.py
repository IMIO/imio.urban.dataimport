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

        metadata, main_table, Session = self.loadMainTable()

        self.metadata = metadata
        self.main_table = main_table
        self.new_session = Session

    def iterdata(self):
        session = self.new_session()

        result = session.main_table.query(self.main_table)
        records = result.all()

        return records

    def loadMainTable(self, importer):
        engine = create_engine(
            'mysql://{username}:{password}@{host}/{db_name}'.format(
                user=importer.username,
                password=importer.password,
                host=importer.host,
                db_name=importer.db_name,
            ),
            echo=True
        )

        metadata = MetaData(engine)
        main_table = Table(importer.table_name, metadata, autoload=True)
        Session = sessionmaker(bind=engine)

        return metadata, main_table, Session


class MySQLDataExtractor(DataExtractor):

    def extractData(self, valuename, line):
        tablename = getattr(self.mapper, 'table_name', self.mapper.importer.table_name)
        datasource = self.datasource
        data = line[datasource.header_indexes[tablename][valuename]]
        return data


class MySQLErrorMessage(ImportErrorMessage):

    def __str__(self):
        key = self.importer.getData(self.importer.key_column, self.line)
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
        db_name: the .mdb filename to query
        table_name: the main table in the data base (the one that will be used as 'central node' to recover licences)
        key_column: the db column used as key value when querying tables joint
    """

    implements(IMySQLImporter)

    def __init__(self, db_name, table_name, key_column, savepoint_length=0):
        super(MySQLDataImporter, self).__init__(savepoint_length)
        self.db_name = db_name
        self.table_name = table_name
        self.key_column = key_column

    def getData(self, valuename, line):
        data_index = self.datasource.header_indexes[self.table_name][valuename]
        data = line[data_index]
        return data
