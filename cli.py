from typing import Set
from scrapli import Scrapli
from scrapli.exceptions import ScrapliAuthenticationFailed, ScrapliConnectionError, ScrapliTimeout
from scrapli.helper import textfsm_parse

from common import Node, Edge, PlatformTypeMap, AccessType

TEXTFSM_PATH = "textfsm_templates"


class SSHNode(Node):

    def parse_neighbors(self, nodeset: Set[Node], edgeset: Set[Edge]) -> Set[Node]:
        newnodes = set()

        parsed = []
        for ip in self.ipaddr:
            print(f'Connecting to {self.name} at {ip}')
            access_type = PlatformTypeMap[self.platform]
            device = {
                "host": ip,
                "auth_username": self.username,
                "auth_password": self.password,
                "auth_strict_key": False,
                "platform": access_type.value,
                "ssh_config_file": True
            }

            try:
                with Scrapli(**device) as conn:
                    response = conn.send_command("show cdp neighbors detail")
                    if access_type is AccessType.IOSXR:
                        parsed += textfsm_parse(f'{TEXTFSM_PATH}/iosxr/show_cdp_neighbors_detail.tmpl', response.result)
                    elif access_type is AccessType.IOS:
                        parsed += textfsm_parse(f'{TEXTFSM_PATH}/ios/show_cdp_neighbors_detail.tmpl', response.result)
                    elif access_type is AccessType.NXOS:
                        parsed += textfsm_parse(f'{TEXTFSM_PATH}/nxos/show_cdp_neighbors_detail.tmpl', response.result)
                break
            except ScrapliAuthenticationFailed:
                print(f"{ip} unreachable")
            except ScrapliConnectionError:
                print(f"SSH not enabled for {ip} or login incorrect")
            except ScrapliTimeout:
                print(f"Platform incorrect for {ip}")

        for x in parsed:
            name = x["host"]
            platform = x['platform']
            node = Node.create_node(platform, name)

            for ip in x['mgmt_ip']:
                node.ipaddr.add(ip)

            node.username = self.username
            node.password = self.password
            node.id = len(nodeset) + 1

            dup = None
            for n in nodeset:
                if n == node:
                    dup = n

            if dup is None:
                nodeset.add(node)
                newnodes.add(node)
            else:
                node = dup

            edge = Edge(self, node, x['local_port'], x['remote_port'])
            edgeset.add(edge)

        return newnodes
