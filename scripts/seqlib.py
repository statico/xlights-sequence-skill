"""Shared machinery for generated musical xLights sequences. A Song holds the beat grid, the per-model effect layers and the
xsq writer; make_<song>.py supplies the tables (sections, themes, house effects per phrase, matrix themes, lyrics).
ADAPT THE CONSTANTS BELOW (LINES, SMALL, FLOODS, FACE, MODELS, GROUP, FONT) to the models in your xlights_rgbeffects.xml.
The rest encodes what a real house taught us; see the skill's reference/ docs before changing behaviour."""
import os, re, xml.dom.minidom as md
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # project root (this file lives in scripts/)
# ---- your layout -------------------------------------------------------------------------------------------
LINES=["roof1","roof2","porch1","porch2","bush1","bush2","trunk","branch"]   # every string/line model that gets its own beat effects
ROOFS=("roof1","roof2","porch1","porch2")   # >150 px: moving VU bars look good
SMALL=("bush1","bush2","trunk","branch")    # ~50 px: any moving effect strobes; they only get decaying pulses
FLOODS=[f"flood{n}" for n in range(1,6)]    # DmxFloodlight models, one effect row each (never through a group)
FACE={"pumpkin":"HiRes Pumpkin Happy","ghost":"Spooky Ghost 1"}   # singing props -> faceInfo name; {} if none
GROUP="house"                               # model group of LINES only (no props, no floods)
FONT="'Melted Monster' 18"                  # a font with a Regular face; never add bold (fake-bold smears at 17 px)
# ---------------------------------------------------------------------------------------------------------------

def pal(*cs): return ",".join(f"C_BUTTON_Palette{i+1}={c}" for i,c in enumerate(cs))+","+",".join(f"C_CHECKBOX_Palette{i+1}=1" for i in range(len(cs)))
def fade(i,o): return f"T_TEXTCTRL_Fadein={i:.2f},T_TEXTCTRL_Fadeout={o:.2f}"
FADE=fade(1,1); UNMASK="T_CHOICE_LayerMethod=1 is Unmask,"; WHITE=pal("#FFFFFF")
def cols(p): return re.findall(r"#[0-9A-Fa-f]{6}",p)
def bright(p): return [c for c in cols(p) if max(int(c[i:i+2],16) for i in (1,3,5))>=0x80]  # pulses need a visible stop
def accent(p): return [c for c in bright(p) if min(int(c[i:i+2],16) for i in (1,3,5))<0xC0] or bright(p)  # never a white flash
def rot(p,n): cs=cols(p); return pal(*(cs[n%len(cs):]+cs[:n%len(cs)]))
def vufx(kind,track="Beats",extra=""): return ("VU Meter",f"E_CHOICE_VUMeter_Type={kind},E_CHOICE_VUMeter_TimingTrack={track},E_SLIDER_VUMeter_Sensitivity=70,E_SLIDER_VUMeter_Bars=12,E_SLIDER_VUMeter_StartNote=48,E_SLIDER_VUMeter_EndNote=96,{extra}T_CHOICE_LayerMethod=Max,"+fade(.3,.3))
PULSE="E_TEXTCTRL_Eff_On_Start=100,E_TEXTCTRL_Eff_On_End=0,T_CHOICE_LayerMethod=Normal"   # one-beat decaying pulse in a palette colour
PULSE_MAX=PULSE.replace("Normal","Max")   # same, but decays into the house-group effect underneath instead of hiding it
HIT=PULSE   # accent hit on a model's top layer: Normal so it replaces whatever is decaying under it
HOUSE_BEAT=["Timing Event Jump","Timing Event Timed Sweep","Timing Event Bar Bounce","Timing Event Sweep 2"]  # whole-house beat layer in drops, per phrase
BOUNCE=[1,2,3,4,5,4,3,2]   # flood chase order: one flood per beat, left-right-left
def dim(c,f=0.45): return "#"+"".join(f"{int(int(c[i:i+2],16)*f):02X}" for i in (1,3,5))
def ramp(p,f=0.45):   # accent stops interleaved with dimmed copies: a chase through this is a gradient, not an on/off edge
    ac=accent(p); return pal(*[c for x in ac for c in (dim(x,f),x)],dim(ac[0],f))

