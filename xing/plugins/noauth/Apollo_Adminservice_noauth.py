from xing.core.BasePlugin import BasePlugin
from xing.utils import http_req
from xing.core import PluginType, SchemeType


class Plugin(BasePlugin):
    def __init__(self):
        super(Plugin, self).__init__()
        self.plugin_type = PluginType.POC
        self.vul_name = "apollo-adminservice 未授权访问"
        self.app_name = 'apollo-adminservice'
        self.scheme = [SchemeType.HTTPS, SchemeType.HTTP]

    def verify(self, target):
        url = target + "/apps"
        conn = http_req(url)
        if b'<' in conn.content:
            return False

        if b'"ownerEmail"' not in conn.content:
            return False

        if b'"ownerName"' in conn.content:
            self.logger.success("found {} {}".format(self.app_name, url))
            return url
