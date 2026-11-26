; Allocated executable sections; ARM mapping-symbol literal pools are data.

eik_sigmoid:
00014578: bltz       a0, 0x2c
0001457c: lui        a2, 0x3f000
00014580: bgeu       a2, a0, 0xf0
00014584: lui        a1, 0x407ff
00014588: bgeu       a1, a0, 0x624
0001458c: lui        a1, 0x418ab
00014590: bgeu       a1, a0, 0x1b4
00014594: lui        a1, 0x7f800
00014598: bltu       a1, a0, 0x2a4
0001459c: lui        a0, 0x3f800
000145a0: ret        
000145a4: lui        a2, 0xbe800
000145a8: bgeu       a2, a0, 0x100
000145ac: lui        a1, 0xbff80
000145b0: bgeu       a1, a0, 0x134
000145b4: lui        a1, 0xc0fff
000145b8: bgeu       a1, a0, 0x1f4
000145bc: lui        a1, 0xc2d00
000145c0: bgeu       a0, a1, 0x274
000145c4: srli       a2, a0, 0x17
000145c8: slli       a3, a0, 9
000145cc: lui        a1, 0x11
000145d0: addi       a1, a1, 0x69c
000145d4: addi       a2, a2, -0x177
000145d8: slli       a7, a2, 3
000145dc: add        a7, a1, a7
000145e0: lw         a4, 0x5c4(a7)
000145e4: lui        a5, 0x1a184
000145e8: sll        a6, a3, a2
000145ec: lw         t0, 0x5c8(a7)
000145f0: mulhu      a3, a4, a3
000145f4: add        a3, a4, a3
000145f8: srli       a2, a3, 0xf
000145fc: srli       a4, a3, 0xe
00014600: srli       t2, a3, 0x18
00014604: srli       t3, a3, 0x1d
00014608: ori        a2, a2, 1
0001460c: andi       a4, a4, 0x3fc
00014610: mul        t0, a2, t0
00014614: mulhu      t1, a2, a5
00014618: sub        a4, a1, a4
0001461c: sub        a5, a6, t0
00014620: lw         a6, 0x3fc(a4)
00014624: add        t1, a5, t1
00014628: mulh       a4, t1, t1
0001462c: srli       t0, a4, 9
00014630: sub        a4, t0, t1
00014634: mulhsu     a4, a4, a6
00014638: srai       a4, a4, 8
0001463c: add        a4, a4, a6
00014640: addi       t1, t2, -0x7d
00014644: bnez       t3, 0x2d0
00014648: srl        a3, a4, t2
0001464c: mulhu      t3, a3, a3
00014650: sub        a3, t3, a3
00014654: mulhu      a4, a3, a4
00014658: addi       a3, a4, -0x46
0001465c: bltz       a3, 0x2bc
00014660: slli       a4, a4, 1
00014664: addi       a4, a4, -0x88
00014668: addi       t1, t2, -0x7c
0001466c: j          0x2ac
00014670: lui        a1, 0x3a689
00014674: bltu       a1, a0, 0x530
00014678: lui        a1, 0x33fff
0001467c: bltu       a0, a1, 0x390
00014680: neg        a0, a0
00014684: lui        a1, 0xff800
00014688: or         a2, a0, a1
0001468c: srli       a0, a0, 0x17
00014690: add        a1, a2, a1
00014694: sra        a0, a1, a0
00014698: lui        a1, 0x7e000
0001469c: sub        a0, a1, a0
000146a0: srli       a0, a0, 1
000146a4: ret        
000146a8: lui        a1, 0xba689
000146ac: bltu       a1, a0, 0x2b8
000146b0: lui        a1, 0xb37ff
000146b4: bltu       a0, a1, 0x358
000146b8: lui        a1, 0xff800
000146bc: sub        a0, a1, a0
000146c0: or         a2, a0, a1
000146c4: add        a1, a2, a1
000146c8: lui        a2, 0x7e000
000146cc: srli       a0, a0, 0x17
000146d0: sra        a0, a1, a0
000146d4: addi       a2, a2, 1
000146d8: add        a0, a0, a2
000146dc: srli       a0, a0, 1
000146e0: ret        
000146e4: srli       a3, a0, 0x12
000146e8: lui        a1, 0xfffe0
000146ec: addi       a1, a1, 0xd4
000146f0: slli       a2, a3, 4
000146f4: add        a1, a1, a2
000146f8: lw         a2, 0x608(a1)
000146fc: lw         a6, 0x60c(a1)
00014700: lw         a7, 0x604(a1)
00014704: lw         a5, 0x600(a1)
00014708: slli       a4, a0, 0xd
0001470c: mulh       a1, a6, a4
00014710: add        a1, a2, a1
00014714: mulh       a1, a1, a4
00014718: add        a1, a7, a1
0001471c: mulh       a1, a1, a4
00014720: add        a1, a5, a1
00014724: bltz       a1, 0xf4
00014728: addi       a2, a1, -0x80
0001472c: andi       a6, a2, 0xff
00014730: beqz       a6, 0x118
00014734: srli       a2, a2, 8
00014738: lui        a0, 0x3f000
0001473c: sub        a0, a0, a2
00014740: ret        
00014744: srli       a5, a0, 0xd
00014748: lui        a3, 0xffff1
0001474c: addi       a3, a3, -0x72c
00014750: andi       a1, a5, -0x10
00014754: add        a1, a3, a1
00014758: lw         a6, -0x3e8(a1)
0001475c: lh         a7, -0x3e4(a1)
00014760: lw         t0, -0x3ec(a1)
00014764: lw         a1, -0x3f0(a1)
00014768: slli       a4, a0, 0xe
0001476c: mulh       a7, a7, a4
00014770: add        a6, a6, a7
00014774: add        a2, a0, a2
00014778: mulh       a6, a6, a4
0001477c: add        a6, t0, a6
00014780: mulh       a6, a6, a4
00014784: add        a1, a1, a6
00014788: addi       a1, a1, -0x40
0001478c: srli       a6, a1, 7
00014790: andi       a1, a1, 0x7f
00014794: sub        a2, a2, a6
00014798: bnez       a1, 0xc
0001479c: andi       a1, a2, 1
000147a0: bnez       a1, 0xe0
000147a4: srli       a0, a2, 1
000147a8: ret        
000147ac: srli       a1, a0, 0x10
000147b0: lui        a2, 5
000147b4: addi       a2, a2, 0x174
000147b8: andi       a1, a1, -4
000147bc: add        a2, a2, a1
000147c0: lw         a1, 0x428(a2)
000147c4: lw         a3, 0x320(a2)
000147c8: slli       a4, a0, 0xd
000147cc: lw         a5, 0x218(a2)
000147d0: mulh       a6, a1, a4
000147d4: add        a3, a3, a6
000147d8: lw         a6, 0x110(a2)
000147dc: mulh       a3, a3, a4
000147e0: add        a3, a5, a3
000147e4: lw         a2, 8(a2)
000147e8: mulh       a3, a3, a4
000147ec: add        a3, a6, a3
000147f0: mulh       a4, a3, a4
000147f4: add        a4, a2, a4
000147f8: slli       a2, a1, 0x17
000147fc: bltz       a4, 0x60
00014800: addi       a3, a4, 0x80
00014804: andi       a4, a3, 0x1f8
00014808: beqz       a4, 0x130
0001480c: srli       a0, a3, 9
00014810: or         a0, a0, a2
00014814: ret        
00014818: addi       a2, a1, -0xc0
0001481c: andi       a6, a2, 0x7f
00014820: beqz       a6, 0xdc
00014824: srli       a2, a2, 7
00014828: lui        a0, 0x3f800
0001482c: sub        a0, a0, a2
00014830: ret        
00014834: lui        a1, 0xff800
00014838: bgeu       a1, a0, 0xf8
0001483c: lui        a1, 0x400
00014840: or         a0, a0, a1
00014844: ret        
00014848: addi       a1, a1, -0x100
0001484c: srli       a2, a2, 8
00014850: lui        a6, 0x3f000
00014854: sub        a2, a6, a2
00014858: j          0x3b8
0001485c: andi       a3, a4, 0xfc
00014860: bnez       a3, 0x14
00014864: lui        a3, 0xc07ff
00014868: bltu       a3, a0, 0x1ac
0001486c: andi       a3, a4, 2
00014870: beqz       a3, 0x1a4
00014874: srai       a0, a4, 8
00014878: add        a0, a0, a2
0001487c: ret        
00014880: slli       a1, a2, 8
00014884: addi       a2, a2, -1
00014888: addi       a5, a5, 0x10
0001488c: lui        a6, 0x80
00014890: srai       a4, a4, 9
00014894: srli       a7, a0, 0x17
00014898: lui        t0, 0x2d8
0001489c: lui        t1, 0xaaaab
000148a0: srli       a2, a2, 1
000148a4: addi       a6, a6, -0x20
000148a8: sll        a4, a4, a7
000148ac: and        a5, a5, a6
000148b0: slli       a6, a4, 6
000148b4: add        a3, a3, a5
000148b8: slli       a5, a5, 0x15
000148bc: mulh       a6, a6, a6
000148c0: addi       a5, a5, 0x80
000148c4: lhu        a7, -0x3f2(a3)
000148c8: lw         t2, -0x3f0(a3)
000148cc: lh         a3, -0x3e2(a3)
000148d0: slli       t3, a6, 2
000148d4: mulhu      a6, t3, t0
000148d8: sub        t0, t1, a6
000148dc: slli       t2, t2, 1
000148e0: slli       a6, a3, 0x10
000148e4: srai       t1, a3, 5
000148e8: sub        a5, a5, t2
000148ec: or         a6, a6, a7
000148f0: sub        a3, a1, a5
000148f4: slli       a7, a3, 7
000148f8: j          0x36c
000148fc: addi       a1, a1, -0x100
00014900: lui        a2, 0x3f800
00014904: srli       a6, a1, 7
00014908: addi       a2, a2, -1
0001490c: sub        a2, a2, a6
00014910: j          0x300
00014914: bgeu       a3, t1, 0xd0
00014918: andi       a3, a4, 0xf8
0001491c: srli       a4, a4, 8
00014920: beqz       a3, 0x30
00014924: slli       t1, t1, 0x17
00014928: sub        a0, a4, t1
0001492c: ret        
00014930: mv         a0, zero
00014934: ret        
00014938: andi       a1, a1, 0x1ff
0001493c: srli       a2, a3, 9
00014940: lui        a4, 0x800
00014944: addi       a3, a1, -1
00014948: or         a4, a2, a4
0001494c: j          0xd4
00014950: neg        a3, t1
00014954: bltz       a6, 0x230
00014958: slli       a0, a0, 0xd
0001495c: bltz       a5, 0x358
00014960: blez       t1, 0x234
00014964: srli       a4, a0, 0x17
00014968: or         a2, a0, a2
0001496c: lui        a5, 0x21d00
00014970: slli       a3, a2, 8
00014974: xori       a1, a4, 0x1f
00014978: srl        a2, a3, a1
0001497c: mulhu      a6, a2, a2
00014980: mulhu      a5, a6, a5
00014984: lui        a7, 0xaaab2
00014988: add        a5, a5, a7
0001498c: mulh       a5, a6, a5
00014990: mulhu      a5, a5, a2
00014994: addi       a5, a5, 0x83
00014998: andi       a6, a5, 0xf8
0001499c: beqz       a6, 0x14
000149a0: srli       a5, a5, 8
000149a4: lui        a0, 0x3f000
000149a8: sub        a0, a0, a5
000149ac: ret        
000149b0: addi       a6, zero, 0x165
000149b4: bltu       a6, a1, 0x350
000149b8: addi       a4, a4, 7
000149bc: srli       a0, a5, 8
000149c0: lui        a6, 0x3f000
000149c4: addi       a1, a1, -0x173
000149c8: andi       a5, a5, -0x100
000149cc: sub        a0, a6, a0
000149d0: sub        a2, a2, a5
000149d4: addi       a2, a2, 0x80
000149d8: sra        a2, a2, a4
000149dc: auipc      t1, 1
000149e0: jalr       zero, t1, 0x64
000149e4: addi       t2, t2, 9
000149e8: addi       a1, a4, -0x7e
000149ec: addi       a2, a4, -0x86
000149f0: srl        a1, a1, t2
000149f4: srl        a2, a2, t2
000149f8: bne        a1, a2, 0x158
000149fc: beqz       a4, 0x10
00014a00: addi       a0, a1, 2
00014a04: srli       a0, a0, 2
00014a08: ret        
00014a0c: lui        a0, 0x3f000
00014a10: ret        
00014a14: andi       a3, a1, 0x1ff
00014a18: srli       a4, a4, 8
00014a1c: addi       a3, a3, -2
00014a20: lui        a1, 0x11
00014a24: addi       a1, a1, 0x69c
00014a28: srli       a2, a0, 0x17
00014a2c: slli       a5, a0, 9
00014a30: lui        a0, 0xd1d57
00014a34: addi       a6, zero, 0x13
00014a38: lw         t0, 0x604(a1)
00014a3c: mulhsu     a7, a0, a5
00014a40: sub        a6, a6, a2
00014a44: add        a0, a7, a0
00014a48: sra        a6, a0, a6
00014a4c: ori        a0, a6, 1
00014a50: andi       a6, a6, 0x1fe
00014a54: add        a7, a1, a6
00014a58: add        a6, a7, a6
00014a5c: lw         a6, 0(a6)
00014a60: mul        t0, a0, t0
00014a64: addi       a2, a2, 9
00014a68: sll        a5, a5, a2
00014a6c: add        a5, t0, a5
00014a70: lui        t0, 0x17184
00014a74: addi       a2, a6, -0x86
00014a78: lhu        a7, 0x400(a7)
00014a7c: lw         a1, 0x608(a1)
00014a80: slli       t1, a3, 0x17
00014a84: addi       t2, zero, 0x50
00014a88: mul        a6, a0, t0
00014a8c: mulh       a0, a0, t0
00014a90: slli       t0, a2, 0x12
00014a94: sub        a5, a0, a5
00014a98: srli       a0, a2, 0xe
00014a9c: mulhu      a6, a0, a6
00014aa0: mul        a0, a5, a0
00014aa4: add        a0, a0, a6
00014aa8: mulh       a6, a5, a5
00014aac: mulhsu     a1, a5, a1
00014ab0: slli       a7, a7, 2
00014ab4: addi       a1, a1, 0x1de
00014ab8: or         a7, a7, t0
00014abc: mulhsu     a1, a1, a6
00014ac0: slli       t0, a7, 8
00014ac4: mulhsu     a7, a5, a7
00014ac8: add        a1, a1, a6
00014acc: add        a0, a0, t0
00014ad0: mulhsu     a1, a1, a2
00014ad4: slli       a1, a1, 9
00014ad8: add        a1, a7, a1
00014adc: add        a1, a0, a1
00014ae0: add        a0, t1, a4
00014ae4: bltu       a3, t2, 0x60
00014ae8: srli       a6, a6, 9
00014aec: slli       a4, a4, 5
00014af0: add        a5, a6, a5
00014af4: neg        a6, a3
00014af8: mulhsu     a5, a5, a2
00014afc: srai       a5, a5, 8
00014b00: add        a2, a5, a2
00014b04: addi       a7, zero, 0x60
00014b08: addi       a5, a4, -0x10
00014b0c: srl        a4, a5, a6
00014b10: bltu       a7, a3, 0xc
00014b14: mulhu      a2, a2, a4
00014b18: j          0x28
00014b1c: mul        a6, a2, a4
00014b20: sll        a3, a5, a3
00014b24: slli       a5, a2, 0x1a
00014b28: slli       a4, a4, 6
00014b2c: mulhu      a2, a2, a3
00014b30: sub        a3, a1, a5
00014b34: add        a2, a6, a2
00014b38: mulhsu     a3, a3, a4
00014b3c: add        a2, a2, a3
00014b40: sub        a1, a1, a2
00014b44: srai       a1, a1, 0x1f
00014b48: add        a0, a0, a1
00014b4c: ret        
00014b50: beqz       a4, -0x314
00014b54: addi       sp, sp, -0x10
00014b58: sw         ra, 0xc(sp)
00014b5c: sw         s0, 8(sp)
00014b60: addi       s0, sp, 0x10
00014b64: auipc      ra, 0
00014b68: jalr       ra, ra, 0x6d4
00014b6c: slli       a0, a0, 1
00014b70: srli       a0, a0, 1
00014b74: lw         ra, 0xc(sp)
00014b78: lw         s0, 8(sp)
00014b7c: addi       sp, sp, 0x10
00014b80: ret        
00014b84: neg        a0, a2
00014b88: andi       a7, a0, 0x1fe
00014b8c: add        a7, a1, a7
00014b90: j          -0x120
00014b94: beqz       a6, 0x10
00014b98: bnez       t0, -0x614
00014b9c: addi       a1, a7, 0x5c4
00014ba0: j          -0x178
00014ba4: lui        a6, 0x3e800
00014ba8: bgeu       a6, a0, 0x10c
00014bac: srli       a3, a0, 0x12
00014bb0: lui        a1, 0
00014bb4: addi       a1, a1, 0xd4
00014bb8: slli       a4, a3, 4
00014bbc: add        a1, a1, a4
00014bc0: lw         a6, 0x608(a1)
00014bc4: lw         a7, 0x60c(a1)
00014bc8: lw         t0, 0x604(a1)
00014bcc: lw         a5, 0x600(a1)
00014bd0: slli       a4, a0, 0xd
00014bd4: mulh       a1, a7, a4
00014bd8: add        a1, a6, a1
00014bdc: mulh       a1, a1, a4
00014be0: add        a1, t0, a1
00014be4: mulh       a1, a1, a4
00014be8: add        a1, a5, a1
00014bec: andi       a7, a1, 0x1fe
00014bf0: srli       a6, a1, 9
00014bf4: beqz       a7, 0xc
00014bf8: add        a0, a6, a2
00014bfc: ret        
00014c00: or         a2, a6, a2
00014c04: andi       a1, a1, -0x200
00014c08: addi       a2, a2, -1
00014c0c: addi       a1, a1, -0x100
00014c10: addi       a5, a5, -0x101
00014c14: addi       a3, a3, 0x61
00014c18: lui        a6, 0x12
00014c1c: addi       a6, a6, -0x328
00014c20: srli       a7, a0, 0x17
00014c24: lui        t0, 0xb6
00014c28: lui        t1, 0xaaaab
00014c2c: andi       t2, a3, 0xfe
00014c30: neg        a7, a7
00014c34: sub        a3, a1, a5
00014c38: addi       t1, t1, -0x584
00014c3c: add        a6, a6, t2
00014c40: sra        a4, a4, a7
00014c44: slli       a7, a3, 5
00014c48: lh         t2, 0(a6)
00014c4c: mulh       t3, a4, a4
00014c50: srai       a4, a4, 8
00014c54: mulhu      a6, t3, t0
00014c58: sub        t0, t1, a6
00014c5c: slli       a6, t2, 0xd
00014c60: srai       t1, t2, 0xa
00014c64: sub        a7, a7, t1
00014c68: mulhu      t0, t3, t0
00014c6c: mulhsu     t1, a4, a1
00014c70: mul        a1, a1, a4
00014c74: slli       a3, a3, 0x1c
00014c78: mulhsu     a4, a7, t0
00014c7c: mulhu      a1, a1, a5
00014c80: mul        a5, a5, t1
00014c84: mulh       a7, t1, a6
00014c88: slli       a4, a4, 0xe
00014c8c: sub        a3, a3, a6
00014c90: slli       a7, a7, 4
00014c94: add        a1, a3, a1
00014c98: add        a1, a1, a5
00014c9c: add        a1, a1, a4
00014ca0: add        a1, a1, a7
00014ca4: xor        a0, a1, a0
00014ca8: srli       a0, a0, 0x1f
00014cac: add        a0, a0, a2
00014cb0: ret        
00014cb4: srli       a4, a0, 0x17
00014cb8: or         a3, a0, a6
00014cbc: lui        a6, 0x21d00
00014cc0: slli       a3, a3, 8
00014cc4: xori       a1, a4, 0x1f
00014cc8: srl        a5, a3, a1
00014ccc: mulhu      a7, a5, a5
00014cd0: mulhu      a6, a7, a6
00014cd4: lui        t0, 0xaaab2
00014cd8: add        a6, a6, t0
00014cdc: mulh       a6, a7, a6
00014ce0: mulhu      a6, a6, a5
00014ce4: addi       a6, a6, 0x103
00014ce8: andi       a7, a6, 0x1f8
00014cec: beqz       a7, 0x10
00014cf0: srai       a0, a6, 9
00014cf4: add        a0, a0, a2
00014cf8: ret        
00014cfc: addi       a7, zero, 0x65
00014d00: bgeu       a7, a1, 0x54
00014d04: addi       a1, a1, 0x1a
00014d08: lui        a2, 0x22
00014d0c: lui        a4, 0x55555
00014d10: srl        a1, a3, a1
00014d14: addi       a2, a2, 0x220
00014d18: mulhu      a3, a1, a1
00014d1c: mulhu      a2, a3, a2
00014d20: addi       a4, a4, 0x554
00014d24: sub        a4, a4, a2
00014d28: mulhu      a2, a4, a1
00014d2c: mulhu      a2, a2, a3
00014d30: bltz       a0, 0x4c
00014d34: lui        a0, 0xfc001
00014d38: add        a0, a2, a0
00014d3c: srai       a0, a0, 0xc
00014d40: sub        a1, a1, a0
00014d44: srli       a1, a1, 0xf
00014d48: lui        a0, 0x3f000
00014d4c: or         a0, a1, a0
00014d50: ret        
00014d54: addi       a4, a4, 7
00014d58: andi       a0, a6, -0x200
00014d5c: addi       a1, a1, -3
00014d60: addi       a0, a0, -0x100
00014d64: srli       a6, a0, 9
00014d68: sub        a5, a5, a0
00014d6c: add        a0, a6, a2
00014d70: sra        a2, a5, a4
00014d74: auipc      t1, 1
00014d78: jalr       zero, t1, -0x334
00014d7c: lui        a0, 0xfe001
00014d80: add        a0, a2, a0
00014d84: srai       a0, a0, 0xc
00014d88: sub        a1, a1, a0
00014d8c: srli       a1, a1, 0xe
00014d90: lui        a0, 0x3f000
00014d94: sub        a0, a0, a1
00014d98: ret        

