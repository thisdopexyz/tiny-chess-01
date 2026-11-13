import urllib.request as u,json,os,sys
E=os.environ.get;U=E("MAKEFUN_ENV_URL")
def post(p,o):
 r=u.Request(U+p,json.dumps(o).encode(),{"Content-Type":"application/json"})
 with u.urlopen(r)as f:return json.loads(f.read())

P,N,B,R,Q,K=1,2,3,4,5,6
V=[0,100,320,330,500,900,20000]
INF=10**9

def N2(s):return(8-int(s[1]))*16+(ord(s[0])-97)
def S2(i):return"abcdefgh"[i&7]+str(8-(i>>4))

def parse(fen):
 b=[0]*128;p=fen.split();w,tm,cs,ep=p[0],p[1],p[2],p[3]
 for r,row in enumerate(w.split('/')):
  f=0
  for c in row:
   if c.isdigit():f+=int(c)
   else:
    j="PNBRQKpnbrqk".index(c);pc=j%6+1
    b[r*16+f]=pc if j<6 else -pc;f+=1
 ca=0
 for k,v in(('K',1),('Q',2),('k',4),('q',8)):
  if k in cs:ca|=v
 return b,0 if tm=='w' else 1,ca,(-1 if ep=='-' else N2(ep))

def att(b,sq,side):
 o=1-side
 if side==0:
  for d in(-15,-17):
   t=sq+d
   if not(t&0x88)and b[t]==-1:return 1
 else:
  for d in(15,17):
   t=sq+d
   if not(t&0x88)and b[t]==1:return 1
 for d in(-33,-31,-18,-14,14,18,31,33):
  t=sq+d
  if not(t&0x88)and b[t]==(-2 if side==0 else 2):return 1
 for d in(-17,-15,15,17,-16,-1,1,16):
  t=sq+d
  while not(t&0x88):
   p=b[t]
   if p:
    ap=p if p>0 else -p;c=0 if p>0 else 1
    if c==o:
     if ap==6 or ap==5:return 1
     if ap==4 and abs(d)in(16,1):return 1
     if ap==3 and abs(d)in(17,15):return 1
    break
   t+=d
 return 0

def in_chk(b,side):
 k=6 if side==0 else -6
 for i in range(128):
  if not(i&0x88)and b[i]==k:return att(b,i,side)
 return 0

def make(b,tm,ca,ep,m):
 a=b[:];f,t,pr=m;p=a[f];a[f]=0;a[t]=p
 nca=ca;ne=-1
 if p==6:nca&=~3
 if p==-6:nca&=~12
 if f==112 or t==112:nca&=~2
 if f==119 or t==119:nca&=~1
 if f==0 or t==0:nca&=~8
 if f==7 or t==7:nca&=~4
 if abs(p)==1 and t==ep and ep!=-1:
  a[t+(16 if tm==0 else -16)]=0
 if p==1 and f-t==32:ne=f-16
 if p==-1 and t-f==32:ne=f+16
 if pr:a[t]=pr if tm==0 else -pr
 if p==6 and f==116:
  if t==118:a[119]=0;a[117]=4
  if t==114:a[112]=0;a[115]=4
 if p==-6 and f==4:
  if t==6:a[7]=0;a[5]=-4
  if t==2:a[0]=0;a[3]=-4
 return a,1-tm,nca,ne

def gen(b,tm,ca,ep):
 ms=[];mine=lambda p:(p>0)==(tm==0)
 for i in range(128):
  if i&0x88:continue
  p=b[i]
  if not p or not mine(p):continue
  ap=p if p>0 else -p
  if ap==1:
   d=-16 if tm==0 else 16;st=6 if tm==0 else 1;pm=0 if tm==0 else 7
   t=i+d
   if not(t&0x88)and b[t]==0:
    if (t>>4)==pm:
     for pr in(5,4,3,2):ms.append((i,t,pr))
    else:
     ms.append((i,t,0))
     if (i>>4)==st and b[i+2*d]==0:ms.append((i,i+2*d,0))
   for dc in(-1,1):
    t=i+d+dc
    if t&0x88:continue
    if(b[t] and not mine(b[t]))or t==ep:
     if (t>>4)==pm:
      for pr in(5,4,3,2):ms.append((i,t,pr))
     else:ms.append((i,t,0))
  elif ap==2:
   for d in(-33,-31,-18,-14,14,18,31,33):
    t=i+d
    if not(t&0x88)and(b[t]==0 or not mine(b[t])):ms.append((i,t,0))
  elif ap==6:
   for d in(-17,-15,15,17,-16,-1,1,16):
    t=i+d
    if not(t&0x88)and(b[t]==0 or not mine(b[t])):ms.append((i,t,0))
  else:
   dr=[]
   if ap in(3,5):dr+=(-17,-15,15,17)
   if ap in(4,5):dr+=(-16,-1,1,16)
   for d in dr:
    t=i+d
    while not(t&0x88):
     if b[t]==0:ms.append((i,t,0))
     else:
      if not mine(b[t]):ms.append((i,t,0))
      break
     t+=d
 if tm==0:
  if ca&1 and b[116]==6 and b[117]==0==b[118] and b[119]==4 and not att(b,116,0)and not att(b,117,0)and not att(b,118,0):ms.append((116,118,0))
  if ca&2 and b[116]==6 and b[115]==0==b[114]==b[113] and b[112]==4 and not att(b,116,0)and not att(b,115,0)and not att(b,114,0):ms.append((116,114,0))
 else:
  if ca&4 and b[4]==-6 and b[5]==0==b[6] and b[7]==-4 and not att(b,4,1)and not att(b,5,1)and not att(b,6,1):ms.append((4,6,0))
  if ca&8 and b[4]==-6 and b[3]==0==b[2]==b[1] and b[0]==-4 and not att(b,4,1)and not att(b,3,1)and not att(b,2,1):ms.append((4,2,0))
 out=[]
 for m in ms:
  b2,nt,nc,ne=make(b,tm,ca,ep,m)
  if not in_chk(b2,tm):out.append(m)
 return out