OUTLINE_FX=[("Bars","E_SLIDER_Bars_BarCount=3,E_CHOICE_Bars_Direction=Left,E_CHECKBOX_Bars_3D=1,E_CHECKBOX_Bars_Gradient=1,E_TEXTCTRL_Bars_Cycles=4.0,"+fade(0,0)),
            ("Meteors","E_CHOICE_Meteors_Type=Palette,E_CHOICE_Meteors_Effect=Left,E_SLIDER_Meteors_Count=25,E_SLIDER_Meteors_Length=60,E_SLIDER_Meteors_Speed=15,"+fade(0,0)),
            ("Bars","E_SLIDER_Bars_BarCount=2,E_CHOICE_Bars_Direction=Right,E_CHECKBOX_Bars_3D=1,E_CHECKBOX_Bars_Gradient=1,E_TEXTCTRL_Bars_Cycles=4.0,"+fade(0,0)),
            ("Wave","E_CHOICE_Wave_Type=Sine,E_CHOICE_Fill_Colors=Palette,E_SLIDER_Number_Waves=2,E_SLIDER_Wave_Height=80,E_SLIDER_Thickness_Percentage=45,E_SLIDER_Wave_Speed=20,"+fade(0,0))]
# Prop outlines in drops, per phrase. Two rules: run the palette through `ramp()`, and use a blending effect.
# Single Strand / Color Wash / Marquee stay 3-4 discrete colours even with an 8-stop palette, so a chase along an
# outline is a square wave that reads as a blink; Bars (Gradient), Meteors and Wave blend into a real travelling glow.
# VU Meter timing-event types render flat on submodels, so outlines need cycle-timed effects either way.
LINE_FX=["Timing Event Bar Bounce","Timing Event Sweep 2","Timing Event Random Bar","Timing Event Bars"]      # roof/porch lines in drops, per phrase
BEAT_LAYER={"drop":("Timing Event Jump","Beats"),"build":("Timing Event Jump","Beats"),"call":("Timing Event Jump","Beats"),"intro":("Timing Event Jump","Bars"),"break":("Timing Event Jump","Bars"),"outro":("Timing Event Jump","Bars")}
OUTLINES=tuple(f"{f}/Outline" for f in FACE)   # prop outline submodels (node ranges from each faceInfo FaceOutline)
MODELS=[GROUP,"matrix"]+list(FACE)+LINES+FLOODS

PH={**{c:"AI" for c in "aiy"},"e":"E","o":"O","u":"U",**{c:"MBP" for c in "mbp"},"f":"FV","v":"FV","l":"L","w":"WQ","q":"WQ"}
def phonemes(word,a,b):  # crude grapheme->xLights phoneme, evenly spread over the word
    ps=[PH.get(c,"etc") for c in re.sub("[^a-z]","",word.lower())]
    ps=[p for i,p in enumerate(ps) if i==0 or p!=ps[i-1]] or ["etc"]
    n=len(ps); w=(b-a)/n
    return [(int(a+i*w),int(a+(i+1)*w),p) for i,p in enumerate(ps)]
def parse_lyrics(text):
    """Lines of `who t word t word ...` (who = pumpkin|ghost|both; a bare timestamp is a rest gap). Returns (words, {face:[phonemes]})."""
    words=[]; ph={f:[] for f in FACE}
    for line in text.strip().split("\n"):
        tok=line.split(); who=tok[0]; ts=tok[1:]
        i=0
        while i<len(ts)-1:
            a=float(ts[i])*1000; w=ts[i+1]
            if re.match(r"^\d",w): i+=1; continue
            b=float(ts[i+2])*1000 if i+2<len(ts) else a+400
            words.append((int(a),int(b),w))
            for f in (list(FACE) if who=="both" else [who]): ph[f]+=phonemes(w,a,b)
            i+=2
    return words,ph

