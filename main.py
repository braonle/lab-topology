import jinja2
import common

node = common.Node.create_node(common.AccessType.IOS, "A-PE4")
node.id = 1
node.ipaddr = "10.1.215.23"
node.username = "cisco"
node.password = "Cisco321"

# node = common.Node.create_node(common.AccessType.NXOS, "N5K_A")
# node.id = 1
# node.ipaddr = "10.5.30.23"
# node.username = "admin"
# node.password = "C1sc0ucs"

nodeset = set()
edgeset = set()
nodeset.add(node)


newset = node.parse_cdp_neighbors(nodeset, edgeset)
while len(newset) != 0:
    print(newset)
    newnode = newset.pop()
    tmpset = newnode.parse_cdp_neighbors(nodeset, edgeset)
    newset = newset.union(tmpset)

templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader)
TEMPLATE_FILE = "index.j2"
template = templateEnv.get_template(TEMPLATE_FILE)
outputText = template.render(nodeset=nodeset, edgeset=edgeset)

with open("index.html", "w") as f:
    f.write(outputText)