eik_tanh:
00014d9c: slli       a1, a0, 1
00014da0: bltz       a1, 0x38
00014da4: lui        a2, 0x7b201
00014da8: bgeu       a1, a2, 0x8c
00014dac: lui        a2, 0x73713
00014db0: bltu       a1, a2, 0x80
00014db4: lui        a2, 0x7627f
00014db8: bltu       a2, a1, 0x2c0
00014dbc: lui        a2, 0x744f7
00014dc0: bltu       a2, a1, 0x28c
00014dc4: lui        a2, 0x73713
00014dc8: addi       a2, a2, 0x744
00014dcc: sltu       a1, a2, a1
00014dd0: sub        a0, a0, a1
00014dd4: ret        
00014dd8: lui        a2, 0x82206
00014ddc: bltu       a2, a1, 0xac
00014de0: srli       a4, a1, 0xe
00014de4: lui        a2, 0xffff1
00014de8: addi       a2, a2, -0x72c
00014dec: andi       a3, a4, -0x10
00014df0: add        a3, a2, a3
00014df4: lw         a5, 0x18(a3)
00014df8: lh         a6, 0x1c(a3)
00014dfc: lw         a7, 0x14(a3)
00014e00: lw         t0, 0x10(a3)
00014e04: slli       a3, a0, 0xe
00014e08: mulh       a6, a6, a3
00014e0c: add        a5, a5, a6
00014e10: mulh       a5, a5, a3
00014e14: add        a5, a7, a5
00014e18: mulh       a5, a5, a3
00014e1c: add        a5, t0, a5
00014e20: andi       a6, a5, 0x7e
00014e24: srli       a7, a5, 7
00014e28: sub        a0, a0, a7
00014e2c: beqz       a6, 0xa8
00014e30: ret        
00014e34: srli       a4, a1, 0x13
00014e38: lui        a2, 3
00014e3c: addi       a2, a2, -0x2a4
00014e40: slli       a3, a4, 4
00014e44: add        a2, a2, a3
00014e48: lw         a6, -0x638(a2)
00014e4c: lw         a3, -0x634(a2)
00014e50: lw         a7, -0x63c(a2)
00014e54: lw         a5, -0x640(a2)
00014e58: slli       a2, a0, 0xd
00014e5c: mulhsu     t0, a3, a1
00014e60: add        a6, a6, t0
00014e64: mulh       a6, a6, a2
00014e68: add        a6, a7, a6
00014e6c: mulh       a6, a6, a2
00014e70: add        a6, a5, a6
00014e74: andi       t0, a6, 0xfe
00014e78: beqz       t0, 0x24
00014e7c: srli       a1, a6, 8
00014e80: sub        a0, a0, a1
00014e84: ret        
00014e88: bltz       a0, 0xa4
00014e8c: lui        a2, 0xff000
00014e90: bltu       a2, a1, 0xac
00014e94: lui        a0, 0x3f800
00014e98: ret        
00014e9c: beqz       a7, 0xac
00014ea0: srli       a7, a6, 8
00014ea4: slli       a1, a0, 6
00014ea8: sub        a4, a0, a7
00014eac: bltz       a1, 0xfc
00014eb0: mv         a1, zero
00014eb4: slli       a0, a0, 8
00014eb8: lui        a3, 0x80000
00014ebc: or         a3, a0, a3
00014ec0: slli       a2, a7, 2
00014ec4: addi       a2, a2, -2
00014ec8: mv         a0, a4
00014ecc: auipc      t1, 1
00014ed0: jalr       zero, t1, -0x48c
00014ed4: lui        a6, 0x80000
00014ed8: andi       a7, a5, 1
00014edc: addi       a5, a4, 0x10
00014ee0: addi       a4, a6, 0x80
00014ee4: andi       a5, a5, -0x20
00014ee8: add        a2, a2, a5
00014eec: slli       a5, a5, 0x15
00014ef0: lw         t0, 0x10(a2)
00014ef4: lhu        t1, 0xe(a2)
00014ef8: lh         a6, 0x1e(a2)
00014efc: add        a5, a5, a4
00014f00: slli       t0, t0, 1
00014f04: sub        a5, a5, t0
00014f08: slli       a2, a6, 0x10
00014f0c: or         a2, a2, t1
00014f10: beqz       a7, 0x204
00014f14: lui        a7, 0xf8000
00014f18: bgeu       a7, a5, 0x1fc
00014f1c: xor        a2, a5, a2
00014f20: seqz       a1, a2
00014f24: add        a0, a0, a1
00014f28: ret        
00014f2c: lui        a1, 0xff800
00014f30: bltu       a1, a0, 0x268
00014f34: lui        a0, 0xbf800
00014f38: ret        
00014f3c: lui        a1, 0x400
00014f40: or         a0, a0, a1
00014f44: ret        
00014f48: beqz       a6, 0x288
00014f4c: andi       a3, a4, 0x60
00014f50: lui        a4, 0x12
00014f54: addi       a4, a4, 0x71c
00014f58: add        a3, a4, a3
00014f5c: slt        a4, a2, a6
00014f60: slli       a4, a4, 4
00014f64: add        a4, a3, a4
00014f68: bge        a2, a6, 0xc
00014f6c: lui        a3, 0x7fffe
00014f70: and        a2, a2, a3
00014f74: lw         a3, 0xc(a4)
00014f78: lw         a6, 8(a4)
00014f7c: lw         a7, 4(a4)
00014f80: lw         a5, 0(a4)
00014f84: mulhsu     a1, a3, a1
00014f88: add        a1, a6, a1
00014f8c: mulh       a1, a1, a2
00014f90: add        a1, a7, a1
00014f94: mulh       a6, a1, a2
00014f98: add        a6, a5, a6
00014f9c: andi       a1, a6, 0xfe
00014fa0: bnez       a1, -0x124
00014fa4: j          -0x104
00014fa8: slli       a0, a4, 8
00014fac: lui        a1, 0x80000
00014fb0: srai       a7, a2, 5
00014fb4: ori        a6, a6, 1
00014fb8: slli       t0, a3, 0xe
00014fbc: sra        t1, a2, a3
00014fc0: andi       a3, a3, 1
00014fc4: add        a5, a7, a5
00014fc8: lui        a7, 0x2e
00014fcc: addi       a1, a1, 0x80
00014fd0: or         a0, a0, a1
00014fd4: lui        a1, 0x55555
00014fd8: srai       t0, t0, 2
00014fdc: sub        a5, a5, a6
00014fe0: slli       a6, t1, 7
00014fe4: addi       a7, a7, -0x7d3
00014fe8: addi       a1, a1, 0x580
00014fec: mulh       a2, a6, a2
00014ff0: sub        a6, a0, a5
00014ff4: sll        a2, a2, a3
00014ff8: mulhsu     a3, t1, a0
00014ffc: mul        a0, a0, t1
00015000: slli       t1, a5, 3
00015004: slli       a5, a5, 0x1d
00015008: mulhu      a7, a2, a7
0001500c: mulhu      a0, a6, a0
00015010: mul        a6, a6, a3
00015014: mulh       a3, a3, t0
00015018: sub        a5, a5, t0
0001501c: sub        a1, a1, a7
00015020: slli       a3, a3, 3
00015024: add        a0, a5, a0
00015028: mulhu      a1, a1, a2
0001502c: mulh       a1, a1, t1
00015030: slli       a1, a1, 0x11
00015034: add        a0, a0, a6
00015038: add        a1, a3, a1
0001503c: add        a0, a0, a1
00015040: srli       a0, a0, 0x1f
00015044: add        a0, a0, a4
00015048: ret        
0001504c: srli       a2, a1, 0x11
00015050: andi       a2, a2, -4
00015054: lui        a3, 0xe
00015058: addi       a3, a3, 0x77c
0001505c: add        a2, a3, a2
00015060: lw         a2, 0x5dc(a2)
00015064: add        a2, a2, a1
00015068: bltz       a2, 0x10
0001506c: srli       a2, a2, 0x18
00015070: sub        a0, a0, a2
00015074: ret        
00015078: srli       a1, a1, 0x18
0001507c: slli       a2, a0, 9
00015080: lui        a3, 0x2000
00015084: lui        a6, 0x1104
00015088: srli       a4, a2, 7
0001508c: addi       a5, a1, 0xb
00015090: or         a3, a4, a3
00015094: sll        a5, a3, a5
00015098: mulhu      a4, a5, a5
0001509c: mulhu      a6, a4, a6
000150a0: lui        a7, 0xaaaa9
000150a4: sub        a6, a7, a6
000150a8: mulhu      a6, a4, a6
000150ac: mulhu      a6, a6, a3
000150b0: bgeu       a2, a6, 0x4c
000150b4: sub        a4, a2, a6
000150b8: lui        a5, 0xff800
000150bc: addi       a4, a4, 0x80
000150c0: and        a0, a0, a5
000150c4: srai       a5, a4, 8
000150c8: andi       a6, a4, 0xfc
000150cc: add        a0, a5, a0
000150d0: bnez       a6, -0x2a0
000150d4: addi       a2, a2, 0x80
000150d8: andi       a5, a4, -0x100
000150dc: addi       a0, a0, -1
000150e0: slli       a3, a3, 6
000150e4: xori       a1, a1, 0x77
000150e8: sub        a2, a2, a5
000150ec: srai       a2, a2, 7
000150f0: addi       a1, a1, 4
000150f4: auipc      t1, 1
000150f8: jalr       zero, t1, -0x6b4
000150fc: addi       a2, a6, 0x104
00015100: andi       a6, a2, 0x1fc
00015104: beqz       a6, 0xa0
00015108: srli       a2, a2, 9
0001510c: sub        a0, a0, a2
00015110: ret        
00015114: srli       a1, a1, 0x18
00015118: slli       a7, a0, 8
0001511c: srai       a3, a3, 8
00015120: lui        t0, 0xb6e
00015124: lui        t1, 0xaaaab
00015128: srai       a6, a6, 5
0001512c: add        a4, a7, a4
00015130: sll        a1, a3, a1
00015134: mulhsu     a3, a1, a4
00015138: sub        a7, a4, a5
0001513c: slli       t2, a1, 6
00015140: mul        a1, a4, a1
00015144: mulh       a4, t2, t2
00015148: slli       t2, a7, 7
0001514c: mulhu      a1, a5, a1
00015150: mul        a5, a5, a3
00015154: mulh       a3, a2, a3
00015158: slli       a7, a7, 0x1c
0001515c: mulhu      t0, a4, t0
00015160: sub        a6, t2, a6
00015164: slli       a3, a3, 4
00015168: add        a5, a7, a5
0001516c: sub        a2, a2, a1
00015170: sub        a1, t1, t0
00015174: sub        a5, a5, a2
00015178: mulhu      a1, a4, a1
0001517c: mulhsu     a1, a6, a1
00015180: slli       a1, a1, 0x10
00015184: add        a3, a5, a3
00015188: add        a1, a3, a1
0001518c: srli       a1, a1, 0x1f
00015190: add        a0, a1, a0
00015194: ret        
00015198: lui        a1, 0xffc00
0001519c: or         a0, a0, a1
000151a0: ret        
000151a4: xori       a1, a1, 0x77
000151a8: addi       a6, zero, 0xc
000151ac: bltu       a1, a6, 0x50
000151b0: srli       a2, a2, 9
000151b4: slli       a3, a3, 6
000151b8: slli       a5, a2, 2
000151bc: sub        a0, a0, a2
000151c0: addi       a2, a5, -2
000151c4: addi       a1, a1, 4
000151c8: auipc      t1, 1
000151cc: jalr       zero, t1, -0x788
000151d0: addi       sp, sp, -0x10
000151d4: sw         ra, 0xc(sp)
000151d8: sw         s0, 8(sp)
000151dc: addi       s0, sp, 0x10
000151e0: auipc      ra, 0
000151e4: jalr       ra, ra, 0x58
000151e8: srli       a0, a0, 0x1f
000151ec: lw         ra, 0xc(sp)
000151f0: lw         s0, 8(sp)
000151f4: addi       sp, sp, 0x10
000151f8: ret        
000151fc: slli       a5, a5, 4
00015200: slli       a3, a3, 6
00015204: lui        a1, 0x1111
00015208: mulhu      a1, a4, a1
0001520c: lui        a2, 0xaaaab
00015210: mulhu      a4, a5, a5
00015214: addi       a2, a2, -0x555
00015218: sub        a2, a2, a1
0001521c: mulhu      a1, a4, a2
00015220: mulhu      a1, a1, a3
00015224: lui        a2, 0x400
00015228: add        a1, a1, a2
0001522c: srli       a1, a1, 0x17
00015230: sub        a0, a0, a1
00015234: ret        

