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
000149e0: jalr       zero, t1, 0x48
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
00014d78: jalr       zero, t1, -0x350
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
00014ed0: jalr       zero, t1, -0x4a8
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
000150f8: jalr       zero, t1, -0x6d0
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
000151cc: jalr       zero, t1, -0x7a4
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
00015238: bltz       a0, 0x20
0001523c: srli       a1, a0, 0x17
00015240: addi       a5, a1, -0x77
00015244: bgeu       a0, a5, 0x40
00015248: addi       a2, a1, -0x67
0001524c: bgeu       a0, a2, 0x17c
00015250: lui        a0, 0x3f800
00015254: ret        
00015258: lui        a1, 0xbf800
0001525c: bltu       a1, a0, 0xac
00015260: lui        a1, 0xba7ff
00015264: bltu       a1, a0, 0x1bc
00015268: lui        a1, 0xb3c00
0001526c: bltu       a1, a0, 0x3f8
00015270: lui        a1, 0xb3000
00015274: bgeu       a1, a0, -0x24
00015278: lui        a1, 0x3f800
0001527c: addi       a0, a1, -1
00015280: ret        
00015284: lui        a1, 0x41000
00015288: bltu       a1, a0, 0x17c
0001528c: slli       a6, a0, 9
00015290: lui        a2, 0x11
00015294: addi       a2, a2, 0x69c
00015298: lw         a0, 0x600(a2)
0001529c: lw         a1, 0x604(a2)
000152a0: sll        a7, a6, a5
000152a4: mulhu      a3, a6, a0
000152a8: sub        a4, a1, a5
000152ac: add        a0, a0, a3
000152b0: srl        a5, a0, a4
000152b4: srli       a0, a5, 1
000152b8: andi       a3, a5, 0x3fc
000152bc: ori        a4, a0, 1
000152c0: add        a3, a2, a3
000152c4: mul        a0, a4, a1
000152c8: lw         a3, 0(a3)
000152cc: sub        a0, a7, a0
000152d0: mulh       a1, a0, a0
000152d4: srli       a1, a1, 9
000152d8: add        a1, a0, a1
000152dc: mulhsu     a1, a1, a3
000152e0: srai       a1, a1, 8
000152e4: add        a1, a1, a3
000152e8: srli       a5, a5, 0xa
000152ec: andi       a6, a1, 0xf8
000152f0: addi       a5, a5, 0x7e
000152f4: bnez       a6, 0x2d8
000152f8: lw         a7, 0x610(a2)
000152fc: mulhu      a6, a7, a4
00015300: add        a0, a0, a6
00015304: j          0x2d8
00015308: lui        a1, 0xc0800
0001530c: bltu       a1, a0, 0x190
00015310: slli       a3, a0, 0xf
00015314: srli       a1, a0, 0xd
00015318: lui        a2, 0xfffb3
0001531c: addi       a2, a2, -0x794
00015320: andi       a1, a1, -0x10
00015324: add        a4, a2, a1
00015328: lw         a5, 0x690(a4)
0001532c: lh         a6, 0x684(a4)
00015330: lw         a1, 0x684(a4)
00015334: lw         a2, 0x688(a4)
00015338: lw         a4, 0x68c(a4)
0001533c: mulhsu     a6, a6, a3
00015340: add        a5, a5, a6
00015344: mulhsu     a5, a5, a3
00015348: add        a4, a4, a5
0001534c: mulhu      a4, a4, a3
00015350: add        a4, a2, a4
00015354: slli       a3, a4, 0x18
00015358: bgeu       a3, a2, 0x300
0001535c: bltz       a2, 0x11c
00015360: srli       a4, a4, 8
00015364: srli       a2, a0, 0x17
00015368: addi       a5, a2, -0x177
0001536c: lui        a2, 0x11
00015370: addi       a2, a2, 0x69c
00015374: lw         a7, 0x604(a2)
00015378: lw         a3, 0x60c(a2)
0001537c: slli       a0, a0, 9
00015380: lui        t0, 0x17184
00015384: sll        t1, a0, a5
00015388: sub        a5, a3, a5
0001538c: mulhsu     a0, a3, a0
00015390: add        a0, a5, a0
00015394: sra        a0, a0, a5
00015398: ori        t2, a0, 1
0001539c: andi       a0, a0, 0x1fe
000153a0: add        a6, a2, a0
000153a4: mul        a5, t2, t0
000153a8: mulh       t0, t2, t0
000153ac: add        a0, a6, a0
000153b0: lw         a3, 0(a0)
000153b4: mul        a0, t2, a7
000153b8: add        a0, a0, t1
000153bc: sub        a0, t0, a0
000153c0: sub        a1, a1, a4
000153c4: j          0x234
000153c8: addi       a2, zero, 0x74
000153cc: bltu       a2, a1, 0x144
000153d0: xori       a2, a1, 0x1f
000153d4: lui        a5, 0x3f800
000153d8: or         a1, a0, a5
000153dc: slli       a3, a1, 8
000153e0: srl        a0, a3, a2
000153e4: mulhu      a4, a0, a0
000153e8: add        a0, a0, a4
000153ec: addi       a4, a0, 0x82
000153f0: andi       a0, a4, 0xfe
000153f4: beqz       a0, 0x338
000153f8: srli       a1, a4, 8
000153fc: xor        a0, a1, a5
00015400: ret        
00015404: lui        a1, 0x42b17
00015408: addi       a1, a1, 0x217
0001540c: bgeu       a1, a0, 0x148
00015410: lui        a1, 0x7f800
00015414: bltu       a1, a0, 0x30c
00015418: mv         a0, a1
0001541c: ret        
00015420: lui        a1, 0xbe800
00015424: bgeu       a1, a0, 0x294
00015428: slli       a3, a0, 0xd
0001542c: srli       a1, a0, 0xf
00015430: lui        a2, 0xffffb
00015434: addi       a2, a2, -0x794
00015438: andi       a1, a1, -0x10
0001543c: add        a4, a2, a1
00015440: lw         a5, 0x390(a4)
00015444: lh         a6, 0x384(a4)
00015448: lw         a1, 0x384(a4)
0001544c: lw         a2, 0x388(a4)
00015450: lw         a4, 0x38c(a4)
00015454: mulhsu     a6, a6, a3
00015458: add        a5, a5, a6
0001545c: mulhsu     a5, a5, a3
00015460: add        a4, a4, a5
00015464: mulhsu     a4, a4, a3
00015468: add        a4, a2, a4
0001546c: slli       a3, a4, 0x18
00015470: bgeu       a3, a2, 0x1e8
00015474: bgez       a2, -0x114
00015478: add        a4, a1, a4
0001547c: slli       a1, a1, 7
00015480: lui        a2, 0x7f800
00015484: and        a1, a1, a2
00015488: bltz       a4, 0x438
0001548c: andi       a2, a4, 0xfc
00015490: srli       a4, a4, 8
00015494: bnez       a2, 0x1c8
00015498: j          -0x134
0001549c: lui        a1, 0xc0fff
000154a0: bltu       a1, a0, 0x270
000154a4: srli       a1, a0, 0x10
000154a8: lui        a2, 8
000154ac: addi       a2, a2, -0x794
000154b0: andi       a1, a1, -4
000154b4: add        a1, a2, a1
000154b8: lw         a2, -0x3f4(a1)
000154bc: lw         a3, -0x474(a1)
000154c0: slli       a4, a0, 0xe
000154c4: lw         a5, -0x4f4(a1)
000154c8: mulhsu     a6, a2, a0
000154cc: add        a3, a3, a6
000154d0: lw         a6, -0x574(a1)
000154d4: mulhsu     a3, a3, a4
000154d8: add        a3, a5, a3
000154dc: lw         a1, -0x5f4(a1)
000154e0: mulhsu     a3, a3, a4
000154e4: add        a3, a6, a3
000154e8: mulhsu     a3, a3, a4
000154ec: add        a3, a1, a3
000154f0: bltz       a3, 0x388
000154f4: addi       a1, a3, 0x80
000154f8: andi       a4, a1, 0x1f8
000154fc: srli       a1, a1, 9
00015500: slli       a2, a2, 0x17
00015504: beqz       a4, 0x384
00015508: sub        a0, a1, a2
0001550c: ret        
00015510: lui        a5, 0x3f800
00015514: not        a2, a1
00015518: or         a1, a0, a5
0001551c: slli       a3, a1, 8
00015520: srl        a0, a3, a2
00015524: lui        a4, 0xaaaab
00015528: mulhu      a4, a0, a4
0001552c: mulhu      a4, a4, a0
00015530: add        a4, a0, a4
00015534: mulhu      a4, a4, a0
00015538: add        a0, a0, a4
0001553c: addi       a4, a0, 0x81
00015540: andi       a0, a4, 0xff
00015544: beqz       a0, 0x3b0
00015548: srli       a1, a4, 8
0001554c: or         a0, a1, a5
00015550: ret        
00015554: slli       a6, a0, 9
00015558: lui        a2, 0x11
0001555c: addi       a2, a2, 0x69c
00015560: lw         a0, 0x600(a2)
00015564: lw         a1, 0x604(a2)
00015568: sll        t0, a6, a5
0001556c: lw         a7, 0x610(a2)
00015570: mulhu      a3, a6, a0
00015574: sub        a4, a1, a5
00015578: add        a0, a0, a3
0001557c: srl        a5, a0, a4
00015580: srli       a0, a5, 1
00015584: andi       a3, a5, 0x3fc
00015588: ori        a4, a0, 1
0001558c: add        a3, a2, a3
00015590: mul        a0, a4, a1
00015594: mulhu      a1, a4, a7
00015598: lw         a3, 0(a3)
0001559c: sub        a0, t0, a0
000155a0: add        a0, a0, a1
000155a4: mulh       a1, a0, a0
000155a8: srli       a1, a1, 9
000155ac: add        a1, a0, a1
000155b0: mulhsu     a1, a1, a3
000155b4: srai       a1, a1, 8
000155b8: add        a1, a1, a3
000155bc: srli       a5, a5, 0xa
000155c0: andi       a6, a1, 0xf8
000155c4: addi       a5, a5, 0x7e
000155c8: beqz       a6, 0x14
000155cc: slli       a5, a5, 0x17
000155d0: srli       a1, a1, 8
000155d4: add        a0, a1, a5
000155d8: ret        
000155dc: andi       a6, a4, 0x1fe
000155e0: slli       a5, a5, 0x17
000155e4: srli       a1, a1, 8
000155e8: add        a6, a2, a6
000155ec: add        a1, a5, a1
000155f0: addi       a1, a1, -1
000155f4: mul        a5, a7, a4
000155f8: lw         a2, 0x608(a2)
000155fc: mulh       a4, a0, a0
00015600: addi       a3, a3, -0x86
00015604: lhu        a6, 0x400(a6)
00015608: slli       a7, a3, 0x10
0001560c: srli       t0, a3, 0x10
00015610: mul        t1, t0, a0
00015614: mulhu      a5, a5, t0
00015618: add        a5, t1, a5
0001561c: mulhsu     a2, a0, a2
00015620: or         a6, a7, a6
00015624: addi       a2, a2, 0x230
00015628: slli       a7, a6, 8
0001562c: mulhsu     a0, a0, a6
00015630: mulhsu     a2, a2, a4
00015634: add        a2, a2, a4
00015638: mulhsu     a2, a2, a3
0001563c: slli       a2, a2, 7
00015640: add        a5, a5, a7
00015644: add        a0, a0, a2
00015648: add        a0, a5, a0
0001564c: srli       a0, a0, 0x1f
00015650: add        a0, a0, a1
00015654: ret        
00015658: srli       a4, a4, 8
0001565c: sub        a0, a1, a4
00015660: ret        
00015664: not        a2, a0
00015668: lui        a5, 0x3f800
0001566c: srli       a2, a2, 0x17
00015670: or         a1, a0, a5
00015674: slli       a3, a1, 8
00015678: srl        a0, a3, a2
0001567c: mulhu      a4, a0, a0
00015680: sub        a4, a0, a4
00015684: addi       a4, a4, 0x41
00015688: andi       a6, a4, 0x7e
0001568c: bnez       a6, 0x78
00015690: addi       a5, a2, -0x90
00015694: bltu       a3, a5, 0x260
00015698: srl        a1, a3, a5
0001569c: mulhu      a0, a0, a1
000156a0: sub        a1, a1, a0
000156a4: srli       a1, a1, 0x16
000156a8: lui        a0, 0x7f000
000156ac: sub        a0, a0, a1
000156b0: srli       a0, a0, 1
000156b4: ret        
000156b8: lui        a1, 0xbd800
000156bc: bltu       a1, a0, 0xa0
000156c0: srli       a2, a0, 0x17
000156c4: lui        a5, 0x3f800
000156c8: lui        a4, 0x53888
000156cc: or         a1, a0, a5
000156d0: not        a2, a2
000156d4: slli       a3, a1, 8
000156d8: srl        a6, a3, a2
000156dc: mulhu      a4, a6, a4
000156e0: lui        a7, 0xaaa46
000156e4: sub        a4, a7, a4
000156e8: mulhu      a4, a4, a6
000156ec: mulhu      a4, a4, a6
000156f0: sub        a4, a4, a6
000156f4: mulhu      a4, a4, a6
000156f8: addi       a4, a4, 0x41
000156fc: andi       a7, a4, 0x7f
00015700: beqz       a7, 0x1e0
00015704: srli       a4, a4, 7
00015708: sub        a0, a5, a4
0001570c: ret        
00015710: lui        a1, 0xc2d00
00015714: bltu       a0, a1, 0xa0
00015718: lui        a1, 0xff800
0001571c: bgeu       a1, a0, 0x17c
00015720: lui        a1, 0x400
00015724: or         a0, a0, a1
00015728: ret        
0001572c: addi       a0, a2, -0x70
00015730: bltu       a3, a0, 0x1c4
00015734: srl        a0, a3, a0
00015738: mulhu      a1, a0, a0
0001573c: srli       a1, a1, 0x10
00015740: add        a0, a0, a1
00015744: srli       a0, a0, 0x17
00015748: addi       a0, a0, 1
0001574c: srli       a0, a0, 1
00015750: lui        a1, 0x3f800
00015754: or         a0, a0, a1
00015758: ret        
0001575c: srli       a1, a0, 0x11
00015760: lui        a2, 0xd
00015764: addi       a2, a2, -0x794
00015768: andi       a1, a1, -0x10
0001576c: add        a1, a2, a1
00015770: lw         a2, 0x14c(a1)
00015774: lw         a3, 0x148(a1)
00015778: lw         a4, 0x144(a1)
0001577c: lw         a1, 0x140(a1)
00015780: mulhsu     a2, a2, a0
00015784: add        a2, a3, a2
00015788: slli       a3, a0, 0xb
0001578c: mulhsu     a2, a2, a3
00015790: add        a2, a4, a2
00015794: mulhsu     a2, a2, a3
00015798: add        a1, a1, a2
0001579c: andi       a2, a1, 0xfc
000157a0: srli       a1, a1, 8
000157a4: beqz       a2, 0x1c8
000157a8: lui        a0, 0x3e800
000157ac: add        a0, a1, a0
000157b0: ret        
000157b4: lui        a1, 0xc2cdb
000157b8: bgeu       a0, a1, 0xe8
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
00015834: bltz       a4, 0x144
00015838: beqz       a3, 0x15c
0001583c: addi       sp, sp, -0x10
00015840: sw         ra, 0xc(sp)
00015844: sw         s0, 8(sp)
00015848: addi       s0, sp, 0x10
0001584c: xori       a1, t2, 0x7f
00015850: srli       a3, a3, 0x1f
00015854: slli       a1, a1, 0x17
00015858: sltiu      a2, a4, 0x10
0001585c: mv         a0, zero
00015860: auipc      ra, 0
00015864: jalr       ra, ra, 0x41c
00015868: lw         ra, 0xc(sp)
0001586c: lw         s0, 8(sp)
00015870: addi       sp, sp, 0x10
00015874: ret        
00015878: andi       a4, a3, 0xf8
0001587c: srai       a1, a3, 8
00015880: slli       a2, a2, 0x17
00015884: bnez       a4, -0x37c
00015888: andi       a3, a3, 6
0001588c: addi       a4, a2, 1
00015890: bnez       a3, -0x52c
00015894: j          -0x238
00015898: mv         a0, zero
0001589c: ret        
000158a0: lui        a1, 0xc2cdc
000158a4: lui        a2, 0xc2cff
000158a8: addi       a1, a1, -0xc9
000158ac: addi       a2, a2, 0x1b5
000158b0: sltu       a1, a0, a1
000158b4: sltu       a0, a0, a2
000158b8: add        a0, a1, a0
000158bc: ret        
000158c0: addi       a4, a4, 0x80
000158c4: andi       a2, a4, 0x1fc
000158c8: srai       a4, a4, 9
000158cc: bnez       a2, -0x270
000158d0: bnez       a1, -0x56c
000158d4: lui        a2, 0x11
000158d8: addi       a2, a2, 0x6a0
000158dc: j          -0x110
000158e0: srli       a5, a6, 0x17
000158e4: beqz       a5, 0x10
000158e8: srli       a4, a4, 7
000158ec: lui        a1, 0x3f800
000158f0: j          -0x58c
000158f4: addi       a2, a2, 0x17
000158f8: lui        a5, 0x55556
000158fc: srl        a0, a3, a2
00015900: mulhu      a2, a0, a0
00015904: mulhu      a3, a0, a5
00015908: mul        a6, a0, a0
0001590c: slli       a7, a0, 0x11
00015910: mulhu      a3, a3, a2
00015914: srli       a6, a6, 0x18
00015918: slli       a2, a2, 8
0001591c: mulhu      a0, a3, a0
00015920: or         a2, a2, a6
00015924: srli       a0, a0, 0xa
00015928: add        a0, a2, a0
0001592c: add        a2, a7, a3
00015930: bltu       a1, a5, 0x20
00015934: srli       a4, a4, 7
00015938: sub        a2, a2, a0
0001593c: srli       a2, a2, 0x1f
00015940: sub        a1, a2, a4
00015944: lui        a0, 0x3f800
00015948: add        a0, a1, a0
0001594c: ret        
00015950: srli       a4, a4, 8
00015954: add        a0, a0, a2
00015958: srai       a0, a0, 0x1f
0001595c: add        a0, a4, a0
00015960: lui        a1, 0x3f800
00015964: add        a0, a0, a1
00015968: ret        
0001596c: lui        a4, 0xc1800
00015970: addi       a4, a4, 1
00015974: j          -0x610
00015978: bgeu       a1, a5, 0x2c
0001597c: andi       a1, a4, 0xf8
00015980: beqz       a1, 0x7c
00015984: srli       a4, a4, 8
00015988: slli       a5, a5, 0x17
0001598c: sub        a0, a4, a5
00015990: ret        
00015994: addi       a2, a2, 4
00015998: bltz       t0, -0x700
0001599c: bgez       t1, -0x628
000159a0: j          -0x440
000159a4: addi       t2, t2, 0xa
000159a8: addi       a1, a4, -0x8e
000159ac: addi       a4, a4, -0x7e
000159b0: srl        a1, a1, t2
000159b4: srl        a4, a4, t2
000159b8: addi       a1, a1, 1
000159bc: addi       a4, a4, 1
000159c0: srli       a1, a1, 1
000159c4: srli       a4, a4, 1
000159c8: beq        a1, a4, -0x5b0
000159cc: neg        a4, a0
000159d0: andi       a6, a4, 0x1fe
000159d4: not        a0, t0
000159d8: beqz       a5, 0x1c
000159dc: srli       a5, a3, 8
000159e0: lui        t0, 0x80000
000159e4: divu       a5, t0, a5
000159e8: mulhsu     a5, a0, a5
000159ec: sub        a0, a0, a5
000159f0: addi       a3, a3, 0x80
000159f4: add        a6, a2, a6
000159f8: j          -0x404
000159fc: neg        a1, a0
00015a00: not        a0, t0
00015a04: srli       a4, a4, 8
00015a08: slli       a6, a5, 0x17
00015a0c: andi       t0, a1, 0x1fe
00015a10: mul        a5, a7, a1
00015a14: not        a1, a6
00015a18: add        a6, a2, t0
00015a1c: add        a1, a4, a1
00015a20: j          -0x428

