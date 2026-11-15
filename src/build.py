# Build audio mix + subtitles + final index.html.
# Swap voice: replace vo/scene1..5.mp3 ; swap SFX: replace files in sfx/ (names in sfx/cues.json). Then rerun.
import json, subprocess, re, base64, os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STARTS=[0,25,55,85,110]; ENDS=[25,55,85,110,120]; LEAD=0.2
texts=[open(f"vo/s{i}.txt").read().strip() for i in range(1,6)]
def dur(f): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]).decode())
def run(c): subprocess.run(c,check=True)
os.makedirs("build",exist_ok=True)
subs=[]; fitted=[]
for i in range(5):
    src=f"vo/scene{i+1}.mp3"; out=f"build/vo{i+1}.wav"
    # trim leading/trailing silence
    run(["ffmpeg","-v","error","-y","-i",src,"-af","silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse","-ar","44100","-ac","2","build/tmp.wav"])
    d=dur("build/tmp.wav"); room=ENDS[i]-STARTS[i]-LEAD-0.35
    tempo=max(1.0,d/room)
    run(["ffmpeg","-v","error","-y","-i","build/tmp.wav","-af",f"atempo={tempo:.4f}",out])
    d2=dur(out); fitted.append((out,STARTS[i]+LEAD,d2,tempo))
    # sentence timing from pauses
    sents=[s.strip()+("।" if not s.strip().endswith(("।","...")) else "") for s in re.split(r"(?<=।)\s*",texts[i]) if s.strip()]
    sents=[s.rstrip("।") + "।" if s.endswith("।।") else s for s in sents]
    log=subprocess.run(["ffmpeg","-i",out,"-af","silencedetect=n=-35dB:d=0.18","-f","null","-"],capture_output=True,text=True).stderr
    st=[float(x) for x in re.findall(r"silence_start: ([\d.]+)",log)]; en=[float(x) for x in re.findall(r"silence_end: ([\d.]+)",log)]
    gaps=[(e-s,(s+e)/2) for s,e in zip(st,en) if 0.3<s<d2-0.3]
    # choose n-1 cut points: longest gaps, near proportional char positions
    n=len(sents); cuts=[]
    tot=sum(len(s) for s in sents); acc=0
    for k in range(n-1):
        acc+=len(sents[k]); target=d2*acc/tot
        cand=[g for g in gaps if abs(g[1]-target)<d2*0.18 and g[1] not in cuts]
        cuts.append(max(cand,key=lambda g:g[0]-abs(g[1]-target)*0.3)[1] if cand else target)
    b=[0]+cuts+[d2]
    for k,s in enumerate(sents):
        subs.append({"a":round(STARTS[i]+LEAD+b[k]-0.05,2),"b":round(STARTS[i]+LEAD+b[k+1]+(0.4 if k==n-1 else 0.05),2),"text":s.replace("।।","।")})
    print(f"scene{i+1}: {d:.2f}s -> tempo {tempo:.3f} -> {d2:.2f}s, starts {STARTS[i]+LEAD}s ends {STARTS[i]+LEAD+d2:.2f}s (window end {ENDS[i]})")
for k in range(len(subs)-1): subs[k]["b"]=min(subs[k]["b"],subs[k+1]["a"])
subs[-1]["b"]=min(subs[-1]["b"],119.6)
json.dump(subs,open("build/subs.json","w"),ensure_ascii=False,indent=1)
cues=json.load(open("sfx/cues.json"))
inp=[];fc=[]
for j,(f,s,d,_) in enumerate(fitted):
    inp+=["-i",f]; fc.append(f"[{j}]adelay={int(s*1000)}|{int(s*1000)},apad=whole_dur=120[v{j}]")
fc.append("".join(f"[v{j}]" for j in range(5))+"amix=inputs=5:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11,asplit=2[vo][sc]")
base=len(fitted)
for k,c in enumerate(cues):
    inp+=["-i","sfx/"+c["file"]]; fc.append(f"[{base+k}]volume={c['gain_db']}dB,adelay={int(c['start']*1000)}|{int(c['start']*1000)},apad=whole_dur=120[s{k}]")
fc.append("".join(f"[s{k}]" for k in range(len(cues)))+f"amix=inputs={len(cues)}:normalize=0,volume=6dB[sfx]")
fc.append("[sfx][sc]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=450[duck]")
fc.append("[vo][duck]amix=inputs=2:normalize=0,alimiter=limit=0.89,atrim=0:120[out]")
run(["ffmpeg","-v","error","-y",*inp,"-filter_complex",";".join(fc),"-map","[out]","-ar","48000","-ac","2","build/mix.wav"])
run(["ffmpeg","-v","error","-y","-i","build/mix.wav","-c:a","aac","-b:a","192k","build/mix.m4a"])
run(["ffmpeg","-v","error","-y","-i","build/mix.wav","-c:a","libmp3lame","-b:a","112k","build/mix.mp3"])
b64="data:audio/mpeg;base64,"+base64.b64encode(open("build/mix.mp3","rb").read()).decode()
h=open("src/template.html").read().replace('"__AUDIO__"',json.dumps(b64)).replace("__SUBS__",json.dumps(subs,ensure_ascii=False))
open("index.html","w").write(h)
h2=open("src/template.html").read().replace('"__AUDIO__"','""').replace("__SUBS__",json.dumps(subs,ensure_ascii=False))
open("build/render.html","w").write(h2)
print("mix",dur("build/mix.wav"),"s; subs",len(subs))
