; Allocated executable sections; ARM mapping-symbol literal pools are data.

eik_sigmoid:
00023ed4: push       {r4, r5, r7, lr}
00023ed6: add        r7, sp, #8
00023ed8: lsls       r1, r0, #1
00023eda: cmp.w      r1, #-1
00023ede: ble        #0x23f3e
00023ee0: sbfx       r1, r0, #0x17, #8
00023ee4: cmp        r1, #0x7d
00023ee6: blt        #0x23f9a
00023ee8: movw       r5, #0x4e0
00023eec: movt       r5, #1
00023ef0: ldm.w      r5, {r1, r2, r4}
00023ef4: ldrd       r3, r5, [r5, #0xc]
00023ef8: subs       r3, r3, r0
00023efa: bmi.w      #0x2406e
00023efe: mvn        r2, #0xf
00023f02: and.w      r2, r2, r3, lsr #12
00023f06: subs       r5, r5, r2
00023f08: ldrd       r2, r4, [r5]
00023f0c: ldr        r3, [r5, #8]
00023f0e: subs       r4, #0x80
00023f10: uxth       r5, r0
00023f12: mls        r3, r3, r5, r2
00023f16: uxtb       r2, r2
00023f18: asrs       r3, r3, #0xf
00023f1a: muls       r3, r5, r3
00023f1c: add.w      r3, r4, r3, asr #15
00023f20: mla        r2, r2, r5, r3
00023f24: tst.w      r2, #0x1fc
00023f28: itt        ne
00023f2a: addne.w    r0, r1, r2, asr #9
00023f2e: popne      {r4, r5, r7, pc}
00023f30: movw       r1, #0xfff8
00023f34: movt       r1, #0x17ff
00023f38: add.w      r1, r1, r2, asr #4
00023f3c: b          #0x241a6
00023f3e: cmp        r0, #0
00023f40: bmi        #0x24012
00023f42: movw       r5, #0x144
00023f46: movt       r5, #1
00023f4a: ldrd       r2, r1, [r5]
00023f4e: subs       r2, r2, r0
00023f50: bmi.w      #0x240bc
00023f54: mvn        r3, #0xf
00023f58: and.w      r2, r3, r2, lsr #12
00023f5c: subs       r5, r1, r2
00023f5e: ldr        r1, [r5]
00023f60: ldr        r2, [r5, #8]
00023f62: uxth       r3, r0
00023f64: uxtb       r4, r1
00023f66: mls        r4, r4, r3, r2
00023f6a: ldr        r5, [r5, #4]
00023f6c: lsrs       r4, r4, #0xf
00023f6e: mls        r1, r4, r3, r1
00023f72: uxth       r2, r2
00023f74: lsrs       r1, r1, #0xf
00023f76: mla        r2, r2, r3, r5
00023f7a: muls       r1, r3, r1
00023f7c: add.w      r1, r2, r1, lsr #15
00023f80: mvn        r2, #0xbf
00023f84: add.w      r1, r2, r1, lsr #2
00023f88: lsls       r2, r1, #0x18
00023f8a: lsr.w      r1, r1, #8
00023f8e: beq.w      #0x2419a
00023f92: add.w      r0, r1, #0x3f400000
00023f96: adds       r0, #1
00023f98: pop        {r4, r5, r7, pc}
00023f9a: cmp        r1, #0x73
00023f9c: bgt        #0x23fd0
00023f9e: cmp        r1, #0x67
00023fa0: itt        lt
00023fa2: movlt.w    r0, #0x3f000000
00023fa6: poplt      {r4, r5, r7, pc}
00023fa8: mov        r2, r0
00023faa: movw       r3, #0xffff
00023fae: rsb        r1, r1, r0, asr #31
00023fb2: bfc        r2, #0x17, #9
00023fb6: movt       r3, #0x7f
00023fba: adds       r1, #0x7f
00023fbc: add        r2, r3
00023fbe: lsr.w      r1, r2, r1
00023fc2: eor.w      r0, r1, r0, asr #31
00023fc6: add.w      r0, r0, #0x7e000000
00023fca: adds       r0, #1
00023fcc: asrs       r0, r0, #1
00023fce: pop        {r4, r5, r7, pc}
00023fd0: cmp        r1, #0x79
00023fd2: bhi        #0x240cc
00023fd4: rsb.w      r1, r1, #0x79
00023fd8: lsls       r2, r1, #0x1e
00023fda: add.w      r2, r2, r0, lsl #7
00023fde: lsrs       r2, r1
00023fe0: lsrs       r1, r2, #0xf
00023fe2: movw       r3, #0xaaa7
00023fe6: muls       r3, r1, r3
00023fe8: lsrs       r3, r3, #0x10
00023fea: muls       r3, r1, r3
00023fec: lsrs       r3, r3, #0x10
00023fee: muls       r1, r3, r1
00023ff0: cmp.w      r0, r2, lsr #15
00023ff4: sub.w      r1, r2, r1, lsr #14
00023ff8: bge.w      #0x24256
00023ffc: tst.w      r1, #0xff0
00024000: beq.w      #0x243f2
00024004: movs       r0, #1
00024006: movt       r0, #0xfc00
0002400a: sub.w      r0, r0, r1, lsr #11
0002400e: lsrs       r0, r0, #2
00024010: pop        {r4, r5, r7, pc}
00024012: movw       r5, #0x4cc
00024016: movt       r5, #1
0002401a: ldrd       r1, r2, [r5]
0002401e: subs       r3, r0, r2
00024020: bhs.w      #0x24134
00024024: asrs       r2, r3, #0x10
00024026: add.w      r5, r1, r2, lsl #4
0002402a: ldr        r1, [r5]
0002402c: ldr        r2, [r5, #8]
0002402e: uxth       r3, r0
00024030: uxtb       r4, r1
00024032: mls        r4, r4, r3, r2
00024036: ldr        r5, [r5, #4]
00024038: lsrs       r4, r4, #0xf
0002403a: mls        r1, r4, r3, r1
0002403e: uxth       r2, r2
00024040: lsrs       r1, r1, #0xf
00024042: mla        r2, r2, r3, r5
00024046: muls       r1, r3, r1
00024048: add.w      r1, r2, r1, lsr #15
0002404c: mvn        r2, #0x86
00024050: add.w      r2, r2, r1, lsl #1
00024054: cmp        r2, #0
00024056: bmi.w      #0x2433e
0002405a: uxtb       r3, r2
0002405c: cmp        r3, #0xf8
0002405e: bhi.w      #0x24384
00024062: movs       r0, #1
00024064: movt       r0, #0x3e00
00024068: sub.w      r0, r0, r2, lsr #8
0002406c: pop        {r4, r5, r7, pc}
0002406e: and.w      r1, r4, r3, lsr #12
00024072: subs       r5, r5, r1
00024074: ldr        r3, [r5]
00024076: ldr        r4, [r5, #8]
00024078: uxth       r1, r0
0002407a: mls        r4, r4, r1, r3
0002407e: ldr        r5, [r5, #4]
00024080: asrs       r4, r4, #0xf
00024082: muls       r4, r1, r4
00024084: uxtb       r3, r3
00024086: add.w      r5, r5, r4, asr #15
0002408a: mla        r1, r3, r1, r5
0002408e: cmp        r1, #0
00024090: bmi.w      #0x241ce
00024094: movs       r3, #0x81
00024096: add.w      r3, r3, r1, lsl #1
0002409a: cmp        r3, #0
0002409c: bmi.w      #0x2432a
000240a0: uxtb       r1, r3
000240a2: cmp        r1, #6
000240a4: lsr.w      r4, r3, #8
000240a8: bhi.w      #0x241da
000240ac: movw       r1, #0xfff8
000240b0: movt       r1, #0x17ff
000240b4: add.w      r1, r1, r3, lsr #5
000240b8: adds       r1, #0xc
000240ba: b          #0x24362
000240bc: movs       r3, #0xf8
000240be: add.w      r2, r3, r2, asr #22
000240c2: cmp        r2, #0xf6
000240c4: bhi.w      #0x241de
000240c8: ldr        r0, [r1, #0x10]
000240ca: pop        {r4, r5, r7, pc}
000240cc: movw       r5, #0x3284
000240d0: movt       r5, #1
000240d4: ldrd       r1, r2, [r5]
000240d8: and.w      r2, r2, r0, lsr #16
000240dc: adds       r5, r1, r2
000240de: ldm.w      r5, {r1, r2, r3}
000240e2: ubfx       r5, r0, #5, #0xf
000240e6: uxtb       r4, r3
000240e8: smlabb     r3, r4, r5, r3
000240ec: lsrs       r3, r3, #0xd
000240ee: uxth       r4, r1
000240f0: mls        r1, r3, r5, r1
000240f4: muls       r4, r0, r4
000240f6: asrs       r1, r1, #0xe
000240f8: add.w      r2, r2, r4, lsr #4
000240fc: muls       r1, r5, r1
000240fe: cmp        r0, r5
00024100: add.w      r1, r2, r1, asr #14
00024104: bge.w      #0x24240
00024108: movw       r2, #0x4a07
0002410c: movt       r2, #0x3ef0
00024110: subs       r1, r2, r1
00024112: tst.w      r1, #0x3f8
00024116: itt        ne
00024118: addne.w    r0, r2, r1, asr #10
0002411c: popne      {r4, r5, r7, pc}
0002411e: sub.w      r3, r1, #8
00024122: add.w      r4, r2, r3, asr #10
00024126: movw       r2, #0x5f98
0002412a: movt       r2, #0x10fb
0002412e: sub.w      r1, r2, r1, asr #6
00024132: b          #0x2445e
00024134: lsrs       r2, r3, #0x10
00024136: cmp        r2, #0x82
00024138: bhi.w      #0x2426e
0002413c: movw       r5, #0x4d4
00024140: movt       r5, #1
00024144: ldr        r3, [r5, #8]
00024146: ldrd       r1, r4, [r5]
0002414a: mla        r5, r1, r2, r3
0002414e: mov        r2, r4
00024150: ldrd       r1, r4, [r5]
00024154: ldr        r3, [r5, #8]
00024156: sxth       r5, r0
00024158: eors       r2, r5
0002415a: uxtb       r5, r3
0002415c: mls        r3, r5, r2, r3
00024160: lsrs       r3, r3, #0xe
00024162: muls       r3, r2, r3
00024164: sub.w      r3, r1, r3, asr #11
00024168: lsrs       r5, r3, #0x10
0002416a: muls       r5, r2, r5
0002416c: uxth       r3, r3
0002416e: muls       r2, r3, r2
00024170: subs       r3, r5, r4
00024172: add.w      r2, r3, r2, asr #16
00024176: cmp.w      r2, #-1
0002417a: ble.w      #0x2440a
0002417e: uxtb       r3, r2
00024180: mov.w      r5, #0x3800000
00024184: cmp        r3, #0xa
00024186: and.w      r1, r5, r1, lsl #23
0002418a: blo.w      #0x24436
0002418e: sub.w      r0, r1, r2, lsr #8
00024192: add.w      r0, r0, #0x3a800000
00024196: adds       r0, #1
00024198: pop        {r4, r5, r7, pc}
0002419a: movw       r2, #0xfff8
0002419e: movt       r2, #0x17ff
000241a2: add.w      r1, r2, r1, lsl #5
000241a6: add.w      r4, r1, #0x18
000241aa: mvn        r1, #0x76
000241ae: lsls       r2, r0, #9
000241b0: add.w      r3, r1, r0, lsr #23
000241b4: movw       r0, #0x329c
000241b8: movt       r0, #1
000241bc: mov        r1, r4
000241be: bl         #0x250cc
000241c2: add.w      r0, r0, r4, lsr #5
000241c6: add.w      r0, r0, #0x3e800000
000241ca: adds       r0, #1
000241cc: pop        {r4, r5, r7, pc}
000241ce: uxtb       r3, r1
000241d0: cmp        r3, #3
000241d2: asr.w      r4, r1, #8
000241d6: blo.w      #0x24358
000241da: subs       r0, r2, r4
000241dc: pop        {r4, r5, r7, pc}
000241de: cmp.w      r0, #0x7f800000
000241e2: itt        hi
000241e4: orrhi      r0, r0, #0x400000
000241e8: pophi      {r4, r5, r7, pc}
000241ea: movw       r2, #0xa122
000241ee: movt       r2, #0x418a
000241f2: cmp        r0, r2
000241f4: itt        hi
000241f6: movhi.w    r0, #0x3f800000
000241fa: pophi      {r4, r5, r7, pc}
000241fc: add.w      r2, r0, #-0x48000000
00024200: add.w      r2, r2, #0x6a80000
00024204: mvn        r3, #0xf
00024208: and.w      r2, r3, r2, lsr #11
0002420c: add        r1, r2
0002420e: movw       r2, #0xdb50
00024212: movt       r2, #0xffff
00024216: ldr        r1, [r1, r2]
00024218: movw       r2, #0x14c
0002421c: ubfx       r1, r1, #8, #7
00024220: movt       r2, #1
00024224: add.w      r2, r2, r1, lsl #4
00024228: ldr.w      r2, [r2, #0x20c]
0002422c: cmp        r0, r2
0002422e: mov.w      r0, #0
00024232: it         lo
00024234: movlo.w    r0, #-1
00024238: subs       r0, r0, r1
0002423a: add.w      r0, r0, #0x3f800000
0002423e: pop        {r4, r5, r7, pc}
00024240: tst.w      r1, #0x7f8
00024244: beq.w      #0x24392
00024248: movw       r0, #0xfcf4
0002424c: movt       r0, #0x3eff
00024250: add.w      r0, r0, r1, lsr #11
00024254: pop        {r4, r5, r7, pc}
00024256: movw       r3, #0x1ff0
0002425a: tst        r1, r3
0002425c: beq.w      #0x243a0
00024260: movs       r0, #1
00024262: movt       r0, #0x7e00
00024266: add.w      r0, r0, r1, lsr #13
0002426a: lsrs       r0, r0, #1
0002426c: pop        {r4, r5, r7, pc}
0002426e: movw       r2, #0xffff
00024272: movt       r2, #0x7f
00024276: add.w      r2, r2, #0x1c00000
0002427a: cmp        r3, r2
0002427c: bls        #0x2429c
0002427e: mvn        r2, #9
00024282: add.w      r2, r2, r3, lsr #22
00024286: cmp        r2, #0xf2
00024288: itt        lo
0002428a: movlo      r0, #0
0002428c: poplo      {r4, r5, r7, pc}
0002428e: movw       r2, #0xac50
00024292: movt       r2, #0xc2ae
00024296: cmp        r0, r2
00024298: bhs.w      #0x24476
0002429c: movs       r1, #0x7f
0002429e: movw       r5, #0x328c
000242a2: add.w      r3, r1, r0, asr #23
000242a6: movt       r5, #1
000242aa: ldm        r5, {r1, r2, r4, r5}
000242ac: ands       r4, r0
000242ae: add        r1, r4
000242b0: lsls       r1, r3
000242b2: lsrs       r3, r1, #0xa
000242b4: muls       r2, r3, r2
000242b6: lsrs       r3, r1, #0xf
000242b8: orr.w      r3, r3, r1, lsl #19
000242bc: ldm        r5, {r1, r4, r5}
000242be: sub.w      r4, r4, r2, lsr #16
000242c2: mla        r1, r4, r1, r3
000242c6: smultt     r2, r1, r1
000242ca: sub.w      r3, r1, r2, lsr #9
000242ce: movw       r1, #0x1ff0
000242d2: and.w      r1, r1, r4, lsl #4
000242d6: ldr        r2, [r5, r1]
000242d8: lsrs       r1, r4, #9
000242da: asrs       r5, r3, #8
000242dc: lsrs       r4, r2, #0x18
000242de: muls       r5, r4, r5
000242e0: ubfx       r4, r2, #8, #0x10
000242e4: asrs       r3, r3, #0x10
000242e6: muls       r3, r4, r3
000242e8: add.w      r3, r5, r3, asr #8
000242ec: movw       r5, #0x7218
000242f0: movt       r5, #0xc1b1
000242f4: asrs       r3, r3, #8
000242f6: cmp        r0, r5
000242f8: sub.w      r2, r2, r3
000242fc: bhi        #0x243fa
000242fe: subs       r2, #0x84
00024300: rsb.w      r3, r1, #0x7d
00024304: lsr.w      r3, r2, r3
00024308: cmp.w      r3, #0x10000
0002430c: bhs.w      #0x244a4
00024310: lsrs       r5, r2, #0x10
00024312: muls       r3, r5, r3
00024314: sub.w      r2, r2, r3, lsr #16
00024318: cmp        r2, #0
0002431a: bpl.w      #0x244c2
0002431e: adds       r2, #0x80
00024320: uxtb       r3, r2
00024322: cmp        r3, #5
00024324: bhs.w      #0x24514
00024328: b          #0x2451c
0002432a: adds       r1, #0xa0
0002432c: tst.w      r1, #0x3c
00024330: beq.w      #0x24448
00024334: mov.w      r0, #0x3f000000
00024338: sub.w      r0, r0, r1, lsr #6
0002433c: pop        {r4, r5, r7, pc}
0002433e: mvn        r2, #0x7f
00024342: add.w      r2, r2, r1, lsl #2
00024346: uxtb       r3, r2
00024348: cmp        r3, #0x14
0002434a: blo        #0x24412
0002434c: movs       r0, #3
0002434e: movt       r0, #0x3d80
00024352: sub.w      r0, r0, r2, lsr #8
00024356: pop        {r4, r5, r7, pc}
00024358: movs       r2, #8
0002435a: movt       r2, #0x800
0002435e: add.w      r1, r2, r1, lsr #4
00024362: movs       r3, #0x89
00024364: lsls       r2, r0, #9
00024366: add.w      r3, r3, r0, asr #23
0002436a: movw       r0, #0x329c
0002436e: movt       r0, #1
00024372: bl         #0x250cc
00024376: movw       r1, #0xffff
0002437a: add        r0, r4
0002437c: movt       r1, #0x3e7f
00024380: subs       r0, r1, r0
00024382: pop        {r4, r5, r7, pc}
00024384: movw       r2, #0xfff8
00024388: movt       r2, #0x17ff
0002438c: add.w      r1, r2, r1, lsr #5
00024390: b          #0x24456
00024392: movw       r2, #0x9e70
00024396: movt       r2, #0xfff
0002439a: add.w      r4, r2, r1, lsr #6
0002439e: b          #0x241aa
000243a0: mul        r3, r0, r0
000243a4: cmp        r3, #5
000243a6: bne        #0x243f2
000243a8: movw       r2, #0x4f4
000243ac: uxtb       r1, r0
000243ae: movt       r2, #1
000243b2: add.w      r5, r2, r1, lsl #4
000243b6: mov        r4, r0
000243b8: bl         #0x24ec8
000243bc: mov        r2, r0
000243be: mov        r0, r4
000243c0: lsrs       r1, r4, #3
000243c2: movs       r4, #1
000243c4: cmp        r2, #0x20
000243c6: mov.w      r3, #0
000243ca: bgt.w      #0x244ee
000243ce: cmp        r2, #0x16
000243d0: ble.w      #0x24524
000243d4: cmp        r2, #0x18
000243d6: ble.w      #0x2456e
000243da: cmp        r2, #0x19
000243dc: beq.w      #0x23ef0
000243e0: cmp        r2, #0x1f
000243e2: beq.w      #0x240de
000243e6: cmp        r2, #0x20
000243e8: mov.w      r4, #0
000243ec: beq.w      #0x242ae
000243f0: b          #0x2401a
000243f2: pop.w      {r4, r5, r7, lr}
000243f6: b.w        #0x24fc4
000243fa: cmp.w      r2, #-1
000243fe: ble        #0x244d8
00024400: subs       r2, #0x42
00024402: pop.w      {r4, r5, r7, lr}
00024406: b.w        #0x25034
0002440a: pop.w      {r4, r5, r7, lr}
0002440e: b.w        #0x24d80
00024412: movw       r2, #0xfff8
00024416: movt       r2, #0x17ff
0002441a: add.w      r1, r2, r1, lsr #5
0002441e: movw       r3, #0x748b
00024422: lsrs       r2, r1, #1
00024424: movt       r3, #0xf0f
00024428: cmp        r2, r3
0002442a: bne        #0x244cc
0002442c: movw       r0, #0x8b74
00024430: movt       r0, #0x3d70
00024434: pop        {r4, r5, r7, pc}
00024436: sub.w      r1, r1, r2, lsr #8
0002443a: add.w      r1, r1, #0x3a800000
0002443e: adds       r1, #1
00024440: pop.w      {r4, r5, r7, lr}
00024444: b.w        #0x24db4
00024448: movw       r2, #0xfff8
0002444c: movt       r2, #0x17ff
00024450: add.w      r1, r2, r1, lsr #4
00024454: adds       r1, #6
00024456: mvn        r2, #0xbb000000
0002445a: sub.w      r4, r2, r1, lsr #2
0002445e: movs       r3, #0x89
00024460: lsls       r2, r0, #9
00024462: add.w      r3, r3, r0, asr #23
00024466: movw       r0, #0x329c
0002446a: movt       r0, #1
0002446e: bl         #0x250cc
00024472: subs       r0, r4, r0
00024474: pop        {r4, r5, r7, pc}
00024476: cmn.w      r0, #0x800000
0002447a: itt        hi
0002447c: orrhi      r0, r0, #0x400000
00024480: pophi      {r4, r5, r7, pc}
00024482: movw       r2, #0xbf37
00024486: movt       r2, #0xc2cd
0002448a: cmp        r0, r2
0002448c: blo        #0x244e6
0002448e: ldr.w      r1, [r1, #0xfd4]
00024492: movw       r2, #0xf1b5
00024496: movt       r2, #0xc2cf
0002449a: cmp        r0, r2
0002449c: mov        r0, r1
0002449e: it         lo
000244a0: addlo      r0, #1
000244a2: pop        {r4, r5, r7, pc}
000244a4: lsrs       r5, r3, #6
000244a6: muls       r5, r5, r5
000244a8: sub.w      r3, r3, r5, lsr #20
000244ac: lsrs       r5, r2, #6
000244ae: lsrs       r4, r3, #0x10
000244b0: muls       r5, r4, r5
000244b2: lsrs       r4, r2, #0x10
000244b4: uxth       r3, r3
000244b6: lsrs       r5, r5, #0xa
000244b8: muls       r3, r4, r3
000244ba: add.w      r3, r5, r3, lsr #16
000244be: subs       r2, r2, r3
000244c0: bmi        #0x2450c
000244c2: adds       r2, #0x42
000244c4: pop.w      {r4, r5, r7, lr}
000244c8: b.w        #0x25034
000244cc: movw       r3, #0xffff
000244d0: movt       r3, #0x4c7f
000244d4: subs       r4, r3, r2
000244d6: b          #0x2445e
000244d8: uxtb       r3, r2
000244da: cmp        r3, #8
000244dc: bls        #0x2451c
000244de: lsls       r0, r1, #0x17
000244e0: add.w      r0, r0, r2, lsr #8
000244e4: pop        {r4, r5, r7, pc}
000244e6: pop.w      {r4, r5, r7, lr}
000244ea: b.w        #0x24ec8
000244ee: cmp        r2, #0x35
000244f0: ble        #0x2453e
000244f2: cmp        r2, #0x3d
000244f4: ble        #0x2457a
000244f6: cmp        r2, #0x3e
000244f8: beq.w      #0x23f5e
000244fc: cmp        r2, #0x42
000244fe: beq.w      #0x24144
00024502: cmp        r2, #0x51
00024504: mov        r3, r2
00024506: beq.w      #0x24156
0002450a: b          #0x2401a
0002450c: adds       r2, #0x81
0002450e: uxtb       r3, r2
00024510: cmp        r3, #0xa
00024512: blo        #0x2451c
00024514: lsrs       r0, r2, #8
00024516: add.w      r0, r0, r1, lsl #23
0002451a: pop        {r4, r5, r7, pc}
0002451c: pop.w      {r4, r5, r7, lr}
00024520: b.w        #0x25034
00024524: cmp        r2, #0xe
00024526: bgt        #0x24554
00024528: cmp        r2, #0xb
0002452a: beq        #0x24588
0002452c: cmp        r2, #0xd
0002452e: bne.w      #0x2401a
00024532: uxth       r5, r0
00024534: mvn        r3, #0x72
00024538: movs       r2, #0xd
0002453a: movs       r1, #0xd
0002453c: b          #0x23f20
0002453e: cmp        r2, #0x26
00024540: bgt        #0x24562
00024542: cmp        r2, #0x21
00024544: beq.w      #0x2402a
00024548: cmp        r2, #0x26
0002454a: mov        r1, r2
0002454c: mov        r3, r2
0002454e: beq.w      #0x23ef8
00024552: b          #0x2401a
00024554: cmp        r2, #0xf
00024556: beq.w      #0x240d4
0002455a: cmp        r2, #0x12
0002455c: beq.w      #0x242c2
00024560: b          #0x2401a
00024562: cmp        r2, #0x27
00024564: beq        #0x24590
00024566: cmp        r2, #0x33
00024568: beq.w      #0x23f4a
0002456c: b          #0x2401a
0002456e: cmp        r2, #0x17
00024570: beq        #0x24594
00024572: cmp        r2, #0x18
00024574: beq.w      #0x24074
00024578: b          #0x2401a
0002457a: cmp        r2, #0x36
0002457c: beq.w      #0x24150
00024580: cmp        r2, #0x3c
00024582: beq.w      #0x242aa
00024586: b          #0x2401a
00024588: mvn        r4, #0x74
0002458c: mov        r1, r2
0002458e: b          #0x23f10
00024590: mov        r1, r2
00024592: b          #0x23f08
00024594: uxth       r1, r0
00024596: movs       r3, #0x17
00024598: movs       r2, #0x17
0002459a: movs       r5, #0x17
0002459c: b          #0x2408a
0002459e: nop        

eik_tanh:
000245a0: push       {r4, r5, r7, lr}
000245a2: add        r7, sp, #8
000245a4: lsls       r1, r0, #1
000245a6: cmp.w      r1, #-1
000245aa: ble        #0x2461a
000245ac: sbfx       r2, r0, #0x17, #8
000245b0: cmp        r2, #0x7c
000245b2: bhs        #0x24648
000245b4: cmp        r2, #0x73
000245b6: it         lo
000245b8: poplo      {r4, r5, r7, pc}
000245ba: cmp        r2, #0x77
000245bc: bls        #0x24694
000245be: movw       r4, #0x3d10
000245c2: movt       r4, #1
000245c6: ldr        r2, [r4, #8]
000245c8: ldrd       r1, r3, [r4]
000245cc: and.w      r2, r2, r0, lsr #16
000245d0: adds       r4, r3, r2
000245d2: ands       r1, r0
000245d4: movs       r2, #0
000245d6: cmp.w      r2, r1, lsr #14
000245da: bne        #0x245e8
000245dc: ldr        r2, [r4, #0xc]
000245de: subs       r2, r1, r2
000245e0: cmp.w      r2, #-1
000245e4: ble.w      #0x24882
000245e8: ldrd       r2, r3, [r4]
000245ec: uxtb       r5, r2
000245ee: mla        r2, r5, r1, r2
000245f2: ldr        r5, [r4, #8]
000245f4: lsrs       r2, r2, #0x10
000245f6: lsrs       r4, r1, #4
000245f8: muls       r2, r4, r2
000245fa: add.w      r2, r3, r2, lsr #12
000245fe: lsrs       r3, r2, #0x10
00024600: mla        r1, r3, r1, r5
00024604: uxth       r2, r2
00024606: muls       r2, r4, r2
00024608: add.w      r1, r1, r2, lsr #12
0002460c: tst.w      r1, #0x3e00
00024610: itt        ne
00024612: subne.w    r0, r0, r1, lsr #14
00024616: popne      {r4, r5, r7, pc}
00024618: b          #0x246d2
0002461a: movw       r4, #0x3ce8
0002461e: movt       r4, #1
00024622: ldrd       r2, r3, [r4]
00024626: adds       r5, r3, r1
00024628: cmp.w      r5, #-1
0002462c: ble.w      #0x2475a
00024630: mov.w      r3, #-1
00024634: add.w      r3, r3, r5, lsr #23
00024638: movs       r4, #8
0002463a: cmp        r3, #0xf8
0002463c: and.w      r3, r4, r0, lsr #28
00024640: bhi.w      #0x2479c
00024644: ldr        r0, [r2, r3]
00024646: pop        {r4, r5, r7, pc}
00024648: movw       r1, #0x1ff0
0002464c: movw       r3, #0x4f4
00024650: and.w      r1, r1, r0, lsr #12
00024654: movt       r3, #1
00024658: cmp        r2, #0x7f
0002465a: add.w      r4, r3, r1
0002465e: bne        #0x246fa
00024660: ldr        r1, [r4]
00024662: ldr        r2, [r4, #8]
00024664: uxth       r3, r0
00024666: uxtb       r5, r1
00024668: mls        r5, r5, r3, r2
0002466c: uxth       r2, r2
0002466e: lsrs       r5, r5, #0xf
00024670: mls        r1, r5, r3, r1
00024674: ldr        r5, [r4, #4]
00024676: lsrs       r1, r1, #0xf
00024678: mla        r2, r2, r3, r5
0002467c: muls       r1, r3, r1
0002467e: add.w      r1, r2, r1, lsr #15
00024682: tst.w      r1, #0x1fc
00024686: beq.w      #0x247ea
0002468a: bfc        r0, #0, #0x17
0002468e: add.w      r0, r0, r1, asr #9
00024692: pop        {r4, r5, r7, pc}
00024694: bne.w      #0x247c0
00024698: movw       r1, #0xff00
0002469c: movt       r1, #0x7f
000246a0: tst        r0, r1
000246a2: beq.w      #0x2488c
000246a6: ubfx       r1, r0, #8, #0x10
000246aa: mul        r2, r1, r1
000246ae: lsrs       r2, r2, #0x10
000246b0: movw       r3, #0xaaaa
000246b4: muls       r2, r3, r2
000246b6: movw       r3, #0x6db8
000246ba: lsrs       r2, r2, #0x10
000246bc: movt       r3, #0x43
000246c0: mla        r1, r2, r1, r3
000246c4: tst.w      r1, #0x7c0000
000246c8: itt        ne
000246ca: subne.w    r0, r0, r1, lsr #23
000246ce: popne      {r4, r5, r7, pc}
000246d0: lsrs       r1, r1, #9
000246d2: lsrs       r2, r1, #0xe
000246d4: mvn        r3, #1
000246d8: add.w      r2, r3, r2, lsl #2
000246dc: sub.w      r4, r0, r1, lsr #14
000246e0: movs       r1, #0x1e
000246e2: bic.w      r3, r1, r4, lsr #22
000246e6: add.w      r1, r2, r2, lsl #1
000246ea: rsb        r2, r2, r2, lsl #4
000246ee: lsls       r2, r2, #0xd
000246f0: lsls       r2, r3
000246f2: bl         #0x252f0
000246f6: add        r0, r4
000246f8: pop        {r4, r5, r7, pc}
000246fa: ldr        r1, [r4]
000246fc: ldr        r2, [r4, #8]
000246fe: uxth       r3, r0
00024700: mls        r2, r2, r3, r1
00024704: ldr        r5, [r4, #4]
00024706: uxtb       r1, r1
00024708: asrs       r2, r2, #0xf
0002470a: mla        r1, r1, r3, r5
0002470e: muls       r2, r3, r2
00024710: add.w      r1, r1, r2, asr #15
00024714: cmp        r1, #0
00024716: bmi.w      #0x24828
0002471a: uxtb       r2, r1
0002471c: cmp        r2, #3
0002471e: rsb        r2, r1, r0, lsl #8
00024722: itt        hs
00024724: subhs.w    r0, r0, r2, lsr #8
00024728: pophs      {r4, r5, r7, pc}
0002472a: subs       r2, #8
0002472c: sub.w      r4, r0, r2, lsr #8
00024730: movw       r2, #0xfff8
00024734: movt       r2, #0x17ff
00024738: adds       r2, #0x10
0002473a: orr.w      r1, r2, r1, lsr #4
0002473e: lsls       r2, r0, #9
00024740: lsrs       r0, r0, #0x17
00024742: mvn        r3, #0x75
00024746: uxtab      r3, r3, r0
0002474a: movw       r0, #0x3d1c
0002474e: movt       r0, #1
00024752: bl         #0x250cc
00024756: add        r0, r4
00024758: pop        {r4, r5, r7, pc}
0002475a: asrs       r1, r5, #0x11
0002475c: add.w      r4, r2, r1, lsl #4
00024760: ldr        r1, [r4]
00024762: ldr        r2, [r4, #8]
00024764: uxth       r3, r0
00024766: uxtb       r5, r1
00024768: mls        r5, r5, r3, r2
0002476c: uxth       r2, r2
0002476e: lsrs       r5, r5, #0xf
00024770: mls        r1, r5, r3, r1
00024774: ldr        r5, [r4, #4]
00024776: lsrs       r1, r1, #0xf
00024778: mla        r2, r2, r3, r5
0002477c: muls       r1, r3, r1
0002477e: add.w      r1, r2, r1, lsr #15
00024782: tst.w      r1, #0x1fc
00024786: lsr.w      r3, r1, #9
0002478a: beq        #0x24850
0002478c: movw       r1, #0x3ec0
00024790: lsrs       r0, r0, #0x1c
00024792: movt       r1, #1
00024796: ldr        r0, [r1, r0]
00024798: add        r0, r3
0002479a: pop        {r4, r5, r7, pc}
0002479c: asrs       r5, r5, #0xf
0002479e: cmp        r5, #0xdf
000247a0: bls        #0x247fc
000247a2: cmp.w      r1, #-0x1000000
000247a6: itt        hi
000247a8: orrhi      r0, r0, #0x400000
000247ac: pophi      {r4, r5, r7, pc}
000247ae: ldr        r0, [r2, r3]
000247b0: movw       r2, #0x5968
000247b4: movt       r2, #0x8220
000247b8: cmp        r1, r2
000247ba: it         lo
000247bc: sublo      r0, #1
000247be: pop        {r4, r5, r7, pc}
000247c0: subs.w     r3, r2, #0x73
000247c4: beq        #0x248be
000247c6: movw       r5, #0x3cf0
000247ca: movt       r5, #1
000247ce: lsls       r2, r0, #9
000247d0: add.w      r4, r5, r3, lsl #3
000247d4: ldrd       r3, r5, [r4]
000247d8: lsrs       r2, r5
000247da: beq.w      #0x248ec
000247de: lsls       r2, r2, #4
000247e0: ldr        r2, [r3, r2]
000247e2: add        r1, r2
000247e4: sub.w      r0, r0, r1, lsr #24
000247e8: pop        {r4, r5, r7, pc}
000247ea: movw       r2, #0xfff8
000247ee: and        r3, r0, #0xff000000
000247f2: movt       r2, #0x17ff
000247f6: orr.w      r4, r3, r1, lsr #9
000247fa: b          #0x24862
000247fc: add.w      r0, r2, r5, lsl #4
00024800: movw       r5, #0xf1e0
00024804: movt       r5, #0xffff
00024808: ldr        r0, [r0, r5]
0002480a: movw       r4, #0xfd1c
0002480e: ubfx       r0, r0, #8, #6
00024812: add.w      r5, r2, r0, lsl #4
00024816: movt       r4, #0xffff
0002481a: ldr        r2, [r2, r3]
0002481c: ldr        r3, [r5, r4]
0002481e: subs       r0, r2, r0
00024820: cmp        r1, r3
00024822: it         lo
00024824: sublo      r0, #1
00024826: pop        {r4, r5, r7, pc}
00024828: lsls       r2, r1, #1
0002482a: cmp.w      r2, #-1
0002482e: ble        #0x248ce
00024830: add.w      r2, r1, #-0x20000000
00024834: adds       r2, #0x60
00024836: bmi        #0x24918
00024838: add.w      r1, r1, #0x20000000
0002483c: add.w      r4, r1, #0x70
00024840: tst.w      r4, #0x1c
00024844: beq        #0x24942
00024846: rsb        r1, r4, r0, lsl #5
0002484a: sub.w      r0, r0, r1, lsr #5
0002484e: pop        {r4, r5, r7, pc}
00024850: and        r5, r0, #0xff000000
00024854: movw       r2, #0xfff8
00024858: add        r3, r5
0002485a: movt       r2, #0x17ff
0002485e: add.w      r4, r3, #-0x1000000
00024862: add.w      r1, r2, r1, lsr #5
00024866: lsls       r2, r0, #9
00024868: lsrs       r0, r0, #0x17
0002486a: mvn        r3, #0x75
0002486e: uxtab      r3, r3, r0
00024872: movw       r0, #0x3d1c
00024876: movt       r0, #1
0002487a: bl         #0x250cc
0002487e: add        r0, r4
00024880: pop        {r4, r5, r7, pc}
00024882: mov        r1, r4
00024884: pop.w      {r4, r5, r7, lr}
00024888: b.w        #0x25288
0002488c: uxtb       r1, r0
0002488e: cmp        r1, #0x2b
00024890: itt        hs
00024892: subhs      r0, #0x2b
00024894: pophs      {r4, r5, r7, pc}
00024896: mul        r2, r0, r0
0002489a: cmp        r2, #5
0002489c: bne        #0x24912
0002489e: movw       r2, #0x4f4
000248a2: movt       r2, #1
000248a6: add.w      r4, r2, r1, lsl #4
000248aa: mov        r5, r0
000248ac: bl         #0x24ec8
000248b0: cmp        r0, #7
000248b2: beq        #0x24976
000248b4: mov        r1, r0
000248b6: cmp        r0, #9
000248b8: bne        #0x2497a
000248ba: mov        r0, r5
000248bc: b          #0x24622
000248be: movw       r2, #0x3745
000248c2: movt       r2, #0x7371
000248c6: cmp        r1, r2
000248c8: it         hi
000248ca: subhi      r0, #1
000248cc: pop        {r4, r5, r7, pc}
000248ce: add.w      r1, r2, #0x81
000248d2: uxtb       r2, r1
000248d4: cmp        r2, #6
000248d6: lsl.w      r2, r0, #8
000248da: bhi        #0x2493a
000248dc: subs       r2, r1, r2
000248de: add.w      r2, r0, r2, asr #8
000248e2: adds       r4, r2, #1
000248e4: movs       r2, #4
000248e6: movt       r2, #0x1000
000248ea: b          #0x24862
000248ec: ldr        r2, [r3]
000248ee: movw       r3, #0xff00
000248f2: movt       r3, #0x7f
000248f6: adds       r3, #0xff
000248f8: add        r1, r2
000248fa: ands       r3, r0
000248fc: lsrs       r2, r1, #0x18
000248fe: adds       r5, r0, r3
00024900: sub.w      r0, r0, r1, lsr #24
00024904: sub.w      r2, r5, r2, lsl #1
00024908: cmp.w      r3, r1, lsr #24
0002490c: it         lo
0002490e: addlo      r0, r2, #1
00024910: pop        {r4, r5, r7, pc}
00024912: add        r0, r1
00024914: subs       r0, #0x55
00024916: pop        {r4, r5, r7, pc}
00024918: tst.w      r2, #0x3c
0002491c: rsb        r1, r2, r0, lsl #6
00024920: itt        ne
00024922: subne.w    r0, r0, r1, lsr #6
00024926: popne      {r4, r5, r7, pc}
00024928: subs       r1, #1
0002492a: sub.w      r4, r0, r1, lsr #6
0002492e: movs       r1, #2
00024930: movt       r1, #0xa00
00024934: add.w      r1, r1, r2, lsr #4
00024938: b          #0x2473e
0002493a: subs       r1, r2, r1
0002493c: sub.w      r0, r0, r1, asr #8
00024940: pop        {r4, r5, r7, pc}
00024942: and        r5, r0, #0xff000000
00024946: movs       r1, #1
00024948: lsls       r2, r0, #9
0002494a: lsrs       r0, r0, #0x17
0002494c: mvn        r3, #0x75
00024950: movt       r1, #0x600
00024954: uxtab      r3, r3, r0
00024958: movw       r0, #0x3d1c
0002495c: add.w      r1, r1, r4, lsr #4
00024960: movt       r0, #1
00024964: bl         #0x250cc
00024968: add.w      r1, r5, r4, lsr #5
0002496c: add        r0, r1
0002496e: add.w      r0, r0, #-0x6000000
00024972: adds       r0, #1
00024974: pop        {r4, r5, r7, pc}
00024976: mov        r0, r5
00024978: b          #0x24660
0002497a: uxth       r0, r1
0002497c: cmp        r0, #0x4d
0002497e: mov        r0, r5
00024980: beq.w      #0x245d4
00024984: cmp        r1, #0x51
00024986: beq.w      #0x245c6
0002498a: cmp        r1, #0x53
0002498c: mov        r2, r1
0002498e: beq.w      #0x247d4
00024992: b          #0x24760

eik_exp:
00024994: push       {r4, r5, r7, lr}
00024996: add        r7, sp, #8
00024998: movs       r1, #0x8a
0002499a: add.w      r2, r1, r0, asr #23
0002499e: movs       r3, #0
000249a0: cmp        r2, #0xb
000249a2: bls        #0x24a44
000249a4: ble        #0x24a9e
000249a6: cmp        r2, #0xff
000249a8: bls.w      #0x24ace
000249ac: uxtb       r2, r2
000249ae: cmp        r2, #0xb
000249b0: bls.w      #0x24b00
000249b4: cmp        r2, #0xe
000249b6: bls        #0x249fa
000249b8: cmp        r2, #0x89
000249ba: bne        #0x249d6
000249bc: mul        r1, r0, r0
000249c0: cmp        r1, #0xd
000249c2: bne.w      #0x24bb6
000249c6: lsrs       r1, r0, #5
000249c8: lsls       r2, r0, #1
000249ca: cmp.w      r3, r0, lsr #10
000249ce: mov        r0, r1
000249d0: bne        #0x249a0
000249d2: mov        r0, r1
000249d4: pop        {r4, r5, r7, pc}
000249d6: cmp        r2, #0xf
000249d8: bne        #0x249ee
000249da: movw       r1, #0x7215
000249de: movt       r1, #0x42b1
000249e2: cmp        r0, r1
000249e4: bls        #0x249fa
000249e6: adds       r1, #2
000249e8: cmp        r0, r1
000249ea: bls.w      #0x24c6c
000249ee: movw       r0, #0x3ed0
000249f2: movt       r0, #1
000249f6: ldr        r0, [r0]
000249f8: pop        {r4, r5, r7, pc}
000249fa: lsls       r3, r0, #9
000249fc: ubfx       r0, r0, #6, #0x11
00024a00: movw       r1, #0x5c55
00024a04: muls       r0, r1, r0
00024a06: movw       r1, #0x40a0
00024a0a: movt       r1, #0x5c55
00024a0e: add.w      r0, r1, r0, lsr #1
00024a12: rsb.w      r1, r2, #0x1e
00024a16: lsr.w      r1, r0, r1
00024a1a: lsl.w      r0, r3, r2
00024a1e: movw       r2, #0x2d78
00024a22: muls       r2, r1, r2
00024a24: add.w      r0, r0, r2, lsr #16
00024a28: movw       r2, #0x3eb4
00024a2c: movt       r2, #1
00024a30: ldrd       r3, r5, [r2]
00024a34: ldr        r2, [r2, #8]
00024a36: add        r1, r3
00024a38: mul        r3, r1, r5
00024a3c: subs       r0, r3, r0
00024a3e: ror.w      r1, r1, #9
00024a42: b          #0x24b28
00024a44: movw       r1, #0x3d28
00024a48: movt       r1, #1
00024a4c: add.w      r2, r1, r2, lsl #5
00024a50: ldrd       r1, ip, [r2, #8]
00024a54: ldr        r3, [r2, #0x10]
00024a56: ldrd       lr, r2, [r2]
00024a5a: muls       r1, r0, r1
00024a5c: lsrs       r0, r0, #9
00024a5e: mla        r0, lr, r0, r3
00024a62: lsrs       r5, r0, #0xf
00024a64: mla        r0, r5, ip, r1
00024a68: ror.w      r1, r5, r3
00024a6c: lsrs       r3, r1, #0x13
00024a6e: ldr        r2, [r2, r3]
00024a70: asrs       r5, r0, #0xa
00024a72: lsrs       r3, r2, #0x16
00024a74: muls       r3, r5, r3
00024a76: ubfx       r5, r2, #7, #0xf
00024a7a: add.w      r5, r5, r3, asr #17
00024a7e: asrs       r4, r0, #0x10
00024a80: muls       r5, r4, r5
00024a82: add.w      r3, r3, r5, asr #9
00024a86: add.w      r2, r2, r3, asr #9
00024a8a: cmp.w      r2, #-1
00024a8e: bgt        #0x24b4e
00024a90: uxtb       r3, r2
00024a92: cmp        r3, #5
00024a94: bhs.w      #0x24bae
00024a98: pop.w      {r4, r5, r7, lr}
00024a9c: b          #0x25188
00024a9e: mvns       r1, r2
00024aa0: cmp        r1, #0xf
00024aa2: bhi.w      #0x24bc4
00024aa6: cmp        r1, #7
00024aa8: add.w      r0, r0, r1, lsl #23
00024aac: blo.w      #0x24bd8
00024ab0: lsls       r0, r0, #8
00024ab2: subs       r1, #7
00024ab4: lsrs       r0, r1
00024ab6: lsrs       r1, r0, #0x10
00024ab8: muls       r1, r1, r1
00024aba: rsb        r0, r0, r1, lsr #17
00024abe: movw       r1, #0xfe01
00024ac2: movt       r1, #0x7eff
00024ac6: add.w      r0, r1, r0, lsr #23
00024aca: lsrs       r0, r0, #1
00024acc: pop        {r4, r5, r7, pc}
00024ace: cmp        r2, #0xf1
00024ad0: blo        #0x24bc0
00024ad2: cmp        r2, #0xf8
00024ad4: bhi.w      #0x24c02
00024ad8: movs       r1, #0
00024ada: bfc        r0, #0x17, #9
00024ade: movt       r1, #0xff80
00024ae2: subs       r0, r1, r0
00024ae4: sub.w      r1, r2, #0xf1
00024ae8: lsls       r0, r1
00024aea: smultt     r1, r0, r0
00024aee: rsb        r0, r0, r1, lsr #16
00024af2: movs       r1, #2
00024af4: movt       r1, #0xfe00
00024af8: add.w      r0, r1, r0, lsr #22
00024afc: lsrs       r0, r0, #2
00024afe: pop        {r4, r5, r7, pc}
00024b00: movw       r1, #0x3d28
00024b04: movt       r1, #1
00024b08: add.w      r2, r1, r2, lsl #5
00024b0c: ldrd       r1, ip, [r2, #8]
00024b10: ldr        r3, [r2, #0x14]
00024b12: ldrd       lr, r2, [r2]
00024b16: muls       r1, r0, r1
00024b18: lsrs       r0, r0, #9
00024b1a: mls        r0, lr, r0, r3
00024b1e: lsrs       r5, r0, #0xf
00024b20: mls        r0, r5, ip, r1
00024b24: ror.w      r1, r5, r3
00024b28: lsrs       r3, r1, #0x13
00024b2a: ldr        r2, [r2, r3]
00024b2c: asrs       r5, r0, #0xa
00024b2e: lsrs       r3, r2, #0x16
00024b30: muls       r3, r5, r3
00024b32: ubfx       r5, r2, #7, #0xf
00024b36: sub.w      r5, r5, r3, asr #17
00024b3a: asrs       r4, r0, #0x10
00024b3c: muls       r5, r4, r5
00024b3e: add.w      r3, r3, r5, asr #9
00024b42: sub.w      r2, r2, r3, asr #9
00024b46: cmp.w      r2, #-1
00024b4a: ble        #0x24ba8
00024b4c: rsbs       r0, r0, #0
00024b4e: cmp.w      r2, #0x40000000
00024b52: ror.w      r1, r1, #0x17
00024b56: bhs        #0x24b84
00024b58: movw       r3, #0xe808
00024b5c: movt       r3, #0x4e8d
00024b60: add        r0, r3
00024b62: movs       r3, #0x42
00024b64: movt       r3, #0x8000
00024b68: adds       r1, #1
00024b6a: add.w      r2, r3, r2, lsr #1
00024b6e: tst.w      r2, #0xf0
00024b72: beq        #0x24b9e
00024b74: movs       r0, #0
00024b76: movt       r0, #0xff80
00024b7a: and.w      r0, r0, r1, lsl #14
00024b7e: add.w      r0, r0, r2, lsr #8
00024b82: pop        {r4, r5, r7, pc}
00024b84: movw       r3, #0x17f8
00024b88: movt       r3, #0xb172
00024b8c: add        r0, r3
00024b8e: mvn        r3, #0x7e
00024b92: subs       r1, #1
00024b94: add.w      r2, r3, r2, lsl #1
00024b98: tst.w      r2, #0xf0
00024b9c: bne        #0x24b74
00024b9e: ror.w      r1, r1, #9
00024ba2: pop.w      {r4, r5, r7, lr}
00024ba6: b          #0x25188
00024ba8: uxtb       r3, r2
00024baa: cmp        r3, #7
00024bac: blo        #0x24bd0
00024bae: lsrs       r0, r2, #8
00024bb0: add.w      r0, r0, r1, lsl #23
00024bb4: pop        {r4, r5, r7, pc}
00024bb6: lsls       r1, r0, #9
00024bb8: it         ne
00024bba: orrne      r0, r0, #0x400000
00024bbe: pop        {r4, r5, r7, pc}
00024bc0: cmp        r2, #0x89
00024bc2: bls        #0x24c3a
00024bc4: movw       r0, #0x3ec0
00024bc8: movt       r0, #1
00024bcc: ldr        r0, [r0]
00024bce: pop        {r4, r5, r7, pc}
00024bd0: rsbs       r0, r0, #0
00024bd2: pop.w      {r4, r5, r7, lr}
00024bd6: b          #0x25188
00024bd8: lsls       r0, r0, #7
00024bda: lsrs       r0, r1
00024bdc: sub.w      r1, r0, #0x47800
00024be0: sub.w      r1, r1, #0x508
00024be4: smultt     r2, r1, r1
00024be8: sub.w      r1, r1, r2, lsr #9
00024bec: tst.w      r1, #0xfc00
00024bf0: asr.w      r4, r1, #0x10
00024bf4: beq        #0x24cac
00024bf6: movw       r0, #0xfffb
00024bfa: movt       r0, #0x3f7f
00024bfe: subs       r0, r0, r4
00024c00: pop        {r4, r5, r7, pc}
00024c02: mvns       r1, r2
00024c04: lsls       r2, r1, #0x1e
00024c06: add.w      r0, r2, r0, lsl #7
00024c0a: rors       r0, r1
00024c0c: add.w      r1, r0, #0xb0000
00024c10: adds       r1, #0x40
00024c12: lsrs       r2, r1, #0x10
00024c14: muls       r2, r2, r2
00024c16: movw       r4, #0xfffb
00024c1a: add.w      r1, r1, r2, lsr #9
00024c1e: movt       r4, #0x3f7f
00024c22: tst.w      r1, #0x1fc00
00024c26: lsr.w      r5, r1, #0x11
00024c2a: itt        ne
00024c2c: addne      r0, r5, r4
00024c2e: popne      {r4, r5, r7, pc}
00024c30: bl         #0x253a4
00024c34: adds       r1, r5, r4
00024c36: subs       r0, r1, r0
00024c38: pop        {r4, r5, r7, pc}
00024c3a: cmp        r2, #0xf
00024c3c: bhi        #0x24c7a
00024c3e: movw       r1, #0x3172
00024c42: cmp        r2, #0xf
00024c44: movt       r1, #0x5c55
00024c48: bne        #0x24cc0
00024c4a: movw       r3, #0xbf37
00024c4e: movt       r3, #0xc2cd
00024c52: cmp        r0, r3
00024c54: blo        #0x24d1c
00024c56: movw       r1, #0xf1b5
00024c5a: movt       r1, #0xc2cf
00024c5e: cmp        r0, r1
00024c60: mov.w      r1, #0
00024c64: it         lo
00024c66: movlo      r1, #1
00024c68: mov        r0, r1
00024c6a: pop        {r4, r5, r7, pc}
00024c6c: movw       r1, #0xf404
00024c70: movt       r1, #0x26c6
00024c74: add.w      r0, r1, r0, lsl #7
00024c78: pop        {r4, r5, r7, pc}
00024c7a: cmp        r2, #0x89
00024c7c: itt        ne
00024c7e: movne      r0, #0
00024c80: popne      {r4, r5, r7, pc}
00024c82: movw       r2, #0x4f4
00024c86: uxtb       r1, r0
00024c88: movt       r2, #1
00024c8c: mul        r3, r0, r0
00024c90: cmp        r3, #0x1d
00024c92: add.w      r2, r2, r1, lsl #4
00024c96: beq.w      #0x24a50
00024c9a: cmp        r3, #0x35
00024c9c: add.w      lr, r0, r0, lsl #2
00024ca0: bne        #0x24d0a
00024ca2: lsr.w      ip, r0, #3
00024ca6: lsls       r3, r0, #5
00024ca8: movs       r1, #0x35
00024caa: b          #0x24a5c
00024cac: rsbs       r0, r0, #0
00024cae: bl         #0x253a4
00024cb2: movw       r1, #0xfffb
00024cb6: subs       r0, r0, r4
00024cb8: movt       r1, #0x3f7f
00024cbc: add        r0, r1
00024cbe: pop        {r4, r5, r7, pc}
00024cc0: add.w      r1, r1, #0x320
00024cc4: lsls       r3, r0, #9
00024cc6: ubfx       r0, r0, #6, #0x11
00024cca: movw       r5, #0x5c55
00024cce: muls       r0, r5, r0
00024cd0: add.w      r0, r0, r3, lsr #18
00024cd4: add.w      r0, r1, r0, lsr #1
00024cd8: rsb.w      r1, r2, #0x1e
00024cdc: lsr.w      r1, r0, r1
00024ce0: lsl.w      r0, r3, r2
00024ce4: movw       r2, #0x2d78
00024ce8: muls       r2, r1, r2
00024cea: add.w      r0, r0, r2, lsr #16
00024cee: movw       r2, #0x3ea8
00024cf2: movt       r2, #1
00024cf6: ldrd       r3, r5, [r2]
00024cfa: ldr        r2, [r2, #8]
00024cfc: subs       r1, r3, r1
00024cfe: mul        r3, r1, r5
00024d02: subs       r0, r3, r0
00024d04: ror.w      r1, r1, #9
00024d08: b          #0x24a6c
00024d0a: lsrs       r1, r0, #1
00024d0c: muls       r1, r0, r1
00024d0e: cmp        r1, #0x25
00024d10: bne        #0x24d3e
00024d12: lsr.w      ip, r0, #3
00024d16: lsls       r3, r0, #5
00024d18: movs       r1, #0x25
00024d1a: b          #0x24b18
00024d1c: movw       r3, #0xac3f
00024d20: movt       r3, #0xc2ae
00024d24: cmp        r0, r3
00024d26: bls        #0x24cc4
00024d28: add.w      r1, r3, #0x14
00024d2c: cmp        r0, r1
00024d2e: bhs        #0x24d5a
00024d30: movw       r1, #0x13e6
00024d34: movt       r1, #0xac2b
00024d38: sub.w      r0, r1, r0, lsl #6
00024d3c: pop        {r4, r5, r7, pc}
00024d3e: cmp        r3, #0x15
00024d40: beq        #0x24d60
00024d42: cmp        r3, #0x3d
00024d44: beq.w      #0x24b0c
00024d48: cmp        r3, #0x4d
00024d4a: bne        #0x24d6e
00024d4c: lsrs       r1, r0, #3
00024d4e: cmp.w      r0, #-1
00024d52: lsl.w      r0, r0, #5
00024d56: bgt        #0x24cf6
00024d58: b          #0x24a30
00024d5a: pop.w      {r4, r5, r7, lr}
00024d5e: b          #0x24ec8
00024d60: cmp.w      r0, #-1
00024d64: lsr.w      r1, r0, #7
00024d68: bgt.w      #0x24c04
00024d6c: b          #0x24aa0
00024d6e: mov        r1, r0
00024d70: bfc        r1, #0x17, #9
00024d74: cmp        r1, #0
00024d76: it         ne
00024d78: orrne      r1, r0, #0x400000
00024d7c: mov        r0, r1
00024d7e: pop        {r4, r5, r7, pc}

t_drb:
00024d80: push       {r7, lr}
00024d82: mov        r7, sp
00024d84: rsbs.w     r3, r2, #0x1cc
00024d88: mov.w      r2, #0x3800000
00024d8c: and.w      r1, r2, r1, lsl #23
00024d90: lsr.w      r2, r3, #7
00024d94: bmi        #0x24da4
00024d96: ands       r3, r3, #0x70
00024d9a: beq        #0x24da4
00024d9c: adds       r0, r1, r2
00024d9e: add.w      r0, r0, #0x39000000
00024da2: pop        {r7, pc}
00024da4: add        r1, r2
00024da6: mvn        r2, #0xc7000000
00024daa: add        r1, r2
00024dac: pop.w      {r7, lr}
00024db0: b          #0x24db4
00024db2: nop        

t_mn:
00024db4: push       {r4, r5, r7, lr}
00024db6: add        r7, sp, #8
00024db8: movs       r3, #0x88
00024dba: movw       ip, #0x5d60
00024dbe: movw       r4, #0xa3ab
00024dc2: lsls       r2, r0, #9
00024dc4: add.w      r3, r3, r0, asr #23
00024dc8: ubfx       r0, r0, #8, #0xf
00024dcc: movt       ip, #0xd1d5
00024dd0: movt       r4, #0xffff
00024dd4: smlabb     r0, r0, r4, ip
00024dd8: asrs       r0, r0, #0xc
00024dda: lsl.w      r4, r2, r3
00024dde: lsls       r0, r3
00024de0: movw       r3, #0x7a02
00024de4: asrs       r2, r0, #0xf
00024de6: movt       r3, #0xd3a3
00024dea: muls       r3, r2, r3
00024dec: sub.w      ip, r3, r4
00024df0: movw       r3, #0x3fe
00024df4: movw       r4, #0x32b8
00024df8: and.w      r3, r3, r2, lsl #1
00024dfc: movt       r4, #1
00024e00: ldrh       r3, [r4, r3]
00024e02: asrs       r0, r0, #0x18
00024e04: movw       r4, #0x5c61
00024e08: muls       r0, r4, r0
00024e0a: movw       r4, #0xf782
00024e0e: movt       r4, #0xec19
00024e12: add.w      r0, r3, r0, asr #2
00024e16: adds.w     lr, r0, #0x18
00024e1a: add.w      r0, ip, r4
00024e1e: it         eq
00024e20: popeq      {r4, r5, r7, pc}
00024e22: movw       r4, #0x1ff0
00024e26: movw       r3, #0x4f4
00024e2a: and.w      r4, r4, r2, lsl #4
00024e2e: movt       r3, #1
00024e32: add        r3, r4
00024e34: ldr        r3, [r3, #0xc]
00024e36: asrs       r5, r0, #0x10
00024e38: sub.w      ip, r3, #0x84
00024e3c: movw       r3, #0xfe00
00024e40: movt       r3, #0xff
00024e44: and.w      r3, r3, r0, lsl #8
00024e48: add.w      r4, lr, r3
00024e4c: movw       r3, #0xaaab
00024e50: muls       r3, r5, r3
00024e52: asrs       r3, r3, #0xe
00024e54: muls       r3, r5, r3
00024e56: smultt     lr, r0, r0
00024e5a: asrs       r0, r4, #8
00024e5c: sub.w      r0, r0, r3, lsr #11
00024e60: sub.w      r3, lr, r4
00024e64: muls       r0, r5, r0
00024e66: add.w      lr, r3, r0, asr #15
00024e6a: movw       r0, #0x1ff
00024e6e: subs       r0, r0, r2
00024e70: movs       r2, #0
00024e72: cmp.w      r2, r0, lsr #14
00024e76: lsr.w      r0, r0, #9
00024e7a: beq        #0x24e88
00024e7c: sub.w      r2, r0, #0x10
00024e80: lsr.w      r4, ip, r2
00024e84: movs       r2, #0
00024e86: b          #0x24e92
00024e88: ror.w      r3, ip, r0
00024e8c: lsr.w      r2, ip, r0
00024e90: lsrs       r4, r3, #0x10
00024e92: add.w      r3, lr, r4
00024e96: add.w      r2, r2, r3, asr #16
00024e9a: rsb        r2, r2, r5, lsl #8
00024e9e: movs       r5, #0x80
00024ea0: movt       r5, #0x8000
00024ea4: orr.w      r5, r5, r1, lsl #8
00024ea8: add.w      r0, r0, r1, lsr #23
00024eac: uxth       r3, r3
00024eae: lsrs       r4, r5, #7
00024eb0: lsrs       r5, r5, #0x10
00024eb2: adds       r0, #9
00024eb4: ror.w      r0, ip, r0
00024eb8: muls       r3, r5, r3
00024eba: sub.w      r0, r0, r3, lsr #7
00024ebe: mla        r0, r2, r4, r0
00024ec2: add.w      r0, r1, r0, lsr #31
00024ec6: pop        {r4, r5, r7, pc}

t_exp_den:
00024ec8: push       {r4, r5, r7, lr}
00024eca: add        r7, sp, #8
00024ecc: ubfx       r2, r0, #6, #0x11
00024ed0: movw       r3, #0x5c55
00024ed4: lsls       r1, r0, #9
00024ed6: muls       r2, r3, r2
00024ed8: add.w      r1, r2, r1, lsr #18
00024edc: movw       r2, #0x3172
00024ee0: movt       r2, #0x5c55
00024ee4: add.w      r3, r2, r1, lsr #1
00024ee8: movw       r2, #0xfbff
00024eec: movw       r5, #0xe808
00024ef0: sub.w      r2, r2, r3, lsr #15
00024ef4: movt       r5, #0x4e8d
00024ef8: muls       r5, r2, r5
00024efa: lsr.w      ip, r3, #0xf
00024efe: sub.w      r0, r5, r0, lsl #24
00024f02: movw       r5, #0x2d78
00024f06: mul        r5, ip, r5
00024f0a: sub.w      r5, r0, r5, lsr #16
00024f0e: smultt     r4, r5, r5
00024f12: add.w      r5, r5, r4, lsr #10
00024f16: movw       r4, #0x1ff0
00024f1a: and.w      r2, r4, r2, lsl #4
00024f1e: movw       r4, #0x4f4
00024f22: movt       r4, #1
00024f26: add        r2, r4
00024f28: ldr        r2, [r2, #0xc]
00024f2a: asrs       r4, r5, #8
00024f2c: lsrs       r1, r2, #0x18
00024f2e: muls       r1, r4, r1
00024f30: ubfx       r4, r2, #9, #0xf
00024f34: smulbt     r5, r4, r5
00024f38: add.w      r1, r1, r5, asr #7
00024f3c: add.w      r2, r2, r1, asr #9
00024f40: movw       r1, #0x1200
00024f44: movt       r1, #0xffff
00024f48: add.w      r1, r1, r3, lsr #15
00024f4c: movs       r3, #0
00024f4e: cmp.w      r3, r2, lsr #30
00024f52: lsr.w      r3, r1, #9
00024f56: bne        #0x24f68
00024f58: lsrs       r0, r2, #1
00024f5a: sub.w      r0, r0, #-0x80000000
00024f5e: subs       r0, #0x41
00024f60: lsrs       r0, r3
00024f62: adds       r0, #1
00024f64: lsrs       r0, r0, #1
00024f66: pop        {r4, r5, r7, pc}
00024f68: mvn        r1, #0x40
00024f6c: add.w      r1, r1, r2, lsr #1
00024f70: lsr.w      r5, r1, r3
00024f74: lsl.w      r2, r5, r3
00024f78: subs       r1, r1, r2
00024f7a: cmp        r1, #1
00024f7c: bls        #0x24f84
00024f7e: adds       r0, r5, #1
00024f80: lsrs       r0, r0, #1
00024f82: pop        {r4, r5, r7, pc}
00024f84: lsls       r1, r5, #0x1f
00024f86: itt        eq
00024f88: lsreq      r0, r5, #1
00024f8a: popeq      {r4, r5, r7, pc}
00024f8c: movs       r1, #0x80
00024f8e: add.w      r4, r1, r2, lsl #1
00024f92: movw       r1, #0xfbff
00024f96: movt       r1, #4
00024f9a: sub.w      r1, r1, ip
00024f9e: movw       r2, #0x38c2
00024fa2: subs       r0, r0, r2
00024fa4: ror.w      r1, r1, #9
00024fa8: mov        r2, r4
00024faa: bl         #0x25188
00024fae: sub.w      r1, r0, r4, lsr #8
00024fb2: lsrs       r0, r5, #1
00024fb4: lsls       r1, r1, #9
00024fb6: mov.w      r1, #1
00024fba: it         ne
00024fbc: addne.w    r0, r1, r5, lsr #1
00024fc0: pop        {r4, r5, r7, pc}
00024fc2: nop        

t_sgr:
00024fc4: push       {r4, r5, r7, lr}
00024fc6: add        r7, sp, #8
00024fc8: lsrs       r3, r2, #0xf
00024fca: mul        ip, r3, r3
00024fce: lsr.w      lr, ip, #0x10
00024fd2: uxth.w     r4, ip
00024fd6: mul        r5, lr, r3
00024fda: muls       r3, r4, r3
00024fdc: add.w      r3, r5, r3, lsr #16
00024fe0: bic        r5, r1, #0xf
00024fe4: subs       r1, r2, r5
00024fe6: bfc        r2, #0xf, #0x11
00024fea: lsls       r1, r1, #0xd
00024fec: mul        r2, lr, r2
00024ff0: sub.w      r1, r1, r2, lsr #15
00024ff4: movw       r2, #0x199a
00024ff8: mul        r2, lr, r2
00024ffc: lsrs       r2, r2, #0x10
00024ffe: lsrs       r4, r3, #0x10
00025000: add.w      r1, r1, r1, lsl #1
00025004: muls       r2, r4, r2
00025006: subs       r1, r1, r3
00025008: add.w      r1, r1, r2, lsr #10
0002500c: cmp        r1, #8
0002500e: movw       r1, #1
00025012: movt       r1, #0x7e00
00025016: it         lt
00025018: sublt      r5, #1
0002501a: add.w      r1, r1, r5, lsr #13
0002501e: movs       r2, #1
00025020: lsrs       r1, r1, #1
00025022: movt       r2, #0xfc00
00025026: sub.w      r2, r2, r5, lsr #11
0002502a: cmp        r0, #0
0002502c: it         mi
0002502e: lsrmi      r1, r2, #2
00025030: mov        r0, r1
00025032: pop        {r4, r5, r7, pc}

t_drj:
00025034: cmp        r2, #0
00025036: bmi        #0x2505a
00025038: cmp        r1, #0
0002503a: it         eq
0002503c: beq        #0x24ec8
0002503e: and        r3, r2, #0x7f
00025042: cmp        r3, #0xd
00025044: sub.w      r1, r1, #1
00025048: ittt       hs
0002504a: lsrhs      r0, r2, #7
0002504c: addhs.w    r0, r0, r1, lsl #23
00025050: bxhs       lr
00025052: lsls       r2, r2, #1
00025054: movw       ip, #0x1ff
00025058: b          #0x2505e
0002505a: mov.w      ip, #0
0002505e: movw       r3, #0x96cc
00025062: movt       r3, #0xc1e4
00025066: cmp        r0, r3
00025068: blo        #0x250c2
0002506a: push       {r4, r6, r7, lr}
0002506c: add        r7, sp, #8
0002506e: movs       r3, #0x8a
00025070: lsl.w      lr, r0, #9
00025074: add.w      r3, r3, r0, asr #23
00025078: ubfx       r0, r0, #6, #0x11
0002507c: movw       r4, #0x5c55
00025080: muls       r0, r4, r0
00025082: movw       r4, #0x38e8
00025086: add.w      r0, r0, lr, lsr #18
0002508a: movt       r4, #0x5c55
0002508e: add.w      r0, r4, r0, lsr #1
00025092: lsrs       r0, r0, #0xf
00025094: lsls       r0, r3
00025096: movw       r4, #0xfbff
0002509a: sub.w      r4, r4, r0, lsr #15
0002509e: movw       r0, #0xe808
000250a2: movt       r0, #0x4e8d
000250a6: cmp.w      r1, r4, lsr #9
000250aa: it         ne
000250ac: orrne.w    r4, ip, r1, lsl #9
000250b0: muls       r0, r4, r0
000250b2: lsl.w      r1, lr, r3
000250b6: subs       r0, r0, r1
000250b8: ror.w      r1, r4, #9
000250bc: pop.w      {r4, r6, r7, lr}
000250c0: b          #0x25188
000250c2: lsrs       r2, r2, #8
000250c4: add.w      r1, r2, r1, lsl #23
000250c8: subs       r1, #1
000250ca: b          #0x24db4

t_mt:
000250cc: push       {r4, r5, r6, r7, lr}
000250ce: add        r7, sp, #0xc
000250d0: str        r8, [sp, #-0x4]!
000250d4: ldrd       ip, r4, [r0]
000250d8: ldr        r0, [r0, #8]
000250da: lsrs       r5, r2, #0x11
000250dc: mls        r0, ip, r5, r0
000250e0: lsls       r2, r3
000250e2: asrs       r0, r0, #0xb
000250e4: lsls       r0, r3
000250e6: asr.w      r8, r0, #0x11
000250ea: ldm.w      r4, {r3, r5, r6, ip}
000250ee: mvn.w      r0, r0, asr #17
000250f2: lsr.w      lr, r0, #9
000250f6: movw       r0, #0x3fe
000250fa: mul        r3, r8, r3
000250fe: and.w      r0, r0, r8, lsl #1
00025102: subs       r4, r3, r2
00025104: ldrh       r3, [r6, r0]
00025106: mul        r2, lr, r5
0002510a: cmp        r3, r2
0002510c: add.w      r0, r4, ip
00025110: beq        #0x25180
00025112: subs       r2, r3, r2
00025114: movw       r3, #0xff80
00025118: movt       r3, #0xff
0002511c: and.w      r3, r3, r0, lsl #7
00025120: asrs       r0, r0, #0x11
00025122: movw       r6, #0xaaab
00025126: muls       r6, r0, r6
00025128: asrs       r6, r6, #0xb
0002512a: muls       r6, r0, r6
0002512c: lsrs       r6, r6, #0xd
0002512e: add        r2, r3
00025130: sub.w      r3, r6, r2, asr #7
00025134: mul        r6, r0, r0
00025138: muls       r3, r0, r3
0002513a: rsb        r3, r6, r3, asr #16
0002513e: adds.w     ip, r3, r2
00025142: beq        #0x25180
00025144: movw       r2, #0x1ff0
00025148: movw       r3, #0x4f4
0002514c: and.w      r2, r2, r8, lsl #4
00025150: movt       r3, #1
00025154: add        r2, r3
00025156: ldr        r2, [r2, #0xc]
00025158: subs       r2, #0x84
0002515a: ror.w      r3, r2, lr
0002515e: lsr.w      r2, r2, lr
00025162: sub.w      r3, ip, r3, lsr #17
00025166: rsb        r0, r2, r0, lsl #9
0002516a: add.w      r0, r0, r3, asr #15
0002516e: lsrs       r2, r1, #0xf
00025170: bfc        r3, #0xf, #0x11
00025174: muls       r2, r3, r2
00025176: sub.w      r2, r2, ip, lsl #14
0002517a: mla        r0, r0, r1, r2
0002517e: asrs       r0, r0, #0x1f
00025180: ldr        r8, [sp], #4
00025184: pop        {r4, r5, r6, r7, pc}
00025186: nop        

t_exp_res:
00025188: push       {r4, r5, r6, r7, lr}
0002518a: add        r7, sp, #0xc
0002518c: str        r8, [sp, #-0x4]!
00025190: movw       r3, #0xc200
00025194: movt       r3, #0xb8
00025198: muls       r3, r1, r3
0002519a: cmp.w      r3, #-1
0002519e: bgt        #0x25202
000251a0: movw       r3, #0x400
000251a4: movt       r3, #0xffff
000251a8: ror.w      r4, r1, #0x17
000251ac: add.w      r3, r3, r1, ror #23
000251b0: eor.w      ip, r3, r4, asr #31
000251b4: movw       r3, #0x2d78
000251b8: mul        r3, ip, r3
000251bc: lsrs       r3, r3, #0x10
000251be: eor.w      r3, r3, r4, asr #31
000251c2: rsb        ip, r3, r4, asr #31
000251c6: movw       r3, #0xdcff
000251ca: movt       r3, #0x9290
000251ce: cmp        r0, r3
000251d0: mvn        r3, #0xe0000000
000251d4: and.w      lr, r3, r1, ror #23
000251d8: bgt        #0x251f2
000251da: movw       r1, #0x17f8
000251de: subs       r4, #1
000251e0: movt       r1, #0xb172
000251e4: add        r0, r1
000251e6: mul        r1, r4, r4
000251ea: cmp        r1, #0xd
000251ec: it         eq
000251ee: moveq.w    lr, #3
000251f2: ror.w      r1, r4, #9
000251f6: sub.w      r3, lr, r1, lsr #23
000251fa: movw       r4, #0x5c61
000251fe: add        r0, ip
00025200: muls       r3, r4, r3
00025202: mvns       r4, r1
00025204: lsr.w      ip, r4, #0x17
00025208: movw       r4, #0x32b8
0002520c: movt       r4, #1
00025210: ldrh.w     r4, [r4, ip, lsl #1]
00025214: lsls       r1, r1, #0x17
00025216: sub.w      r3, r3, r4, lsl #11
0002521a: movw       r4, #0x8218
0002521e: movt       r4, #0xa590
00025222: add.w      lr, r3, r4
00025226: movw       r4, #0x281c
0002522a: movt       r4, #0xedbe
0002522e: add        r0, r4
00025230: add.w      r4, r0, lr, asr #17
00025234: uxth       r3, r4
00025236: asrs       r5, r4, #0x10
00025238: smultt     r4, r4, r4
0002523c: lsrs       r6, r4, #0xe
0002523e: mul        r8, r5, r3
00025242: muls       r5, r6, r5
00025244: asrs       r5, r5, #0xe
00025246: movw       r6, #0x2aab
0002524a: muls       r5, r6, r5
0002524c: movw       r6, #0x4f4
00025250: movt       r6, #1
00025254: add.w      r6, r6, ip, lsl #4
00025258: ldr        r6, [r6, #0xc]
0002525a: mvn        r3, #3
0002525e: add.w      r2, r3, r2, lsr #5
00025262: sub.w      r3, r6, #0x84
00025266: add.w      r6, lr, r8, asr #8
0002526a: add.w      r0, r6, r0, lsl #17
0002526e: add.w      r0, r0, r4, lsl #7
00025272: muls       r3, r2, r3
00025274: add.w      r0, r0, r5, asr #5
00025278: subs       r0, r3, r0
0002527a: add.w      r1, r1, r2, lsr #3
0002527e: add.w      r0, r1, r0, lsr #31
00025282: ldr        r8, [sp], #4
00025286: pop        {r4, r5, r6, r7, pc}

t_tw_low2:
00025288: push       {r4, r5, r7, lr}
0002528a: add        r7, sp, #8
0002528c: mov        r2, r0
0002528e: bfc        r2, #0xe, #0x12
00025292: ldrh.w     ip, [r1, #2]
00025296: lsrs       r3, r2, #4
00025298: ldrd       r1, lr, [r1, #4]
0002529c: mul        r3, ip, r3
000252a0: add.w      r1, r1, r3, lsr #12
000252a4: lsrs       r1, r1, #6
000252a6: muls       r1, r2, r1
000252a8: movs       r2, #1
000252aa: mov        r3, r0
000252ac: bfi        r3, r2, #0x17, #9
000252b0: lsls       r2, r3, #8
000252b2: add.w      r1, lr, r1, lsr #10
000252b6: adds       r2, #0xc8
000252b8: sub.w      r4, r2, r1, lsr #6
000252bc: lsls       r2, r3, #2
000252be: lsrs       r1, r4, #7
000252c0: adds       r2, #1
000252c2: sub.w      r2, r2, r1, lsl #1
000252c6: movs       r1, #0x1e
000252c8: bic.w      r3, r1, r0, lsr #22
000252cc: add.w      r1, r2, r2, lsl #1
000252d0: rsb        r2, r2, r2, lsl #4
000252d4: lsls       r2, r2, #0xd
000252d6: mov        r5, r0
000252d8: lsls       r2, r3
000252da: bfc        r5, #0, #0x17
000252de: bl         #0x252f0
000252e2: add        r0, r5
000252e4: add.w      r0, r0, r4, lsr #7
000252e8: mvn        r1, #0x1000000
000252ec: add        r0, r1
000252ee: pop        {r4, r5, r7, pc}

t_pd2:
000252f0: push       {r4, r5, r6, r7, lr}
000252f2: add        r7, sp, #0xc
000252f4: str        fp, [sp, #-0x4]!
000252f8: mov.w      ip, #1
000252fc: uxtb       r6, r0
000252fe: bfi        r0, ip, #0x17, #9
00025302: lsrs       r4, r0, #8
00025304: add.w      r5, r0, r0, lsl #2
00025308: rsb        lr, r1, r5, lsl #1
0002530c: muls       r6, r4, r6
0002530e: mul        r5, r4, r4
00025312: add.w      ip, r5, r6, lsr #7
00025316: lsr.w      r4, ip, #0x10
0002531a: mul        r4, r4, lr
0002531e: cmp        r3, #0xd
00025320: sub.w      r2, r4, r2
00025324: blo        #0x25338
00025326: lsr.w      r0, lr, #0xc
0002532a: uxth.w     r1, ip
0002532e: muls       r0, r1, r0
00025330: add.w      r0, r2, r0, lsr #4
00025334: adds       r0, #0xff
00025336: b          #0x25392
00025338: muls       r0, r0, r0
0002533a: sub.w      r0, r0, ip, lsl #16
0002533e: lsr.w      r4, lr, #0xe
00025342: muls       r0, r4, r0
00025344: add.w      r0, r2, r0, lsr #18
00025348: cbz        r0, #0x2539a
0002534a: lsr.w      r2, lr, #0x10
0002534e: uxth.w     r4, ip
00025352: uxth.w     r6, lr
00025356: muls       r2, r4, r2
00025358: muls       r6, r4, r6
0002535a: add.w      r2, r2, r6, lsr #16
0002535e: add        r0, r2
00025360: lsr.w      r2, ip, #0x11
00025364: mul        r6, r2, r2
00025368: lsrs       r6, r6, #0xe
0002536a: movw       r5, #0x4e03
0002536e: muls       r6, r5, r6
00025370: lsrs       r1, r1, #4
00025372: lsrs       r6, r6, #0x10
00025374: muls       r1, r6, r1
00025376: cmp        r3, #8
00025378: lsr.w      r1, r1, r3
0002537c: bne        #0x25390
0002537e: lsrs       r3, r1, #8
00025380: muls       r2, r3, r2
00025382: lsrs       r2, r2, #0xd
00025384: movw       r3, #0x931
00025388: muls       r2, r3, r2
0002538a: adds       r0, #0x6a
0002538c: sub.w      r1, r1, r2, lsr #16
00025390: add        r0, r1
00025392: lsrs       r0, r0, #0x1f
00025394: ldr        fp, [sp], #4
00025398: pop        {r4, r5, r6, r7, pc}
0002539a: movs       r0, #0
0002539c: ldr        fp, [sp], #4
000253a0: pop        {r4, r5, r6, r7, pc}
000253a2: nop        

t_exp_small_fix:
000253a4: push       {r7, lr}
000253a6: mov        r7, sp
000253a8: asrs       r1, r0, #0xf
000253aa: mul        r2, r1, r1
000253ae: lsrs       r3, r2, #0x14
000253b0: mul        ip, r3, r1
000253b4: ubfx       r3, r2, #7, #0xd
000253b8: add.w      r3, r3, ip, asr #14
000253bc: muls       r1, r3, r1
000253be: lsrs       r3, r2, #0x1a
000253c0: lsls       r2, r2, #5
000253c2: add.w      r3, r3, r0, asr #15
000253c6: add.w      r2, r2, r0, lsl #16
000253ca: bfc        r0, #0xf, #0x11
000253ce: muls       r0, r3, r0
000253d0: add.w      r0, r2, r0, asr #9
000253d4: add.w      r1, ip, r1, asr #13
000253d8: add.w      r0, r0, r0, lsl #1
000253dc: add        r0, r1
000253de: lsrs       r0, r0, #0x1f
000253e0: pop        {r7, pc}
000253e2: bmi        #0x2538e

memcpy:
000253e4: cmp        r2, #0
000253e6: it         eq
000253e8: bxeq       lr
000253ea: push       {r4, r6, r7, lr}
000253ec: add        r7, sp, #8
000253ee: ands       r3, r2, #3
000253f2: beq        #0x2540c
000253f4: mov        ip, r1
000253f6: ldrb       r4, [ip], #1
000253fa: mov        lr, r0
000253fc: cmp        r3, #1
000253fe: strb       r4, [lr], #1
00025402: bne        #0x25418
00025404: subs       r3, r2, #1
00025406: cmp        r2, #4
00025408: bhs        #0x25442
0002540a: b          #0x25464
0002540c: mov        ip, r1
0002540e: mov        lr, r0
00025410: mov        r3, r2
00025412: cmp        r2, #4
00025414: bhs        #0x25442
00025416: b          #0x25464
00025418: ldrb       r4, [r1, #1]
0002541a: cmp        r3, #2
0002541c: strb       r4, [r0, #1]
0002541e: bne        #0x25430
00025420: subs       r3, r2, #2
00025422: add.w      ip, r1, #2
00025426: add.w      lr, r0, #2
0002542a: cmp        r2, #4
0002542c: bhs        #0x25442
0002542e: b          #0x25464
00025430: add.w      ip, r1, #3
00025434: ldrb       r1, [r1, #2]
00025436: subs       r3, r2, #3
00025438: add.w      lr, r0, #3
0002543c: strb       r1, [r0, #2]
0002543e: cmp        r2, #4
00025440: blo        #0x25464
00025442: sub.w      r1, ip, #4
00025446: sub.w      r2, lr, #4
0002544a: nop        
0002544c: ldrb       r4, [r1, #4]!
00025450: subs       r3, #4
00025452: strb       r4, [r2, #4]!
00025456: ldrb       r4, [r1, #1]
00025458: strb       r4, [r2, #1]
0002545a: ldrb       r4, [r1, #2]
0002545c: strb       r4, [r2, #2]
0002545e: ldrb       r4, [r1, #3]
00025460: strb       r4, [r2, #3]
00025462: bne        #0x2544c
00025464: pop.w      {r4, r6, r7, lr}
00025468: bx         lr
0002546a: nop        

memmove:
0002546c: push       {r4, r6, r7, lr}
0002546e: add        r7, sp, #8
00025470: cmp        r0, r1
00025472: bhs        #0x25492
00025474: cmp        r2, #0
00025476: beq        #0x25548
00025478: ands       r3, r2, #3
0002547c: beq        #0x254f6
0002547e: mov        ip, r1
00025480: ldrb       r4, [ip], #1
00025484: mov        lr, r0
00025486: cmp        r3, #1
00025488: strb       r4, [lr], #1
0002548c: bne        #0x254fe
0002548e: subs       r3, r2, #1
00025490: b          #0x25520
00025492: cmp        r2, #0
00025494: beq        #0x25548
00025496: ands       ip, r2, #3
0002549a: mov        r4, r2
0002549c: beq        #0x254c4
0002549e: subs       r4, r2, #1
000254a0: ldrb.w     lr, [r1, r4]
000254a4: cmp.w      ip, #1
000254a8: strb.w     lr, [r0, r4]
000254ac: beq        #0x254c4
000254ae: subs       r4, r2, #2
000254b0: ldrb.w     lr, [r1, r4]
000254b4: cmp.w      ip, #2
000254b8: strb.w     lr, [r0, r4]
000254bc: beq        #0x254c4
000254be: subs       r4, r2, #3
000254c0: ldrb       r3, [r1, r4]
000254c2: strb       r3, [r0, r4]
000254c4: cmp        r2, #4
000254c6: blo        #0x25548
000254c8: sub.w      ip, r0, #2
000254cc: sub.w      lr, r1, #4
000254d0: add.w      r3, lr, r4
000254d4: ldrb       r2, [r3, #3]
000254d6: add.w      r1, ip, r4
000254da: strb       r2, [r1, #1]
000254dc: ldrb       r2, [r3, #2]
000254de: strb.w     r2, [ip, r4]
000254e2: ldrb       r2, [r3, #1]
000254e4: strb       r2, [r1, #-0x1]
000254e8: ldrb.w     r2, [lr, r4]
000254ec: subs       r4, #4
000254ee: strb       r2, [r1, #-0x2]
000254f2: bne        #0x254d0
000254f4: b          #0x25548
000254f6: mov        ip, r1
000254f8: mov        lr, r0
000254fa: mov        r3, r2
000254fc: b          #0x25520
000254fe: ldrb       r4, [r1, #1]
00025500: cmp        r3, #2
00025502: strb       r4, [r0, #1]
00025504: bne        #0x25512
00025506: subs       r3, r2, #2
00025508: add.w      ip, r1, #2
0002550c: add.w      lr, r0, #2
00025510: b          #0x25520
00025512: add.w      ip, r1, #3
00025516: ldrb       r1, [r1, #2]
00025518: subs       r3, r2, #3
0002551a: add.w      lr, r0, #3
0002551e: strb       r1, [r0, #2]
00025520: cmp        r2, #4
00025522: it         lo
00025524: poplo      {r4, r6, r7, pc}
00025526: sub.w      r1, ip, #4
0002552a: sub.w      r2, lr, #4
0002552e: nop        
00025530: ldrb       r4, [r1, #4]!
00025534: subs       r3, #4
00025536: strb       r4, [r2, #4]!
0002553a: ldrb       r4, [r1, #1]
0002553c: strb       r4, [r2, #1]
0002553e: ldrb       r4, [r1, #2]
00025540: strb       r4, [r2, #2]
00025542: ldrb       r4, [r1, #3]
00025544: strb       r4, [r2, #3]
00025546: bne        #0x25530
00025548: pop        {r4, r6, r7, pc}
0002554a: nop        

memset:
0002554c: cmp        r2, #0
0002554e: it         eq
00025550: bxeq       lr
00025552: push       {r7, lr}
00025554: mov        r7, sp
00025556: ands       lr, r2, #3
0002555a: mov        ip, r0
0002555c: mov        r3, r2
0002555e: beq        #0x25582
00025560: mov        ip, r0
00025562: cmp.w      lr, #1
00025566: strb       r1, [ip], #1
0002556a: bne        #0x25574
0002556c: subs       r3, r2, #1
0002556e: cmp        r2, #4
00025570: bhs        #0x25586
00025572: b          #0x2559a
00025574: cmp.w      lr, #2
00025578: strb       r1, [r0, #1]
0002557a: bne        #0x255a0
0002557c: subs       r3, r2, #2
0002557e: add.w      ip, r0, #2
00025582: cmp        r2, #4
00025584: blo        #0x2559a
00025586: sub.w      r2, ip, #4
0002558a: nop        
0002558c: strb       r1, [r2, #4]!
00025590: subs       r3, #4
00025592: strb       r1, [r2, #1]
00025594: strb       r1, [r2, #2]
00025596: strb       r1, [r2, #3]
00025598: bne        #0x2558c
0002559a: pop.w      {r7, lr}
0002559e: bx         lr
000255a0: subs       r3, r2, #3
000255a2: add.w      ip, r0, #3
000255a6: strb       r1, [r0, #2]
000255a8: cmp        r2, #4
000255aa: bhs        #0x25586
000255ac: b          #0x2559a
000255ae: nop        

eik_batch:
000255b0: cmp        r3, #0
000255b2: it         eq
000255b4: bxeq       lr
000255b6: push       {r4, r5, r6, r7, lr}
000255b8: add        r7, sp, #0xc
000255ba: str        r8, [sp, #-0x4]!
000255be: mov        r4, r3
000255c0: mov        r5, r2
000255c2: mov        r6, r1
000255c4: mov        r8, r0
000255c6: b          #0x255d4
000255c8: bl         #0x245a0
000255cc: subs       r4, #1
000255ce: str        r0, [r5], #4
000255d2: beq        #0x255f2
000255d4: ldr        r0, [r6], #4
000255d8: cmp.w      r8, #1
000255dc: beq        #0x255c8
000255de: cmp.w      r8, #0
000255e2: bne        #0x255ec
000255e4: bl         #0x23ed4
000255e8: b          #0x255cc
000255ea: nop        
000255ec: bl         #0x24994
000255f0: b          #0x255cc
000255f2: ldr        r8, [sp], #4
000255f6: pop.w      {r4, r5, r6, r7, lr}
000255fa: bx         lr