th_sdecb_r:
00015a24: bltz       a2, 0x90
00015a28: slli       a4, a1, 1
00015a2c: srli       a5, a3, 7
00015a30: mulhu      a6, a3, a3
00015a34: addi       a7, zero, 0x342
00015a38: lui        t0, 0x22
00015a3c: mul        t1, a5, a5
00015a40: mulhu      t2, a5, a5
00015a44: mul        t2, a5, t2
00015a48: mulhu      a5, t1, a5
00015a4c: lui        t1, 0xfe800
00015a50: sll        t1, t1, a4
00015a54: mul        a2, t1, a2
00015a58: lui        t1, 0x14b9
00015a5c: srl        a4, a6, a4
00015a60: addi       t0, t0, -0x674
00015a64: mulhu      a7, a4, a7
00015a68: sub        a7, t0, a7
00015a6c: lui        t0, 0xccccd
00015a70: addi       t1, t1, 0x503
00015a74: addi       t0, t0, -0x311
00015a78: add        a2, t2, a2
00015a7c: mulhu      a7, a7, a4
00015a80: sub        a7, t1, a7
00015a84: mulhu      a7, a7, a4
00015a88: sub        a7, t0, a7
00015a8c: mulhu      a4, a7, a4
00015a90: mulhu      a4, a4, a6
00015a94: mulhu      a3, a4, a3
00015a98: slli       a3, a3, 4
00015a9c: add        a2, a2, a5
00015aa0: sub        a2, a2, a3
00015aa4: xor        a1, a2, a1
00015aa8: srli       a1, a1, 0x1f
00015aac: add        a0, a1, a0
00015ab0: ret        
00015ab4: addi       sp, sp, -0x10
00015ab8: sw         ra, 0xc(sp)
00015abc: sw         s0, 8(sp)
00015ac0: addi       s0, sp, 0x10
00015ac4: xor        a0, a3, a0
00015ac8: add        a3, a3, a1
00015acc: auipc      ra, 0
00015ad0: jalr       ra, ra, 0x1b0
00015ad4: lw         ra, 0xc(sp)
00015ad8: lw         s0, 8(sp)
00015adc: addi       sp, sp, 0x10
00015ae0: ret        