def m2s(m):s=S2(m[0])+S2(m[1]);return s+" nbrq"[m[2]] if m[2]else s

def ev(b):
 s=0
 for i in range(128):
  if i&0x88:continue
  p=b[i]
  if not p:continue
  ap=p if p>0 else -p;v=V[ap];r=i>>4;f=i&7
  if ap==1:
   rk=r if p<0 else 7-r;v+=rk*8
   if 2<=f<=5:v+=4
  elif ap==2:v+=(3-abs(3-f)-abs(3-r))*3
  elif ap in(3,4):v+=(3-abs(3-f)-abs(3-r))
  elif ap==5:v+=(3-abs(3-f)-abs(3-r))*1
  s+=v if p>0 else -v
 return s

def ok(b,tm,ep,m):return b[m[1]] or m[2] or (abs(b[m[0]])==1 and m[1]==ep)

def order(b,tm,ep,m):
 s=0
 if b[m[1]]:s+=10*abs(b[m[1]])-abs(b[m[0]])
 if m[2]:s+=90
 if abs(b[m[0]])==1 and m[1]==ep:s+=10
 return -s

def q(b,tm,ca,ep,a,be):
 st=ev(b) if tm==0 else -ev(b)
 if st>=be:return be
 if st>a:a=st
 ms=[m for m in gen(b,tm,ca,ep) if ok(b,tm,ep,m)]
 ms.sort(key=lambda m:order(b,tm,ep,m))
 for m in ms:
  b2,nt,nc,ne=make(b,tm,ca,ep,m)
  sc=-q(b2,nt,nc,ne,-be,-a)
  if sc>=be:return be
  if sc>a:a=sc
 return a

def search(b,tm,ca,ep,d,a,be):
 ms=gen(b,tm,ca,ep)
 if not ms:return (-INF+50) if in_chk(b,tm) else 0
 ms.sort(key=lambda m:order(b,tm,ep,m))
 best=-INF
 for m in ms:
  b2,nt,nc,ne=make(b,tm,ca,ep,m)
  sc=-q(b2,nt,nc,ne,-be,-a) if d<=1 else -search(b2,nt,nc,ne,d-1,-be,-a)
  if sc>best:best=sc
  if sc>a:a=sc
  if a>=be:break
 return best

def pick(b,tm,ca,ep,legal):
 ms=gen(b,tm,ca,ep)
 if legal:
  ls=set(legal);f=[m for m in ms if m2s(m) in ls]
  if f:ms=f
 if not ms:return legal[0] if legal else "0000"
 ms.sort(key=lambda m:order(b,tm,ep,m))
 D=3;best=-INF;bm=ms[0];a=-INF;be=INF
 for m in ms:
  b2,nt,nc,ne=make(b,tm,ca,ep,m)
  sc=-search(b2,nt,nc,ne,D-1,-be,-a)
  if sc>best:best=sc;bm=m
  if sc>a:a=sc
 return m2s(bm)

def play():
 g=post("/game",{})
 while 1:
  st=g.get("status")
  if st=="done":
   print(f"done: {g.get('wins')} won, {g.get('draws')} drawn, {g.get('losses')} lost",file=sys.stderr);return
  if st=="your_move":
   b,tm,ca,ep=parse(g["fen"]);mv=pick(b,tm,ca,ep,g.get("legal_moves")or[])
   g=post("/move",{"game":g["game"],"move":mv})
  else:
   g=post("/game",{})

if __name__=="__main__":play()
