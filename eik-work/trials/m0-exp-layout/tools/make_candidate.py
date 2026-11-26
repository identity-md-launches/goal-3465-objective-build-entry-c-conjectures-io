import re
src=open('eik-work/baselines/former-50/entry.c').read()
m=re.search(r'static const struct t_ep t_eps\[\]=\{\n(.*?)\n\};',src,re.S)
rows=m.group(1).split('\n')
aux=[]
for r in rows[:512]:
    mm=re.fullmatch(r'\{(\d+)u,(\d+)u,(\d+)u,(\d+)u\},?',r)
    assert mm,r
    aux.append(mm.group(4)+'u')
assert len(aux)==512
bank='static const uint32_t t_hb[512]={\n'+',\n'.join(','.join(aux[i:i+8]) for i in range(0,512,8))+'};\n'
def rep(old,new,cnt=1):
    global src
    assert src.count(old)==cnt,(old,src.count(old))
    src=src.replace(old,new)
rep('struct t_ep {uint32_t t_q,t_v,t_p,t_aux;};\n','struct t_ep {uint32_t t_q,t_v,t_p,t_aux;};\n'+bank)
rep('uint32_t Th = *((const uint32_t *) (((const uint8_t *) (&t_eps[0].t_aux)) + ((((uint32_t) kp) << 23) >> 19)));','uint32_t Th = t_hb[((uint32_t) kp) & 511u];')
rep('uint32_t Th = *((const uint32_t *) (((const uint8_t *) (&t_eps[0].t_aux)) + (n >> 19)));','uint32_t Th = t_hb[n >> 23];')
rep('uint32_t Tn = *((const uint32_t *) (((const uint8_t *) (&t_eps[0].t_aux)) + (m << 4)));','uint32_t Tn = t_hb[m];')
rep('uint32_t t_T = *((const uint32_t *) (((const uint8_t *) (&(*(&t_eps[0])).t_aux)) + ((t_kb & 511u) << 4)));','uint32_t t_T = t_hb[t_kb & 511u];')
rep('uint32_t t_T = *((const uint32_t *) (t_tb + (t_kb >> 19)));','uint32_t t_T = t_hb[t_kb >> 23];',2)
open('eik-work/trials/m0-exp-layout/entry.c','w').write(src)
