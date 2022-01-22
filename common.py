from enum import Enum
from typing import Set


class AccessType(Enum):
    NONE = 'none'
    NXOS = 'cisco_nxos'
    IOS = 'cisco_iosxe'
    IOSXR = 'cisco_iosxr'
    FI = 'cisco_nxos'


PlatformTypeMap = {
    'WS-C3750X-48P': AccessType.IOS,
    'FAS3210': AccessType.NONE,
    'UCS-FI-6248UP': AccessType.FI,
    'N9K-C93180YC-EX': AccessType.NXOS,
    'N5K-C5548UP': AccessType.NXOS,
    'WS-C3750G-48PS': AccessType.IOS,
    'ISE-VM-K9': AccessType.NONE,
    'ASR-920-24SZ-IM': AccessType.IOS,
    'Cisco-VM-SPID': AccessType.NONE,
    'ME-C3750-24TE': AccessType.IOS,
    'WS-C3560X-24P': AccessType.IOS,
    'CISCO2901/K9': AccessType.IOS,
    'WS-C3560X-24': AccessType.IOS,
    'ASR9K': AccessType.IOSXR,
    'NCS-5500': AccessType.IOSXR,
    'ASR9K Series': AccessType.IOSXR,
    '891': AccessType.IOS,
    '892': AccessType.IOS,
    'ESX': AccessType.NONE,
    'WS-C3850-48U': AccessType.IOS,
    'N9K-C9300v': AccessType.NXOS,
    'WS-C4900M': AccessType.IOS,
    'N9K-C9332C': AccessType.NXOS
}


class Node:
    id: int
    name: str
    ipaddr: Set[str]
    accessType: AccessType
    username: str
    password: str

    def __init__(self, name):
        self.name = name
        self.ipaddr = set()
        self.accessType = AccessType.NONE
        self.id = 0
        self.username = ""
        self.password = ""

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented

        return self.name == other.name and self.accessType == other.accessType

    def __hash__(self):
        return hash((self.name, self.accessType))

    def parse_neighbors(self, nodeset: Set['Node'], edgeset: Set['Node']) -> Set['Node']:
        pass

    def get_title(self):
        lst = list(self.ipaddr)
        length = len(self.ipaddr)

        if length == 0:
            return "unknown"
        elif length == 1:
            return lst[0]

        result = lst[0]
        for s in lst[1:]:
            result = result + f", {s}"

        return result


    @staticmethod
    def create_node(access_type: AccessType, name: str) -> 'Node':
        import cli
        if access_type == AccessType.NONE:
            return NoneNode(name)
        elif access_type in (AccessType.NXOS, AccessType.IOS, AccessType.IOSXR):
            node = cli.SSHNode(name)
            node.accessType = access_type
            return node


class NoneNode(Node):
    def parse_neighbors(self, nodeset: Set['Node'], edgeset: Set['Node']) -> Set['Node']:
        return set()


class Edge:
    head: Node
    tail: Node
    headIntf: str
    tailIntf: str
    headId: int
    tailId: int

    def __init__(self, head: Node, tail: Node, head_intf: str, tail_intf: str):
        self.head = head
        self.tail = tail
        self.headIntf = head_intf
        self.tailIntf = tail_intf
        self.headId = 0
        self.tailId = 0

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented

        # Node sequence is the same
        if self.head == other.head and self.tail == other.tail:
            # Interface sequence is the same
            if self.headIntf == other.headIntf and self.tailIntf == other.tailIntf:
                return True
        # Node sequence is reverse
        elif self.head == other.tail and self.tail == other.head:
            # Interface sequence is reverse
            if self.headIntf == other.tailIntf and self.tailIntf == other.headIntf:
                return True

        return False

    def __hash__(self):
        return hash((self.head, self.headIntf)) + hash((self.tail, self.tailIntf))

    def get_title(self):
        return f"{self.head.name}[{self.headIntf}]---{self.tail.name}[{self.tailIntf}]"
