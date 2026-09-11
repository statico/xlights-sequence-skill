"""usage: python3 scripts/tools/textfit.py
Every left-scrolling matrix Text effect in every .xsq: predicted traversal time 0.341*(11*chars+35)/speed vs the
effect's own window. Target ratio is ~1.18 (the .85 margin in S.txtfit): the line is still crossing as the window
closes and the fade-out covers the tail. CUT (>1.4) never gets across; EARLY (<0.9) leaves the matrix showing the
background bare through the stencil, which reads as a flash."""
import re,glob,sys
for f in sorted(glob.glob('xlights/sequences/*.xsq')):
    x=open(f).read(); db=re.findall(r"<Effect>(.*?)</Effect>",x.split("<EffectDB>")[1].split("</EffectDB>")[0])
    m=re.search(r'<Element type="model" name="matrix">(.*?)</Element>',x,re.S)
    if not m: continue
    rows=[]
    for r,n,a,b in re.findall(r'ref="(\d+)" name="([^"]*)" startTime="(\d+)" endTime="(\d+)"',m.group(1)):
        if n!="Text": continue
        s=db[int(r)]; t=re.search(r"E_TEXTCTRL_Text=([^,]*)",s).group(1)
        d=re.search(r"Text_Dir=([^,]*)",s).group(1)
        sp=re.search(r"E_TEXTCTRL_Text_Speed=([^,]*)",s)
        sp=float(sp.group(1)) if sp else 10.0
        if d!="left": continue
        win=(int(b)-int(a))/1000; need=.341*(11*len(t)+35)/sp
        flag="CUT" if need>win*1.4 else ("EARLY" if need<win*.9 else "ok")
        if flag!="ok": rows.append(f"   {int(a)/1000:8.2f}s win {win:5.2f} need {need:5.2f} sp {sp:4.0f} {flag:5s} {t}")
    print(f.split('/')[-1], f"{len(rows)} bad"); print("\n".join(rows))
