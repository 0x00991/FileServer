from flask import Flask, make_response, request, redirect
import os
import sys
import psutil
_g = psutil.Process().cmdline()[0].split("\\")[-1].split("/")[-1]
_h = psutil.Process().cmdline()[1].split("\\")[-1].split("/")[-1]
self_name = _h if _g == "python.exe" and _h.endswith(".py") else _g

PW = None if len(sys.argv) <= 1 else sys.argv[1]

exts = {
    "image/jpeg": ["jpg"],
    "image/x-icon": ["ico"],
    "image/*": ["png", "gif", "jpeg", "webp"],
    
    "text/plain": ["txt", "py", "bat", "cmd", "ps1", "php", "md"],
    "text/javascript": ["js"],
    "text/*": ["html", "css"],
    
    "audio/*": ["mp3", "m4a", "3gp", "aac", "wav", "audio/webm"],
    "video/*": ["mp4", "webm"]
}

app = Flask(__name__)
# app.debug = True
@app.route("/")
def hello():
    return "Hi Wor1d"

def uploadget():
    return """<style>input {width: 30%}</style><form action="/upload" method="POST" enctype="multipart/form-data">
    <input name="passwd" placeholder="password"><br>
    <input name="filepath" placeholder="File name+path"><br>
    <input type="file" name="file"><br>
    <input type="submit" value="Go">"""

def uploadpost():
    try:
        password = request.form.get("passwd", "")
        if PW is not None and password != PW:
            return "? NAGA"
        file = request.files["file"]
        downpath = request.form["filepath"]
        if downpath.find("..") != -1:
            return "NAGA"
        for i, downpath_dir in enumerate(downpath.split("/")):
            ddir = "./"+"/".join(downpath.split("/")[:i])
            if i+1 != len(downpath.split("/")):
                ddir += "/"+downpath_dir
    
            if not os.path.isdir(ddir): os.mkdir(ddir)

        file.save(downpath, 1024*1024*16) # buffer 16MB
        return redirect(downpath)
    except Exception as e:
        return f"er {e}"

@app.before_request
def bef_request():
    path = request.path[1:] if len(request.path) > 1 else "./"
    
    if path == "upload":
        if request.method == "GET":
            return uploadget()
        elif request.method == "POST":
            return uploadpost()
        else:
            return "", 500

    if any([path.find(i) != -1 for i in ["..", "\\", "?"]]) or path.startswith("/"): # or 
        return "", 400


    if os.path.isdir(path):
        items = os.listdir(path)
        for i in [self_name]: # blacklist
            if items.__contains__(i):
                items.remove(i)
        for i in items.copy():
            if i.startswith(".") or i.startswith("$"):
                items.remove(i)

        ret = f"<ul><li><a href='/{'/'.join(path.split('/')[:-1])}'>../</a></li>"
        for i in items:
            isfile = os.path.isfile(path+"/"+i)
            ret += f'<li><a href="/{(path+"/") if path != "./" else ""}{i}"{" target=_blank" if isfile else ""}>{i}</a></li>'
        ret += "</ul>"
        return ret
    if os.path.isfile(path):
        file_type = "application/octet-stream"
        
        ext = path.split("/")[-1].split(".")[-1]
        
        for k, v in exts.items():
            if ext in v:
                file_type = k.replace("*", ext, 1)

        read_type = "r" if file_type.startswith("text") else "rb"
        

        with open(path, read_type, encoding=("UTF-8" if read_type == "r" else None)) as f:
            res = make_response(f.read())
            res.content_type = file_type+"; charset=utf-8"
            return res

# app.run(host="0.0.0.0", port=443, ssl_context="adhoc")
app.run(host="0.0.0.0", port=80)