from typing import Set
from scrapli import Scrapli
from scrapli.exceptions import ScrapliAuthenticationFailed, ScrapliConnectionError
from scrapli.helper import textfsm_parse

from common import Node, Edge, PlatformTypeMap, AccessType

import re


class SSHNode(Node):

    def parse_cdp_neighbors(self, nodeset: Set[Node], edgeset: Set[Edge]) -> Set[Node]:
        print(f'Connecting to {self.name}')
        newnodes = set()

        device = {
            "host": self.ipaddr,
            "auth_username": self.username,
            "auth_password": self.password,
            "auth_strict_key": False,
            "platform": self.accessType.value,
            "ssh_config_file": True
        }

        try:
            with Scrapli(**device) as conn:
                #TODO
                if self.accessType == AccessType.FI:
                    conn.send_command("connect nxos")

                response = conn.send_command("show cdp neighbors detail")
                if self.accessType is AccessType.IOSXR:
                    parsed = textfsm_parse('iosxr_show_cdp_neighbors_detail.tmpl', response.result)
                else:
                    parsed = textfsm_parse('ios_show_cdp_neighbors_detail.tmpl', response.result)
        except ScrapliAuthenticationFailed:
            return newnodes
        except ScrapliConnectionError:
            print(f"Failed SSH to {self.ipaddr}")
            return newnodes

        for x in parsed:
            name = x["host"]
            platform = x['platform']
            node = Node.create_node(PlatformTypeMap[platform], name)
            node.ipaddr = x['mgmt_ip']
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