eik_exp:
00015238: addi       sp, sp, -0x10
0001523c: sw         ra, 0xc(sp)
00015240: sw         s0, 8(sp)
00015244: sw         s1, 4(sp)
00015248: addi       s0, sp, 0x10
0001524c: lui        a1, 0x40800
00015250: addi       a1, a1, -1
00015254: add        a1, a0, a1
00015258: srli       a1, a1, 0x18
0001525c: bnez       a1, 0x118
00015260: slli       a3, a0, 0xf
00015264: srli       a1, a0, 0xd
00015268: lui        a2, 0xfffb3
0001526c: addi       a2, a2, -0x794
00015270: andi       a1, a1, -0x10
00015274: add        a4, a2, a1
00015278: lw         a5, 0x690(a4)
0001527c: lh         a6, 0x684(a4)
00015280: lw         a1, 0x684(a4)
00015284: lw         a2, 0x688(a4)
00015288: lw         a4, 0x68c(a4)
0001528c: mulhsu     a6, a6, a3
00015290: add        a5, a5, a6
00015294: mulhsu     a5, a5, a3
00015298: add        a4, a4, a5
0001529c: mulhu      a4, a4, a3
000152a0: add        a4, a2, a4
000152a4: slli       a3, a4, 0x18
000152a8: bgeu       a3, a2, 0x2e8
000152ac: bltz       a2, 0x2c0
000152b0: srli       a4, a4, 8
000152b4: srli       a2, a0, 0x17
000152b8: addi       a5, a2, -0x177
000152bc: lui        a2, 0x11
000152c0: addi       a2, a2, 0x69c
000152c4: lw         a7, 0x604(a2)
000152c8: lw         a3, 0x60c(a2)
000152cc: slli       a0, a0, 9
000152d0: lui        t0, 0x17184
000152d4: sll        t1, a0, a5
000152d8: sub        a5, a3, a5
000152dc: mulhsu     a0, a3, a0
000152e0: add        a0, a5, a0
000152e4: sra        a0, a0, a5
000152e8: ori        t2, a0, 1
000152ec: andi       a0, a0, 0x1fe
000152f0: add        a6, a2, a0
000152f4: mul        a5, t2, t0
000152f8: mulh       t0, t2, t0
000152fc: add        a0, a6, a0
00015300: lw         a3, 0(a0)
00015304: mul        a0, t2, a7
00015308: add        a0, a0, t1
0001530c: sub        a0, t0, a0
00015310: sub        a1, a1, a4
00015314: lw         a2, 0x608(a2)
00015318: mulh       a4, a0, a0
0001531c: addi       a3, a3, -0x86
00015320: lhu        a6, 0x400(a6)
00015324: slli       a7, a3, 0x10
00015328: srli       t0, a3, 0x10
0001532c: mul        t1, t0, a0
00015330: mulhu      a5, a5, t0
00015334: add        a5, t1, a5
00015338: mulhsu     a2, a0, a2
0001533c: or         a6, a7, a6
00015340: addi       a2, a2, 0x230
00015344: slli       a7, a6, 8
00015348: mulhsu     a0, a0, a6
0001534c: mulhsu     a2, a2, a4
00015350: add        a2, a2, a4
00015354: mulhsu     a2, a2, a3
00015358: slli       a2, a2, 7
0001535c: add        a5, a5, a7
00015360: add        a0, a0, a2
00015364: add        a0, a5, a0
00015368: srli       a0, a0, 0x1f
0001536c: add        a1, a0, a1
00015370: j          0x228
00015374: bltz       a0, 0x20
00015378: srli       a1, a0, 0x17
0001537c: addi       a5, a1, -0x77
00015380: bgeu       a0, a5, 0x40
00015384: addi       a2, a1, -0x67
00015388: bgeu       a0, a2, 0x138
0001538c: lui        a1, 0x3f800
00015390: j          0x208
00015394: lui        a1, 0xbf800
00015398: bltu       a1, a0, 0xac
0001539c: lui        a1, 0xba7ff
000153a0: bltu       a1, a0, 0x174
000153a4: lui        a1, 0xb3c00
000153a8: bltu       a1, a0, 0x314
000153ac: lui        a1, 0xb3000
000153b0: bgeu       a1, a0, -0x24
000153b4: lui        a1, 0x3f800
000153b8: addi       a1, a1, -1
000153bc: j          0x1dc
000153c0: lui        a1, 0x41000
000153c4: bltu       a1, a0, 0x138
000153c8: slli       a6, a0, 9
000153cc: lui        a2, 0x11
000153d0: addi       a2, a2, 0x69c
000153d4: lw         a0, 0x600(a2)
000153d8: lw         a1, 0x604(a2)
000153dc: sll        a7, a6, a5
000153e0: mulhu      a3, a6, a0
000153e4: sub        a4, a1, a5
000153e8: add        a0, a0, a3
000153ec: srl        a5, a0, a4
000153f0: srli       a0, a5, 1
000153f4: andi       a3, a5, 0x3fc
000153f8: ori        a4, a0, 1
000153fc: add        a3, a2, a3
00015400: mul        a0, a4, a1
00015404: lw         a3, 0(a3)
00015408: sub        a0, a7, a0
0001540c: mulh       a1, a0, a0
00015410: srli       a1, a1, 9
00015414: add        a1, a0, a1
00015418: mulhsu     a1, a1, a3
0001541c: srai       a1, a1, 8
00015420: add        a1, a1, a3
00015424: srli       a5, a5, 0xa
00015428: andi       a6, a1, 0xf8
0001542c: addi       a5, a5, 0x7e
00015430: bnez       a6, 0x25c
00015434: lw         a7, 0x610(a2)
00015438: mulhu      a6, a7, a4
0001543c: add        a0, a0, a6
00015440: j          0x25c
00015444: lui        a1, 0xc0800
00015448: bgeu       a1, a0, -0x1e8
0001544c: lui        a1, 0xc0fff
00015450: bltu       a1, a0, 0x2c0
00015454: srli       a1, a0, 0x10
00015458: lui        a2, 8
0001545c: addi       a2, a2, -0x794
00015460: andi       a1, a1, -4
00015464: add        a1, a2, a1
00015468: lw         a2, -0x3f4(a1)
0001546c: lw         a3, -0x474(a1)
00015470: slli       a4, a0, 0xe
00015474: lw         a5, -0x4f4(a1)
00015478: mulhsu     a6, a2, a0
0001547c: add        a3, a3, a6
00015480: lw         a6, -0x574(a1)
00015484: mulhsu     a3, a3, a4
00015488: add        a3, a5, a3
0001548c: lw         a1, -0x5f4(a1)
00015490: mulhsu     a3, a3, a4
00015494: add        a3, a6, a3
00015498: mulhsu     a3, a3, a4
0001549c: add        a3, a1, a3
000154a0: bltz       a3, 0x410
000154a4: addi       a1, a3, 0x80
000154a8: andi       a4, a1, 0x1f8
000154ac: srli       a1, a1, 9
000154b0: slli       a2, a2, 0x17
000154b4: beqz       a4, 0x40c
000154b8: sub        a1, a1, a2
000154bc: j          0xdc
000154c0: addi       a2, zero, 0x74
000154c4: bltu       a2, a1, 0x10c
000154c8: xori       a2, a1, 0x1f
000154cc: lui        a5, 0x3f800
000154d0: or         a1, a0, a5
000154d4: slli       a3, a1, 8
000154d8: srl        a0, a3, a2
000154dc: mulhu      a4, a0, a0
000154e0: add        a0, a0, a4
000154e4: addi       a4, a0, 0x82
000154e8: andi       a0, a4, 0xfe
000154ec: beqz       a0, 0x298
000154f0: srli       a1, a4, 8
000154f4: xor        a1, a1, a5
000154f8: j          0xa0
000154fc: lui        a1, 0x42b17
00015500: addi       a1, a1, 0x217
00015504: bgeu       a1, a0, 0x110
00015508: lui        a1, 0x7f800
0001550c: bgeu       a1, a0, 0x8c
00015510: j          0x210
00015514: lui        a1, 0xbe800
00015518: bgeu       a1, a0, 0x214
0001551c: slli       a3, a0, 0xd
00015520: srli       a1, a0, 0xf
00015524: lui        a2, 0xffffb
00015528: addi       a2, a2, -0x794
0001552c: andi       a1, a1, -0x10
00015530: add        a4, a2, a1
00015534: lw         a5, 0x390(a4)
00015538: lh         a6, 0x384(a4)
0001553c: lw         a1, 0x384(a4)
00015540: lw         a2, 0x388(a4)
00015544: lw         a4, 0x38c(a4)
00015548: mulhsu     a6, a6, a3
0001554c: add        a5, a5, a6
00015550: mulhsu     a5, a5, a3
00015554: add        a4, a4, a5
00015558: mulhsu     a4, a4, a3
0001555c: add        a4, a2, a4
00015560: slli       a3, a4, 0x18
00015564: bgeu       a3, a2, 0x2c
00015568: bgez       a2, -0x2b8
0001556c: add        a4, a1, a4
00015570: slli       a1, a1, 7
00015574: lui        a2, 0x7f800
00015578: and        a1, a1, a2
0001557c: bltz       a4, 0x34
00015580: andi       a2, a4, 0xfc
00015584: srli       a4, a4, 8
00015588: bnez       a2, 0xc
0001558c: j          -0x2d8
00015590: srli       a4, a4, 8
00015594: sub        a1, a1, a4
00015598: mv         a0, a1
0001559c: lw         ra, 0xc(sp)
000155a0: lw         s0, 8(sp)
000155a4: lw         s1, 4(sp)
000155a8: addi       sp, sp, 0x10
000155ac: ret        
000155b0: addi       a4, a4, 0x80
000155b4: andi       a2, a4, 0x1fc
000155b8: srai       a4, a4, 9
000155bc: bnez       a2, -0x28
000155c0: bnez       a1, -0x30c
000155c4: lui        a2, 0x11
000155c8: addi       a2, a2, 0x6a0
000155cc: j          0x200
000155d0: lui        a5, 0x3f800
000155d4: not        a2, a1
000155d8: or         a1, a0, a5
000155dc: slli       a3, a1, 8
000155e0: srl        a0, a3, a2
000155e4: lui        a4, 0xaaaab
000155e8: mulhu      a4, a0, a4
000155ec: mulhu      a4, a4, a0
000155f0: add        a4, a0, a4
000155f4: mulhu      a4, a4, a0
000155f8: add        a0, a0, a4
000155fc: addi       a4, a0, 0x81
00015600: andi       a0, a4, 0xff
00015604: beqz       a0, 0x308
00015608: srli       a1, a4, 8
0001560c: or         a1, a1, a5
00015610: j          -0x78
00015614: slli       a6, a0, 9
00015618: lui        a2, 0x11
0001561c: addi       a2, a2, 0x69c
00015620: lw         a0, 0x600(a2)
00015624: lw         a1, 0x604(a2)
00015628: sll        t0, a6, a5
0001562c: lw         a7, 0x610(a2)
00015630: mulhu      a3, a6, a0
00015634: sub        a4, a1, a5
00015638: add        a0, a0, a3
0001563c: srl        a5, a0, a4
00015640: srli       a0, a5, 1
00015644: andi       a3, a5, 0x3fc
00015648: ori        a4, a0, 1
0001564c: add        a3, a2, a3
00015650: mul        a0, a4, a1
00015654: mulhu      a1, a4, a7
00015658: lw         a3, 0(a3)
0001565c: sub        a0, t0, a0
00015660: add        a0, a0, a1
00015664: mulh       a1, a0, a0
00015668: srli       a1, a1, 9
0001566c: add        a1, a0, a1
00015670: mulhsu     a1, a1, a3
00015674: srai       a1, a1, 8
00015678: add        a1, a1, a3
0001567c: srli       a5, a5, 0xa
00015680: andi       a6, a1, 0xf8
00015684: addi       a5, a5, 0x7e
00015688: beqz       a6, 0x14
0001568c: slli       a5, a5, 0x17
00015690: srli       a1, a1, 8
00015694: add        a1, a1, a5
00015698: j          -0x100
0001569c: andi       a6, a4, 0x1fe
000156a0: slli       a5, a5, 0x17
000156a4: srli       a1, a1, 8
000156a8: add        a6, a2, a6
000156ac: add        a1, a5, a1
000156b0: addi       a1, a1, -1
000156b4: mul        a5, a7, a4
000156b8: j          -0x3a4
000156bc: not        a2, a0
000156c0: lui        a5, 0x3f800
000156c4: srli       a2, a2, 0x17
000156c8: or         a1, a0, a5
000156cc: slli       a3, a1, 8
000156d0: srl        a0, a3, a2
000156d4: mulhu      a4, a0, a0
000156d8: sub        a4, a0, a4
000156dc: addi       a4, a4, 0x41
000156e0: andi       a6, a4, 0x7e
000156e4: bnez       a6, 0x94
000156e8: addi       a5, a2, -0x90
000156ec: bltu       a3, a5, 0x220
000156f0: srl        a1, a3, a5
000156f4: mulhu      a0, a0, a1
000156f8: sub        a1, a1, a0
000156fc: srli       a1, a1, 0x16
00015700: lui        a0, 0x7f000
00015704: sub        a0, a0, a1
00015708: srli       a1, a0, 1
0001570c: j          -0x174
00015710: lui        a1, 0xc2d00
00015714: bltu       a0, a1, 0xa0
00015718: lui        a1, 0xff800
0001571c: bgeu       a1, a0, 0x1b4
00015720: lui        a1, 0x400
00015724: or         a1, a0, a1
00015728: j          -0x190
0001572c: lui        a1, 0xbd800
00015730: bltu       a1, a0, 0x130
00015734: srli       a2, a0, 0x17
00015738: lui        a5, 0x3f800
0001573c: lui        a4, 0x53888
00015740: or         a1, a0, a5
00015744: not        a2, a2
00015748: slli       a3, a1, 8
0001574c: srl        a6, a3, a2
00015750: mulhu      a4, a6, a4
00015754: lui        a7, 0xaaa46
00015758: sub        a4, a7, a4
0001575c: mulhu      a4, a4, a6
00015760: mulhu      a4, a4, a6
00015764: sub        a4, a4, a6
00015768: mulhu      a4, a4, a6
0001576c: addi       a4, a4, 0x41
00015770: andi       a7, a4, 0x7f
00015774: beqz       a7, 0x184
00015778: srli       a4, a4, 7
0001577c: sub        a1, a5, a4
00015780: j          -0x1e8
00015784: addi       a0, a2, -0x70
00015788: bltu       a3, a0, 0x184
0001578c: srl        a0, a3, a0
00015790: mulhu      a1, a0, a0
00015794: srli       a1, a1, 0x10
00015798: add        a0, a0, a1
0001579c: srli       a0, a0, 0x17
000157a0: addi       a0, a0, 1
000157a4: srli       a0, a0, 1
000157a8: lui        a1, 0x3f800
000157ac: or         a1, a0, a1
000157b0: j          -0x218
000157b4: lui        a1, 0xc2cdb
000157b8: bgeu       a0, a1, 0x120
000157bc: srli       a1, a0, 0x17
000157c0: addi       a4, a1, -0x177
000157c4: lui        a2, 0x11
000157c8: addi       a2, a2, 0x69c
000157cc: slli       a6, a0, 9
000157d0: lw         a0, 0x600(a2)
000157d4: lw         a3, 0x604(a2)
000157d8: lw         a7, 0x610(a2)
000157dc: sll        a5, a6, a4
000157e0: mulhu      a1, a0, a6
000157e4: sub        a4, a3, a4
000157e8: add        a0, a0, a1
000157ec: srl        a1, a0, a4
000157f0: srli       a0, a1, 1
000157f4: andi       a4, a1, 0x3fc
000157f8: ori        a0, a0, 1
000157fc: sub        a4, a2, a4
00015800: mul        t0, a0, a3
00015804: mulhu      t1, a0, a7
00015808: lw         a3, 0x3fc(a4)
0001580c: sub        t0, a5, t0
00015810: add        t0, t0, t1
00015814: mulh       a4, t0, t0
00015818: srli       a4, a4, 9
0001581c: sub        t1, a4, t0
00015820: mulhsu     a4, t1, a3
00015824: srai       a4, a4, 8
00015828: add        a4, a4, a3
0001582c: srli       t2, a1, 0xa
00015830: addi       a5, t2, -0x7d
00015834: bltz       a4, 0x160
00015838: beqz       a3, 0x178
0001583c: xori       a1, t2, 0x7f
00015840: srli       a3, a3, 0x1f
00015844: slli       a1, a1, 0x17
00015848: sltiu      a2, a4, 0x10
0001584c: mv         a0, zero
00015850: auipc      ra, 0
00015854: jalr       ra, ra, 0x490
00015858: mv         a1, a0
0001585c: j          -0x2c4
00015860: srli       a1, a0, 0x11
00015864: lui        a2, 0x13
00015868: addi       a2, a2, -0x794
0001586c: andi       a1, a1, -0x10
00015870: add        a1, a2, a1
00015874: lui        a2, 0xffffa
00015878: addi       a2, a2, 0x140
0001587c: add        a3, a1, a2
00015880: slli       a2, a0, 0xb
00015884: mv         a1, a0
00015888: mv         a0, a3
0001588c: mv         s1, a1
00015890: auipc      ra, 0
00015894: jalr       ra, ra, 0x270
00015898: andi       a2, a0, 0xfc
0001589c: srli       a1, a0, 8
000158a0: beqz       a2, 0xe4
000158a4: lui        a0, 0x3e800
000158a8: add        a1, a1, a0
000158ac: j          -0x314
000158b0: andi       a4, a3, 0xf8
000158b4: srai       a1, a3, 8
000158b8: slli       a2, a2, 0x17
000158bc: bnez       a4, -0x404
000158c0: andi       a3, a3, 6
000158c4: addi       a4, a2, 1
000158c8: bnez       a3, -0x614
000158cc: j          -0x338
000158d0: mv         a1, zero
000158d4: j          -0x33c
000158d8: lui        a1, 0xc2cdc
000158dc: lui        a2, 0xc2cff
000158e0: addi       a1, a1, -0xc9
000158e4: addi       a2, a2, 0x1b5
000158e8: sltu       a1, a0, a1
000158ec: sltu       a0, a0, a2
000158f0: add        a1, a1, a0
000158f4: j          -0x35c
000158f8: srli       a5, a6, 0x17
000158fc: beqz       a5, 0x10
00015900: srli       a4, a4, 7
00015904: lui        a1, 0x3f800
00015908: j          -0x654
0001590c: addi       a2, a2, 0x17
00015910: lui        a5, 0x55556
00015914: srl        a0, a3, a2
00015918: mulhu      a2, a0, a0
0001591c: mulhu      a3, a0, a5
00015920: mul        a6, a0, a0
00015924: slli       a7, a0, 0x11
00015928: mulhu      a3, a3, a2
0001592c: srli       a6, a6, 0x18
00015930: slli       a2, a2, 8
00015934: mulhu      a0, a3, a0
00015938: or         a2, a2, a6
0001593c: srli       a0, a0, 0xa
00015940: add        a0, a2, a0
00015944: add        a2, a7, a3
00015948: bltu       a1, a5, 0x20
0001594c: srli       a4, a4, 7
00015950: sub        a2, a2, a0
00015954: srli       a2, a2, 0x1f
00015958: sub        a1, a2, a4
0001595c: lui        a0, 0x3f800
00015960: add        a1, a1, a0
00015964: j          -0x3cc
00015968: srli       a4, a4, 8
0001596c: add        a0, a0, a2
00015970: srai       a0, a0, 0x1f
00015974: add        a0, a4, a0
00015978: lui        a1, 0x3f800
0001597c: add        a1, a0, a1
00015980: j          -0x3e8
00015984: lui        a4, 0xc1800
00015988: addi       a4, a4, 1
0001598c: mv         a0, s1
00015990: j          -0x6dc
00015994: bgeu       a1, a5, 0x2c
00015998: andi       a1, a4, 0xf8
0001599c: beqz       a1, 0x7c
000159a0: srli       a4, a4, 8
000159a4: slli       a5, a5, 0x17
000159a8: sub        a1, a4, a5
000159ac: j          -0x414
000159b0: addi       a2, a2, 4
000159b4: bltz       t0, -0x5e0
000159b8: bgez       t1, -0x6f4
000159bc: j          -0x39c
000159c0: addi       t2, t2, 0xa
000159c4: addi       a1, a4, -0x8e
000159c8: addi       a4, a4, -0x7e
000159cc: srl        a1, a1, t2
000159d0: srl        a4, a4, t2
000159d4: addi       a1, a1, 1
000159d8: addi       a4, a4, 1
000159dc: srli       a1, a1, 1
000159e0: srli       a4, a4, 1
000159e4: beq        a1, a4, -0x44c
000159e8: neg        a4, a0
000159ec: andi       a6, a4, 0x1fe
000159f0: not        a0, t0
000159f4: beqz       a5, 0x1c
000159f8: srli       a5, a3, 8
000159fc: lui        t0, 0x80000
00015a00: divu       a5, t0, a5
00015a04: mulhsu     a5, a0, a5
00015a08: sub        a0, a0, a5
00015a0c: addi       a3, a3, 0x80
00015a10: add        a6, a2, a6
00015a14: j          -0x360
00015a18: neg        a1, a0
00015a1c: not        a0, t0
00015a20: srli       a4, a4, 8
00015a24: slli       a6, a5, 0x17
00015a28: andi       t0, a1, 0x1fe
00015a2c: mul        a5, a7, a1
00015a30: not        a1, a6
00015a34: add        a6, a2, t0
00015a38: add        a1, a4, a1
00015a3c: j          -0x728

