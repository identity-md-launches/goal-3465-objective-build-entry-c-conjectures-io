; Allocated executable sections; ARM mapping-symbol literal pools are data.

eik_sigmoid:
00023ed4: push       {r4, r5, r7, lr}
00023ed6: add        r7, sp, #8
00023ed8: lsls       r1, r0, #1
00023eda: bmi        #0x23f16
00023edc: asrs       r1, r1, #0x18
00023ede: cmp        r1, #0x7d
00023ee0: blt        #0x23f58
00023ee2: ldr        r5, [pc, #0x3f4]
00023ee4: ldm        r5, {r1, r2, r3, r4, r5}
00023ee6: subs       r4, r4, r0
00023ee8: bmi        #0x23fe4
00023eea: lsrs       r2, r4, #0x10
00023eec: lsls       r2, r2, #4
00023eee: subs       r5, r5, r2
00023ef0: ldm        r5!, {r2, r3, r4}
00023ef2: subs       r3, #0x80
00023ef4: uxth       r5, r0
00023ef6: muls       r4, r5, r4
00023ef8: subs       r4, r2, r4
00023efa: asrs       r4, r4, #0xf
00023efc: muls       r4, r5, r4
00023efe: asrs       r4, r4, #0xf
00023f00: adds       r3, r4, r3
00023f02: uxtb       r2, r2
00023f04: muls       r5, r2, r5
00023f06: adds       r2, r3, r5
00023f08: lsls       r3, r2, #0x17
00023f0a: lsrs       r3, r3, #0x19
00023f0c: bne        #0x23f10
00023f0e: b          #0x24082
00023f10: asrs       r0, r2, #9
00023f12: adds       r0, r0, r1
00023f14: pop        {r4, r5, r7, pc}
00023f16: cmp        r0, #0
00023f18: bmi        #0x23fa0
00023f1a: ldr        r5, [pc, #0x3d0]
00023f1c: ldm        r5!, {r1, r2}
00023f1e: subs       r1, r1, r0
00023f20: bmi        #0x2401c
00023f22: lsrs       r1, r1, #0x10
00023f24: lsls       r1, r1, #4
00023f26: subs       r5, r2, r1
00023f28: uxth       r1, r0
00023f2a: ldm        r5!, {r2, r3, r4}
00023f2c: uxth       r5, r4
00023f2e: muls       r5, r1, r5
00023f30: adds       r3, r5, r3
00023f32: uxtb       r5, r2
00023f34: muls       r5, r1, r5
00023f36: subs       r4, r4, r5
00023f38: lsrs       r4, r4, #0xf
00023f3a: muls       r4, r1, r4
00023f3c: subs       r2, r2, r4
00023f3e: lsrs       r2, r2, #0xf
00023f40: muls       r2, r1, r2
00023f42: lsrs       r1, r2, #0xf
00023f44: adds       r1, r3, r1
00023f46: lsrs       r2, r1, #2
00023f48: subs       r2, #0xc0
00023f4a: lsrs       r1, r2, #8
00023f4c: lsls       r2, r2, #0x18
00023f4e: bne        #0x23f52
00023f50: b          #0x240d0
00023f52: ldr        r0, [pc, #0x39c]
00023f54: adds       r0, r1, r0
00023f56: pop        {r4, r5, r7, pc}
00023f58: cmp        r1, #0x73
00023f5a: bgt        #0x23f66
00023f5c: cmp        r1, #0x67
00023f5e: bge        #0x24028
00023f60: movs       r0, #0x3f
00023f62: lsls       r0, r0, #0x18
00023f64: pop        {r4, r5, r7, pc}
00023f66: cmp        r1, #0x79
00023f68: bhi        #0x24040
00023f6a: movs       r2, #0x79
00023f6c: subs       r1, r2, r1
00023f6e: lsls       r2, r1, #0x1e
00023f70: lsls       r3, r0, #7
00023f72: adds       r2, r2, r3
00023f74: lsrs       r2, r1
00023f76: lsrs       r3, r2, #0xf
00023f78: ldr        r1, [pc, #0x378]
00023f7a: muls       r1, r3, r1
00023f7c: lsrs       r1, r1, #0x10
00023f7e: muls       r1, r3, r1
00023f80: lsrs       r1, r1, #0x10
00023f82: muls       r1, r3, r1
00023f84: lsrs       r1, r1, #0xe
00023f86: subs       r1, r2, r1
00023f88: cmp        r0, r3
00023f8a: blt        #0x23f8e
00023f8c: b          #0x24116
00023f8e: lsls       r3, r1, #0x14
00023f90: lsrs       r3, r3, #0x18
00023f92: bne        #0x23f96
00023f94: b          #0x24216
00023f96: lsrs       r0, r1, #0xb
00023f98: ldr        r1, [pc, #0x35c]
00023f9a: subs       r0, r1, r0
00023f9c: lsrs       r0, r0, #2
00023f9e: pop        {r4, r5, r7, pc}
00023fa0: ldr        r5, [pc, #0x358]
00023fa2: ldm        r5!, {r1, r2}
00023fa4: subs       r2, r0, r2
00023fa6: bhs        #0x24086
00023fa8: asrs       r2, r2, #0x10
00023faa: lsls       r2, r2, #4
00023fac: adds       r5, r1, r2
00023fae: uxth       r1, r0
00023fb0: ldm        r5!, {r2, r3, r4}
00023fb2: uxth       r5, r4
00023fb4: muls       r5, r1, r5
00023fb6: adds       r3, r5, r3
00023fb8: uxtb       r5, r2
00023fba: muls       r5, r1, r5
00023fbc: subs       r4, r4, r5
00023fbe: lsrs       r4, r4, #0xf
00023fc0: muls       r4, r1, r4
00023fc2: subs       r2, r2, r4
00023fc4: lsrs       r2, r2, #0xf
00023fc6: muls       r2, r1, r2
00023fc8: lsrs       r1, r2, #0xf
00023fca: adds       r1, r3, r1
00023fcc: lsls       r2, r1, #1
00023fce: subs       r2, #0x87
00023fd0: bpl        #0x23fd4
00023fd2: b          #0x2414c
00023fd4: uxtb       r3, r2
00023fd6: cmp        r3, #0xf8
00023fd8: bls        #0x23fdc
00023fda: b          #0x2417a
00023fdc: lsrs       r0, r2, #8
00023fde: ldr        r1, [pc, #0x320]
00023fe0: subs       r0, r1, r0
00023fe2: pop        {r4, r5, r7, pc}
00023fe4: lsrs       r1, r4, #0xc
00023fe6: ands       r1, r3
00023fe8: subs       r5, r5, r1
00023fea: uxth       r1, r0
00023fec: ldm        r5, {r3, r4, r5}
00023fee: muls       r5, r1, r5
00023ff0: subs       r5, r3, r5
00023ff2: asrs       r5, r5, #0xf
00023ff4: muls       r5, r1, r5
00023ff6: asrs       r5, r5, #0xf
00023ff8: adds       r4, r4, r5
00023ffa: uxtb       r3, r3
00023ffc: muls       r1, r3, r1
00023ffe: adds       r1, r4, r1
00024000: bmi        #0x240ee
00024002: lsls       r3, r1, #1
00024004: adds       r3, #0x81
00024006: bpl        #0x2400a
00024008: b          #0x2413a
0002400a: lsrs       r4, r3, #8
0002400c: uxtb       r1, r3
0002400e: cmp        r1, #6
00024010: bhi        #0x240f6
00024012: lsrs       r1, r3, #5
00024014: ldr        r2, [pc, #0x3ec]
00024016: adds       r1, r1, r2
00024018: adds       r1, #0xc
0002401a: b          #0x24164
0002401c: asrs       r1, r1, #0x16
0002401e: adds       r1, #0xf8
00024020: cmp        r1, #0xf6
00024022: bhi        #0x240fa
00024024: ldr        r0, [r2, #0x10]
00024026: pop        {r4, r5, r7, pc}
00024028: ldr        r2, [pc, #0x3dc]
0002402a: asrs       r3, r0, #0x1f
0002402c: ands       r0, r2
0002402e: adds       r0, r0, r2
00024030: subs       r1, r3, r1
00024032: adds       r1, #0x7f
00024034: lsrs       r0, r1
00024036: eors       r0, r3
00024038: ldr        r1, [pc, #0x3d4]
0002403a: adds       r0, r0, r1
0002403c: asrs       r0, r0, #1
0002403e: pop        {r4, r5, r7, pc}
00024040: ldr        r5, [pc, #0x3c8]
00024042: lsrs       r1, r0, #0x10
00024044: ldm        r5!, {r2, r3}
00024046: ands       r3, r1
00024048: adds       r5, r2, r3
0002404a: ldm        r5!, {r1, r2, r3}
0002404c: uxth       r4, r1
0002404e: muls       r4, r0, r4
00024050: lsrs       r4, r4, #4
00024052: adds       r2, r4, r2
00024054: lsls       r4, r0, #0xc
00024056: lsrs       r4, r4, #0x11
00024058: uxtb       r5, r3
0002405a: muls       r5, r4, r5
0002405c: adds       r3, r5, r3
0002405e: lsrs       r3, r3, #0xd
00024060: muls       r3, r4, r3
00024062: subs       r1, r1, r3
00024064: asrs       r1, r1, #0xe
00024066: muls       r1, r4, r1
00024068: asrs       r1, r1, #0xe
0002406a: adds       r1, r2, r1
0002406c: cmp        r0, r4
0002406e: bge        #0x24108
00024070: ldr        r2, [pc, #0x3b4]
00024072: subs       r1, r2, r1
00024074: lsls       r3, r1, #0x16
00024076: lsrs       r3, r3, #0x19
00024078: bne        #0x2407c
0002407a: b          #0x241ba
0002407c: asrs       r0, r1, #0xa
0002407e: adds       r0, r0, r2
00024080: pop        {r4, r5, r7, pc}
00024082: asrs       r1, r2, #4
00024084: b          #0x240d2
00024086: lsrs       r3, r2, #0x10
00024088: cmp        r3, #0x82
0002408a: bhi        #0x24126
0002408c: ldr        r5, [pc, #0x3dc]
0002408e: ldm        r5!, {r1, r2, r4}
00024090: muls       r1, r3, r1
00024092: adds       r5, r4, r1
00024094: ldm        r5!, {r1, r3, r4}
00024096: sxth       r5, r0
00024098: eors       r5, r2
0002409a: uxtb       r2, r4
0002409c: muls       r2, r5, r2
0002409e: subs       r2, r4, r2
000240a0: lsrs       r2, r2, #0xe
000240a2: muls       r2, r5, r2
000240a4: asrs       r2, r2, #0xb
000240a6: subs       r2, r1, r2
000240a8: lsrs       r4, r2, #0x10
000240aa: muls       r4, r5, r4
000240ac: subs       r3, r4, r3
000240ae: uxth       r2, r2
000240b0: muls       r2, r5, r2
000240b2: asrs       r2, r2, #0x10
000240b4: adds       r2, r3, r2
000240b6: bpl        #0x240ba
000240b8: b          #0x2421c
000240ba: lsls       r1, r1, #0x1d
000240bc: lsrs       r1, r1, #6
000240be: uxtb       r3, r2
000240c0: cmp        r3, #0xa
000240c2: bhs        #0x240c6
000240c4: b          #0x24234
000240c6: ldr        r0, [pc, #0x3a8]
000240c8: adds       r0, r1, r0
000240ca: lsrs       r1, r2, #8
000240cc: subs       r0, r0, r1
000240ce: pop        {r4, r5, r7, pc}
000240d0: lsls       r1, r1, #5
000240d2: ldr        r2, [pc, #0x35c]
000240d4: adds       r1, r1, r2
000240d6: adds       r1, #0x18
000240d8: lsrs       r4, r1, #5
000240da: lsls       r2, r0, #9
000240dc: lsrs       r3, r0, #0x17
000240de: subs       r3, #0x77
000240e0: ldr        r0, [pc, #0x33c]
000240e2: bl         #0x24e40
000240e6: adds       r0, r4, r0
000240e8: ldr        r1, [pc, #0x338]
000240ea: adds       r0, r0, r1
000240ec: pop        {r4, r5, r7, pc}
000240ee: asrs       r4, r1, #8
000240f0: uxtb       r3, r1
000240f2: cmp        r3, #3
000240f4: blo        #0x2415e
000240f6: subs       r0, r2, r4
000240f8: pop        {r4, r5, r7, pc}
000240fa: ldr        r1, [pc, #0x340]
000240fc: cmp        r0, r1
000240fe: blo        #0x24182
00024100: movs       r1, #1
00024102: lsls       r1, r1, #0x16
00024104: orrs       r0, r1
00024106: pop        {r4, r5, r7, pc}
00024108: lsls       r2, r1, #0x15
0002410a: lsrs       r2, r2, #0x18
0002410c: beq        #0x241c8
0002410e: lsrs       r0, r1, #0xb
00024110: ldr        r1, [pc, #0x304]
00024112: adds       r0, r0, r1
00024114: pop        {r4, r5, r7, pc}
00024116: lsls       r3, r1, #0x13
00024118: lsrs       r3, r3, #0x17
0002411a: beq        #0x241d0
0002411c: lsrs       r0, r1, #0xd
0002411e: ldr        r1, [pc, #0x2f0]
00024120: adds       r0, r0, r1
00024122: lsrs       r0, r0, #1
00024124: pop        {r4, r5, r7, pc}
00024126: lsrs       r2, r2, #0x16
00024128: cmp        r2, #9
0002412a: bhs        #0x2412e
0002412c: b          #0x24266
0002412e: subs       r2, #0xa
00024130: cmp        r2, #0xf2
00024132: blo        #0x24136
00024134: b          #0x24260
00024136: movs       r0, #0
00024138: pop        {r4, r5, r7, pc}
0002413a: adds       r1, #0xa0
0002413c: lsls       r2, r1, #0x1a
0002413e: lsrs       r2, r2, #0x1c
00024140: beq        #0x24242
00024142: lsrs       r0, r1, #6
00024144: movs       r1, #0x3f
00024146: lsls       r1, r1, #0x18
00024148: subs       r0, r1, r0
0002414a: pop        {r4, r5, r7, pc}
0002414c: lsls       r2, r1, #2
0002414e: subs       r2, #0x80
00024150: uxtb       r3, r2
00024152: cmp        r3, #0x14
00024154: blo        #0x24222
00024156: lsrs       r0, r2, #8
00024158: ldr        r1, [pc, #0x324]
0002415a: subs       r0, r1, r0
0002415c: pop        {r4, r5, r7, pc}
0002415e: lsrs       r1, r1, #4
00024160: ldr        r2, [pc, #0x2d4]
00024162: adds       r1, r1, r2
00024164: lsls       r2, r0, #9
00024166: asrs       r3, r0, #0x17
00024168: adds       r3, #0x89
0002416a: ldr        r0, [pc, #0x2b4]
0002416c: bl         #0x24e40
00024170: adds       r0, r4, r0
00024172: ldr        r1, [pc, #0x2b0]
00024174: subs       r0, r1, r0
00024176: subs       r0, r0, #2
00024178: pop        {r4, r5, r7, pc}
0002417a: lsrs       r1, r1, #5
0002417c: ldr        r2, [pc, #0x2b0]
0002417e: adds       r1, r1, r2
00024180: b          #0x2424a
00024182: movs       r1, #0x7f
00024184: lsls       r1, r1, #0x17
00024186: ldr        r3, [pc, #0x2b8]
00024188: cmp        r0, r3
0002418a: bls        #0x2418e
0002418c: b          #0x24342
0002418e: ldr        r3, [pc, #0x2b4]
00024190: adds       r3, r0, r3
00024192: lsrs       r3, r3, #0xf
00024194: lsls       r3, r3, #4
00024196: adds       r2, r2, r3
00024198: ldr        r3, [pc, #0x2ac]
0002419a: ldr        r2, [r2, r3]
0002419c: lsls       r2, r2, #0x11
0002419e: lsrs       r2, r2, #0x19
000241a0: lsls       r3, r2, #4
000241a2: ldr        r4, [pc, #0x2a8]
000241a4: adds       r3, r4, r3
000241a6: movs       r4, #0x83
000241a8: lsls       r4, r4, #2
000241aa: ldr        r4, [r3, r4]
000241ac: movs       r3, #0
000241ae: cmp        r0, r4
000241b0: bhs        #0x241b4
000241b2: mvns       r3, r3
000241b4: subs       r0, r3, r2
000241b6: adds       r0, r0, r1
000241b8: pop        {r4, r5, r7, pc}
000241ba: asrs       r3, r1, #6
000241bc: subs       r1, #8
000241be: asrs       r1, r1, #0xa
000241c0: adds       r4, r2, r1
000241c2: ldr        r1, [pc, #0x268]
000241c4: subs       r1, r1, r3
000241c6: b          #0x24250
000241c8: lsrs       r1, r1, #6
000241ca: ldr        r2, [pc, #0x250]
000241cc: adds       r1, r1, r2
000241ce: b          #0x240d8
000241d0: mov        r3, r0
000241d2: muls       r3, r0, r3
000241d4: cmp        r3, #5
000241d6: bne        #0x24216
000241d8: uxtb       r1, r0
000241da: lsls       r1, r1, #4
000241dc: ldr        r2, [pc, #0x234]
000241de: adds       r5, r2, r1
000241e0: mov        r4, r0
000241e2: bl         #0x24c5c
000241e6: mov        r2, r0
000241e8: mov        r0, r4
000241ea: lsrs       r1, r4, #3
000241ec: movs       r3, #1
000241ee: movs       r4, #0
000241f0: cmp        r2, #0x20
000241f2: ble        #0x241f6
000241f4: b          #0x24352
000241f6: cmp        r2, #0x16
000241f8: bgt        #0x241fc
000241fa: b          #0x2437e
000241fc: cmp        r2, #0x18
000241fe: bgt        #0x24202
00024200: b          #0x243d0
00024202: cmp        r2, #0x19
00024204: bne        #0x24208
00024206: b          #0x23ee4
00024208: cmp        r2, #0x1f
0002420a: bne        #0x2420e
0002420c: b          #0x2404a
0002420e: cmp        r2, #0x20
00024210: mov        r3, r4
00024212: beq        #0x24270
00024214: b          #0x23fa2
00024216: bl         #0x24d34
0002421a: pop        {r4, r5, r7, pc}
0002421c: bl         #0x24b44
00024220: pop        {r4, r5, r7, pc}
00024222: lsrs       r1, r1, #5
00024224: ldr        r2, [pc, #0x208]
00024226: adds       r1, r1, r2
00024228: lsrs       r2, r1, #1
0002422a: ldr        r3, [pc, #0x24c]
0002422c: cmp        r2, r3
0002422e: bne        #0x242e8
00024230: ldr        r0, [pc, #0x240]
00024232: pop        {r4, r5, r7, pc}
00024234: ldr        r3, [pc, #0x238]
00024236: adds       r1, r1, r3
00024238: lsrs       r2, r2, #8
0002423a: subs       r1, r1, r2
0002423c: bl         #0x24b78
00024240: pop        {r4, r5, r7, pc}
00024242: lsrs       r1, r1, #4
00024244: ldr        r2, [pc, #0x1e8]
00024246: adds       r1, r1, r2
00024248: adds       r1, r1, #6
0002424a: lsrs       r2, r1, #2
0002424c: ldr        r3, [pc, #0x1e4]
0002424e: subs       r4, r3, r2
00024250: lsls       r2, r0, #9
00024252: asrs       r3, r0, #0x17
00024254: adds       r3, #0x89
00024256: ldr        r0, [pc, #0x1c8]
00024258: bl         #0x24e40
0002425c: subs       r0, r4, r0
0002425e: pop        {r4, r5, r7, pc}
00024260: ldr        r2, [pc, #0x1ec]
00024262: cmp        r0, r2
00024264: bhs        #0x2432a
00024266: asrs       r4, r0, #0x17
00024268: adds       r4, #0x7f
0002426a: ldr        r5, [pc, #0x1f8]
0002426c: ldm        r5, {r1, r2, r3, r5}
0002426e: ands       r3, r0
00024270: adds       r1, r3, r1
00024272: lsls       r1, r4
00024274: lsls       r3, r1, #0x13
00024276: lsrs       r4, r1, #0xf
00024278: adds       r4, r4, r3
0002427a: lsrs       r1, r1, #0xa
0002427c: muls       r1, r2, r1
0002427e: lsrs       r2, r1, #0x10
00024280: ldm        r5, {r1, r3, r5}
00024282: subs       r3, r3, r2
00024284: muls       r1, r3, r1
00024286: adds       r1, r1, r4
00024288: asrs       r2, r1, #0x10
0002428a: muls       r2, r2, r2
0002428c: lsrs       r2, r2, #9
0002428e: subs       r1, r1, r2
00024290: asrs       r4, r1, #8
00024292: lsls       r2, r3, #0x17
00024294: lsrs       r2, r2, #0x13
00024296: ldr        r2, [r5, r2]
00024298: lsrs       r5, r2, #0x18
0002429a: muls       r5, r4, r5
0002429c: asrs       r1, r1, #0x10
0002429e: lsrs       r4, r2, #8
000242a0: uxth       r4, r4
000242a2: muls       r4, r1, r4
000242a4: asrs       r1, r4, #8
000242a6: adds       r1, r1, r5
000242a8: asrs       r4, r1, #8
000242aa: lsrs       r1, r3, #9
000242ac: ldr        r3, [pc, #0x1b8]
000242ae: cmp        r0, r3
000242b0: bhi        #0x242dc
000242b2: movs       r3, #0x7d
000242b4: subs       r5, r3, r1
000242b6: subs       r2, r2, r4
000242b8: subs       r2, #0x84
000242ba: mov        r3, r2
000242bc: lsrs       r3, r5
000242be: lsrs       r4, r3, #0x10
000242c0: bne        #0x24304
000242c2: lsrs       r4, r2, #0x10
000242c4: muls       r3, r4, r3
000242c6: lsrs       r3, r3, #0x10
000242c8: subs       r2, r2, r3
000242ca: bpl        #0x24322
000242cc: adds       r2, #0x80
000242ce: uxtb       r3, r2
000242d0: cmp        r3, #5
000242d2: bhs        #0x24376
000242d4: b          #0x2434c
000242d6: mov        r8, r8
000242d8: .word      0x000104e0
000242dc: subs       r2, r2, r4
000242de: bmi        #0x24346
000242e0: subs       r2, #0x42
000242e2: bl         #0x24da0
000242e6: pop        {r4, r5, r7, pc}
000242e8: ldr        r3, [pc, #0x190]
000242ea: b          #0x2424e
000242ec: .word      0x00010144
000242f0: .word      0x3f400001
000242f4: .word      0x0000aaa7
000242f8: .word      0xfc000001
000242fc: .word      0x000104cc
00024300: .word      0x3e000001
00024304: lsrs       r4, r3, #6
00024306: muls       r4, r4, r4
00024308: lsrs       r4, r4, #0x14
0002430a: subs       r3, r3, r4
0002430c: uxth       r4, r3
0002430e: lsrs       r5, r2, #0x10
00024310: muls       r5, r4, r5
00024312: lsrs       r4, r5, #0x10
00024314: lsrs       r3, r3, #0x10
00024316: lsrs       r5, r2, #6
00024318: muls       r5, r3, r5
0002431a: lsrs       r3, r5, #0xa
0002431c: adds       r3, r3, r4
0002431e: subs       r2, r2, r3
00024320: bmi        #0x2436e
00024322: adds       r2, #0x42
00024324: bl         #0x24da0
00024328: pop        {r4, r5, r7, pc}
0002432a: ldr        r2, [pc, #0x128]
0002432c: cmp        r0, r2
0002432e: blo        #0x24332
00024330: b          #0x24100
00024332: ldr        r2, [pc, #0x124]
00024334: cmp        r0, r2
00024336: blo        #0x243b0
00024338: ldr        r2, [pc, #0x120]
0002433a: ldr        r1, [r1, r2]
0002433c: ldr        r2, [pc, #0x120]
0002433e: cmp        r0, r2
00024340: blo        #0x243ea
00024342: mov        r0, r1
00024344: pop        {r4, r5, r7, pc}
00024346: uxtb       r3, r2
00024348: cmp        r3, #8
0002434a: bhi        #0x24376
0002434c: bl         #0x24da0
00024350: pop        {r4, r5, r7, pc}
00024352: cmp        r2, #0x35
00024354: ble        #0x2439a
00024356: cmp        r2, #0x3d
00024358: ble        #0x243dc
0002435a: cmp        r2, #0x3e
0002435c: bne        #0x24360
0002435e: b          #0x23f28
00024360: cmp        r2, #0x42
00024362: beq        #0x243f6
00024364: cmp        r2, #0x51
00024366: mov        r4, r2
00024368: bne        #0x2436c
0002436a: b          #0x24096
0002436c: b          #0x23fa2
0002436e: adds       r2, #0x81
00024370: uxtb       r3, r2
00024372: cmp        r3, #0xa
00024374: blo        #0x2434c
00024376: lsls       r0, r1, #0x17
00024378: lsrs       r1, r2, #8
0002437a: adds       r0, r1, r0
0002437c: pop        {r4, r5, r7, pc}
0002437e: cmp        r2, #0xe
00024380: bgt        #0x243b6
00024382: movs       r1, #0x74
00024384: mvns       r3, r1
00024386: cmp        r2, #0xb
00024388: beq        #0x243ee
0002438a: cmp        r2, #0xd
0002438c: beq        #0x24390
0002438e: b          #0x23fa2
00024390: adds       r3, r3, #2
00024392: uxth       r5, r0
00024394: movs       r1, #0xd
00024396: mov        r2, r1
00024398: b          #0x23f04
0002439a: cmp        r2, #0x26
0002439c: bgt        #0x243c4
0002439e: cmp        r2, #0x21
000243a0: bne        #0x243a4
000243a2: b          #0x23fae
000243a4: cmp        r2, #0x26
000243a6: mov        r1, r2
000243a8: mov        r4, r2
000243aa: bne        #0x243ae
000243ac: b          #0x23ee6
000243ae: b          #0x23fa2
000243b0: bl         #0x24c5c
000243b4: pop        {r4, r5, r7, pc}
000243b6: cmp        r2, #0xf
000243b8: bne        #0x243bc
000243ba: b          #0x24042
000243bc: cmp        r2, #0x12
000243be: bne        #0x243c2
000243c0: b          #0x24284
000243c2: b          #0x23fa2
000243c4: cmp        r2, #0x27
000243c6: beq        #0x243f2
000243c8: cmp        r2, #0x33
000243ca: bne        #0x243ce
000243cc: b          #0x23f1c
000243ce: b          #0x23fa2
000243d0: cmp        r2, #0x17
000243d2: beq        #0x243fa
000243d4: cmp        r2, #0x18
000243d6: bne        #0x243da
000243d8: b          #0x23fea
000243da: b          #0x23fa2
000243dc: cmp        r2, #0x36
000243de: bne        #0x243e2
000243e0: b          #0x24094
000243e2: cmp        r2, #0x3c
000243e4: bne        #0x243e8
000243e6: b          #0x2426c
000243e8: b          #0x23fa2
000243ea: adds       r0, r1, #1
000243ec: pop        {r4, r5, r7, pc}
000243ee: mov        r1, r2
000243f0: b          #0x23ef4
000243f2: mov        r1, r2
000243f4: b          #0x23ef0
000243f6: mov        r3, r2
000243f8: b          #0x2408e
000243fa: uxth       r1, r0
000243fc: movs       r2, #0x17
000243fe: mov        r3, r2
00024400: mov        r4, r2
00024402: b          #0x23ffc
00024404: .word      0x17fffff8
00024408: .word      0x007fffff
0002440c: .word      0x00013284
00024410: .word      0x7e000001
00024414: .word      0x000104f4
00024418: .word      0x3efffcf4
0002441c: .word      0x0fff9e70
00024420: .word      0x0001329c
00024424: .word      0x3e800001
00024428: .word      0x3ef04a07
0002442c: .word      0x10fb5f98
00024430: .word      0x17fffff8
00024434: .word      0x44ffffff
00024438: .word      0x08000008
0002443c: .word      0x7f800001
00024440: .word      0x418aa122
00024444: .word      0xbea80000
00024448: .word      0xffffdb50
0002444c: .word      0x0001014c
00024450: .word      0xc2aeac50
00024454: .word      0xff800001
00024458: .word      0xc2cdbf37
0002445c: .word      0x00000fd4
00024460: .word      0xc2cff1b5
00024464: .word      0x0001328c
00024468: .word      0xc1b17218
0002446c: .word      0x000104d4
00024470: .word      0x3a800001
00024474: .word      0x3d708b74
00024478: .word      0x0f0f748b
0002447c: .word      0x4c7fffff
00024480: .word      0x3d800003

eik_tanh:
00024484: push       {r4, r5, r7, lr}
00024486: add        r7, sp, #8
00024488: lsls       r1, r0, #1
0002448a: bmi        #0x24498
0002448c: asrs       r2, r1, #0x18
0002448e: cmp        r2, #0x7c
00024490: bhs        #0x244b0
00024492: cmp        r2, #0x73
00024494: bhs        #0x244ec
00024496: pop        {r4, r5, r7, pc}
00024498: ldr        r4, [pc, #0x2f8]
0002449a: ldm        r4!, {r2, r3}
0002449c: adds       r4, r3, r1
0002449e: bmi        #0x2455e
000244a0: lsrs       r3, r0, #0x1f
000244a2: lsls       r3, r3, #3
000244a4: lsrs       r5, r4, #0x17
000244a6: subs       r5, r5, #1
000244a8: cmp        r5, #0xf8
000244aa: bhi        #0x24594
000244ac: ldr        r0, [r2, r3]
000244ae: pop        {r4, r5, r7, pc}
000244b0: lsrs       r1, r0, #0xc
000244b2: ldr        r3, [pc, #0x2e4]
000244b4: ands       r3, r1
000244b6: ldr        r1, [pc, #0x2e4]
000244b8: adds       r4, r1, r3
000244ba: cmp        r2, #0x7f
000244bc: bne        #0x24536
000244be: uxth       r1, r0
000244c0: ldm        r4, {r2, r3, r4}
000244c2: uxth       r5, r4
000244c4: muls       r5, r1, r5
000244c6: adds       r3, r5, r3
000244c8: uxtb       r5, r2
000244ca: muls       r5, r1, r5
000244cc: subs       r4, r4, r5
000244ce: lsrs       r4, r4, #0xf
000244d0: muls       r4, r1, r4
000244d2: subs       r2, r2, r4
000244d4: lsrs       r2, r2, #0xf
000244d6: muls       r2, r1, r2
000244d8: lsrs       r1, r2, #0xf
000244da: adds       r1, r3, r1
000244dc: lsls       r2, r1, #0x17
000244de: lsrs       r2, r2, #0x19
000244e0: beq        #0x245d6
000244e2: ldr        r2, [pc, #0x2f0]
000244e4: ands       r0, r2
000244e6: asrs       r1, r1, #9
000244e8: adds       r0, r1, r0
000244ea: pop        {r4, r5, r7, pc}
000244ec: cmp        r2, #0x77
000244ee: bls        #0x245aa
000244f0: ldr        r4, [pc, #0x2cc]
000244f2: ldm        r4!, {r1, r2, r3}
000244f4: ands       r1, r0
000244f6: lsrs       r4, r0, #0x10
000244f8: ands       r4, r3
000244fa: adds       r4, r2, r4
000244fc: lsrs       r2, r1, #0xe
000244fe: bne        #0x24508
00024500: ldr        r2, [r4, #0xc]
00024502: subs       r2, r1, r2
00024504: bpl        #0x24508
00024506: b          #0x246a0
00024508: ldm        r4, {r2, r3, r4}
0002450a: uxtb       r5, r2
0002450c: muls       r5, r1, r5
0002450e: adds       r2, r5, r2
00024510: lsrs       r2, r2, #0x10
00024512: lsrs       r5, r1, #4
00024514: muls       r2, r5, r2
00024516: lsrs       r2, r2, #0xc
00024518: adds       r2, r2, r3
0002451a: lsrs       r3, r2, #0x10
0002451c: muls       r3, r1, r3
0002451e: adds       r1, r3, r4
00024520: uxth       r2, r2
00024522: muls       r2, r5, r2
00024524: lsrs       r2, r2, #0xc
00024526: adds       r1, r1, r2
00024528: lsls       r2, r1, #0x12
0002452a: lsrs       r2, r2, #0x1b
0002452c: bne        #0x24530
0002452e: b          #0x246f2
00024530: lsrs       r1, r1, #0xe
00024532: subs       r0, r0, r1
00024534: pop        {r4, r5, r7, pc}
00024536: uxth       r1, r0
00024538: ldm        r4, {r2, r3, r4}
0002453a: uxtb       r5, r2
0002453c: muls       r5, r1, r5
0002453e: adds       r3, r5, r3
00024540: muls       r4, r1, r4
00024542: subs       r2, r2, r4
00024544: asrs       r2, r2, #0xf
00024546: muls       r2, r1, r2
00024548: asrs       r1, r2, #0xf
0002454a: adds       r2, r3, r1
0002454c: bmi        #0x24600
0002454e: lsls       r1, r0, #8
00024550: subs       r1, r1, r2
00024552: uxtb       r3, r2
00024554: cmp        r3, #3
00024556: blo        #0x24642
00024558: lsrs       r1, r1, #8
0002455a: subs       r0, r0, r1
0002455c: pop        {r4, r5, r7, pc}
0002455e: asrs       r1, r4, #0x11
00024560: lsls       r1, r1, #4
00024562: adds       r4, r2, r1
00024564: uxth       r1, r0
00024566: ldm        r4, {r2, r3, r4}
00024568: uxth       r5, r4
0002456a: muls       r5, r1, r5
0002456c: adds       r3, r5, r3
0002456e: uxtb       r5, r2
00024570: muls       r5, r1, r5
00024572: subs       r4, r4, r5
00024574: lsrs       r4, r4, #0xf
00024576: muls       r4, r1, r4
00024578: subs       r2, r2, r4
0002457a: lsrs       r2, r2, #0xf
0002457c: muls       r2, r1, r2
0002457e: lsrs       r1, r2, #0xf
00024580: adds       r1, r3, r1
00024582: lsrs       r2, r1, #9
00024584: lsls       r3, r1, #0x17
00024586: lsrs       r3, r3, #0x19
00024588: beq        #0x2461e
0002458a: lsrs       r0, r0, #0x1c
0002458c: ldr        r1, [pc, #0x258]
0002458e: ldr        r0, [r1, r0]
00024590: adds       r0, r0, r2
00024592: pop        {r4, r5, r7, pc}
00024594: asrs       r4, r4, #0xf
00024596: cmp        r4, #0xdf
00024598: bls        #0x245e2
0002459a: movs       r4, #0xff
0002459c: lsls       r4, r4, #0x18
0002459e: cmp        r1, r4
000245a0: bls        #0x24680
000245a2: movs       r1, #1
000245a4: lsls       r1, r1, #0x16
000245a6: orrs       r0, r1
000245a8: pop        {r4, r5, r7, pc}
000245aa: bne        #0x24662
000245ac: lsls       r1, r0, #9
000245ae: lsrs       r1, r1, #0x11
000245b0: beq        #0x246a8
000245b2: lsrs       r1, r0, #8
000245b4: uxth       r1, r1
000245b6: mov        r2, r1
000245b8: muls       r2, r1, r2
000245ba: lsrs       r2, r2, #0x10
000245bc: ldr        r3, [pc, #0x20c]
000245be: muls       r3, r2, r3
000245c0: lsrs       r2, r3, #0x10
000245c2: muls       r2, r1, r2
000245c4: ldr        r1, [pc, #0x208]
000245c6: adds       r1, r2, r1
000245c8: lsls       r2, r1, #9
000245ca: lsrs       r2, r2, #0x1b
000245cc: bne        #0x245d0
000245ce: b          #0x246f0
000245d0: lsrs       r1, r1, #0x17
000245d2: subs       r0, r0, r1
000245d4: pop        {r4, r5, r7, pc}
000245d6: movs       r2, #0xff
000245d8: lsls       r2, r2, #0x18
000245da: ands       r2, r0
000245dc: lsrs       r3, r1, #9
000245de: adds       r4, r3, r2
000245e0: b          #0x2462a
000245e2: ldr        r0, [r2, r3]
000245e4: lsls       r3, r4, #4
000245e6: adds       r3, r2, r3
000245e8: ldr        r4, [pc, #0x1f0]
000245ea: ldr        r3, [r3, r4]
000245ec: lsls       r3, r3, #0x12
000245ee: lsrs       r3, r3, #0x1a
000245f0: subs       r0, r0, r3
000245f2: lsls       r3, r3, #4
000245f4: adds       r2, r2, r3
000245f6: ldr        r3, [pc, #0x1e8]
000245f8: ldr        r2, [r2, r3]
000245fa: cmp        r1, r2
000245fc: blo        #0x246ba
000245fe: b          #0x24496
00024600: lsls       r1, r2, #1
00024602: bmi        #0x2468a
00024604: ldr        r1, [pc, #0x198]
00024606: adds       r1, r2, r1
00024608: bmi        #0x246be
0002460a: ldr        r1, [pc, #0x1a0]
0002460c: adds       r4, r2, r1
0002460e: lsls       r1, r4, #0x1b
00024610: lsrs       r1, r1, #0x1d
00024612: beq        #0x24714
00024614: lsls       r1, r0, #5
00024616: subs       r1, r1, r4
00024618: lsrs       r1, r1, #5
0002461a: subs       r0, r0, r1
0002461c: pop        {r4, r5, r7, pc}
0002461e: movs       r3, #0xff
00024620: lsls       r3, r3, #0x18
00024622: mov        r4, r0
00024624: ands       r4, r3
00024626: adds       r2, r4, r2
00024628: adds       r4, r2, r3
0002462a: ldr        r2, [pc, #0x190]
0002462c: lsrs       r1, r1, #5
0002462e: adds       r1, r1, r2
00024630: lsls       r2, r0, #9
00024632: lsrs       r0, r0, #0x17
00024634: uxtb       r3, r0
00024636: subs       r3, #0x76
00024638: ldr        r0, [pc, #0x16c]
0002463a: bl         #0x24e40
0002463e: adds       r0, r0, r4
00024640: pop        {r4, r5, r7, pc}
00024642: subs       r1, #8
00024644: lsrs       r1, r1, #8
00024646: subs       r4, r0, r1
00024648: ldr        r3, [pc, #0x170]
0002464a: adds       r3, #0x10
0002464c: lsrs       r1, r2, #4
0002464e: orrs       r1, r3
00024650: lsls       r2, r0, #9
00024652: lsrs       r0, r0, #0x17
00024654: uxtb       r3, r0
00024656: subs       r3, #0x76
00024658: ldr        r0, [pc, #0x14c]
0002465a: bl         #0x24e40
0002465e: adds       r0, r4, r0
00024660: pop        {r4, r5, r7, pc}
00024662: subs       r2, #0x73
00024664: beq        #0x246b2
00024666: lsls       r2, r2, #3
00024668: ldr        r3, [pc, #0x158]
0002466a: adds       r4, r3, r2
0002466c: lsls       r2, r0, #9
0002466e: ldm        r4, {r3, r4}
00024670: lsrs       r2, r4
00024672: beq        #0x246d6
00024674: lsls       r2, r2, #4
00024676: ldr        r2, [r3, r2]
00024678: adds       r1, r2, r1
0002467a: lsrs       r1, r1, #0x18
0002467c: subs       r0, r0, r1
0002467e: pop        {r4, r5, r7, pc}
00024680: ldr        r0, [r2, r3]
00024682: ldr        r2, [pc, #0x160]
00024684: cmp        r1, r2
00024686: blo        #0x246ba
00024688: b          #0x24496
0002468a: lsls       r2, r0, #8
0002468c: adds       r1, #0x81
0002468e: uxtb       r3, r1
00024690: cmp        r3, #6
00024692: bhi        #0x246ce
00024694: subs       r2, r1, r2
00024696: asrs       r2, r2, #8
00024698: adds       r2, r0, r2
0002469a: adds       r4, r2, #1
0002469c: ldr        r2, [pc, #0x118]
0002469e: b          #0x2462c
000246a0: mov        r1, r4
000246a2: bl         #0x24fa4
000246a6: pop        {r4, r5, r7, pc}
000246a8: uxtb       r1, r0
000246aa: cmp        r1, #0x2b
000246ac: blo        #0x2473a
000246ae: subs       r0, #0x2b
000246b0: pop        {r4, r5, r7, pc}
000246b2: ldr        r2, [pc, #0x114]
000246b4: cmp        r1, r2
000246b6: bhi        #0x246ba
000246b8: b          #0x24496
000246ba: subs       r0, r0, #1
000246bc: pop        {r4, r5, r7, pc}
000246be: lsls       r2, r0, #6
000246c0: subs       r2, r2, r1
000246c2: lsls       r3, r1, #0x1a
000246c4: lsrs       r3, r3, #0x1c
000246c6: beq        #0x2475c
000246c8: lsrs       r1, r2, #6
000246ca: subs       r0, r0, r1
000246cc: pop        {r4, r5, r7, pc}
000246ce: subs       r1, r2, r1
000246d0: asrs       r1, r1, #8
000246d2: subs       r0, r0, r1
000246d4: pop        {r4, r5, r7, pc}
000246d6: ldr        r2, [pc, #0x100]
000246d8: adds       r2, #0xff
000246da: ands       r2, r0
000246dc: ldr        r3, [r3]
000246de: adds       r1, r3, r1
000246e0: lsrs       r1, r1, #0x18
000246e2: cmp        r2, r1
000246e4: bhs        #0x2476a
000246e6: adds       r0, r0, r2
000246e8: lsls       r1, r1, #1
000246ea: subs       r0, r0, r1
000246ec: adds       r0, r0, #1
000246ee: pop        {r4, r5, r7, pc}
000246f0: lsrs       r1, r1, #9
000246f2: lsrs       r1, r1, #0xe
000246f4: subs       r4, r0, r1
000246f6: lsrs       r2, r4, #0x16
000246f8: movs       r3, #0x1e
000246fa: bics       r3, r2
000246fc: movs       r2, #0xf
000246fe: lsls       r2, r2, #0xd
00024700: lsls       r1, r1, #2
00024702: subs       r5, r1, #2
00024704: muls       r2, r5, r2
00024706: lsls       r2, r3
00024708: movs       r1, #3
0002470a: muls       r1, r5, r1
0002470c: bl         #0x25018
00024710: adds       r0, r4, r0
00024712: pop        {r4, r5, r7, pc}
00024714: movs       r1, #0xff
00024716: lsls       r5, r1, #0x18
00024718: ands       r5, r0
0002471a: lsrs       r1, r4, #4
0002471c: ldr        r2, [pc, #0x90]
0002471e: adds       r1, r1, r2
00024720: lsls       r2, r0, #9
00024722: lsrs       r0, r0, #0x17
00024724: uxtb       r3, r0
00024726: subs       r3, #0x76
00024728: ldr        r0, [pc, #0x7c]
0002472a: bl         #0x24e40
0002472e: lsrs       r1, r4, #5
00024730: adds       r1, r5, r1
00024732: adds       r0, r1, r0
00024734: ldr        r1, [pc, #0x7c]
00024736: adds       r0, r0, r1
00024738: pop        {r4, r5, r7, pc}
0002473a: mov        r2, r0
0002473c: muls       r2, r0, r2
0002473e: cmp        r2, #5
00024740: bne        #0x2476e
00024742: lsls       r1, r1, #4
00024744: ldr        r2, [pc, #0x54]
00024746: adds       r4, r2, r1
00024748: mov        r5, r0
0002474a: bl         #0x24c5c
0002474e: cmp        r0, #7
00024750: beq        #0x24774
00024752: mov        r1, r0
00024754: cmp        r0, #9
00024756: bne        #0x24778
00024758: mov        r0, r5
0002475a: b          #0x2449a
0002475c: subs       r2, r2, #1
0002475e: lsrs       r2, r2, #6
00024760: subs       r4, r0, r2
00024762: lsrs       r1, r1, #4
00024764: ldr        r2, [pc, #0x3c]
00024766: adds       r1, r1, r2
00024768: b          #0x24650
0002476a: subs       r0, r0, r1
0002476c: pop        {r4, r5, r7, pc}
0002476e: adds       r0, r0, r1
00024770: subs       r0, #0x55
00024772: pop        {r4, r5, r7, pc}
00024774: mov        r0, r5
00024776: b          #0x244be
00024778: uxth       r0, r1
0002477a: cmp        r0, #0x4d
0002477c: mov        r0, r5
0002477e: bne        #0x24782
00024780: b          #0x244fc
00024782: cmp        r1, #0x51
00024784: bne        #0x24788
00024786: b          #0x244f2
00024788: cmp        r1, #0x53
0002478a: mov        r2, r1
0002478c: bne        #0x24790
0002478e: b          #0x2466e
00024790: b          #0x24564
00024792: mov        r8, r8
00024794: .word      0x00013ce8
00024798: .word      0x00001ff0
0002479c: .word      0x000104f4
000247a0: .word      0xe0000060
000247a4: .word      0x0a000002
000247a8: .word      0x00013d1c
000247ac: .word      0x20000070
000247b0: .word      0x06000001
000247b4: .word      0xfa000001
000247b8: .word      0x10000004
000247bc: .word      0x17fffff8
000247c0: .word      0x00013d10
000247c4: .word      0x00013cf0
000247c8: .word      0x73713745
000247cc: .word      0x0000aaaa
000247d0: .word      0x00436db8
000247d4: .word      0xff800000
000247d8: .word      0x007fff00
000247dc: .word      0xfffff1e0
000247e0: .word      0xfffffd1c
000247e4: .word      0x82205968
000247e8: .word      0x00013ec0

eik_exp:
000247ec: push       {r4, r5, r7, lr}
000247ee: add        r7, sp, #8
000247f0: asrs       r2, r0, #0x17
000247f2: adds       r2, #0x8a
000247f4: cmp        r2, #0xb
000247f6: bls        #0x2486c
000247f8: ble        #0x248b0
000247fa: cmp        r2, #0xff
000247fc: bls        #0x248d6
000247fe: uxtb       r2, r2
00024800: cmp        r2, #0xb
00024802: bls        #0x248fc
00024804: cmp        r2, #0xe
00024806: bls        #0x2483c
00024808: cmp        r2, #0x89
0002480a: bne        #0x24824
0002480c: mov        r1, r0
0002480e: muls       r1, r0, r1
00024810: cmp        r1, #0xd
00024812: beq        #0x24816
00024814: b          #0x24976
00024816: lsrs       r1, r0, #5
00024818: lsls       r2, r0, #1
0002481a: lsrs       r0, r0, #0xa
0002481c: mov        r0, r1
0002481e: bne        #0x247f4
00024820: mov        r0, r1
00024822: pop        {r4, r5, r7, pc}
00024824: cmp        r2, #0xf
00024826: bne        #0x24836
00024828: ldr        r1, [pc, #0x2ac]
0002482a: cmp        r0, r1
0002482c: bls        #0x2483c
0002482e: adds       r1, r1, #2
00024830: cmp        r0, r1
00024832: bhi        #0x24836
00024834: b          #0x249f6
00024836: ldr        r0, [pc, #0x2a4]
00024838: ldr        r0, [r0]
0002483a: pop        {r4, r5, r7, pc}
0002483c: movs       r1, #0x1e
0002483e: subs       r3, r1, r2
00024840: lsls       r0, r0, #9
00024842: lsrs       r1, r0, #0xf
00024844: ldr        r4, [pc, #0x29c]
00024846: muls       r4, r1, r4
00024848: lsrs       r1, r4, #1
0002484a: ldr        r4, [pc, #0x29c]
0002484c: adds       r1, r1, r4
0002484e: lsrs       r1, r3
00024850: ldr        r3, [pc, #0x298]
00024852: muls       r3, r1, r3
00024854: lsrs       r3, r3, #0x10
00024856: lsls       r0, r2
00024858: adds       r3, r3, r0
0002485a: ldr        r2, [pc, #0x294]
0002485c: ldm        r2!, {r0, r4}
0002485e: ldr        r2, [r2]
00024860: adds       r1, r0, r1
00024862: movs       r0, #9
00024864: muls       r4, r1, r4
00024866: rors       r1, r0
00024868: subs       r0, r4, r3
0002486a: b          #0x24916
0002486c: lsls       r1, r2, #5
0002486e: ldr        r2, [pc, #0x284]
00024870: adds       r5, r2, r1
00024872: ldm        r5, {r1, r2, r3, r4, r5}
00024874: muls       r3, r0, r3
00024876: lsrs       r0, r0, #9
00024878: muls       r0, r1, r0
0002487a: adds       r0, r0, r5
0002487c: lsrs       r1, r0, #0xf
0002487e: muls       r4, r1, r4
00024880: rors       r1, r5
00024882: adds       r0, r4, r3
00024884: lsrs       r3, r1, #0x13
00024886: ldr        r2, [r2, r3]
00024888: lsls       r3, r2, #0xa
0002488a: lsrs       r3, r3, #0x11
0002488c: lsrs       r4, r2, #0x16
0002488e: asrs       r5, r0, #0xa
00024890: muls       r5, r4, r5
00024892: asrs       r4, r5, #0x11
00024894: adds       r3, r4, r3
00024896: asrs       r4, r0, #0x10
00024898: muls       r4, r3, r4
0002489a: asrs       r3, r4, #9
0002489c: adds       r3, r3, r5
0002489e: asrs       r3, r3, #9
000248a0: adds       r2, r3, r2
000248a2: bpl        #0x24938
000248a4: uxtb       r3, r2
000248a6: cmp        r3, #5
000248a8: bhs        #0x2496e
000248aa: bl         #0x24ed0
000248ae: pop        {r4, r5, r7, pc}
000248b0: mvns       r1, r2
000248b2: cmp        r1, #0xf
000248b4: bhi        #0x24990
000248b6: lsls       r2, r1, #0x17
000248b8: adds       r0, r2, r0
000248ba: cmp        r1, #7
000248bc: blo        #0x2499e
000248be: subs       r1, r1, #7
000248c0: lsls       r0, r0, #8
000248c2: lsrs       r0, r1
000248c4: lsrs       r1, r0, #0x10
000248c6: muls       r1, r1, r1
000248c8: lsrs       r1, r1, #0x11
000248ca: subs       r0, r1, r0
000248cc: lsrs       r0, r0, #0x17
000248ce: ldr        r1, [pc, #0x264]
000248d0: adds       r0, r0, r1
000248d2: lsrs       r0, r0, #1
000248d4: pop        {r4, r5, r7, pc}
000248d6: cmp        r2, #0xf1
000248d8: blo        #0x2498c
000248da: cmp        r2, #0xf8
000248dc: bhi        #0x249bc
000248de: ldr        r1, [pc, #0x220]
000248e0: ands       r0, r1
000248e2: ldr        r1, [pc, #0x244]
000248e4: subs       r0, r1, r0
000248e6: subs       r2, #0xf1
000248e8: lsls       r0, r2
000248ea: asrs       r1, r0, #0x10
000248ec: muls       r1, r1, r1
000248ee: lsrs       r1, r1, #0x10
000248f0: subs       r0, r1, r0
000248f2: lsrs       r0, r0, #0x16
000248f4: ldr        r1, [pc, #0x234]
000248f6: adds       r0, r0, r1
000248f8: lsrs       r0, r0, #2
000248fa: pop        {r4, r5, r7, pc}
000248fc: lsls       r1, r2, #5
000248fe: ldr        r2, [pc, #0x1f4]
00024900: adds       r5, r2, r1
00024902: ldm        r5!, {r1, r2, r3, r4}
00024904: muls       r3, r0, r3
00024906: ldr        r5, [r5, #4]
00024908: lsrs       r0, r0, #9
0002490a: muls       r0, r1, r0
0002490c: subs       r0, r5, r0
0002490e: lsrs       r1, r0, #0xf
00024910: muls       r4, r1, r4
00024912: rors       r1, r5
00024914: subs       r0, r3, r4
00024916: lsrs       r3, r1, #0x13
00024918: ldr        r2, [r2, r3]
0002491a: lsls       r3, r2, #0xa
0002491c: lsrs       r3, r3, #0x11
0002491e: lsrs       r4, r2, #0x16
00024920: asrs       r5, r0, #0xa
00024922: muls       r5, r4, r5
00024924: asrs       r4, r5, #0x11
00024926: subs       r3, r3, r4
00024928: asrs       r4, r0, #0x10
0002492a: muls       r4, r3, r4
0002492c: asrs       r3, r4, #9
0002492e: adds       r3, r3, r5
00024930: asrs       r3, r3, #9
00024932: subs       r2, r2, r3
00024934: bmi        #0x24968
00024936: rsbs       r0, r0, #0
00024938: movs       r3, #0x17
0002493a: rors       r1, r3
0002493c: lsrs       r3, r2, #0x1e
0002493e: bne        #0x2494e
00024940: ldr        r3, [pc, #0x1f8]
00024942: adds       r0, r0, r3
00024944: lsrs       r2, r2, #1
00024946: ldr        r3, [pc, #0x1f8]
00024948: adds       r2, r2, r3
0002494a: adds       r1, r1, #1
0002494c: b          #0x24958
0002494e: ldr        r3, [pc, #0x1e8]
00024950: adds       r0, r0, r3
00024952: subs       r1, r1, #1
00024954: lsls       r2, r2, #1
00024956: subs       r2, #0x7f
00024958: lsls       r3, r2, #0x18
0002495a: lsrs       r3, r3, #0x1c
0002495c: beq        #0x24982
0002495e: lsrs       r0, r2, #8
00024960: lsrs       r1, r1, #9
00024962: lsls       r1, r1, #0x17
00024964: adds       r0, r0, r1
00024966: pop        {r4, r5, r7, pc}
00024968: uxtb       r3, r2
0002496a: cmp        r3, #7
0002496c: blo        #0x24996
0002496e: lsls       r0, r1, #0x17
00024970: lsrs       r1, r2, #8
00024972: adds       r0, r1, r0
00024974: pop        {r4, r5, r7, pc}
00024976: lsls       r1, r0, #9
00024978: beq        #0x24980
0002497a: movs       r1, #1
0002497c: lsls       r1, r1, #0x16
0002497e: orrs       r0, r1
00024980: pop        {r4, r5, r7, pc}
00024982: movs       r3, #9
00024984: rors       r1, r3
00024986: bl         #0x24ed0
0002498a: pop        {r4, r5, r7, pc}
0002498c: cmp        r2, #0x89
0002498e: bls        #0x249e0
00024990: ldr        r0, [pc, #0x164]
00024992: ldr        r0, [r0]
00024994: pop        {r4, r5, r7, pc}
00024996: rsbs       r0, r0, #0
00024998: bl         #0x24ed0
0002499c: pop        {r4, r5, r7, pc}
0002499e: lsls       r0, r0, #7
000249a0: lsrs       r0, r1
000249a2: ldr        r1, [pc, #0x18c]
000249a4: adds       r1, r0, r1
000249a6: asrs       r2, r1, #0x10
000249a8: muls       r2, r2, r2
000249aa: lsrs       r2, r2, #9
000249ac: subs       r1, r1, r2
000249ae: asrs       r4, r1, #0x10
000249b0: lsls       r1, r1, #0x10
000249b2: lsrs       r1, r1, #0x1a
000249b4: beq        #0x24a22
000249b6: ldr        r0, [pc, #0x16c]
000249b8: subs       r0, r0, r4
000249ba: pop        {r4, r5, r7, pc}
000249bc: mvns       r1, r2
000249be: lsls       r0, r0, #7
000249c0: lsls       r2, r1, #0x1e
000249c2: adds       r0, r2, r0
000249c4: rors       r0, r1
000249c6: ldr        r1, [pc, #0x158]
000249c8: adds       r1, r0, r1
000249ca: lsrs       r2, r1, #0x10
000249cc: muls       r2, r2, r2
000249ce: lsrs       r2, r2, #9
000249d0: adds       r2, r2, r1
000249d2: lsrs       r1, r2, #0x11
000249d4: lsls       r2, r2, #0xf
000249d6: lsrs       r2, r2, #0x19
000249d8: ldr        r2, [pc, #0x148]
000249da: beq        #0x24a30
000249dc: adds       r0, r1, r2
000249de: pop        {r4, r5, r7, pc}
000249e0: cmp        r2, #0xf
000249e2: bhi        #0x249fe
000249e4: bne        #0x24a3e
000249e6: ldr        r1, [pc, #0x120]
000249e8: cmp        r0, r1
000249ea: blo        #0x24a72
000249ec: ldr        r1, [pc, #0x12c]
000249ee: cmp        r0, r1
000249f0: bhs        #0x24a3a
000249f2: movs       r0, #1
000249f4: pop        {r4, r5, r7, pc}
000249f6: lsls       r0, r0, #7
000249f8: ldr        r1, [pc, #0xe4]
000249fa: adds       r0, r0, r1
000249fc: pop        {r4, r5, r7, pc}
000249fe: cmp        r2, #0x89
00024a00: bne        #0x24a3a
00024a02: uxtb       r1, r0
00024a04: lsls       r1, r1, #4
00024a06: ldr        r2, [pc, #0xf4]
00024a08: adds       r2, r2, r1
00024a0a: mov        r3, r0
00024a0c: muls       r3, r0, r3
00024a0e: cmp        r3, #0x1d
00024a10: beq        #0x24a86
00024a12: movs       r1, #5
00024a14: muls       r1, r0, r1
00024a16: cmp        r3, #0x35
00024a18: bne        #0x24a8a
00024a1a: lsls       r5, r0, #5
00024a1c: lsrs       r4, r0, #3
00024a1e: movs       r3, #0x35
00024a20: b          #0x24876
00024a22: rsbs       r0, r0, #0
00024a24: bl         #0x250b0
00024a28: subs       r0, r0, r4
00024a2a: ldr        r1, [pc, #0xf8]
00024a2c: adds       r0, r0, r1
00024a2e: pop        {r4, r5, r7, pc}
00024a30: adds       r4, r1, r2
00024a32: bl         #0x250b0
00024a36: subs       r0, r4, r0
00024a38: pop        {r4, r5, r7, pc}
00024a3a: movs       r0, #0
00024a3c: pop        {r4, r5, r7, pc}
00024a3e: ldr        r1, [pc, #0xc4]
00024a40: movs       r3, #0x1e
00024a42: subs       r3, r3, r2
00024a44: lsls       r0, r0, #9
00024a46: lsrs       r4, r0, #0xf
00024a48: ldr        r5, [pc, #0x98]
00024a4a: muls       r5, r4, r5
00024a4c: lsrs       r4, r0, #0x12
00024a4e: adds       r4, r5, r4
00024a50: lsrs       r4, r4, #1
00024a52: adds       r1, r1, r4
00024a54: lsrs       r1, r3
00024a56: ldr        r3, [pc, #0x94]
00024a58: muls       r3, r1, r3
00024a5a: lsrs       r3, r3, #0x10
00024a5c: lsls       r0, r2
00024a5e: adds       r3, r3, r0
00024a60: ldr        r2, [pc, #0xb0]
00024a62: ldm        r2!, {r0, r4}
00024a64: ldr        r2, [r2]
00024a66: subs       r1, r0, r1
00024a68: movs       r0, #9
00024a6a: muls       r4, r1, r4
00024a6c: rors       r1, r0
00024a6e: subs       r0, r4, r3
00024a70: b          #0x24884
00024a72: ldr        r1, [pc, #0x9c]
00024a74: cmp        r0, r1
00024a76: bls        #0x24a9a
00024a78: adds       r1, #0x14
00024a7a: cmp        r0, r1
00024a7c: bhs        #0x24ab4
00024a7e: lsls       r0, r0, #6
00024a80: ldr        r1, [pc, #0x94]
00024a82: subs       r0, r1, r0
00024a84: pop        {r4, r5, r7, pc}
00024a86: mov        r5, r2
00024a88: b          #0x24872
00024a8a: lsrs       r4, r0, #1
00024a8c: muls       r4, r0, r4
00024a8e: cmp        r4, #0x25
00024a90: bne        #0x24a9e
00024a92: lsls       r5, r0, #5
00024a94: lsrs       r4, r0, #3
00024a96: movs       r3, #0x25
00024a98: b          #0x24908
00024a9a: ldr        r1, [pc, #0x70]
00024a9c: b          #0x24a40
00024a9e: cmp        r3, #0x15
00024aa0: beq        #0x24abe
00024aa2: cmp        r3, #0x3d
00024aa4: beq        #0x24aba
00024aa6: cmp        r3, #0x4d
00024aa8: bne        #0x24ac8
00024aaa: lsls       r3, r0, #5
00024aac: lsrs       r1, r0, #3
00024aae: cmp        r0, #0
00024ab0: bpl        #0x24a62
00024ab2: b          #0x2485c
00024ab4: bl         #0x24c5c
00024ab8: pop        {r4, r5, r7, pc}
00024aba: mov        r5, r2
00024abc: b          #0x24902
00024abe: lsrs       r1, r0, #7
00024ac0: cmp        r0, #0
00024ac2: bmi        #0x24ac6
00024ac4: b          #0x249be
00024ac6: b          #0x248b2
00024ac8: ldr        r1, [pc, #0x34]
00024aca: ands       r1, r0
00024acc: bne        #0x24ad0
00024ace: b          #0x24820
00024ad0: movs       r1, #1
00024ad2: lsls       r1, r1, #0x16
00024ad4: orrs       r0, r1
00024ad6: pop        {r4, r5, r7, pc}
00024ad8: .word      0x42b17215
00024adc: .word      0x00013ed0
00024ae0: .word      0x26c6f404
00024ae4: .word      0x00005c55
00024ae8: .word      0x5c5540a0
00024aec: .word      0x00002d78
00024af0: .word      0x00013eb4
00024af4: .word      0x00013d28
00024af8: .word      0x00013ec0
00024afc: .word      0x000104f4
00024b00: .word      0x007fffff
00024b04: .word      0x5c553492
00024b08: .word      0xc2cdbf37
00024b0c: .word      0x5c553172
00024b10: .word      0xc2aeac3f
00024b14: .word      0x00013ea8
00024b18: .word      0xac2b13e6
00024b1c: .word      0xc2cff1b5
00024b20: .word      0x000b0040
00024b24: .word      0x3f7ffffb
00024b28: .word      0xff800000
00024b2c: .word      0xfe000002
00024b30: .word      0xfffb82f8
00024b34: .word      0x7efffe01
00024b38: .word      0xb17217f8
00024b3c: .word      0x4e8de808
00024b40: .word      0x80000042

t_drb:
00024b44: push       {r4, r5, r7, lr}
00024b46: add        r7, sp, #8
00024b48: movs       r3, #0x73
00024b4a: lsls       r3, r3, #2
00024b4c: subs       r4, r3, r2
00024b4e: lsrs       r2, r4, #7
00024b50: lsls       r1, r1, #0x1d
00024b52: lsrs       r1, r1, #6
00024b54: ldr        r3, [pc, #0x1c]
00024b56: cmp        r4, #0
00024b58: bmi        #0x24b68
00024b5a: movs       r5, #0x70
00024b5c: ands       r4, r5
00024b5e: beq        #0x24b68
00024b60: adds       r0, r3, r1
00024b62: adds       r0, r0, r2
00024b64: adds       r0, r0, #1
00024b66: pop        {r4, r5, r7, pc}
00024b68: adds       r1, r1, r3
00024b6a: adds       r1, r1, r2
00024b6c: bl         #0x24b78
00024b70: pop        {r4, r5, r7, pc}
00024b72: mov        r8, r8
00024b74: .word      0x38ffffff

t_mn:
00024b78: push       {r4, r5, r6, r7, lr}
00024b7a: add        r7, sp, #0xc
00024b7c: lsls       r3, r0, #9
00024b7e: asrs       r0, r0, #0x17
00024b80: adds       r0, #0x88
00024b82: lsrs       r2, r3, #0x11
00024b84: lsls       r3, r0
00024b86: ldr        r4, [pc, #0xa8]
00024b88: muls       r4, r2, r4
00024b8a: ldr        r2, [pc, #0xa8]
00024b8c: adds       r2, r4, r2
00024b8e: asrs       r5, r2, #0xc
00024b90: lsls       r5, r0
00024b92: asrs       r2, r5, #0xf
00024b94: ldr        r0, [pc, #0xa0]
00024b96: muls       r0, r2, r0
00024b98: subs       r0, r0, r3
00024b9a: ldr        r3, [pc, #0xa0]
00024b9c: adds       r0, r0, r3
00024b9e: lsls       r4, r2, #0x17
00024ba0: lsrs       r3, r4, #0x16
00024ba2: ldr        r6, [pc, #0x9c]
00024ba4: ldrh       r3, [r6, r3]
00024ba6: asrs       r5, r5, #0x18
00024ba8: ldr        r6, [pc, #0x98]
00024baa: muls       r6, r5, r6
00024bac: asrs       r5, r6, #2
00024bae: adds       r5, r5, r3
00024bb0: adds       r5, #0x18
00024bb2: beq        #0x24c2e
00024bb4: lsls       r6, r0, #8
00024bb6: ldr        r3, [pc, #0x94]
00024bb8: ands       r3, r6
00024bba: adds       r5, r5, r3
00024bbc: asrs       r3, r5, #8
00024bbe: asrs       r0, r0, #0x10
00024bc0: ldr        r6, [pc, #0x8c]
00024bc2: muls       r6, r0, r6
00024bc4: asrs       r6, r6, #0xe
00024bc6: muls       r6, r0, r6
00024bc8: lsrs       r6, r6, #0xb
00024bca: subs       r3, r3, r6
00024bcc: muls       r3, r0, r3
00024bce: asrs       r3, r3, #0xf
00024bd0: mov        r6, r0
00024bd2: muls       r6, r0, r6
00024bd4: subs       r5, r6, r5
00024bd6: adds       r5, r5, r3
00024bd8: ldr        r3, [pc, #0x6c]
00024bda: subs       r6, r3, r2
00024bdc: lsrs       r3, r6, #9
00024bde: lsrs       r2, r4, #0x13
00024be0: ldr        r4, [pc, #0x70]
00024be2: adds       r2, r4, r2
00024be4: ldr        r2, [r2, #0xc]
00024be6: subs       r2, #0x84
00024be8: lsrs       r4, r6, #0xe
00024bea: beq        #0x24bf8
00024bec: mov        r4, r3
00024bee: subs       r4, #0x10
00024bf0: mov        r6, r2
00024bf2: lsrs       r6, r4
00024bf4: movs       r4, #0
00024bf6: b          #0x24c02
00024bf8: mov        r4, r2
00024bfa: lsrs       r4, r3
00024bfc: mov        r6, r2
00024bfe: rors       r6, r3
00024c00: lsrs       r6, r6, #0x10
00024c02: adds       r5, r5, r6
00024c04: asrs       r6, r5, #0x10
00024c06: adds       r4, r4, r6
00024c08: lsls       r0, r0, #8
00024c0a: subs       r4, r0, r4
00024c0c: lsls       r0, r1, #8
00024c0e: ldr        r6, [pc, #0x48]
00024c10: orrs       r6, r0
00024c12: lsrs       r0, r6, #7
00024c14: muls       r0, r4, r0
00024c16: uxth       r4, r5
00024c18: lsrs       r5, r6, #0x10
00024c1a: muls       r5, r4, r5
00024c1c: lsrs       r4, r5, #7
00024c1e: lsrs       r5, r1, #0x17
00024c20: adds       r3, r3, r5
00024c22: adds       r3, #9
00024c24: rors       r2, r3
00024c26: subs       r2, r2, r4
00024c28: adds       r0, r2, r0
00024c2a: lsrs       r0, r0, #0x1f
00024c2c: adds       r0, r0, r1
00024c2e: pop        {r4, r5, r6, r7, pc}
00024c30: .word      0xffffa3ab
00024c34: .word      0xd1d55d60
00024c38: .word      0xd3a37a02
00024c3c: .word      0xec19f782
00024c40: .word      0x000132b8
00024c44: .word      0x00005c61
00024c48: .word      0x000001ff
00024c4c: .word      0x00fffe00
00024c50: .word      0x0000aaab
00024c54: .word      0x000104f4
00024c58: .word      0x80000080

t_exp_den:
00024c5c: push       {r4, r5, r7, lr}
00024c5e: add        r7, sp, #8
00024c60: lsls       r1, r0, #9
00024c62: lsrs       r2, r1, #0xf
00024c64: ldr        r3, [pc, #0xa4]
00024c66: muls       r3, r2, r3
00024c68: lsrs       r1, r1, #0x12
00024c6a: adds       r1, r3, r1
00024c6c: lsrs       r1, r1, #1
00024c6e: ldr        r2, [pc, #0xa0]
00024c70: adds       r1, r1, r2
00024c72: lsrs       r1, r1, #0xf
00024c74: ldr        r2, [pc, #0x9c]
00024c76: subs       r2, r2, r1
00024c78: ldr        r3, [pc, #0x9c]
00024c7a: muls       r3, r2, r3
00024c7c: lsls       r0, r0, #0x18
00024c7e: subs       r0, r3, r0
00024c80: ldr        r3, [pc, #0x98]
00024c82: muls       r3, r1, r3
00024c84: lsrs       r3, r3, #0x10
00024c86: subs       r3, r0, r3
00024c88: asrs       r4, r3, #0x10
00024c8a: muls       r4, r4, r4
00024c8c: lsrs       r4, r4, #0xa
00024c8e: adds       r3, r4, r3
00024c90: asrs       r4, r3, #8
00024c92: lsls       r2, r2, #0x17
00024c94: lsrs       r2, r2, #0x13
00024c96: ldr        r5, [pc, #0x88]
00024c98: adds       r2, r5, r2
00024c9a: ldr        r2, [r2, #0xc]
00024c9c: lsrs       r5, r2, #0x18
00024c9e: muls       r5, r4, r5
00024ca0: asrs       r3, r3, #0x10
00024ca2: lsls       r4, r2, #8
00024ca4: lsrs       r4, r4, #0x11
00024ca6: muls       r4, r3, r4
00024ca8: asrs       r3, r4, #7
00024caa: adds       r3, r3, r5
00024cac: asrs       r3, r3, #9
00024cae: adds       r2, r3, r2
00024cb0: lsrs       r3, r2, #1
00024cb2: ldr        r4, [pc, #0x70]
00024cb4: adds       r4, r1, r4
00024cb6: lsrs       r4, r4, #9
00024cb8: lsrs       r2, r2, #0x1e
00024cba: bne        #0x24cc6
00024cbc: ldr        r0, [pc, #0x70]
00024cbe: adds       r0, r3, r0
00024cc0: lsrs       r0, r4
00024cc2: adds       r0, r0, #1
00024cc4: b          #0x24cd8
00024cc6: subs       r3, #0x41
00024cc8: mov        r5, r3
00024cca: lsrs       r5, r4
00024ccc: mov        r2, r5
00024cce: lsls       r2, r4
00024cd0: subs       r3, r3, r2
00024cd2: cmp        r3, #1
00024cd4: bls        #0x24cdc
00024cd6: adds       r0, r5, #1
00024cd8: lsrs       r0, r0, #1
00024cda: pop        {r4, r5, r7, pc}
00024cdc: lsls       r3, r5, #0x1f
00024cde: bne        #0x24ce4
00024ce0: lsrs       r0, r5, #1
00024ce2: pop        {r4, r5, r7, pc}
00024ce4: ldr        r3, [pc, #0x40]
00024ce6: adds       r0, r0, r3
00024ce8: ldr        r3, [pc, #0x40]
00024cea: subs       r1, r3, r1
00024cec: movs       r3, #9
00024cee: rors       r1, r3
00024cf0: lsls       r4, r2, #1
00024cf2: adds       r4, #0x80
00024cf4: mov        r2, r4
00024cf6: bl         #0x24ed0
00024cfa: lsrs       r1, r4, #8
00024cfc: subs       r0, r0, r1
00024cfe: lsls       r1, r0, #9
00024d00: lsrs       r0, r5, #1
00024d02: cmp        r1, #0
00024d04: beq        #0x24cda
00024d06: adds       r0, r0, #1
00024d08: pop        {r4, r5, r7, pc}
00024d0a: mov        r8, r8
00024d0c: .word      0x00005c55
00024d10: .word      0x5c553172
00024d14: .word      0x0000fbff
00024d18: .word      0x4e8de808
00024d1c: .word      0x00002d78
00024d20: .word      0x000104f4
00024d24: .word      0xffff1200
00024d28: .word      0xffffc73e
00024d2c: .word      0x0004fbff
00024d30: .word      0x7fffffbf

t_sgr:
00024d34: push       {r4, r5, r6, r7, lr}
00024d36: add        r7, sp, #0xc
00024d38: lsrs       r4, r2, #0xf
00024d3a: mov        r5, r4
00024d3c: muls       r5, r4, r5
00024d3e: lsrs       r3, r5, #0x10
00024d40: mov        r6, r4
00024d42: muls       r6, r3, r6
00024d44: uxth       r5, r5
00024d46: muls       r5, r4, r5
00024d48: lsrs       r4, r5, #0x10
00024d4a: adds       r4, r4, r6
00024d4c: movs       r5, #0xf
00024d4e: bics       r1, r5
00024d50: subs       r5, r2, r1
00024d52: lsls       r5, r5, #0xd
00024d54: ldr        r6, [pc, #0x38]
00024d56: ands       r6, r2
00024d58: muls       r6, r3, r6
00024d5a: lsrs       r2, r6, #0xf
00024d5c: subs       r2, r5, r2
00024d5e: movs       r5, #3
00024d60: muls       r5, r2, r5
00024d62: subs       r2, r5, r4
00024d64: lsrs       r4, r4, #0x10
00024d66: ldr        r5, [pc, #0x2c]
00024d68: muls       r5, r3, r5
00024d6a: lsrs       r3, r5, #0x10
00024d6c: muls       r3, r4, r3
00024d6e: lsrs       r3, r3, #0xa
00024d70: adds       r2, r2, r3
00024d72: cmp        r2, #8
00024d74: bge        #0x24d78
00024d76: subs       r1, r1, #1
00024d78: cmp        r0, #0
00024d7a: bmi        #0x24d86
00024d7c: lsrs       r0, r1, #0xd
00024d7e: ldr        r1, [pc, #0x1c]
00024d80: adds       r0, r0, r1
00024d82: lsrs       r0, r0, #1
00024d84: pop        {r4, r5, r6, r7, pc}
00024d86: lsrs       r0, r1, #0xb
00024d88: ldr        r1, [pc, #0xc]
00024d8a: subs       r0, r1, r0
00024d8c: lsrs       r0, r0, #2
00024d8e: pop        {r4, r5, r6, r7, pc}
00024d90: .word      0x00007fff
00024d94: .word      0x0000199a
00024d98: .word      0xfc000001
00024d9c: .word      0x7e000001

t_drj:
00024da0: push       {r4, r5, r6, r7, lr}
00024da2: add        r7, sp, #0xc
00024da4: sub        sp, #4
00024da6: cmp        r2, #0
00024da8: bmi        #0x24dc2
00024daa: cmp        r1, #0
00024dac: beq        #0x24dc6
00024dae: movs       r3, #0x7f
00024db0: ands       r3, r2
00024db2: subs       r1, r1, #1
00024db4: cmp        r3, #0xd
00024db6: blo        #0x24dce
00024db8: lsls       r0, r1, #0x17
00024dba: lsrs       r1, r2, #7
00024dbc: adds       r0, r1, r0
00024dbe: add        sp, #4
00024dc0: pop        {r4, r5, r6, r7, pc}
00024dc2: movs       r3, #0
00024dc4: b          #0x24dd2
00024dc6: bl         #0x24c5c
00024dca: add        sp, #4
00024dcc: pop        {r4, r5, r6, r7, pc}
00024dce: lsls       r2, r2, #1
00024dd0: ldr        r3, [pc, #0x54]
00024dd2: ldr        r4, [pc, #0x58]
00024dd4: cmp        r0, r4
00024dd6: blo        #0x24e18
00024dd8: lsls       r4, r0, #9
00024dda: lsrs       r5, r4, #0xf
00024ddc: ldr        r6, [pc, #0x50]
00024dde: muls       r6, r5, r6
00024de0: lsrs       r5, r4, #0x12
00024de2: adds       r5, r6, r5
00024de4: lsrs       r5, r5, #1
00024de6: ldr        r6, [pc, #0x4c]
00024de8: adds       r5, r5, r6
00024dea: lsrs       r5, r5, #0xf
00024dec: asrs       r0, r0, #0x17
00024dee: adds       r0, #0x8a
00024df0: lsls       r5, r0
00024df2: lsrs       r5, r5, #0xf
00024df4: ldr        r6, [pc, #0x40]
00024df6: subs       r5, r6, r5
00024df8: lsrs       r6, r5, #9
00024dfa: cmp        r1, r6
00024dfc: beq        #0x24e02
00024dfe: lsls       r1, r1, #9
00024e00: adds       r5, r1, r3
00024e02: movs       r3, #9
00024e04: mov        r1, r5
00024e06: rors       r1, r3
00024e08: ldr        r3, [pc, #0x30]
00024e0a: muls       r3, r5, r3
00024e0c: lsls       r4, r0
00024e0e: subs       r0, r3, r4
00024e10: bl         #0x24ed0
00024e14: add        sp, #4
00024e16: pop        {r4, r5, r6, r7, pc}
00024e18: lsls       r1, r1, #0x17
00024e1a: lsrs       r2, r2, #8
00024e1c: adds       r1, r2, r1
00024e1e: subs       r1, r1, #1
00024e20: bl         #0x24b78
00024e24: add        sp, #4
00024e26: pop        {r4, r5, r6, r7, pc}
00024e28: .word      0x000001ff
00024e2c: .word      0xc1e496cc
00024e30: .word      0x00005c55
00024e34: .word      0x5c5538e8
00024e38: .word      0x0000fbff
00024e3c: .word      0x4e8de808

t_mt:
00024e40: push       {r4, r5, r6, r7, lr}
00024e42: add        r7, sp, #0xc
00024e44: lsrs       r4, r2, #0x11
00024e46: lsls       r2, r3
00024e48: ldm        r0!, {r5, r6}
00024e4a: ldr        r0, [r0]
00024e4c: muls       r5, r4, r5
00024e4e: subs       r0, r0, r5
00024e50: asrs       r0, r0, #0xb
00024e52: lsls       r0, r3
00024e54: asrs       r3, r0, #0x11
00024e56: ldm        r6, {r0, r4, r5, r6}
00024e58: muls       r0, r3, r0
00024e5a: subs       r0, r0, r2
00024e5c: adds       r0, r0, r6
00024e5e: mvns       r2, r3
00024e60: lsrs       r2, r2, #9
00024e62: muls       r4, r2, r4
00024e64: lsls       r3, r3, #0x17
00024e66: lsrs       r6, r3, #0x16
00024e68: ldrh       r5, [r5, r6]
00024e6a: cmp        r5, r4
00024e6c: beq        #0x24ec2
00024e6e: subs       r4, r5, r4
00024e70: lsls       r5, r0, #0xf
00024e72: lsrs       r5, r5, #8
00024e74: adds       r4, r5, r4
00024e76: asrs       r5, r4, #7
00024e78: asrs       r0, r0, #0x11
00024e7a: ldr        r6, [pc, #0x48]
00024e7c: muls       r6, r0, r6
00024e7e: asrs       r6, r6, #0xb
00024e80: muls       r6, r0, r6
00024e82: lsrs       r6, r6, #0xd
00024e84: subs       r5, r6, r5
00024e86: muls       r5, r0, r5
00024e88: asrs       r5, r5, #0x10
00024e8a: mov        r6, r0
00024e8c: muls       r6, r0, r6
00024e8e: subs       r5, r5, r6
00024e90: adds       r4, r5, r4
00024e92: beq        #0x24ec2
00024e94: lsrs       r3, r3, #0x13
00024e96: ldr        r5, [pc, #0x30]
00024e98: adds       r3, r5, r3
00024e9a: ldr        r3, [r3, #0xc]
00024e9c: subs       r3, #0x84
00024e9e: mov        r5, r3
00024ea0: lsrs       r5, r2
00024ea2: lsls       r0, r0, #9
00024ea4: subs       r0, r0, r5
00024ea6: rors       r3, r2
00024ea8: lsrs       r2, r3, #0x11
00024eaa: subs       r2, r4, r2
00024eac: asrs       r3, r2, #0xf
00024eae: adds       r0, r0, r3
00024eb0: muls       r0, r1, r0
00024eb2: ldr        r3, [pc, #0x18]
00024eb4: ands       r3, r2
00024eb6: lsrs       r1, r1, #0xf
00024eb8: muls       r1, r3, r1
00024eba: lsls       r2, r4, #0xe
00024ebc: subs       r1, r1, r2
00024ebe: adds       r0, r1, r0
00024ec0: asrs       r0, r0, #0x1f
00024ec2: pop        {r4, r5, r6, r7, pc}
00024ec4: .word      0x0000aaab
00024ec8: .word      0x000104f4
00024ecc: .word      0x00007fff

t_exp_res:
00024ed0: push       {r4, r5, r6, r7, lr}
00024ed2: add        r7, sp, #0xc
00024ed4: ldr        r3, [pc, #0xa0]
00024ed6: muls       r3, r1, r3
00024ed8: bpl        #0x24f1c
00024eda: movs       r3, #0x17
00024edc: rors       r1, r3
00024ede: ldr        r3, [pc, #0x9c]
00024ee0: adds       r3, r1, r3
00024ee2: asrs       r4, r1, #0x1f
00024ee4: eors       r3, r4
00024ee6: ldr        r5, [pc, #0x98]
00024ee8: muls       r5, r3, r5
00024eea: lsrs       r3, r5, #0x10
00024eec: eors       r3, r4
00024eee: subs       r4, r4, r3
00024ef0: movs       r3, #7
00024ef2: lsls       r5, r3, #0x1d
00024ef4: mov        r3, r1
00024ef6: bics       r3, r5
00024ef8: ldr        r5, [pc, #0x88]
00024efa: cmp        r0, r5
00024efc: bgt        #0x24f0e
00024efe: subs       r1, r1, #1
00024f00: mov        r5, r1
00024f02: muls       r5, r1, r5
00024f04: cmp        r5, #0xd
00024f06: bne        #0x24f0a
00024f08: movs       r3, #3
00024f0a: ldr        r5, [pc, #0x7c]
00024f0c: adds       r0, r0, r5
00024f0e: adds       r0, r4, r0
00024f10: movs       r4, #9
00024f12: rors       r1, r4
00024f14: lsrs       r4, r1, #0x17
00024f16: subs       r4, r3, r4
00024f18: ldr        r3, [pc, #0x70]
00024f1a: muls       r3, r4, r3
00024f1c: ldr        r4, [pc, #0x70]
00024f1e: adds       r4, r0, r4
00024f20: mvns       r0, r1
00024f22: lsrs       r0, r0, #0x17
00024f24: lsls       r5, r0, #1
00024f26: ldr        r6, [pc, #0x6c]
00024f28: ldrh       r5, [r6, r5]
00024f2a: lsls       r5, r5, #0xb
00024f2c: subs       r3, r3, r5
00024f2e: ldr        r5, [pc, #0x68]
00024f30: adds       r3, r3, r5
00024f32: asrs       r5, r3, #0x11
00024f34: adds       r5, r5, r4
00024f36: uxth       r6, r5
00024f38: asrs       r5, r5, #0x10
00024f3a: muls       r6, r5, r6
00024f3c: asrs       r6, r6, #8
00024f3e: adds       r3, r3, r6
00024f40: lsls       r4, r4, #0x11
00024f42: adds       r3, r4, r3
00024f44: mov        r4, r5
00024f46: muls       r4, r5, r4
00024f48: lsls       r6, r4, #7
00024f4a: adds       r3, r3, r6
00024f4c: lsrs       r4, r4, #0xe
00024f4e: muls       r4, r5, r4
00024f50: asrs       r4, r4, #0xe
00024f52: ldr        r5, [pc, #0x48]
00024f54: muls       r5, r4, r5
00024f56: asrs       r4, r5, #5
00024f58: adds       r3, r3, r4
00024f5a: lsls       r0, r0, #4
00024f5c: ldr        r4, [pc, #0x40]
00024f5e: adds       r0, r4, r0
00024f60: ldr        r0, [r0, #0xc]
00024f62: subs       r0, #0x84
00024f64: lsrs       r2, r2, #5
00024f66: subs       r2, r2, #4
00024f68: muls       r0, r2, r0
00024f6a: subs       r0, r0, r3
00024f6c: lsrs       r0, r0, #0x1f
00024f6e: lsls       r1, r1, #0x17
00024f70: lsrs       r2, r2, #3
00024f72: adds       r1, r1, r2
00024f74: adds       r0, r1, r0
00024f76: pop        {r4, r5, r6, r7, pc}
00024f78: .word      0x00b8c200
00024f7c: .word      0xffff0400
00024f80: .word      0x00002d78
00024f84: .word      0x9290dcff
00024f88: .word      0xb17217f8
00024f8c: .word      0x00005c61
00024f90: .word      0xedbe281c
00024f94: .word      0x000132b8
00024f98: .word      0xa5908218
00024f9c: .word      0x00002aab
00024fa0: .word      0x000104f4

t_tw_low2:
00024fa4: push       {r4, r5, r7, lr}
00024fa6: add        r7, sp, #8
00024fa8: mov        r4, r0
00024faa: ldr        r0, [pc, #0x5c]
00024fac: ands       r0, r4
00024fae: lsrs       r2, r0, #4
00024fb0: ldrh       r3, [r1, #2]
00024fb2: muls       r3, r2, r3
00024fb4: lsrs       r2, r3, #0xc
00024fb6: ldr        r3, [r1, #4]
00024fb8: ldr        r1, [r1, #8]
00024fba: adds       r2, r2, r3
00024fbc: lsrs       r2, r2, #6
00024fbe: muls       r2, r0, r2
00024fc0: lsrs       r0, r2, #0xa
00024fc2: adds       r0, r0, r1
00024fc4: lsrs       r0, r0, #6
00024fc6: ldr        r1, [pc, #0x44]
00024fc8: mov        r2, r4
00024fca: ands       r2, r1
00024fcc: adds       r1, r2, r1
00024fce: adds       r1, r1, #1
00024fd0: lsls       r2, r1, #8
00024fd2: adds       r2, #0xc8
00024fd4: subs       r0, r2, r0
00024fd6: lsrs       r5, r0, #7
00024fd8: lsls       r0, r5, #1
00024fda: lsls       r1, r1, #2
00024fdc: adds       r1, r1, #1
00024fde: subs       r0, r1, r0
00024fe0: movs       r1, #3
00024fe2: muls       r1, r0, r1
00024fe4: movs       r2, #0xf
00024fe6: lsls       r2, r2, #0xd
00024fe8: muls       r2, r0, r2
00024fea: lsrs       r0, r4, #0x16
00024fec: movs       r3, #0x1e
00024fee: bics       r3, r0
00024ff0: lsls       r2, r3
00024ff2: mov        r0, r4
00024ff4: bl         #0x25018
00024ff8: ldr        r1, [pc, #0x14]
00024ffa: ands       r1, r4
00024ffc: adds       r0, r1, r0
00024ffe: adds       r0, r0, r5
00025000: ldr        r1, [pc, #0x10]
00025002: adds       r0, r0, r1
00025004: pop        {r4, r5, r7, pc}
00025006: mov        r8, r8
00025008: .word      0x00003fff
0002500c: .word      0x007fffff
00025010: .word      0xff800000
00025014: .word      0xfeffffff

t_pd2:
00025018: push       {r4, r5, r6, r7, lr}
0002501a: add        r7, sp, #0xc
0002501c: ldr        r4, [pc, #0x84]
0002501e: uxtb       r6, r0
00025020: ands       r0, r4
00025022: adds       r0, r0, r4
00025024: adds       r5, r0, #1
00025026: lsrs       r0, r5, #8
00025028: muls       r6, r0, r6
0002502a: muls       r0, r0, r0
0002502c: lsrs       r4, r6, #7
0002502e: adds       r4, r4, r0
00025030: lsrs       r6, r4, #0x10
00025032: movs       r0, #0xa
00025034: muls       r0, r5, r0
00025036: subs       r0, r0, r1
00025038: muls       r6, r0, r6
0002503a: subs       r2, r6, r2
0002503c: cmp        r3, #0xd
0002503e: blo        #0x25050
00025040: lsrs       r0, r0, #0xc
00025042: uxth       r1, r4
00025044: muls       r1, r0, r1
00025046: lsrs       r0, r1, #4
00025048: adds       r0, r0, r2
0002504a: adds       r0, #0xff
0002504c: lsrs       r0, r0, #0x1f
0002504e: pop        {r4, r5, r6, r7, pc}
00025050: lsls       r6, r4, #0x10
00025052: muls       r5, r5, r5
00025054: subs       r5, r5, r6
00025056: lsrs       r6, r0, #0xe
00025058: muls       r6, r5, r6
0002505a: lsrs       r5, r6, #0x12
0002505c: adds       r2, r5, r2
0002505e: beq        #0x2509e
00025060: lsrs       r5, r0, #0x10
00025062: uxth       r6, r4
00025064: muls       r5, r6, r5
00025066: uxth       r0, r0
00025068: muls       r0, r6, r0
0002506a: lsrs       r0, r0, #0x10
0002506c: adds       r0, r0, r5
0002506e: adds       r0, r0, r2
00025070: lsrs       r2, r4, #0x11
00025072: mov        r4, r2
00025074: muls       r4, r2, r4
00025076: lsrs       r4, r4, #0xe
00025078: ldr        r5, [pc, #0x2c]
0002507a: muls       r5, r4, r5
0002507c: lsrs       r4, r5, #0x10
0002507e: lsrs       r1, r1, #4
00025080: muls       r1, r4, r1
00025082: lsrs       r1, r3
00025084: cmp        r3, #8
00025086: bne        #0x25098
00025088: lsrs       r3, r1, #8
0002508a: muls       r2, r3, r2
0002508c: lsrs       r2, r2, #0xd
0002508e: ldr        r3, [pc, #0x1c]
00025090: muls       r3, r2, r3
00025092: lsrs       r2, r3, #0x10
00025094: subs       r1, r1, r2
00025096: adds       r0, #0x6a
00025098: adds       r0, r1, r0
0002509a: lsrs       r0, r0, #0x1f
0002509c: pop        {r4, r5, r6, r7, pc}
0002509e: movs       r0, #0
000250a0: pop        {r4, r5, r6, r7, pc}
000250a2: mov        r8, r8
000250a4: .word      0x007fffff
000250a8: .word      0x00004e03
000250ac: .word      0x00000931

t_exp_small_fix:
000250b0: push       {r4, r6, r7, lr}
000250b2: add        r7, sp, #8
000250b4: ldr        r3, [pc, #0x34]
000250b6: ands       r3, r0
000250b8: asrs       r1, r0, #0xf
000250ba: mov        r2, r1
000250bc: muls       r2, r1, r2
000250be: lsrs       r4, r2, #0x1a
000250c0: adds       r4, r4, r1
000250c2: muls       r4, r3, r4
000250c4: asrs       r3, r4, #9
000250c6: lsls       r0, r0, #0x10
000250c8: lsls       r4, r2, #5
000250ca: adds       r0, r4, r0
000250cc: adds       r0, r0, r3
000250ce: movs       r3, #3
000250d0: muls       r3, r0, r3
000250d2: lsrs       r0, r2, #0x14
000250d4: muls       r0, r1, r0
000250d6: asrs       r4, r0, #0xe
000250d8: lsls       r2, r2, #0xc
000250da: lsrs       r2, r2, #0x13
000250dc: adds       r2, r4, r2
000250de: muls       r2, r1, r2
000250e0: asrs       r1, r2, #0xd
000250e2: adds       r0, r1, r0
000250e4: adds       r0, r0, r3
000250e6: lsrs       r0, r0, #0x1f
000250e8: pop        {r4, r6, r7, pc}
000250ea: mov        r8, r8
000250ec: .word      0x00007fff

memcpy:
000250f0: push       {r4, r6, r7, lr}
000250f2: add        r7, sp, #8
000250f4: cmp        r2, #0
000250f6: beq        #0x25156
000250f8: movs       r3, #3
000250fa: ands       r3, r2
000250fc: beq        #0x25112
000250fe: ldrb       r4, [r1]
00025100: strb       r4, [r0]
00025102: cmp        r3, #1
00025104: bne        #0x2511c
00025106: adds       r3, r0, #1
00025108: adds       r1, r1, #1
0002510a: subs       r4, r2, #1
0002510c: cmp        r2, #4
0002510e: bhs        #0x2513e
00025110: b          #0x25156
00025112: mov        r3, r0
00025114: mov        r4, r2
00025116: cmp        r2, #4
00025118: bhs        #0x2513e
0002511a: b          #0x25156
0002511c: ldrb       r4, [r1, #1]
0002511e: strb       r4, [r0, #1]
00025120: cmp        r3, #2
00025122: bne        #0x25130
00025124: adds       r3, r0, #2
00025126: adds       r1, r1, #2
00025128: subs       r4, r2, #2
0002512a: cmp        r2, #4
0002512c: bhs        #0x2513e
0002512e: b          #0x25156
00025130: ldrb       r3, [r1, #2]
00025132: strb       r3, [r0, #2]
00025134: adds       r3, r0, #3
00025136: adds       r1, r1, #3
00025138: subs       r4, r2, #3
0002513a: cmp        r2, #4
0002513c: blo        #0x25156
0002513e: ldrb       r2, [r1]
00025140: strb       r2, [r3]
00025142: ldrb       r2, [r1, #1]
00025144: strb       r2, [r3, #1]
00025146: ldrb       r2, [r1, #2]
00025148: strb       r2, [r3, #2]
0002514a: ldrb       r2, [r1, #3]
0002514c: strb       r2, [r3, #3]
0002514e: adds       r3, r3, #4
00025150: adds       r1, r1, #4
00025152: subs       r4, r4, #4
00025154: bne        #0x2513e
00025156: pop        {r4, r6, r7, pc}

memmove:
00025158: push       {r4, r5, r6, r7, lr}
0002515a: add        r7, sp, #0xc
0002515c: cmp        r0, r1
0002515e: bhs        #0x2517e
00025160: cmp        r2, #0
00025162: beq        #0x2520a
00025164: movs       r3, #3
00025166: ands       r3, r2
00025168: beq        #0x251c6
0002516a: ldrb       r4, [r1]
0002516c: strb       r4, [r0]
0002516e: cmp        r3, #1
00025170: bne        #0x251d0
00025172: adds       r3, r0, #1
00025174: adds       r1, r1, #1
00025176: subs       r4, r2, #1
00025178: cmp        r2, #4
0002517a: bhs        #0x251f2
0002517c: b          #0x2520a
0002517e: cmp        r2, #0
00025180: beq        #0x2520a
00025182: movs       r4, #3
00025184: ands       r4, r2
00025186: mov        r3, r2
00025188: beq        #0x251a4
0002518a: subs       r3, r2, #1
0002518c: ldrb       r5, [r1, r3]
0002518e: strb       r5, [r0, r3]
00025190: cmp        r4, #1
00025192: beq        #0x251a4
00025194: subs       r3, r2, #2
00025196: ldrb       r5, [r1, r3]
00025198: strb       r5, [r0, r3]
0002519a: cmp        r4, #2
0002519c: beq        #0x251a4
0002519e: subs       r3, r2, #3
000251a0: ldrb       r4, [r1, r3]
000251a2: strb       r4, [r0, r3]
000251a4: cmp        r2, #4
000251a6: blo        #0x2520a
000251a8: subs       r1, r1, #4
000251aa: subs       r2, r0, #4
000251ac: adds       r4, r2, r3
000251ae: adds       r5, r1, r3
000251b0: ldrb       r6, [r5, #3]
000251b2: strb       r6, [r4, #3]
000251b4: ldrb       r6, [r5, #2]
000251b6: strb       r6, [r4, #2]
000251b8: ldrb       r5, [r5, #1]
000251ba: strb       r5, [r4, #1]
000251bc: ldrb       r4, [r1, r3]
000251be: strb       r4, [r2, r3]
000251c0: subs       r3, r3, #4
000251c2: bne        #0x251ac
000251c4: b          #0x2520a
000251c6: mov        r3, r0
000251c8: mov        r4, r2
000251ca: cmp        r2, #4
000251cc: bhs        #0x251f2
000251ce: b          #0x2520a
000251d0: ldrb       r4, [r1, #1]
000251d2: strb       r4, [r0, #1]
000251d4: cmp        r3, #2
000251d6: bne        #0x251e4
000251d8: adds       r3, r0, #2
000251da: adds       r1, r1, #2
000251dc: subs       r4, r2, #2
000251de: cmp        r2, #4
000251e0: bhs        #0x251f2
000251e2: b          #0x2520a
000251e4: ldrb       r3, [r1, #2]
000251e6: strb       r3, [r0, #2]
000251e8: adds       r3, r0, #3
000251ea: adds       r1, r1, #3
000251ec: subs       r4, r2, #3
000251ee: cmp        r2, #4
000251f0: blo        #0x2520a
000251f2: ldrb       r2, [r1]
000251f4: strb       r2, [r3]
000251f6: ldrb       r2, [r1, #1]
000251f8: strb       r2, [r3, #1]
000251fa: ldrb       r2, [r1, #2]
000251fc: strb       r2, [r3, #2]
000251fe: ldrb       r2, [r1, #3]
00025200: strb       r2, [r3, #3]
00025202: adds       r3, r3, #4
00025204: adds       r1, r1, #4
00025206: subs       r4, r4, #4
00025208: bne        #0x251f2
0002520a: pop        {r4, r5, r6, r7, pc}

memset:
0002520c: push       {r4, r5, r7, lr}
0002520e: add        r7, sp, #8
00025210: cmp        r2, #0
00025212: beq        #0x2524a
00025214: movs       r5, #3
00025216: ands       r5, r2
00025218: mov        r3, r0
0002521a: mov        r4, r2
0002521c: beq        #0x25238
0002521e: strb       r1, [r0]
00025220: cmp        r5, #1
00025222: bne        #0x2522e
00025224: adds       r3, r0, #1
00025226: subs       r4, r2, #1
00025228: cmp        r2, #4
0002522a: bhs        #0x2523c
0002522c: b          #0x2524a
0002522e: strb       r1, [r0, #1]
00025230: cmp        r5, #2
00025232: bne        #0x2524c
00025234: adds       r3, r0, #2
00025236: subs       r4, r2, #2
00025238: cmp        r2, #4
0002523a: blo        #0x2524a
0002523c: strb       r1, [r3, #3]
0002523e: strb       r1, [r3, #2]
00025240: strb       r1, [r3, #1]
00025242: strb       r1, [r3]
00025244: adds       r3, r3, #4
00025246: subs       r4, r4, #4
00025248: bne        #0x2523c
0002524a: pop        {r4, r5, r7, pc}
0002524c: strb       r1, [r0, #2]
0002524e: adds       r3, r0, #3
00025250: subs       r4, r2, #3
00025252: cmp        r2, #4
00025254: bhs        #0x2523c
00025256: b          #0x2524a

eik_batch:
00025258: push       {r4, r5, r6, r7, lr}
0002525a: add        r7, sp, #0xc
0002525c: sub        sp, #4
0002525e: cmp        r3, #0
00025260: beq        #0x25290
00025262: mov        r4, r3
00025264: mov        r5, r2
00025266: mov        r6, r1
00025268: mov        r1, r0
0002526a: str        r0, [sp]
0002526c: b          #0x2527a
0002526e: bl         #0x24484
00025272: stm        r5!, {r0}
00025274: subs       r4, r4, #1
00025276: ldr        r1, [sp]
00025278: beq        #0x25290
0002527a: ldm        r6!, {r0}
0002527c: cmp        r1, #1
0002527e: beq        #0x2526e
00025280: cmp        r1, #0
00025282: bne        #0x2528a
00025284: bl         #0x23ed4
00025288: b          #0x25272
0002528a: bl         #0x247ec
0002528e: b          #0x25272
00025290: add        sp, #4
00025292: pop        {r4, r5, r6, r7, pc}
