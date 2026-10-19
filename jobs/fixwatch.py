import json,urllib.request as u,time,re,sys
after=int(sys.argv[1]); end=time.time()+float(sys.argv[2]); out=open(sys.argv[3],"a",encoding="utf-8")
while time.time()<end:
    try: j=json.load(u.urlopen("http://127.0.0.1:9890/wait?me=blender-fixwatch&after=%d&timeout=20"%after,timeout=30))
    except Exception: time.sleep(10); continue
    for m in j.get("messages",[]):
        t=json.dumps(m.get("body")).lower()
        if re.search(r"watcher|artqueue|multi-object|4481|2963|15378",t) and m.get("from")!="blender-team": out.write("%s %s %s\n"%(m.get("id"),m.get("from"),t[:500])); out.flush()
    after=j.get("last",after)
