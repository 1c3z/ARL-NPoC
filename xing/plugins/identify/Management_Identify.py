from lxml.html import fromstring
from xing.core.BasePlugin import BasePlugin
from xing.utils import http_req, get_title
from xing.core import PluginType, SchemeType


# 参考https://gist.github.com/leveryd/334b719e253261ffd0abfd161e499ae7
# 源gist 代码中应该还有一个目标爆破的逻辑，这里没有用,所以is_valid函数没有实现


class Plugin(BasePlugin):
    def __init__(self):
        super(Plugin, self).__init__()
        self.plugin_type = PluginType.POC
        self.vul_name = "疑似管理后台"
        self.app_name = 'Management'
        self.scheme = [SchemeType.HTTP, SchemeType.HTTPS]

    def verify(self, target):
        manage_word_list = ['admin', 'manage', 'manager', 'backend', 'monitor']
        title_word_list = ["管理后台", "后台管理", "管理系统", "管理平台"]

        conn = http_req(target)
        if conn.status_code not in [200, 301, 302]:
            return

        next_location = conn.headers.get("Location", "")

        # 域名关键字判断
        for word in manage_word_list:
            if word in self.target_info["host"] or word in next_location:
                self.logger.success("found 管理后台 {} by {}".format(target, word))
                return True

        # 网站标题判断
        target_title = get_title(conn.content)
        for title in title_word_list:
            if title in target_title:
                self.logger.success("found 管理后台 {} by {}".format(target, title))
                return True

        # vue 判断
        if conn.status_code == 200:
            if b"<table>" in conn.content:
                return True

            # body下所有的元素，只能有script/div/noscript/strong标签，必须有script/div标签
            if b'</body>' not in conn.content:
                return False

            black_tag_list = [b'</svg>', b'<a>', b'<p>']
            for black_tag in black_tag_list:
                if black_tag in conn.content:
                    return False

            dom = fromstring(conn.content)
            tag_list = ["script", 'div', 'noscript']
            target_tag_list = []

            for children in list(dom.body):
                if not isinstance(children.tag, str):
                    return
                target_tag = children.tag.lower()
                if target_tag not in tag_list:
                    return False
                target_tag_list.append(target_tag)

                if target_tag == 'noscript':
                    continue

                for next_children in list(children):
                    target_tag = next_children.tag.lower()
                    if target_tag not in tag_list:
                        return False
                    target_tag_list.append(target_tag)

            if "script" in target_tag_list and "div" in target_tag_list:
                self.logger.success("found 管理后台 {} Vue".format(target))
                return True