th_sdecb_r:
00015a40: bltz       a2, 0x90
00015a44: slli       a4, a1, 1
00015a48: srli       a5, a3, 7
00015a4c: mulhu      a6, a3, a3
00015a50: addi       a7, zero, 0x342
00015a54: lui        t0, 0x22
00015a58: mul        t1, a5, a5
00015a5c: mulhu      t2, a5, a5
00015a60: mul        t2, a5, t2
00015a64: mulhu      a5, t1, a5
00015a68: lui        t1, 0xfe800
00015a6c: sll        t1, t1, a4
00015a70: mul        a2, t1, a2
00015a74: lui        t1, 0x14b9
00015a78: srl        a4, a6, a4
00015a7c: addi       t0, t0, -0x674
00015a80: mulhu      a7, a4, a7
00015a84: sub        a7, t0, a7
00015a88: lui        t0, 0xccccd
00015a8c: addi       t1, t1, 0x503
00015a90: addi       t0, t0, -0x311
00015a94: add        a2, t2, a2
00015a98: mulhu      a7, a7, a4
00015a9c: sub        a7, t1, a7
00015aa0: mulhu      a7, a7, a4
00015aa4: sub        a7, t0, a7
00015aa8: mulhu      a4, a7, a4
00015aac: mulhu      a4, a4, a6
00015ab0: mulhu      a3, a4, a3
00015ab4: slli       a3, a3, 4
00015ab8: add        a2, a2, a5
00015abc: sub        a2, a2, a3
00015ac0: xor        a1, a2, a1
00015ac4: srli       a1, a1, 0x1f
00015ac8: add        a0, a1, a0
00015acc: ret        
00015ad0: addi       sp, sp, -0x10
00015ad4: sw         ra, 0xc(sp)
00015ad8: sw         s0, 8(sp)
00015adc: addi       s0, sp, 0x10
00015ae0: xor        a0, a3, a0
00015ae4: add        a3, a3, a1
00015ae8: auipc      ra, 0
00015aec: jalr       ra, ra, 0x1f8
00015af0: lw         ra, 0xc(sp)
00015af4: lw         s0, 8(sp)
00015af8: addi       sp, sp, 0x10
00015afc: ret        

