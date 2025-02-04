from typing import List

from cheshirecat_python_sdk.endpoints.base import AbstractEndpoint, MultipartPayload
from cheshirecat_python_sdk.models.api.admins import (
    AdminOutput,
    ResetOutput,
    CreatedOutput,
    PluginInstallOutput,
    PluginInstallFromRegistryOutput,
    PluginDetailsOutput,
    PluginDeleteOutput,
)
from cheshirecat_python_sdk.models.api.nested.plugins import PluginSettingsOutput
from cheshirecat_python_sdk.models.api.plugins import PluginCollectionOutput, PluginsSettingsOutput
from cheshirecat_python_sdk.models.api.tokens import TokenOutput
from cheshirecat_python_sdk.utils import deserialize, file_attributes


class AdminsEndpoint(AbstractEndpoint):
    def __init__(self, client: "CheshireCatClient"):
        super().__init__(client)
        self.prefix = "/admins"

    def token(self, username: str, password: str) -> TokenOutput:
        """
        This endpoint is used to get a token for the user. The token is used to authenticate the user in the system.
        When the token expires, the user must request a new token.
        :param username: The username of the user.
        :param password: The password of the user.
        :return: TokenOutput, the token of the user.
        """
        response = self.get_http_client().post(
            self.format_url("/auth/token"),
            json={"username": username, "password": password},
        )
        result = deserialize(response.json(), TokenOutput)
        self.client.add_token(result.access_token)
        return result

    def post_admin(self, username: str, password: str, permissions: dict | None = None) -> AdminOutput:
        """
        Create a new admin user.
        :param username: The username of the user.
        :param password: The password of the user.
        :param permissions: The permissions of the user.
        :return: AdminOutput, the details of the user.
        """
        payload = {"username": username, "password": password}
        if permissions:
            payload["permissions"] = permissions

        return self.post_json(self.format_url("/users"), AdminOutput, payload, self.system_id)

    def get_admins(self, limit: int | None = None, skip: int | None = None) -> List[AdminOutput]:
        """
        Get a list of all admin users.
        :param limit: The maximum number of users to return.
        :param skip: The number of users to skip.
        :return: List[AdminOutput], the details
        """
        query = {}
        if limit:
            query["limit"] = limit
        if skip:
            query["skip"] = skip

        response = self.get_http_client(self.system_id).get(self.format_url("/users"), params=query)
        result = []
        for item in response.json():
            result.append(deserialize(item, AdminOutput))
        return result

    def get_admin(self, admin_id: str) -> AdminOutput:
        """
        Get the details of an admin user.
        :param admin_id: The ID of the user.
        :return: AdminOutput, the details of the user.
        """
        return self.get(self.format_url(f"/users/{admin_id}"), AdminOutput, self.system_id)

    def put_admin(
        self,
        admin_id: str,
        username: str | None = None,
        password: str | None = None,
        permissions: dict | None = None,
    ) -> AdminOutput:
        """
        Update the details of an admin user.
        :param admin_id: The ID of the user.
        :param username: The new username.
        :param password: The new password.
        :param permissions: The new permissions.
        :return: AdminOutput, the details of the user.
        """
        payload = {}
        if username:
            payload["username"] = username
        if password:
            payload["password"] = password
        if permissions:
            payload["permissions"] = permissions

        return self.put(self.format_url(f"/users/{admin_id}"), AdminOutput, payload, self.system_id)

    def delete_admin(self, admin_id: str) -> AdminOutput:
        """
        Delete an admin user.
        :param admin_id: The ID of the user.
        :return: AdminOutput, the details of the user.
        """
        return self.delete(self.format_url(f"/users/{admin_id}"), AdminOutput, self.system_id)

    def post_factory_reset(self) -> ResetOutput:
        """
        Reset the system to the factory settings.
        :return: ResetOutput, the details of the reset.
        """
        return self.post_json(self.format_url("/utils/factory/reset/"), ResetOutput, {}, self.system_id)

    def get_agents(self) -> List[str]:
        """
        Get a list of all agents.
        :return: List[str], the IDs of the agents.
        """
        return self.get(self.format_url("/utils/agents/"), None, agent_id=self.system_id)

    def post_agent_create(self, agent_id: str | None = None) -> CreatedOutput:
        """
        Create a new agent.
        :param agent_id: The ID of the agent.
        :return: CreatedOutput, the details of the agent.
        """
        return self.post_json(self.format_url("/utils/agent/create/"), CreatedOutput, {}, agent_id)

    def post_agent_reset(self, agent_id: str | None = None) -> ResetOutput:
        """
        Reset an agent to the factory settings.
        :param agent_id: The ID of the agent.
        :return: ResetOutput, the details of the reset.
        """
        return self.post_json(self.format_url("/utils/agent/reset/"), ResetOutput, {}, agent_id)

    def post_agent_destroy(self, agent_id: str | None = None) -> ResetOutput:
        """
        Destroy an agent.
        :param agent_id: The ID of the agent.
        :return: ResetOutput, the details of the reset.
        """
        return self.post_json(self.format_url("/utils/agent/destroy/"), ResetOutput, {}, agent_id)

    def get_available_plugins(self, plugin_name: str | None = None) -> PluginCollectionOutput:
        """
        Get a list of all available plugins.
        :param plugin_name: The name of the plugin.
        :return: PluginCollectionOutput, the details of the plugins.
        """
        return self.get(
            self.format_url("/plugins"),
            PluginCollectionOutput,
            self.system_id,
            query={"query": plugin_name} if plugin_name else None,
        )

    def post_install_plugin_from_zip(self, path_zip: str) -> PluginInstallOutput:
        payload = MultipartPayload()

        with open(path_zip, "rb") as file:
            payload.files = [("file", file_attributes(path_zip, file))]
            result = self.post_multipart(
                self.format_url("/plugins/upload"), PluginInstallOutput, payload, self.system_id
            )
        return result

    def post_install_plugin_from_registry(self, url: str) -> PluginInstallFromRegistryOutput:
        """
        Install a new plugin from a registry. The plugin is installed asynchronously.
        :param url: The URL of the plugin.
        :return: PluginInstallFromRegistryOutput, the details of the installation.
        """
        return self.post_json(self.format_url("/plugins/upload/registry"), PluginInstallFromRegistryOutput, {"url": url}, self.system_id)

    def get_plugins_settings(self) -> PluginsSettingsOutput:
        """
        Get the default settings of all the plugins.
        :return: PluginsSettingsOutput, the details of the settings.
        """
        return self.get(self.format_url("/plugins/settings"), PluginsSettingsOutput, self.system_id)

    def get_plugin_settings(self, plugin_id: str) -> PluginSettingsOutput:
        """
        Get the default settings of a specific plugin.
        :param plugin_id: The ID of the plugin.
        :return: PluginSettingsOutput, the details of the settings.
        """
        return self.get(self.format_url(f"/plugins/settings/{plugin_id}"), PluginSettingsOutput, self.system_id)

    def get_plugin_details(self, plugin_id: str) -> PluginDetailsOutput:
        """
        Get the details of a specific plugin.
        :param plugin_id: The ID of the plugin.
        :return: PluginDetailsOutput, the details of the plugin.
        """
        return self.get(self.format_url(f"/plugins/{plugin_id}"), PluginDetailsOutput, self.system_id)

    def delete_plugin(self, plugin_id: str) -> PluginDeleteOutput:
        """
        Delete a specific plugin.
        :param plugin_id: The ID of the plugin.
        :return: PluginDeleteOutput, the details of the plugin.
        """
        return self.delete(self.format_url(f"/plugins/{plugin_id}"), PluginDeleteOutput, self.system_id)
