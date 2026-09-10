"""usage: tmp/venv/bin/python scripts/analyze.py xlights/music/<song>.mp3  -> tempo, fitted beat grid, per-second energy, segment bounds; writes tmp/<song>.analysis.json"""
import librosa, numpy as np, json, sys, os
f=sys.argv[1]; name=os.path.splitext(os.path.basename(f))[0]
y,sr=librosa.load(f,sr=22050,mono=True); dur=len(y)/sr
tempo,beats=librosa.beat.beat_track(y=y,sr=sr,units='time',trim=False); tempo=float(np.atleast_1d(tempo)[0])
# straight-line fit: beat k = B0 + BP*k (ms). Trust a round bpm over the raw median; check the residual.
k=np.arange(len(beats)); BP,B0=np.polyfit(k,beats*1000,1); resid=np.abs(beats*1000-(B0+BP*k)).max()
print(f"dur {dur:.2f}s ({int(dur*1000)} ms) tempo {tempo:.2f} bpm fit: B0={B0:.2f} BP={BP:.3f} ({60000/BP:.2f} bpm) max residual {resid:.0f} ms, {len(beats)} beats, first {np.round(beats[:4],3).tolist()}")
hop=512; rms=librosa.feature.rms(y=y,hop_length=hop)[0]; t=librosa.frames_to_time(np.arange(len(rms)),sr=sr,hop_length=hop)
S=np.abs(librosa.stft(y,hop_length=hop)); freqs=librosa.fft_frequencies(sr=sr); bass=S[freqs<150].sum(0); hi=S[freqs>2000].sum(0)
on=librosa.onset.onset_strength(y=y,sr=sr,hop_length=hop)
print("sec  rms  bass  hi  onset")
for s in range(int(dur)):
    m=(t>=s)&(t<s+1); print(f"{s:3d} {rms[m].mean():.3f} {bass[m].mean():7.1f} {hi[m].mean():6.1f} {on[m].mean():5.2f}")
C=librosa.feature.chroma_cqt(y=y,sr=sr,hop_length=hop); bf=librosa.beat.beat_track(y=y,sr=sr,hop_length=hop,trim=False)[1]
Cs=librosa.util.sync(C,bf,aggregate=np.median); bounds=librosa.segment.agglomerative(Cs,16); bt=librosa.frames_to_time(bf[bounds],sr=sr,hop_length=hop)
print("agglomerative bounds:",np.round(bt,2).tolist())
json.dump({"tempo":tempo,"B0":B0,"BP":BP,"dur_ms":int(dur*1000),"beats":[round(float(b),3) for b in beats],"bounds":[round(float(b),3) for b in bt]},open(f"tmp/{name}.analysis.json","w"))