class Song:
    def __init__(self,name,media,dur,b0,bp,title,artist):
        self.name=name; self.out=os.path.join(ROOT,"xlights","sequences",name+".xsq"); self.media=os.path.join(ROOT,"xlights","music",media)
        self.DUR=dur; self.B0=b0; self.BP=bp; self.NB=int((dur-b0)//bp); self.title=title; self.artist=artist
        self.db=[]; self.pals=[]; self.fx=0; self.mx=0; self.mxspan=1; self.floor=35   # pulse floor %: every 100->0 On decays to this instead of black (100->0 every beat was jarring)
        self.L={k:[[],[],[]] for k in [GROUP,"matrix"]+list(FACE)+list(OUTLINES)+LINES+FLOODS}; self.L[GROUP].append([])   # house: 0 fx, 1 Fire floor, 2 beat VU (a VU layer hides everything under it)
        self.DROP_FX=[]; self.MATRIX_DROP=[]; self.font=FONT; self.cues=[]; self.theme_at=lambda ms:pal("#FF6A00","#8000FF")
    def bt(self,k): return int(round(self.B0+self.BP*k))
    def kof(self,ms): return int(round((ms-self.B0)/self.BP))
    def idx(self,lst,v):
        if v not in lst: lst.append(v)
        return lst.index(v)
    def eff(self,n,s,p,a,b):
        if self.floor and n=="On": s=s.replace("Eff_On_Start=100,E_TEXTCTRL_Eff_On_End=0,",f"Eff_On_Start=100,E_TEXTCTRL_Eff_On_End={self.floor},")
        return f'<Effect ref="{self.idx(self.db,s)}" name="{n}" startTime="{a}" endTime="{b}" palette="{self.idx(self.pals,p)}"/>'
    def add(self,model,layer,n,s,p,a,b):
        if n=="VU Meter" and ("Timing Event Jump" in s or (model in SMALL and "Timing Event" in s)):   # Jump is a hard blink; any sweep/bounce on a 50 px model is a square wave
            return self.pulses(model,layer,p,a,b,4 if "TimingTrack=Bars" in s else 1)
        self.L[model][layer].append(self.eff(n,s,p,a,b))
    def pulses(self,model,layer,p,a,b,every=1,blend=PULSE_MAX):
        """Decaying pulse (100 -> 0) per beat (or per `every` beats) in the palette's accent colours, rotating.
        Replaces VU Meter "Timing Event Jump", which is a hard 225 ms on/off blink and hides the group effect."""
        ac=accent(p) or cols(p); k=self.kof(a)
        if self.bt(k)<a: k+=1
        while self.bt(k)<b:
            self.L[model][layer].append(self.eff("On",blend,pal(ac[(k//every)%len(ac)]),self.bt(k),min(self.bt(k+every),b))); k+=every
    # ---- house / matrix / floods primitives
    def house(self,n,s,p,a,b):   # the GROUP effect for a section/phrase
        self.add(GROUP,0,n,s,p,a,b)
        if n=="Fire": self.add(GROUP,1,"On","E_TEXTCTRL_Eff_On_Start=50,E_TEXTCTRL_Eff_On_End=50,T_CHOICE_LayerMethod=Normal",pal(accent(p)[0]),a,b)   # Fire grows from black over ~4 s; a floor under it so the props never start dark
    def pic(self,f,a,b,layer=0,dir="none",speed=1.0): self.add("matrix",layer,"Pictures",f"E_TEXTCTRL_Pictures_Filename=sprites/{f},E_CHOICE_Pictures_Direction={dir},E_TEXTCTRL_Pictures_Speed={speed},E_TEXTCTRL_Pictures_FrameRateAdj=1.0,E_CHOICE_Scaling=Scale To Fit,E_CHECKBOX_Pictures_TransparentBlack=1,"+UNMASK+fade(0,0),WHITE,a,b)
    def txt(self,s,a,b,dir="left",speed=12,fi=0,fo=0,p=WHITE,layer=0,mask=True):
        # Speed is a TEXTCTRL key; E_SLIDER_Text_Speed is silently ignored and everything scrolls at the default rate.
        # mask=True: the text is a stencil, the layer below shows through the glyphs (and nothing shows between lines).
        # mask=False: solid glyphs blended over whatever is below, so a background effect stays visible in the gaps.
        self.add("matrix",layer,"Text",f"E_TEXTCTRL_Text={s},E_CHOICE_Text_Dir={dir},E_TEXTCTRL_Text_Speed={speed},E_FONTPICKER_Text_Font={self.font},E_CHECKBOX_Text_PixelOffsets=0,"+(UNMASK if mask else "T_CHOICE_LayerMethod=Max,")+fade(fi,fo),p,a,b)
    def txtfit(self,s,a,b,margin=.85,**kw):
        """Scrolling text sized to its own window: a `left` scroll crosses once and stops, in
        0.341*(11*chars+35)/speed seconds (measured, 18 px display font on a 35 px matrix). The formula overestimates
        on short strings, so margin .85 runs a little slow and the effect's fade-out covers the tail."""
        sec=max((b-a)/1000,.2); return self.txt(s,a,b,speed=max(3,round(margin*.341*(11*len(s)+35)/sec)),**kw)
    def bg(self,n,s,p,a,b): self.add("matrix",1,n,s,p,a,b)
    def floods_wash(self,p,a,b,cycles=1.0):
        for n in range(1,6): self.add(f"flood{n}",0,"Color Wash",f"E_TEXTCTRL_ColorWash_Cycles={cycles},"+FADE,rot(p,n),a,b)
    def beat_pics(self,frames,a,b,layer=0):   # one sprite frame per beat, cycling through `frames`; exact, unlike GIF frame rates
        for k in range(self.kof(a),self.NB):
            if self.bt(k)>=b: break
            self.pic(frames[k%len(frames)],self.bt(k),min(self.bt(k+1),b),layer)
    def sub_pics(self,frames,k0,k1,subs,layer=0):   # riser: `subs[i]` frames inside beat k0+i
        for kk in range(k0,k1):
            n=subs[kk-k0]
            for j in range(n): self.pic(frames[j%len(frames)],self.bt(kk)+int(self.BP*j/n),self.bt(kk)+int(self.BP*(j+1)/n),layer)
    def sprite(self,f,a,b,moves,layer=0):   # GIF that changes movement every bar
        k=self.kof(a)
        while self.bt(k)<b:
            d,sp=moves[(k//4)%len(moves)]; self.pic(f,self.bt(k),min(self.bt(k+4),b),layer,dir=d,speed=sp); k+=4
    def plasma(self,p,a,b,style=3,dens=3,speed=12,fo=0): self.bg("Plasma",f"E_CHOICE_Plasma_Color=Normal,E_SLIDER_Plasma_Style={style},E_SLIDER_Plasma_Line_Density={dens},E_SLIDER_Plasma_Speed={speed},"+fade(0,fo),p,a,b)
    def vu(self,kind,p,a,b,bars=12): self.bg("VU Meter",f"E_CHOICE_VUMeter_Type={kind},E_SLIDER_VUMeter_Bars={bars},E_SLIDER_VUMeter_Sensitivity=15,E_SLIDER_VUMeter_StartNote=48,E_SLIDER_VUMeter_EndNote=96,E_CHECKBOX_VUMeter_SlowDownFalls=1,"+fade(0,0),p,a,b)
    def swirl(self,p,a,b): self.bg("Spirals","E_SLIDER_Spirals_Count=3,E_SLIDER_Spirals_Rotation=40,E_SLIDER_Spirals_Thickness=45,E_CHECKBOX_Spirals_Blend=1,E_CHECKBOX_Spirals_3D=1,E_CHECKBOX_Spirals_Grow=1,E_TEXTCTRL_Spirals_Movement=6.0,"+fade(0,0),p,a,b)
    def galaxy(self,p,a,b): self.bg("Galaxy","E_SLIDER_Galaxy_Start_Radius=1,E_SLIDER_Galaxy_End_Radius=60,E_SLIDER_Galaxy_Revolutions=1440,E_SLIDER_Galaxy_Start_Width=20,E_SLIDER_Galaxy_End_Width=60,E_SLIDER_Galaxy_Duration=60,E_CHECKBOX_Galaxy_Blend_Edges=1,"+fade(0,0),p,a,b)
    def fire(self,p,a,b,height=100,layer=1): self.add("matrix",layer,"Fire",f"E_SLIDER_Fire_Height={height},E_SLIDER_Fire_HueShift=0,"+fade(0,0),p,a,b)
    # ---- section builders
    def drop(self,k0,k1,theme,phrase=16):
        """Drop section: house effect per phrase from DROP_FX, whole-house beat layer, outline chases, flood pulses,
        line pulses/bars, matrix theme from MATRIX_DROP. Themes cycle per phrase."""
        for i,ph in enumerate(range(k0,k1,phrase)):
            n,s,_=self.DROP_FX[self.fx%len(self.DROP_FX)]; p=theme[self.fx%len(theme)]; self.fx+=1; fx=self.fx
            pa,pb=self.bt(ph),min(self.bt(min(ph+phrase,k1)),self.DUR); self.house(n,s,p,pa,pb)
            self.add(GROUP,2,*vufx(HOUSE_BEAT[fx%len(HOUSE_BEAT)]),pal(*accent(p)),pa,pb)
            for r in OUTLINES: self.add(r,0,*OUTLINE_FX[fx%len(OUTLINE_FX)],ramp(p),pa,pb)   # accents only: a wash/bars through the theme's dark shades reads as fading from black
            ac=accent(p)
            for k in range(ph,min(ph+phrase,k1)):        # floods: even phrases pulse alternate halves, odd phrases chase back and forth
                for n in range(1,6):
                    if (n%2==k%2) if fx%2 else (n==BOUNCE[k%8]): self.add(f"flood{n}",0,"On",PULSE,pal(ac[(n+k//4)%len(ac)]),self.bt(k),self.bt(k+1))
            for r in ROOFS:   # lines: whole-line beat pulse in the accent colour + a chunky beat bar in the theme
                self.add(r,0,*vufx("Timing Event Jump"),pal(*ac),pa,pb)
                self.add(r,1,*vufx(LINE_FX[fx%len(LINE_FX)],extra="E_SLIDER_VUMeter_Bars=4,"),p,pa,pb)
            for r in SMALL: self.add(r,0,*vufx("Timing Event Jump"),p,pa,pb)  # Level Pulse jitters on small models
            if i%self.mxspan==0:   # matrix theme spans `mxspan` phrases
                self.MATRIX_DROP[self.mx%len(self.MATRIX_DROP)](pa,min(self.bt(min(ph+phrase*self.mxspan,k1)),self.DUR),p); self.mx+=1
        return p
    def calm_beats(self,sections,themes):
        """Non-drop sections: a Bars/Beats jump layer on the house and a slow Color Wash on the prop outlines."""
        for i,(k0,k1,kind) in enumerate(sections):
            if kind=="drop": continue
            n,st=vufx(*BEAT_LAYER[kind]); a,b=self.bt(k0),min(self.bt(k1),self.DUR)
            self.add(GROUP,2,n,st,pal(*accent(themes[i][0])),a,b)
            for r in OUTLINES: self.add(r,0,"Color Wash","E_TEXTCTRL_ColorWash_Cycles=%.1f,"%((k1-k0)/8)+fade(0,0),themes[i][0],a,b)
    def top(self,model):   # fresh top layer (EffectLayer 0); never rotate layers by index, that is how a line VU Meter ended up above the pulses and hid them
        self.L[model].insert(0,[]); return self.L[model][0]
    def hits(self,hits,color):
        """Accent hits [(beat, length_in_beats)] on every line model and flood, on a new top layer. color(beat_ms, length) -> palette."""
        T={r:self.top(r) for r in LINES+FLOODS}
        for k,d in hits:
            a,b=int(round(self.B0+self.BP*k)),int(round(self.B0+self.BP*(k+d))); c=color(a,d)
            for r in T: T[r].append(self.eff("On",HIT,c,a,b))   # per model, not the group: a model's own Max layers would mix the hit into near-white
    def faces(self,phon,facepal,face=FACE):
        """Faces from phoneme lists {who:[(a,b,ph)]}; facepal(who, ms) -> palette (mouth, eyes, outline)."""
        for who,fd in face.items():
            # Faces draws the outline itself and paints over the Outline submodel layers; turn it off where
            # the submodel has its own effects, or the prop's outline sits at a flat colour for the whole song.
            base=f"E_CHOICE_Faces_FaceDefinition={fd},E_CHOICE_Faces_Eyes=Auto,E_CHECKBOX_Faces_Outline={0 if any(self.L.get(who+'/Outline',[])) else 1},E_CHOICE_Faces_TimingTrack=,E_CHECKBOX_Faces_TransparentBlack=0,E_CHOICE_Faces_Phoneme="
            t=0; out=[]
            for a,b,ph in sorted(phon[who]):
                if a>t: out.append((t,a,"rest"))
                out.append((a,b,ph)); t=b
            out.append((t,self.DUR,"rest"))
            self.L[who][0]=[self.eff("Faces",base+ph,facepal(who,a),a,b) for a,b,ph in out if b>a]
    def timings(self,sections,words):
        bt,NB,DUR=self.bt,self.NB,self.DUR
        t={"Sections":[(bt(a),min(bt(b),DUR),k) for a,b,k in sections],"Bars":[(bt(k),bt(k+4),str(k//4+1)) for k in range(0,NB-4,4)],
           "Beats":[(bt(k),bt(k+1),"") for k in range(NB-1)],"Lyrics":words}
        t["Cues"]=self.cues   # always present (empty on a fresh sequence) so it can be drawn on in the GUI
        return t
    def load_cues(self):
        """Marks the user drew on a `Cues` timing track in the xLights GUI (kept across regeneration). Returns [(beat_start, beat_end, label)],
        snapped to half beats. Labels: hit | hit8 (two eighths) | double | triplet | 4x | text:WORDS | dark. See apply_cues."""
        self.cues=[]
        if not os.path.exists(self.out): return []
        x=open(self.out).read(); m=re.search(r'<Element type="timing" name="Cues">(.*?)</Element>',x,re.S)
        if not m: return []
        self.cues=[(int(a),int(b),l) for l,a,b in re.findall(r'<Effect label="([^"]*)" startTime="(\d+)" endTime="(\d+)"',m.group(1))]
        q=lambda ms:round((ms-self.B0)/self.BP*2)/2
        return [(q(a),q(b),l.strip()) for a,b,l in self.cues if l.strip()]
    def apply_cues(self,cues,frames,color=None):
        """hit/hit8: accent hits on lines+floods (see hits); double/triplet/4x: sprite frames subdivided per beat on the matrix top layer
        and floods pulsing at that subdivision; text:WORDS: matrix text; dark: house, lines and floods off (a black Normal layer on top)."""
        color=color or (lambda a,d:pal(accent(self.theme_at(a))[0]))
        hits=[]; sub={"double":2,"triplet":3,"4x":4}; T={r:self.top(r) for r in ["matrix",GROUP]+LINES+FLOODS}
        for a,b,l in cues:
            ms=self.bt(int(a)) if a==int(a) else int(round(self.B0+self.BP*a)); me=int(round(self.B0+self.BP*b))
            if l=="hit": hits.append((a,max(b-a,0.5)))
            elif l=="hit8": hits+= [(a,0.5),(a+0.5,0.5)]
            elif l in sub:
                n=sub[l]; k=int(a)
                while self.bt(k)<me:
                    for j in range(n):
                        ta,tb=self.bt(k)+int(self.BP*j/n),self.bt(k)+int(self.BP*(j+1)/n)
                        if frames: self.pic(frames[j%len(frames)],ta,tb,0)
                        for f in FLOODS: T[f].append(self.eff("On",PULSE,pal(accent(self.theme_at(ta))[j%len(accent(self.theme_at(ta)))]),ta,tb))
                    k+=1
            elif l.startswith("text:"): self.txt(l[5:].strip(),ms,me,speed=18,layer=0)
            elif l=="dark":
                for r in [GROUP]+LINES+FLOODS: T[r].append(self.eff("On","E_TEXTCTRL_Eff_On_Start=0,E_TEXTCTRL_Eff_On_End=0,T_CHOICE_LayerMethod=Normal",pal("#000000"),ms,me))
        if hits: self.hits(hits,color)
    def write(self,timings,script,extra=""):
        L=self.L; NL="\n"
        def elem(x): return f'    <Element type="model" name="{x}">'+"".join(f"<EffectLayer>{''.join(l)}</EffectLayer>" for l in ([l for l in L.get(x,[[]]) if l] or [[]]))+"".join(f'<SubModelEffectLayer name="Outline">{"".join(l)}</SubModelEffectLayer>' for l in L.get(x+"/Outline",[]) if l)+"</Element>"+NL
        def timing(name,evs): return f'    <Element type="timing" name="{name}"><EffectLayer>'+"".join(f'<Effect label="{l}" startTime="{a}" endTime="{b}"/>' for a,b,l in evs)+"</EffectLayer></Element>"+NL
        doc=f'''<?xml version="1.0" encoding="UTF-8"?>
<xsequence BaseChannel="0" ChanCtrlBasic="0" ChanCtrlColor="0" FixedPointTiming="1" ModelBlending="true">
  <head><version>2026.16</version><author></author><author-email></author-email><author-website></author-website><song>{self.title}</song><artist>{self.artist}</artist><album></album><MusicURL></MusicURL><comment>Generated by {script} on a {60000/self.BP:.0f} bpm grid.{extra}</comment><sequenceTiming>25 ms</sequenceTiming><sequenceType>Media</sequenceType><mediaFile>{self.media}</mediaFile><sequenceDuration>{self.DUR/1000:.3f}</sequenceDuration><imageDir></imageDir></head>
  <nextid>1</nextid>
  <Jukebox/>
  <ColorPalettes>{"".join(f"<ColorPalette>{p}</ColorPalette>" for p in self.pals)}</ColorPalettes>
  <EffectDB>{"".join(f"<Effect>{s}</Effect>" for s in self.db)}</EffectDB>
  <DataLayers><DataLayer lor_params="0" channel_offset="0" num_channels="0" num_frames="0" data="&lt;rendered: erase-mode&gt;" source="&lt;auto-generated&gt;" name="Nutcracker"/></DataLayers>
  <DisplayElements>
{"".join(f'    <Element collapsed="0" type="timing" name="{t}" visible="1" views="Master View" active="1"/>'+NL for t in timings)}{"".join(f'    <Element collapsed="0" type="model" name="{x}" visible="1"/>'+NL for x in MODELS)}  </DisplayElements>
  <ElementEffects>
{"".join(timing(t,e) for t,e in timings.items())}{"".join(elem(x) for x in MODELS)}  </ElementEffects>
  <lastView>0</lastView>
  <TimingTags>{"".join(f'<Tag number="{i}" position="-1"/>' for i in range(10))}</TimingTags>
</xsequence>
'''
        md.parseString(doc)
        open(self.out,"w").write(doc); print("wrote",self.out,f"{self.NB} beats, {len(self.db)} effect defs")