nx_cell_r:
00015b00: addi       sp, sp, -0x10
00015b04: sw         ra, 0xc(sp)
00015b08: sw         s0, 8(sp)
00015b0c: addi       s0, sp, 0x10
00015b10: lw         a3, 0xc(a0)
00015b14: lw         a4, 8(a0)
00015b18: lw         a5, 4(a0)
00015b1c: lw         a0, 0(a0)
00015b20: mulhsu     a1, a3, a1
00015b24: add        a1, a4, a1
00015b28: mulhsu     a1, a1, a2
00015b2c: add        a1, a5, a1
00015b30: mulhsu     a1, a1, a2
00015b34: add        a0, a0, a1
00015b38: lw         ra, 0xc(sp)
00015b3c: lw         s0, 8(sp)
00015b40: addi       sp, sp, 0x10
00015b44: ret        

memcpy:
00015b48: beqz       a2, 0x40
00015b4c: addi       sp, sp, -0x10
00015b50: sw         ra, 0xc(sp)
00015b54: sw         s0, 8(sp)
00015b58: addi       s0, sp, 0x10
00015b5c: add        a2, a0, a2
00015b60: mv         a3, a0
00015b64: lbu        a4, 0(a1)
00015b68: addi       a1, a1, 1
00015b6c: addi       a5, a3, 1
00015b70: sb         a4, 0(a3)
00015b74: mv         a3, a5
00015b78: bne        a5, a2, -0x14
00015b7c: lw         ra, 0xc(sp)
00015b80: lw         s0, 8(sp)
00015b84: addi       sp, sp, 0x10
00015b88: ret        

