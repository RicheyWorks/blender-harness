from PIL import Image, ImageStat, ImageFilter
import sys
def stats(p):
    im=Image.open(p).convert('RGB'); im.thumbnail((480,270))
    L=im.convert('L'); s=ImageStat.Stat(L); h=L.histogram(); n=sum(h)
    px=list(im.getdata())
    med=[sorted(c)[len(c)//2] for c in zip(*px)]
    subj=sum(1 for q in px if sum(abs(a-b) for a,b in zip(q,med))>60)/len(px)
    e=ImageStat.Stat(L.filter(ImageFilter.FIND_EDGES)).mean[0]
    return dict(mean=round(s.mean[0],1),std=round(s.stddev[0],1),clip=round(sum(h[240:])/n,3),subject=round(subj,3),edge=round(e,2))
for p in sys.argv[1:]: print(p, stats(p))
