import jinja2
import common

templateLoader = jinja2.FileSystemLoader(searchpath="./jinja2")
templateEnv = jinja2.Environment(loader=templateLoader)
TEMPLATE_FILE = "index.j2"
template = templateEnv.get_template(TEMPLATE_FILE)
outputText = template.render(nodeset=set(), edgeset=set(), platforms=list(common.PlatformTypeMap.keys()))

with open("static/index.html", "w") as f:
    f.write(outputText)