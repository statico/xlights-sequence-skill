"""usage: tmp/venv/bin/python scripts/lyrics.py xlights/music/<song>.mp3 START END [START END ...] ["initial prompt with the real lyrics"]
Runs mlx-whisper (large-v3-turbo, local) with word timestamps on 10-30 s clips; whole-file runs hallucinate on chopped vocals.
Prints one line per segment: `who START word END word ...`-ready `word@t` pairs. Only keep words that are really sung (check against the known lyrics)."""
import sys, subprocess, mlx_whisper, os
f=sys.argv[1]; args=sys.argv[2:]; prompt=args.pop() if args and not args[-1].replace(".","").isdigit() else ""
for a,b in zip(args[::2],args[1::2]):
    clip=f"tmp/clip_{os.path.basename(f)}_{a}.wav"
    subprocess.run(["ffmpeg","-v","error","-y","-ss",a,"-to",b,"-i",f,"-ac","1","-ar","16000",clip],check=True)
    r=mlx_whisper.transcribe(clip,path_or_hf_repo="mlx-community/whisper-large-v3-turbo",word_timestamps=True,language="en",initial_prompt=prompt,condition_on_previous_text=False)
    for s in r["segments"]:
        print(f"{float(a)+s['start']:6.2f}-{float(a)+s['end']:6.2f} {s['text'].strip()}")
        print("    "+" ".join(f"{w['word'].strip()}@{float(a)+w['start']:.2f}" for w in s.get("words",[])))
