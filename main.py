import jinja2
import common
import threading
from flask import Flask, redirect, request, url_for
from flask_caching import Cache

app = Flask(__name__)
cache = Cache()
cache.init_app(app=app, config={"CACHE_TYPE": "filesystem",'CACHE_DIR': '/tmp'})
cache.set("set_length", 0)


def rediscover(name: str, access_type: str, ip: str, username: str, passwd: str):
    node = common.Node.create_node(common.AccessType(access_type), name)
    node.id = 1
    node.ipaddr.add(ip)
    node.username = username
    node.password = passwd

    nodeset = set()
    edgeset = set()
    nodeset.add(node)

    newset = node.parse_neighbors(nodeset, edgeset)
    while len(newset) != 0:
        print(f"Nodes left to query: {len(newset)}")
        cache.set("set_length", len(newset))
        newnode = newset.pop()
        tmpset = newnode.parse_neighbors(nodeset, edgeset)
        newset = newset.union(tmpset)

    cache.set("set_length", 0)
    templateLoader = jinja2.FileSystemLoader(searchpath="./jinja2")
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "index.j2"
    template = templateEnv.get_template(TEMPLATE_FILE)
    outputText = template.render(nodeset=nodeset, edgeset=edgeset)

    with open("static/index.html", "w") as f:
        f.write(outputText)


@app.route("/rediscover", methods=['POST'])
def front_rediscover():
    with open("static/index.html", "w") as f:
        f.write("Rediscovering")

    if cache.get("set_length") == 0:
        cache.set("set_length", 1)
        name = request.form["name"]
        ip = request.form["ip"]
        username = request.form["login"]
        passwd = request.form["pass"]
        access_type = request.form["type"]
        t = threading.Thread(target=rediscover, args=(name, access_type, ip, username, passwd))
        t.start()
    return redirect(url_for('front_status_rediscover'))


@app.route("/status", methods=['GET'])
def front_status():
    set_length = cache.get("set_length")
    return f'<meta http-equiv="refresh" content="5">Nodes left to query: {set_length}'


@app.route("/status_rediscover", methods=['GET'])
def front_status_rediscover():
    set_length = cache.get("set_length")

    if set_length == 0:
        return redirect('/')

    return f'<meta http-equiv="refresh" content="5">Nodes left to query: {set_length}'
