	.loc	2 1264 29 is_stmt 1             # eik-work/trials/rv-tanh-quadratic/entry.c:1264:29 @[ eik-work/trials/rv-tanh-quadratic/entry.c:4827:16 ]
	slli	a7, a3, 4
	lui	a2, %hi(tld_r)
	addi	a2, a2, %lo(tld_r)
	add	a7, a2, a7
.Ltmp414:
	.loc	2 0 0 is_stmt 0                 # eik-work/trials/rv-tanh-quadratic/entry.c:0 @[ eik-work/trials/rv-tanh-quadratic/entry.c:4827:16 ]
	lw	a6, 4(a7)
.Ltmp415:
	.loc	2 1266 13                       # eik-work/trials/rv-tanh-quadratic/entry.c:1266:13 @[ eik-work/trials/rv-tanh-quadratic/entry.c:4827:16 ]
	srli	a5, a1, 26
	li	t0, 31
.Ltmp416:
	.loc	2 1265 13 is_stmt 1             # eik-work/trials/rv-tanh-quadratic/entry.c:1265:13 @[ eik-work/trials/rv-tanh-quadratic/entry.c:4827:16 ]
	slli	a2, a0, 13
.Ltmp417:
	.loc	2 1266 13                       # eik-work/trials/rv-tanh-quadratic/entry.c:1266:13 @[ eik-work/trials/rv-tanh-quadratic/entry.c:4827:16 ]
	bgeu	a5, t0, .LBB1_15
.Ltmp418:
# %bb.10:
	.loc	2 1268 37 is_stmt 0             # eik-work/trials/rv-tanh-quadratic/entry.c:1268:37 @[ eik-work/trials/rv-tanh-quadratic/entry.c:4827:16 ]
	slli	a3, a3, 2
.Ltmp419:
	lui	a5, %hi(tq_r)
	addi	a5, a5, %lo(tq_r)
	add	a3, a5, a3
	lw	a5, 0(a3)
.Ltmp420:
	.loc	2 568 36                        # eik-work/trials/rv-tanh-quadratic/entry.c:568:36 @[ eik-work/trials/rv-tanh-quadratic/entry.c:1268:29 @[ eik-work/trials/rv-tanh-quadratic/entry.c:4827:16 ] ]
	srai	t0, a2, 31
.Ltmp421:
	.loc	2 1269 25                       # eik-work/trials/rv-tanh-quadratic/entry.c:1269:25 @[ eik-work/trials/rv-tanh-quadratic/entry.c:4827:16 ]
	lw	a3, 0(a7)
.Ltmp422:
	.loc	2 1270 18                       # eik-work/trials/rv-tanh-quadratic/entry.c:1270:18 @[ eik-work/trials/rv-tanh-quadratic/entry.c:4827:16 ]
	andi	t1, t0, 216
.Ltmp423:
	.loc	2 568 39 is_stmt 1              # eik-work/trials/rv-tanh-quadratic/entry.c:568:39 @[ eik-work/trials/rv-tanh-quadratic/entry.c:1268:29 @[ eik-work/trials/rv-tanh-quadratic/entry.c:4827:16 ] ]
	mulh	a5, a5, a2
.Ltmp424:
	.loc	2 1268 27                       # eik-work/trials/rv-tanh-quadratic/entry.c:1268:27 @[ eik-work/trials/rv-tanh-quadratic/entry.c:4827:16 ]
	add	a5, a6, a5
.Ltmp425:
	.loc	2 568 39                        # eik-work/trials/rv-tanh-quadratic/entry.c:568:39 @[ eik-work/trials/rv-tanh-quadratic/entry.c:1269:41 @[ eik-work/trials/rv-tanh-quadratic/entry.c:4827:16 ] ]
	mulh	a5, a5, a2
.Ltmp426:
	.loc	2 1269 28                       # eik-work/trials/rv-tanh-quadratic/entry.c:1269:28 @[ eik-work/trials/rv-tanh-quadratic/entry.c:4827:16 ]
	add	a5, a3, a5
.Ltmp427:
	.loc	2 1270 18 is_stmt 0             # eik-work/trials/rv-tanh-quadratic/entry.c:1270:18 @[ eik-work/trials/rv-tanh-quadratic/entry.c:4827:16 ]
	add	t1, t1, a5
	.loc	2 1270 24                       # eik-work/trials/rv-tanh-quadratic/entry.c:1270:24 @[ eik-work/trials/rv-tanh-quadratic/entry.c:4827:16 ]
	addi	t1, t1, 252
	.loc	2 1270 45                       # eik-work/trials/rv-tanh-quadratic/entry.c:1270:45 @[ eik-work/trials/rv-tanh-quadratic/entry.c:4827:16 ]
	andi	t1, t1, 254
	li	t2, 210
	bgeu	t1, t2, .LBB1_16
.Ltmp428:
# %bb.11:
	.loc	2 0 45                          # eik-work/trials/rv-tanh-quadratic/entry.c:0:45
	srli	a5, a5, 8
	sub	a0, a0, a5
.Ltmp429:
	.loc	2 4827 9 is_stmt 1              # eik-work/trials/rv-tanh-quadratic/entry.c:4827:9
	ret
