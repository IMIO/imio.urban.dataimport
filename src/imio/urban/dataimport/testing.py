from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

import imio.urban.dataimport


IMIO_URBAN_DATAIMPORT = PloneWithPackageLayer(
    zcml_package=imio.urban.dataimport,
    zcml_filename='testing.zcml',
    gs_profile_id='imio.urban.dataimport:testing',
    name="IMIO_URBAN_DATAIMPORT")

IMIO_URBAN_DATAIMPORT_INTEGRATION = IntegrationTesting(
    bases=(IMIO_URBAN_DATAIMPORT, ),
    name="IMIO_URBAN_DATAIMPORT_INTEGRATION")

IMIO_URBAN_DATAIMPORT_FUNCTIONAL = FunctionalTesting(
    bases=(IMIO_URBAN_DATAIMPORT, ),
    name="IMIO_URBAN_DATAIMPORT_FUNCTIONAL")