memmove:
00015b8c: addi       sp, sp, -0x10
00015b90: sw         ra, 0xc(sp)
00015b94: sw         s0, 8(sp)
00015b98: addi       s0, sp, 0x10
00015b9c: bgeu       a0, a1, 0x2c
00015ba0: beqz       a2, 0x50
00015ba4: add        a2, a0, a2
00015ba8: mv         a3, a0
00015bac: lbu        a4, 0(a1)
00015bb0: addi       a1, a1, 1
00015bb4: addi       a5, a3, 1
00015bb8: sb         a4, 0(a3)
00015bbc: mv         a3, a5
00015bc0: bne        a5, a2, -0x14
00015bc4: j          0x2c
00015bc8: beqz       a2, 0x28
00015bcc: addi       a3, a2, -1
00015bd0: add        a2, a0, a3
00015bd4: add        a1, a1, a3
00015bd8: addi       a3, a0, -1
00015bdc: lbu        a4, 0(a1)
00015be0: sb         a4, 0(a2)
00015be4: addi       a2, a2, -1
00015be8: addi       a1, a1, -1
00015bec: bne        a2, a3, -0x10
00015bf0: lw         ra, 0xc(sp)
00015bf4: lw         s0, 8(sp)
00015bf8: addi       sp, sp, 0x10
00015bfc: ret        

