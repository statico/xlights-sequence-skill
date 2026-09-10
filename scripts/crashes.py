"""usage: tmp/venv/bin/python scripts/crashes.py xlights/music/<song>.mp3 B0 BP [min_sustain=2.5]
Grid-free cymbal crash finder: treble (4-11 kHz) onset peaks that keep ringing 250-400 ms later (a crash sustains, a hi-hat
doesn't). Prints ms, beat (fractional, on the B0/BP grid, so you can see on-beat vs anticipated), sustain ratio and attack
strength (fraction of the song's loudest). Paste the ms list into the song script; don't snap to the grid, drummers don't."""
import sys, librosa, numpy as np
f, B0, BP = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); ms_ = float(sys.argv[4]) if len(sys.argv) > 4 else 2.5
y, sr = librosa.load(f, sr=22050, mono=True); hop = 256
S = np.abs(librosa.stft(y, n_fft=2048, hop_length=hop)); fq = librosa.fft_frequencies(sr=sr, n_fft=2048)
band = S[(fq > 4000) & (fq < 11000)].sum(0); flux = np.maximum(np.diff(band, prepend=0), 0)
t = librosa.frames_to_time(np.arange(len(band)), sr=sr, hop_length=hop)
pk = librosa.util.peak_pick(flux, pre_max=8, post_max=8, pre_avg=40, post_avg=40, delta=np.percentile(flux, 96), wait=20)
fr = lambda s: int(s * sr / hop)
out = []
for i in pk:
    after = band[i + fr(.25):i + fr(.4)].mean(); before = band[max(0, i - fr(.15)):max(1, i - fr(.06))].mean()
    if after > ms_ * before: out.append((int(t[i] * 1000), round((t[i] * 1000 - B0) / BP, 2), round(after / before, 1), round(flux[i] / flux[pk].max(), 2)))
print(len(out), "crashes: ms, beat, sustain, attack")
for o in out: print(o)
print("MS =", [o[0] for o in out])
