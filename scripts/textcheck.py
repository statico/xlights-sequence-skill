"""For every left-scrolling matrix Text effect in a rendered show: is the text still on screen 85% of the way
through its window (fits), and is the matrix ever bare (no glyphs, background blasting through the stencil)?"""
import sys,os,re,glob,numpy as np; sys.path.insert(0,'scripts/tools'); import fseq
for f in sorted(glob.glob('xlights/sequences/*.fseq')):
    x=open(f.replace('.fseq','.xsq')).read()
    db=re.findall(r"<Effect>(.*?)</Effect>",x.split("<EffectDB>")[1].split("</EffectDB>")[0])
    m=re.search(r'<Element type="model" name="matrix">(.*?)</Element>',x,re.S)
    if not m: continue
    F,step,starts=fseq.load(f); s=starts['matrix']; W,H=35,17
    lit=F[:,s:s+W*H*3].reshape(len(F),-1,3).max(2)
    bad=[]
    for r,n,a,b in re.findall(r'ref="(\d+)" name="([^"]*)" startTime="(\d+)" endTime="(\d+)"',m.group(1)):
        if n!="Text": continue
        st=db[int(r)]
        if "Text_Dir=left" not in st: continue
        t=re.search(r"E_TEXTCTRL_Text=([^,]*)",st).group(1); a,b=int(a),int(b)
        fr=lit[int(a/step):int(b/step)]
        if not len(fr): continue
        cov=(fr>40).mean(1)                       # fraction of the matrix lit per frame
        late=cov[int(len(cov)*.85):]
        if late.max()<.02: bad.append(f"   {a/1000:7.2f}s EMPTY at the end: {t}")
        if cov.max()>.85: bad.append(f"   {a/1000:7.2f}s background blasting through ({cov.max():.0%} lit): {t}")
    print(f"{os.path.basename(f):22s} {'OK' if not bad else str(len(bad))+' bad'}"); print("\n".join(bad))
