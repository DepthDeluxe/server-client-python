import xml.etree.ElementTree as ET

from .exceptions import UnpopulatedPropertyError


class ItemWithPermissions(object):
    def __init__(self):
        self._permissions = None

    @property
    def permissions(self):
        if self._permissions is None:
            error = "Server item must be populated with permissions first."
            raise UnpopulatedPropertyError(error)
        return self._permissions()

    def _set_permissions(self, permissions):
        self._permissions = permissions


class Permission:
    class Type:
        Datasource = 'datasource'
        Workbook = 'workbook'
        Project = 'project'

    class GranteeType:
        User = 'user'
        Group = 'group'

    class CapabilityMode:
        Allow = 'Allow'
        Deny = 'Deny'

    class DatasourceCapabilityType:
        ChangePermissions = 'ChangePermissions'
        Connect = 'Connect'
        Delete = 'Delete'
        ExportXml = 'ExportXml'
        Read = 'Read'
        Write = 'Write'

    class WorkbookCapabilityType:
        AddComment = 'AddComment'
        ChangeHierarchy = 'ChangeHierarchy'
        ChangePermissions = 'ChangePermissions'
        Delete = 'Delete'
        ExportData = 'ExportData'
        ExportImage = 'ExportImage'
        ExportXml = 'ExportXml'
        Filter = 'Filter'
        Read = 'Read'
        ShareView = 'ShareView'
        ViewComments = 'ViewComments'
        ViewUnderlyingData = 'ViewUnderlyingData'
        WebAuthoring = 'WebAuthoring'
        Write = 'Write'

    class ProjectCapabilityType:
        ProjectLeader = 'ProjectLeader'
        Read = 'Read'
        Write = 'Write'


class GranteeCapabilityItem(object):
    def __init__(self, grantee_type=None, grantee_id=None, capabilities=None):
        self._grantee_type = grantee_type
        self._grantee_id = grantee_id
        self._capabilities = capabilities

    def _set_values(self, grantee_type, grantee_id, capabilities):
        self._grantee_type = grantee_type
        self._grantee_id = grantee_id
        self._capabilities = capabilities

    @property
    def grantee_type(self):
        return self._grantee_type

    @property
    def grantee_id(self):
        return self._grantee_id

    @property
    def capabilities(self):
        return self._capabilities


class PermissionsItem(object):
    def __init__(self):
        self._type = None
        self._item_id = None
        self._grantee_capabilities = None

    def _set_values(self, type, item_id, grantee_capabilities):
        self._type = type
        self._item_id = item_id
        self._grantee_capabilities = grantee_capabilities

    @property
    def type(self):
        return self._type

    @property
    def item_id(self):
        return self._item_id

    @property
    def grantee_capabilities(self):
        return self._grantee_capabilities

    @property
    def is_user_permission(self):
        return self._user_id is not None

    @property
    def is_group_permission(self):
        return self._group_id is not None

    @classmethod
    def from_response(cls, resp, ns=None):
        permissions = PermissionsItem()
        parsed_response = ET.fromstring(resp)

        for option in ('workbook', 'datasource', 'project'):
            try:
                item_id = parsed_response.find('.//t:{0}'.format(option), namespaces=ns).get('id')
                permission_type = option
                break
            except AttributeError:
                pass

        all_xml = parsed_response.findall('.//t:granteeCapabilities', namespaces=ns)

        grantee_capabilities = []
        for grantee_capability_xml in all_xml:
            grantee_capability = GranteeCapabilityItem()

            try:
                grantee_id = grantee_capability_xml.find('.//t:group', namespaces=ns).get('id')
                grantee_type = Permission.GranteeType.Group
            except AttributeError:
                pass

            try:
                grantee_id = grantee_capability_xml.find('.//t:user', namespaces=ns).get('id')
                grantee_type = Permission.GranteeType.User
            except AttributeError:
                pass

            assert grantee_id is not None

            capabilities = {}
            for capability_xml in grantee_capability_xml.findall('.//t:capabilities/t:capability', namespaces=ns):
                name = capability_xml.get('name')
                mode = capability_xml.get('mode')

                capabilities[name] = mode

            grantee_capability._set_values(grantee_type, grantee_id, capabilities)
            grantee_capabilities.append(grantee_capability)

        permissions._set_values(permission_type, item_id, grantee_capabilities)
        return permissions
