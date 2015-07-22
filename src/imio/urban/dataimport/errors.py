# -*- coding: utf-8 -*-


class IdentifierError(StandardError):
    """ Every imported object should have an identifier 'id' """


class FactoryArgumentsError(StandardError):
    """ """


class NoPortalTypeError(StandardError):
    """ Every imported object should have an type."""