memset:
00015c00: beqz       a2, 0x38
00015c04: addi       sp, sp, -0x10
00015c08: sw         ra, 0xc(sp)
00015c0c: sw         s0, 8(sp)
00015c10: addi       s0, sp, 0x10
00015c14: add        a2, a0, a2
00015c18: mv         a3, a0
00015c1c: addi       a4, a3, 1
00015c20: sb         a1, 0(a3)
00015c24: mv         a3, a4
00015c28: bne        a4, a2, -0xc
00015c2c: lw         ra, 0xc(sp)
00015c30: lw         s0, 8(sp)
00015c34: addi       sp, sp, 0x10
00015c38: ret        

eik_batch:
00015c3c: beqz       a3, 0xa0
00015c40: addi       sp, sp, -0x20
00015c44: sw         ra, 0x1c(sp)
00015c48: sw         s0, 0x18(sp)
00015c4c: sw         s1, 0x14(sp)
00015c50: sw         s2, 0x10(sp)
00015c54: sw         s3, 0xc(sp)
00015c58: sw         s4, 8(sp)
00015c5c: sw         s5, 4(sp)
00015c60: addi       s0, sp, 0x20
00015c64: mv         s1, a2
00015c68: mv         s2, a1
00015c6c: mv         s3, a0
00015c70: slli       a3, a3, 2
00015c74: add        s4, a1, a3
00015c78: addi       s5, zero, 1
00015c7c: j          0x1c
00015c80: auipc      ra, 0xfffff
00015c84: jalr       ra, ra, 0x11c
00015c88: sw         a0, 0(s1)
00015c8c: addi       s2, s2, 4
00015c90: addi       s1, s1, 4
00015c94: beq        s2, s4, 0x28
00015c98: lw         a0, 0(s2)
00015c9c: beq        s3, s5, -0x1c
00015ca0: bnez       s3, 0x10
00015ca4: auipc      ra, 0xfffff
00015ca8: jalr       ra, ra, -0x72c
00015cac: j          -0x24
00015cb0: auipc      ra, 0xfffff
00015cb4: jalr       ra, ra, 0x588
00015cb8: j          -0x30
00015cbc: lw         ra, 0x1c(sp)
00015cc0: lw         s0, 0x18(sp)
00015cc4: lw         s1, 0x14(sp)
00015cc8: lw         s2, 0x10(sp)
00015ccc: lw         s3, 0xc(sp)
00015cd0: lw         s4, 8(sp)
00015cd4: lw         s5, 4(sp)
00015cd8: addi       sp, sp, 0x20
00015cdc: ret        

__udivdi3:
00015ce0: addi       sp, sp, -0x10
00015ce4: sw         ra, 0xc(sp)
00015ce8: sw         s0, 8(sp)
00015cec: addi       s0, sp, 0x10
00015cf0: mv         a4, zero
00015cf4: lw         ra, 0xc(sp)
00015cf8: lw         s0, 8(sp)
00015cfc: addi       sp, sp, 0x10
00015d00: auipc      t1, 0
00015d04: jalr       zero, t1, 8

