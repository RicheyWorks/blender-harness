import json,sys,os
sys.path.insert(0,r"C:\Users\730ri\projects\blender-harness"); os.chdir(r"C:\Users\730ri\projects\blender-harness")
from bharness.bus import Bus
J=os.path.join(os.environ["LOCALAPPDATA"],"Daedalus","jobs"); WL=os.path.join(J,"worklog.jsonl")
L=open(WL,encoding="utf-8").readlines()
pick=[l for l in L if '"TURN-IN' in l or '"CLAIM Asset' in l]
open(WL,"w",encoding="utf-8").writelines([l for l in L if l not in pick])
b=Bus(r"C:\Users\730ri\projects\bot-team\art")
for l in pick:
    t=json.loads(l)["text"]; r=b.send("note",{"text":t},to="*"); print(r, t[:70])