memcpy:
00015ae4: beqz       a2, 0x40
00015ae8: addi       sp, sp, -0x10
00015aec: sw         ra, 0xc(sp)
00015af0: sw         s0, 8(sp)
00015af4: addi       s0, sp, 0x10
00015af8: add        a2, a0, a2
00015afc: mv         a3, a0
00015b00: lbu        a4, 0(a1)
00015b04: addi       a1, a1, 1
00015b08: addi       a5, a3, 1
00015b0c: sb         a4, 0(a3)
00015b10: mv         a3, a5
00015b14: bne        a5, a2, -0x14
00015b18: lw         ra, 0xc(sp)
00015b1c: lw         s0, 8(sp)
00015b20: addi       sp, sp, 0x10
00015b24: ret        

memmove:
00015b28: addi       sp, sp, -0x10
00015b2c: sw         ra, 0xc(sp)
00015b30: sw         s0, 8(sp)
00015b34: addi       s0, sp, 0x10
00015b38: bgeu       a0, a1, 0x2c
00015b3c: beqz       a2, 0x50
00015b40: add        a2, a0, a2
00015b44: mv         a3, a0
00015b48: lbu        a4, 0(a1)
00015b4c: addi       a1, a1, 1
00015b50: addi       a5, a3, 1
00015b54: sb         a4, 0(a3)
00015b58: mv         a3, a5
00015b5c: bne        a5, a2, -0x14
00015b60: j          0x2c
00015b64: beqz       a2, 0x28
00015b68: addi       a3, a2, -1
00015b6c: add        a2, a0, a3
00015b70: add        a1, a1, a3
00015b74: addi       a3, a0, -1
00015b78: lbu        a4, 0(a1)
00015b7c: sb         a4, 0(a2)
00015b80: addi       a2, a2, -1
00015b84: addi       a1, a1, -1
00015b88: bne        a2, a3, -0x10
00015b8c: lw         ra, 0xc(sp)
00015b90: lw         s0, 8(sp)
00015b94: addi       sp, sp, 0x10
00015b98: ret        

