import xml.etree.ElementTree as ET
import logging

from .exceptions import UnknownGranteeTypeError


logger = logging.getLogger('tableau.models.permissions_item')


class Permission:

    class CapabilityMode:
        Allow = 'Allow'
        Deny = 'Deny'

    class CapabilityType:
        AddComment = 'AddComment'
        ChangeHierarchy = 'ChangeHierarchy'
        ChangePermissions = 'ChangePermissions'
        Connect = 'Connect'
        Delete = 'Delete'
        ExportData = 'ExportData'
        ExportImage = 'ExportImage'
        ExportXml = 'ExportXml'
        Filter = 'Filter'
        ProjectLeader = 'ProjectLeader'
        Read = 'Read'
        ShareView = 'ShareView'
        ViewComments = 'ViewComments'
        ViewUnderlyingData = 'ViewUnderlyingData'
        WebAuthoring = 'WebAuthoring'
        Write = 'Write'




class PermissionsRule(object):
    def __init__(self, type=None, object_id=None, caps_map={}):  # Dict[Capability: Mode]
        self._type = type
        self._object_id = object_id
        self.caps_map = caps_map  # Dict[Capability: Mode]
        self.map = self.caps_map

    @property
    def type(self):
        return self._type

    @property
    def object_id(self):
        return self._object_id

class PermissionsGrantee():
    def __init__(self, grantee_xml):
        self.type = None
        grantee_id = grantee_element.get('id', None)
        self.typegrantee_type = grantee_element.tag.split('}')[1]

class PermissionsCollection(object):
    def __init__(self):
        self._rules = None

    def _set_values(self, rules):
        self._rules = rules

    @property
    def rules(self):
        return self._rules

    @classmethod
    def from_response(cls, resp, ns=None):
        permissions = PermissionsCollection()
        parsed_response = ET.fromstring(resp)

        breakpoint()

        capabilities = {}
        all_xml = parsed_response.findall('.//t:granteeCapabilities',
                                          namespaces=ns)

        for grantee_capability_xml in all_xml:
            capability_map = {}

            grantee_element = grantee_capability_xml.findall('.//*[@id]', namespaces=ns).pop()
            grantee_id = grantee_element.get('id', None)
            grantee_type = grantee_element.tag.split('}')[1]
    
            if grantee_id is None:
                logger.error('Cannot find grantee type in response')
                raise UnknownGranteeTypeError()

            for capability_xml in grantee_capability_xml.findall(
                    './/t:capabilities/t:capability', namespaces=ns):
                name = capability_xml.get('name')
                mode = capability_xml.get('mode')

                capability_map[name] = mode

            capability_item = CapabilityItem(grantee_type, grantee_id,
                                             capability_map)
            capabilities[(grantee_type, grantee_id)] = capability_item

        permissions._set_values(capabilities)
        return permissions


## Compat Tests

PermissionsItem = PermissionsCollection
CapabilityItem = PermissionsRule