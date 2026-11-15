# Placeholder procedural SFX stems (swap any file for an ElevenLabs SFX of the same name).
import numpy as np, wave, json, os
SR=44100; rng=np.random.default_rng(7); OUT="sfx"
def band(x,lo,hi):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); m=((f>=lo)&(f<=hi)).astype(float)
    # soft edges
    m=np.convolve(m,np.ones(50)/50,mode="same"); return np.fft.irfft(X*m,len(x))
def noise(d): return rng.standard_normal(int(d*SR))
def env(d,pts):
    t=np.arange(int(d*SR))/SR; a,b=zip(*pts); return np.interp(t,a,b)
def norm(x,peak=0.8): return x/ (np.max(np.abs(x))+1e-9)*peak
def save(name,x):
    x=np.clip(x,-1,1); y=(x*32767).astype(np.int16)
    st=np.stack([y,y],1) if y.ndim==1 else y
    with wave.open(f"{OUT}/{name}.wav","wb") as w: w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes(st.tobytes())
def lfo(d,hz,depth): t=np.arange(int(d*SR))/SR; return 1-depth/2+depth/2*np.sin(2*np.pi*hz*t+rng.random()*6)
t_=lambda d: np.arange(int(d*SR))/SR
cues=[]
def cue(name,start,gain,x):
    save(name,norm(x)); cues.append({"file":f"{name}.wav","start":start,"gain_db":gain})

# --- scene 1
d=25; x=band(noise(d),30,180)*lfo(d,0.07,0.5)+0.3*np.sin(2*np.pi*55*t_(d))*0.05
cue("s1_space_hum",0,-30,x*env(d,[(0,0),(2,1),(23,1),(25,0)]))
def clunk(d=1.2,f0=70):
    t=t_(d); return (np.sin(2*np.pi*f0*t)*np.exp(-t*9)+0.6*band(noise(d),200,2500)*np.exp(-t*30)+0.3*np.sin(2*np.pi*f0*2.7*t)*np.exp(-t*14))
def servo(d=1.5,f=240):
    t=t_(d); fm=f*(1+0.25*np.sin(np.pi*t/d)); ph=np.cumsum(fm)/SR
    return (np.sign(np.sin(2*np.pi*ph))*0.3+np.sin(2*np.pi*ph))*env(d,[(0,0),(0.1,1),(d-0.15,1),(d,0)])
x=np.concatenate([servo(1.4,180),clunk(1.0,60)]); cue("s1_door_open",1.4,-22,x)
cue("s1_door_close",9.8,-22,np.concatenate([servo(1.2,200),clunk(1.0,55)]))
d=10; x=np.zeros(int(d*SR))
for i in range(26):
    s=int(i*0.26*SR); p=band(noise(0.35),800,6000)*np.exp(-t_(0.35)*14)
    x[s:s+len(p)]+=p*(0.6+0.4*rng.random())
cue("s1_satellite_puffs",2.8,-26,x)
d=9; t=t_(d); x=band(noise(d),25,400)*env(d,[(0,0),(0.25,1),(6.5,0.9),(9,0)])+0.4*band(noise(d),400,2000)*env(d,[(0,0),(0.2,0.6),(1,0.25),(6.5,0)])
cue("s1_engine_ignite_burn",14.0,-20,x[:len(t)])
# --- scene 2
d=31; x=(band(noise(d),40,900)*lfo(d,0.6,0.35)+0.5*band(noise(d),900,4000)*lfo(d,1.7,0.6))*env(d,[(0,0),(1.5,0.4),(5,1),(19,1),(28,0.25),(31,0)])
cue("s2_reentry_roar",24.6,-19,x)
d=29; x=np.zeros(int(d*SR))
for k in np.arange(1.0,27,2.4):
    s=servo(0.7,320+60*rng.random()); i=int(k*SR); x[i:i+len(s)]+=s*0.8
cue("s2_flap_servos",26,-30,x)
# --- scene 3
d=12; cue("s3_cloud_wind",54.6,-22,band(noise(d),150,2500)*lfo(d,0.4,0.6)*env(d,[(0,0),(1,1),(5,0.8),(8,0.2),(12,0)]))
d=27; t=t_(d); w=band(noise(d),100,1800)*(0.55+0.45*np.sin(2*np.pi*0.13*t)**2)
cue("s3_ocean_waves",57,-28,w*env(d,[(0,0),(3,1),(26,1),(27,0)]))
d=24.5; x=band(noise(d),20,600)+0.5*band(noise(d),600,3500)*lfo(d,8,0.3)
cue("s3_raptor_flip_roar",61.0,-16,x*env(d,[(0,0),(0.15,1),(2.5,1),(4,0.75),(23.5,0.75),(24.5,0.6)]))
# --- scene 4
d=16.6; x=band(noise(d),20,700)+0.4*band(noise(d),700,3000)
cue("s4_engines_smoke",84.4,-17,x*env(d,[(0,0),(0.8,0.7),(14,0.8),(15.9,0.8),(16.6,0)]))
x=np.concatenate([servo(2.4,140),np.zeros(int(0.1*SR))]); cue("s4_tower_arms",98.0,-20,x)
d=2.5; t=t_(d); x=np.zeros(int(d*SR))
for f,a in [(180,1),(431,0.6),(977,0.4),(1630,0.25)]: x+=a*np.sin(2*np.pi*f*t)*np.exp(-t*(4+f/400))
x+=band(noise(d),300,5000)*np.exp(-t*25)*0.8
cue("s4_catch_clank",100.4,-14,x)
d=3; cue("s4_engine_cutoff",100.8,-20,band(noise(d),20,500)*env(d,[(0,1),(0.3,0.5),(3,0)]))
# --- scene 5
d=19; cue("s5_steam_hiss",102,-30,band(noise(d),2500,9000)*lfo(d,0.3,0.6)*env(d,[(0,0),(2,1),(18,1),(19,0)]))
d=20; cue("s5_breeze",100,-32,band(noise(d),120,1200)*lfo(d,0.15,0.7)*env(d,[(0,0),(3,1),(19,1),(20,0)]))
d=10.5; t=t_(d); x=np.zeros(len(t))
for f in [130.81,196.0,261.63,329.63,392.0]:
    x+=np.sin(2*np.pi*f*t+0.002*np.sin(2*np.pi*4*t))+0.3*np.sin(2*np.pi*f*2.003*t)
cue("s5_triumphant_swell",109.5,-24,x*env(d,[(0,0),(4,0.8),(8,1),(10.5,0)]))
json.dump(cues,open(f"{OUT}/cues.json","w"),indent=1,ensure_ascii=False)
print(len(cues),"cues")