memset:
00015b9c: beqz       a2, 0x38
00015ba0: addi       sp, sp, -0x10
00015ba4: sw         ra, 0xc(sp)
00015ba8: sw         s0, 8(sp)
00015bac: addi       s0, sp, 0x10
00015bb0: add        a2, a0, a2
00015bb4: mv         a3, a0
00015bb8: addi       a4, a3, 1
00015bbc: sb         a1, 0(a3)
00015bc0: mv         a3, a4
00015bc4: bne        a4, a2, -0xc
00015bc8: lw         ra, 0xc(sp)
00015bcc: lw         s0, 8(sp)
00015bd0: addi       sp, sp, 0x10
00015bd4: ret        

eik_batch:
00015bd8: beqz       a3, 0xa0
00015bdc: addi       sp, sp, -0x20
00015be0: sw         ra, 0x1c(sp)
00015be4: sw         s0, 0x18(sp)
00015be8: sw         s1, 0x14(sp)
00015bec: sw         s2, 0x10(sp)
00015bf0: sw         s3, 0xc(sp)
00015bf4: sw         s4, 8(sp)
00015bf8: sw         s5, 4(sp)
00015bfc: addi       s0, sp, 0x20
00015c00: mv         s1, a2
00015c04: mv         s2, a1
00015c08: mv         s3, a0
00015c0c: slli       a3, a3, 2
00015c10: add        s4, a1, a3
00015c14: addi       s5, zero, 1
00015c18: j          0x1c
00015c1c: auipc      ra, 0xfffff
00015c20: jalr       ra, ra, 0x180
00015c24: sw         a0, 0(s1)
00015c28: addi       s2, s2, 4
00015c2c: addi       s1, s1, 4
00015c30: beq        s2, s4, 0x28
00015c34: lw         a0, 0(s2)
00015c38: beq        s3, s5, -0x1c
00015c3c: bnez       s3, 0x10
00015c40: auipc      ra, 0xfffff
00015c44: jalr       ra, ra, -0x6c8
00015c48: j          -0x24
00015c4c: auipc      ra, 0xfffff
00015c50: jalr       ra, ra, 0x5ec
00015c54: j          -0x30
00015c58: lw         ra, 0x1c(sp)
00015c5c: lw         s0, 0x18(sp)
00015c60: lw         s1, 0x14(sp)
00015c64: lw         s2, 0x10(sp)
00015c68: lw         s3, 0xc(sp)
00015c6c: lw         s4, 8(sp)
00015c70: lw         s5, 4(sp)
00015c74: addi       sp, sp, 0x20
00015c78: ret        