__udivmoddi4:
00015d08: addi       sp, sp, -0x10
00015d0c: sw         ra, 0xc(sp)
00015d10: sw         s0, 8(sp)
00015d14: addi       s0, sp, 0x10
00015d18: beq        a1, a3, 0x26c
00015d1c: sltu       a5, a1, a3
00015d20: bnez       a5, 0x26c
00015d24: beqz       a3, 0x294
00015d28: srli       a5, a3, 1
00015d2c: lui        a6, 0x55555
00015d30: or         a5, a3, a5
00015d34: addi       a6, a6, 0x555
00015d38: srli       a7, a5, 2
00015d3c: or         a5, a5, a7
00015d40: srli       a7, a5, 4
00015d44: or         a5, a5, a7
00015d48: srli       a7, a5, 8
00015d4c: or         a5, a5, a7
00015d50: srli       a7, a5, 0x10
00015d54: or         a5, a5, a7
00015d58: not        a5, a5
00015d5c: srli       a7, a5, 1
00015d60: and        a6, a7, a6
00015d64: lui        a7, 0x33333
00015d68: addi       a7, a7, 0x333
00015d6c: sub        a5, a5, a6
00015d70: and        a6, a5, a7
00015d74: srli       a5, a5, 2
00015d78: and        a5, a5, a7
00015d7c: lui        a7, 0xf0f1
00015d80: add        a5, a6, a5
00015d84: srli       a6, a5, 4
00015d88: add        a5, a5, a6
00015d8c: lui        a6, 0x1010
00015d90: addi       a7, a7, -0xf1
00015d94: and        a5, a5, a7
00015d98: addi       a6, a6, 0x101
00015d9c: mul        a5, a5, a6
00015da0: srli       a7, a5, 0x18
00015da4: beqz       a7, 0x358
00015da8: neg        a6, a7
00015dac: sll        a5, a3, a7
00015db0: srl        t0, a2, a6
00015db4: or         a5, t0, a5
00015db8: sll        a7, a1, a7
00015dbc: srl        t0, a0, a6
00015dc0: beqz       a5, 0x4d8
00015dc4: srli       t1, a5, 1
00015dc8: lui        t2, 0x55555
00015dcc: or         t1, a5, t1
00015dd0: addi       t2, t2, 0x555
00015dd4: srli       t3, t1, 2
00015dd8: or         t1, t1, t3
00015ddc: srli       t3, t1, 4
00015de0: or         t1, t1, t3
00015de4: srli       t3, t1, 8
00015de8: or         t1, t1, t3
00015dec: srli       t3, t1, 0x10
00015df0: or         t1, t1, t3
00015df4: not        t1, t1
00015df8: srli       t3, t1, 1
00015dfc: and        t2, t3, t2
00015e00: lui        t3, 0x33333
00015e04: addi       t3, t3, 0x333
00015e08: sub        t1, t1, t2
00015e0c: and        t2, t1, t3
00015e10: srli       t1, t1, 2
00015e14: and        t1, t1, t3
00015e18: lui        t3, 0xf0f1
00015e1c: add        t1, t2, t1
00015e20: srli       t2, t1, 4
00015e24: add        t1, t1, t2
00015e28: lui        t2, 0x1010
00015e2c: addi       t3, t3, -0xf1
00015e30: and        t1, t1, t3
00015e34: addi       t2, t2, 0x101
00015e38: mul        t1, t1, t2
00015e3c: srli       t3, t1, 0x18
00015e40: or         t1, t0, a7
00015e44: andi       a7, t3, 0x1f
00015e48: srl        t2, a1, a6
00015e4c: beqz       a7, 0x1c
00015e50: sll        a5, a5, a7
00015e54: sll        a6, t2, a7
00015e58: neg        t0, t3
00015e5c: srl        t0, t1, t0
00015e60: or         t2, a6, t0
00015e64: sll        t1, t1, a7
00015e68: srli       a6, a5, 0x10
00015e6c: divu       a7, t2, a6
00015e70: lui        t0, 0x10
00015e74: addi       t4, t0, -1
00015e78: and        t0, a5, t4
00015e7c: srli       t3, t1, 0x10
00015e80: and        t1, t1, t4
00015e84: mul        t4, a7, a6
00015e88: sub        t4, t2, t4
00015e8c: j          0x14
00015e90: add        t4, t4, a6
00015e94: srli       t5, t4, 0x10
00015e98: addi       a7, a7, -1
00015e9c: bnez       t5, 0x1c
00015ea0: srli       t5, a7, 0x10
00015ea4: bnez       t5, -0x14
00015ea8: mul        t5, a7, t0
00015eac: slli       t6, t4, 0x10
00015eb0: or         t6, t6, t3
00015eb4: bltu       t6, t5, -0x24
00015eb8: slli       t2, t2, 0x10
00015ebc: or         t2, t2, t3
00015ec0: mul        a5, a7, a5
00015ec4: sub        t2, t2, a5
00015ec8: divu       a5, t2, a6
00015ecc: mul        t3, a5, a6
00015ed0: sub        t2, t2, t3
00015ed4: j          0x14
00015ed8: add        t2, t2, a6
00015edc: srli       t3, t2, 0x10
00015ee0: addi       a5, a5, -1
00015ee4: bnez       t3, 0x1c
00015ee8: srli       t3, a5, 0x10
00015eec: bnez       t3, -0x14
00015ef0: mul        t3, a5, t0
00015ef4: slli       t4, t2, 0x10
00015ef8: or         t4, t4, t1
00015efc: bltu       t4, t3, -0x24
00015f00: slli       a6, a7, 0x10
00015f04: add        a6, a5, a6
00015f08: mulhu      a5, a2, a6
00015f0c: mulhu      t0, a3, a6
00015f10: mul        a7, a3, a6
00015f14: add        a5, a7, a5
00015f18: sltu       a7, a5, a7
00015f1c: neg        t1, a7
00015f20: mul        a7, a2, a6
00015f24: bne        t0, t1, 0x10
00015f28: bltu       a1, a5, 0xc
00015f2c: bne        a5, a1, 0x20
00015f30: bgeu       a0, a7, 0x1c
00015f34: addi       a6, a6, -1
00015f38: sub        a2, a7, a2
00015f3c: sltu       a7, a7, a2
00015f40: add        a3, a7, a3
00015f44: sub        a5, a5, a3
00015f48: mv         a7, a2
00015f4c: beqz       a4, 0x1c
00015f50: sub        a2, a0, a7
00015f54: sub        a1, a1, a5
00015f58: sltu       a0, a0, a2
00015f5c: sub        a1, a1, a0
00015f60: sw         a2, 0(a4)
00015f64: sw         a1, 4(a4)
00015f68: mv         a5, zero
00015f6c: mv         a0, a6
00015f70: mv         a1, a5
00015f74: lw         ra, 0xc(sp)
00015f78: lw         s0, 8(sp)
00015f7c: addi       sp, sp, 0x10
00015f80: ret        
00015f84: sltu       a5, a0, a2
00015f88: beqz       a5, -0x264
00015f8c: mv         a6, zero
00015f90: mv         a5, zero
00015f94: beqz       a4, -0x28
00015f98: sw         a0, 0(a4)
00015f9c: sw         a1, 4(a4)
00015fa0: mv         a0, a6
00015fa4: mv         a1, a5
00015fa8: lw         ra, 0xc(sp)
00015fac: lw         s0, 8(sp)
00015fb0: addi       sp, sp, 0x10
00015fb4: ret        
00015fb8: bgeu       a1, a2, 0x164
00015fbc: srli       a3, a2, 1
00015fc0: lui        a5, 0x55555
00015fc4: or         a3, a2, a3
00015fc8: addi       a5, a5, 0x555
00015fcc: srli       a6, a3, 2
00015fd0: or         a3, a3, a6
00015fd4: srli       a6, a3, 4
00015fd8: or         a3, a3, a6
00015fdc: srli       a6, a3, 8
00015fe0: or         a3, a3, a6
00015fe4: srli       a6, a3, 0x10
00015fe8: or         a3, a3, a6
00015fec: not        a3, a3
00015ff0: srli       a6, a3, 1
00015ff4: and        a5, a6, a5
00015ff8: lui        a6, 0x33333
00015ffc: addi       a6, a6, 0x333
00016000: sub        a3, a3, a5
00016004: and        a5, a3, a6
00016008: srli       a3, a3, 2
0001600c: and        a3, a3, a6
00016010: lui        a6, 0xf0f1
00016014: add        a3, a5, a3
00016018: srli       a5, a3, 4
0001601c: add        a3, a3, a5
00016020: lui        a5, 0x1010
00016024: addi       a6, a6, -0xf1
00016028: and        a3, a3, a6
0001602c: addi       a5, a5, 0x101
00016030: mul        a3, a3, a5
00016034: srli       a6, a3, 0x18
00016038: beqz       a6, 0x1c
0001603c: sll        a2, a2, a6
00016040: sll        a1, a1, a6
00016044: neg        a3, a6
00016048: srl        a3, a0, a3
0001604c: or         a1, a3, a1
00016050: sll        a0, a0, a6
00016054: srli       a5, a2, 0x10
00016058: divu       a3, a1, a5
0001605c: lui        a7, 0x10
00016060: addi       a7, a7, -1
00016064: and        t0, a2, a7
00016068: srli       t1, a0, 0x10
0001606c: and        a7, a0, a7
00016070: mul        a0, a3, a5
00016074: sub        a0, a1, a0
00016078: j          0x14
0001607c: add        a0, a0, a5
00016080: srli       t2, a0, 0x10
00016084: addi       a3, a3, -1
00016088: bnez       t2, 0x1c
0001608c: srli       t2, a3, 0x10
00016090: bnez       t2, -0x14
00016094: mul        t2, a3, t0
00016098: slli       t3, a0, 0x10
0001609c: or         t3, t3, t1
000160a0: bltu       t3, t2, -0x24
000160a4: slli       a1, a1, 0x10
000160a8: or         a0, a1, t1
000160ac: mul        a1, a3, a2
000160b0: sub        a1, a0, a1
000160b4: divu       a0, a1, a5
000160b8: mul        t1, a0, a5
000160bc: sub        t1, a1, t1
000160c0: j          0x14
000160c4: add        t1, t1, a5
000160c8: srli       t2, t1, 0x10
000160cc: addi       a0, a0, -1
000160d0: bnez       t2, 0x1c
000160d4: srli       t2, a0, 0x10
000160d8: bnez       t2, -0x14
000160dc: mul        t2, a0, t0
000160e0: slli       t3, t1, 0x10
000160e4: or         t3, t3, a7
000160e8: bltu       t3, t2, -0x24
000160ec: mv         a5, zero
000160f0: slli       a1, a1, 0x10
000160f4: or         a1, a1, a7
000160f8: j          0x168
000160fc: addi       a6, zero, 1
00016100: mv         a5, zero
00016104: beqz       a4, -0x198
00016108: sub        a1, a1, a3
0001610c: sltu       a3, a0, a2
00016110: sub        a0, a0, a2
00016114: sub        a1, a1, a3
00016118: j          -0x180
0001611c: divu       a5, a1, a2
00016120: srli       a3, a2, 1
00016124: lui        a6, 0x55555
00016128: or         a3, a2, a3
0001612c: addi       a6, a6, 0x555
00016130: srli       a7, a3, 2
00016134: or         a3, a3, a7
00016138: srli       a7, a3, 4
0001613c: or         a3, a3, a7
00016140: srli       a7, a3, 8
00016144: or         a3, a3, a7
00016148: srli       a7, a3, 0x10
0001614c: or         a3, a3, a7
00016150: not        a3, a3
00016154: srli       a7, a3, 1
00016158: and        a6, a7, a6
0001615c: lui        a7, 0x33333
00016160: addi       a7, a7, 0x333
00016164: sub        a3, a3, a6
00016168: and        a6, a3, a7
0001616c: srli       a3, a3, 2
00016170: and        a3, a3, a7
00016174: lui        a7, 0xf0f1
00016178: add        a3, a6, a3
0001617c: srli       a6, a3, 4
00016180: add        a3, a3, a6
00016184: lui        a6, 0x1010
00016188: addi       a7, a7, -0xf1
0001618c: and        a3, a3, a7
00016190: mul        a7, a5, a2
00016194: addi       a6, a6, 0x101
00016198: mul        a3, a3, a6
0001619c: srli       a6, a3, 0x18
000161a0: sub        t1, a1, a7
000161a4: beqz       a6, 0x1c
000161a8: sll        a2, a2, a6
000161ac: sll        a1, t1, a6
000161b0: neg        a3, a6
000161b4: srl        a3, a0, a3
000161b8: or         t1, a1, a3
000161bc: sll        a0, a0, a6
000161c0: srli       a1, a2, 0x10
000161c4: divu       a3, t1, a1
000161c8: lui        a7, 0x10
000161cc: addi       a7, a7, -1
000161d0: and        t0, a2, a7
000161d4: srli       t2, a0, 0x10
000161d8: and        a7, a0, a7
000161dc: mul        a0, a3, a1
000161e0: sub        a0, t1, a0
000161e4: j          0x14
000161e8: add        a0, a0, a1
000161ec: srli       t3, a0, 0x10
000161f0: addi       a3, a3, -1
000161f4: bnez       t3, 0x1c
000161f8: srli       t3, a3, 0x10
000161fc: bnez       t3, -0x14
00016200: mul        t3, a3, t0
00016204: slli       t4, a0, 0x10
00016208: or         t4, t4, t2
0001620c: bltu       t4, t3, -0x24
00016210: slli       t1, t1, 0x10
00016214: or         a0, t1, t2
00016218: mul        t1, a3, a2
0001621c: sub        t1, a0, t1
00016220: divu       a0, t1, a1
00016224: mul        t2, a0, a1
00016228: sub        t2, t1, t2
0001622c: j          0x14
00016230: add        t2, t2, a1
00016234: srli       t3, t2, 0x10
00016238: addi       a0, a0, -1
0001623c: bnez       t3, 0x1c
00016240: srli       t3, a0, 0x10
00016244: bnez       t3, -0x14
00016248: mul        t3, a0, t0
0001624c: slli       t4, t2, 0x10
00016250: or         t4, t4, a7
00016254: bltu       t4, t3, -0x24
00016258: slli       t1, t1, 0x10
0001625c: or         a1, t1, a7
00016260: mul        a2, a0, a2
00016264: sub        a1, a1, a2
00016268: srl        a1, a1, a6
0001626c: slli       a3, a3, 0x10
00016270: add        a6, a0, a3
00016274: beqz       a4, -0x308
00016278: sw         a1, 0(a4)
0001627c: sw         zero, 4(a4)
00016280: mv         a0, a6
00016284: mv         a1, a5
00016288: lw         ra, 0xc(sp)
0001628c: lw         s0, 8(sp)
00016290: addi       sp, sp, 0x10
00016294: ret        
00016298: addi       t3, zero, 0x20
0001629c: or         t1, t0, a7
000162a0: andi       a7, t3, 0x1f
000162a4: srl        t2, a1, a6
000162a8: bnez       a7, -0x458
000162ac: j          -0x444
