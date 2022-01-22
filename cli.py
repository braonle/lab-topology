from typing import Set
from scrapli import Scrapli
from scrapli.exceptions import ScrapliAuthenticationFailed, ScrapliConnectionError
from scrapli.helper import textfsm_parse

from common import Node, Edge, PlatformTypeMap, AccessType

TEXTFSM_PATH = "textfsm_templates"


class SSHNode(Node):

    def parse_neighbors(self, nodeset: Set[Node], edgeset: Set[Edge]) -> Set[Node]:
        newnodes = set()

        parsed = []
        for ip in self.ipaddr:
            print(f'Connecting to {self.name} at {ip}')
            device = {
                "host": ip,
                "auth_username": self.username,
                "auth_password": self.password,
                "auth_strict_key": False,
                "platform": self.accessType.value,
                "ssh_config_file": True
            }

            try:
                with Scrapli(**device) as conn:
                    # TODO
                    # if self.accessType == AccessType.FI:
                    #     conn.send_command("connect nxos")

                    response = conn.send_command("show cdp neighbors detail")
                    if self.accessType is AccessType.IOSXR:
                        parsed += textfsm_parse(f'{TEXTFSM_PATH}/iosxr/show_cdp_neighbors_detail.tmpl', response.result)
                    elif self.accessType is AccessType.IOS:
                        parsed += textfsm_parse(f'{TEXTFSM_PATH}/ios/show_cdp_neighbors_detail.tmpl', response.result)
                    elif self.accessType is AccessType.NXOS:
                        parsed += textfsm_parse(f'{TEXTFSM_PATH}/nxos/show_cdp_neighbors_detail.tmpl', response.result)
                break
            except ScrapliAuthenticationFailed:
                print(f"{ip} unreachable")
            except ScrapliConnectionError:
                print(f"SSH not enabled for {ip}")

        for x in parsed:
            name = x["host"]
            platform = x['platform']
            node = Node.create_node(PlatformTypeMap[platform], name)

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