__udivdi3:
00015c7c: addi       sp, sp, -0x10
00015c80: sw         ra, 0xc(sp)
00015c84: sw         s0, 8(sp)
00015c88: addi       s0, sp, 0x10
00015c8c: mv         a4, zero
00015c90: lw         ra, 0xc(sp)
00015c94: lw         s0, 8(sp)
00015c98: addi       sp, sp, 0x10
00015c9c: auipc      t1, 0
00015ca0: jalr       zero, t1, 8

__udivmoddi4:
00015ca4: addi       sp, sp, -0x10
00015ca8: sw         ra, 0xc(sp)
00015cac: sw         s0, 8(sp)
00015cb0: addi       s0, sp, 0x10
00015cb4: beq        a1, a3, 0x26c
00015cb8: sltu       a5, a1, a3
00015cbc: bnez       a5, 0x26c
00015cc0: beqz       a3, 0x294
00015cc4: srli       a5, a3, 1
00015cc8: lui        a6, 0x55555
00015ccc: or         a5, a3, a5
00015cd0: addi       a6, a6, 0x555
00015cd4: srli       a7, a5, 2
00015cd8: or         a5, a5, a7
00015cdc: srli       a7, a5, 4
00015ce0: or         a5, a5, a7
00015ce4: srli       a7, a5, 8
00015ce8: or         a5, a5, a7
00015cec: srli       a7, a5, 0x10
00015cf0: or         a5, a5, a7
00015cf4: not        a5, a5
00015cf8: srli       a7, a5, 1
00015cfc: and        a6, a7, a6
00015d00: lui        a7, 0x33333
00015d04: addi       a7, a7, 0x333
00015d08: sub        a5, a5, a6
00015d0c: and        a6, a5, a7
00015d10: srli       a5, a5, 2
00015d14: and        a5, a5, a7
00015d18: lui        a7, 0xf0f1
00015d1c: add        a5, a6, a5
00015d20: srli       a6, a5, 4
00015d24: add        a5, a5, a6
00015d28: lui        a6, 0x1010
00015d2c: addi       a7, a7, -0xf1
00015d30: and        a5, a5, a7
00015d34: addi       a6, a6, 0x101
00015d38: mul        a5, a5, a6
00015d3c: srli       a7, a5, 0x18
00015d40: beqz       a7, 0x358
00015d44: neg        a6, a7
00015d48: sll        a5, a3, a7
00015d4c: srl        t0, a2, a6
00015d50: or         a5, t0, a5
00015d54: sll        a7, a1, a7
00015d58: srl        t0, a0, a6
00015d5c: beqz       a5, 0x4d8
00015d60: srli       t1, a5, 1
00015d64: lui        t2, 0x55555
00015d68: or         t1, a5, t1
00015d6c: addi       t2, t2, 0x555
00015d70: srli       t3, t1, 2
00015d74: or         t1, t1, t3
00015d78: srli       t3, t1, 4
00015d7c: or         t1, t1, t3
00015d80: srli       t3, t1, 8
00015d84: or         t1, t1, t3
00015d88: srli       t3, t1, 0x10
00015d8c: or         t1, t1, t3
00015d90: not        t1, t1
00015d94: srli       t3, t1, 1
00015d98: and        t2, t3, t2
00015d9c: lui        t3, 0x33333
00015da0: addi       t3, t3, 0x333
00015da4: sub        t1, t1, t2
00015da8: and        t2, t1, t3
00015dac: srli       t1, t1, 2
00015db0: and        t1, t1, t3
00015db4: lui        t3, 0xf0f1
00015db8: add        t1, t2, t1
00015dbc: srli       t2, t1, 4
00015dc0: add        t1, t1, t2
00015dc4: lui        t2, 0x1010
00015dc8: addi       t3, t3, -0xf1
00015dcc: and        t1, t1, t3
00015dd0: addi       t2, t2, 0x101
00015dd4: mul        t1, t1, t2
00015dd8: srli       t3, t1, 0x18
00015ddc: or         t1, t0, a7
00015de0: andi       a7, t3, 0x1f
00015de4: srl        t2, a1, a6
00015de8: beqz       a7, 0x1c
00015dec: sll        a5, a5, a7
00015df0: sll        a6, t2, a7
00015df4: neg        t0, t3
00015df8: srl        t0, t1, t0
00015dfc: or         t2, a6, t0
00015e00: sll        t1, t1, a7
00015e04: srli       a6, a5, 0x10
00015e08: divu       a7, t2, a6
00015e0c: lui        t0, 0x10
00015e10: addi       t4, t0, -1
00015e14: and        t0, a5, t4
00015e18: srli       t3, t1, 0x10
00015e1c: and        t1, t1, t4
00015e20: mul        t4, a7, a6
00015e24: sub        t4, t2, t4
00015e28: j          0x14
00015e2c: add        t4, t4, a6
00015e30: srli       t5, t4, 0x10
00015e34: addi       a7, a7, -1
00015e38: bnez       t5, 0x1c
00015e3c: srli       t5, a7, 0x10
00015e40: bnez       t5, -0x14
00015e44: mul        t5, a7, t0
00015e48: slli       t6, t4, 0x10
00015e4c: or         t6, t6, t3
00015e50: bltu       t6, t5, -0x24
00015e54: slli       t2, t2, 0x10
00015e58: or         t2, t2, t3
00015e5c: mul        a5, a7, a5
00015e60: sub        t2, t2, a5
00015e64: divu       a5, t2, a6
00015e68: mul        t3, a5, a6
00015e6c: sub        t2, t2, t3
00015e70: j          0x14
00015e74: add        t2, t2, a6
00015e78: srli       t3, t2, 0x10
00015e7c: addi       a5, a5, -1
00015e80: bnez       t3, 0x1c
00015e84: srli       t3, a5, 0x10
00015e88: bnez       t3, -0x14
00015e8c: mul        t3, a5, t0
00015e90: slli       t4, t2, 0x10
00015e94: or         t4, t4, t1
00015e98: bltu       t4, t3, -0x24
00015e9c: slli       a6, a7, 0x10
00015ea0: add        a6, a5, a6
00015ea4: mulhu      a5, a2, a6
00015ea8: mulhu      t0, a3, a6
00015eac: mul        a7, a3, a6
00015eb0: add        a5, a7, a5
00015eb4: sltu       a7, a5, a7
00015eb8: neg        t1, a7
00015ebc: mul        a7, a2, a6
00015ec0: bne        t0, t1, 0x10
00015ec4: bltu       a1, a5, 0xc
00015ec8: bne        a5, a1, 0x20
00015ecc: bgeu       a0, a7, 0x1c
00015ed0: addi       a6, a6, -1
00015ed4: sub        a2, a7, a2
00015ed8: sltu       a7, a7, a2
00015edc: add        a3, a7, a3
00015ee0: sub        a5, a5, a3
00015ee4: mv         a7, a2
00015ee8: beqz       a4, 0x1c
00015eec: sub        a2, a0, a7
00015ef0: sub        a1, a1, a5
00015ef4: sltu       a0, a0, a2
00015ef8: sub        a1, a1, a0
00015efc: sw         a2, 0(a4)
00015f00: sw         a1, 4(a4)
00015f04: mv         a5, zero
00015f08: mv         a0, a6
00015f0c: mv         a1, a5
00015f10: lw         ra, 0xc(sp)
00015f14: lw         s0, 8(sp)
00015f18: addi       sp, sp, 0x10
00015f1c: ret        
00015f20: sltu       a5, a0, a2
00015f24: beqz       a5, -0x264
00015f28: mv         a6, zero
00015f2c: mv         a5, zero
00015f30: beqz       a4, -0x28
00015f34: sw         a0, 0(a4)
00015f38: sw         a1, 4(a4)
00015f3c: mv         a0, a6
00015f40: mv         a1, a5
00015f44: lw         ra, 0xc(sp)
00015f48: lw         s0, 8(sp)
00015f4c: addi       sp, sp, 0x10
00015f50: ret        
00015f54: bgeu       a1, a2, 0x164
00015f58: srli       a3, a2, 1
00015f5c: lui        a5, 0x55555
00015f60: or         a3, a2, a3
00015f64: addi       a5, a5, 0x555
00015f68: srli       a6, a3, 2
00015f6c: or         a3, a3, a6
00015f70: srli       a6, a3, 4
00015f74: or         a3, a3, a6
00015f78: srli       a6, a3, 8
00015f7c: or         a3, a3, a6
00015f80: srli       a6, a3, 0x10
00015f84: or         a3, a3, a6
00015f88: not        a3, a3
00015f8c: srli       a6, a3, 1
00015f90: and        a5, a6, a5
00015f94: lui        a6, 0x33333
00015f98: addi       a6, a6, 0x333
00015f9c: sub        a3, a3, a5
00015fa0: and        a5, a3, a6
00015fa4: srli       a3, a3, 2
00015fa8: and        a3, a3, a6
00015fac: lui        a6, 0xf0f1
00015fb0: add        a3, a5, a3
00015fb4: srli       a5, a3, 4
00015fb8: add        a3, a3, a5
00015fbc: lui        a5, 0x1010
00015fc0: addi       a6, a6, -0xf1
00015fc4: and        a3, a3, a6
00015fc8: addi       a5, a5, 0x101
00015fcc: mul        a3, a3, a5
00015fd0: srli       a6, a3, 0x18
00015fd4: beqz       a6, 0x1c
00015fd8: sll        a2, a2, a6
00015fdc: sll        a1, a1, a6
00015fe0: neg        a3, a6
00015fe4: srl        a3, a0, a3
00015fe8: or         a1, a3, a1
00015fec: sll        a0, a0, a6
00015ff0: srli       a5, a2, 0x10
00015ff4: divu       a3, a1, a5
00015ff8: lui        a7, 0x10
00015ffc: addi       a7, a7, -1
00016000: and        t0, a2, a7
00016004: srli       t1, a0, 0x10
00016008: and        a7, a0, a7
0001600c: mul        a0, a3, a5
00016010: sub        a0, a1, a0
00016014: j          0x14
00016018: add        a0, a0, a5
0001601c: srli       t2, a0, 0x10
00016020: addi       a3, a3, -1
00016024: bnez       t2, 0x1c
00016028: srli       t2, a3, 0x10
0001602c: bnez       t2, -0x14
00016030: mul        t2, a3, t0
00016034: slli       t3, a0, 0x10
00016038: or         t3, t3, t1
0001603c: bltu       t3, t2, -0x24
00016040: slli       a1, a1, 0x10
00016044: or         a0, a1, t1
00016048: mul        a1, a3, a2
0001604c: sub        a1, a0, a1
00016050: divu       a0, a1, a5
00016054: mul        t1, a0, a5
00016058: sub        t1, a1, t1
0001605c: j          0x14
00016060: add        t1, t1, a5
00016064: srli       t2, t1, 0x10
00016068: addi       a0, a0, -1
0001606c: bnez       t2, 0x1c
00016070: srli       t2, a0, 0x10
00016074: bnez       t2, -0x14
00016078: mul        t2, a0, t0
0001607c: slli       t3, t1, 0x10
00016080: or         t3, t3, a7
00016084: bltu       t3, t2, -0x24
00016088: mv         a5, zero
0001608c: slli       a1, a1, 0x10
00016090: or         a1, a1, a7
00016094: j          0x168
00016098: addi       a6, zero, 1
0001609c: mv         a5, zero
000160a0: beqz       a4, -0x198
000160a4: sub        a1, a1, a3
000160a8: sltu       a3, a0, a2
000160ac: sub        a0, a0, a2
000160b0: sub        a1, a1, a3
000160b4: j          -0x180
000160b8: divu       a5, a1, a2
000160bc: srli       a3, a2, 1
000160c0: lui        a6, 0x55555
000160c4: or         a3, a2, a3
000160c8: addi       a6, a6, 0x555
000160cc: srli       a7, a3, 2
000160d0: or         a3, a3, a7
000160d4: srli       a7, a3, 4
000160d8: or         a3, a3, a7
000160dc: srli       a7, a3, 8
000160e0: or         a3, a3, a7
000160e4: srli       a7, a3, 0x10
000160e8: or         a3, a3, a7
000160ec: not        a3, a3
000160f0: srli       a7, a3, 1
000160f4: and        a6, a7, a6
000160f8: lui        a7, 0x33333
000160fc: addi       a7, a7, 0x333
00016100: sub        a3, a3, a6
00016104: and        a6, a3, a7
00016108: srli       a3, a3, 2
0001610c: and        a3, a3, a7
00016110: lui        a7, 0xf0f1
00016114: add        a3, a6, a3
00016118: srli       a6, a3, 4
0001611c: add        a3, a3, a6
00016120: lui        a6, 0x1010
00016124: addi       a7, a7, -0xf1
00016128: and        a3, a3, a7
0001612c: mul        a7, a5, a2
00016130: addi       a6, a6, 0x101
00016134: mul        a3, a3, a6
00016138: srli       a6, a3, 0x18
0001613c: sub        t1, a1, a7
00016140: beqz       a6, 0x1c
00016144: sll        a2, a2, a6
00016148: sll        a1, t1, a6
0001614c: neg        a3, a6
00016150: srl        a3, a0, a3
00016154: or         t1, a1, a3
00016158: sll        a0, a0, a6
0001615c: srli       a1, a2, 0x10
00016160: divu       a3, t1, a1
00016164: lui        a7, 0x10
00016168: addi       a7, a7, -1
0001616c: and        t0, a2, a7
00016170: srli       t2, a0, 0x10
00016174: and        a7, a0, a7
00016178: mul        a0, a3, a1
0001617c: sub        a0, t1, a0
00016180: j          0x14
00016184: add        a0, a0, a1
00016188: srli       t3, a0, 0x10
0001618c: addi       a3, a3, -1
00016190: bnez       t3, 0x1c
00016194: srli       t3, a3, 0x10
00016198: bnez       t3, -0x14
0001619c: mul        t3, a3, t0
000161a0: slli       t4, a0, 0x10
000161a4: or         t4, t4, t2
000161a8: bltu       t4, t3, -0x24
000161ac: slli       t1, t1, 0x10
000161b0: or         a0, t1, t2
000161b4: mul        t1, a3, a2
000161b8: sub        t1, a0, t1
000161bc: divu       a0, t1, a1
000161c0: mul        t2, a0, a1
000161c4: sub        t2, t1, t2
000161c8: j          0x14
000161cc: add        t2, t2, a1
000161d0: srli       t3, t2, 0x10
000161d4: addi       a0, a0, -1
000161d8: bnez       t3, 0x1c
000161dc: srli       t3, a0, 0x10
000161e0: bnez       t3, -0x14
000161e4: mul        t3, a0, t0
000161e8: slli       t4, t2, 0x10
000161ec: or         t4, t4, a7
000161f0: bltu       t4, t3, -0x24
000161f4: slli       t1, t1, 0x10
000161f8: or         a1, t1, a7
000161fc: mul        a2, a0, a2
00016200: sub        a1, a1, a2
00016204: srl        a1, a1, a6
00016208: slli       a3, a3, 0x10
0001620c: add        a6, a0, a3
00016210: beqz       a4, -0x308
00016214: sw         a1, 0(a4)
00016218: sw         zero, 4(a4)
0001621c: mv         a0, a6
00016220: mv         a1, a5
00016224: lw         ra, 0xc(sp)
00016228: lw         s0, 8(sp)
0001622c: addi       sp, sp, 0x10
00016230: ret        
00016234: addi       t3, zero, 0x20
00016238: or         t1, t0, a7
0001623c: andi       a7, t3, 0x1f
00016240: srl        t2, a1, a6
00016244: bnez       a7, -0x458
00016248: j          -0x444
