import json,urllib.request as u,time,re
a=27404; end=time.time()+3*3600+300
while time.time()<end:
    try: ms=json.load(u.urlopen("http://127.0.0.1:9890/wait?me=blender-team-mon&after=%d&timeout=60"%a,timeout=90)).get("messages",[])
    except Exception as e: time.sleep(30); continue
    for m in ms:
        a=max(a,m["id"]); t=json.dumps(m.get("body"))
        if re.search(r"blender|AssetLod|BBA|0c18e693",t,re.I) and m.get("from")!="blender-team":
            open("mentions.jsonl","a",encoding="utf-8").write(json.dumps({"id":m["id"],"from":m.get("from"),"to":m.get("to"),"t":t[:500]})+"\n")
