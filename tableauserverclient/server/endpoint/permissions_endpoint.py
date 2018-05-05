import logging

from .. import RequestFactory, PermissionsItem

from .endpoint import Endpoint, api
from .exceptions import MissingRequiredFieldError


logger = logging.getLogger(__name__)


class EndpointWithPermissions(Endpoint):
    @api(version='2.0')
    def update_permission(self, item, permission_item):
        url = '{0}/{1}/permissions'.format(self.baseurl, item.id)
        update_req = RequestFactory.Permission.add_req(permission_item)
        response = self.put_request(url, update_req)
        permissions = PermissionsItem.from_response(response.content)

        logger.info('Updated permissions for item {0}'.format(item.id))

        return permissions

    @api(version='2.0')
    def delete_permission(self, item, grantee_capability):
        for capability_type in grantee_capability.capabilities:
            capability_mode = grantee_capability.capabilities[capability_type]

            url = '{0}/{1}/permissions/{2}/{3}/{4}/{5}'.format(
                self.baseurl, item.id, grantee_capability.type + 's',
                grantee_capability.grantee_id, capability_type,
                capability_mode)

            logger.debug('Removing {0} permission for capabilty {1}'.format(
                capability_mode, capability_type))

            self.delete_request(url)

        logger.info('Deleted permission for {0} {1} item {2}'.format(
            grantee_capability.type,
            grantee_capability.grantee_id,
            item.id))

    def populate_permissions(self, item):
        if not item.id:
            error = "Server item is missing ID. Item must be retrieved from server first."
            raise MissingRequiredFieldError(error)

        def permission_fetcher():
            return self._get_permissions(item)

        item._set_permissions(permission_fetcher)
        logger.info('Populated permissions for item (ID: {0})'.format(item.id))

    def _get_permissions(self, item, req_options=None):
        url = "{0}/{1}/permissions".format(self.baseurl, item.id)
        server_response = self.get_request(url, req_options)
        permissions = PermissionsItem.from_response(server_response.content, self.parent_srv.namespace)
        return permissions
