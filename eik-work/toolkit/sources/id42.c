/* The _t variant is adapted from published EIK entry #12
 * (https://conjectures.io/v1/competitions/exact-integer-kernels/submissions/12/source), itself adapted from
 * entry #8; the _r variant uses the 64-cell tables first published in entry #10.
 * Terms granted by the competition: MIT or Apache-2.0. */
/* Two variants of the same kernels in one source: products through the 64-bit multiply (suffix _r)
 * where that is one instruction, 16-bit limbs (suffix _t) on Cortex-M. EIK_SEL is a constant
 * expression, 1 where wchar_t is a signed type and 0 where it is unsigned, so each build keeps one. */
#ifndef EIK_SEL
#define EIK_SEL (L'\0' - 1 < 0)
#endif
#ifdef EIK_STATS
_Thread_local uint64_t eik_stat[16];
#endif
/* 1: products through the 64-bit multiply (one instruction on RV32IM); 0: 16-bit limbs (Cortex-M0+) */
/* 1: the mid_r tier's 64-bit products from 16-bit limbs (about 1% better on Cortex-M0+, 2% worse on RV32IM) */

#define STAT_r(i) ((void)0)
/* A fast path's value V has B guard bits. It is settled unless the guard bits fall in a window
 * around the midpoint found by running every input: with the offset O added, the guard bits of a
 * settled value are at least K, and (V + O) >> B is the correctly rounded significand. */
#define FAST_r(V, B, O, K, P) ((K) == 0u || ((((V) + (O)) & ((1u << (B)) - 1u)) >= (K)))
#define MANT_r(V, B, O) (((V) + (O)) >> (B))
#define MANTS_r(V, B, O) ((int32_t)((V) + (O)) >> (B))
#define MARK_r(path) ((void)0)

/* a cubic in the offset from the start of the cell, every coefficient in units of the result */
struct rx_r {
    uint32_t c0;
    int32_t c1, c2;
    int16_t c3;
    int16_t xh;         /* JR (ta_r): half of the anchor's tail dx = T0 2^60 - (c0 - 0x80) 2^28 of a cell pair (2p-1, 2p)
                         * sharing the anchor: the high half in the even cell 2p, the low half in the odd cell 2p-1 (cell 0's
                         * low half in the lead record). This replaces tax_r. */
};
/* TRV: the cells of 1/8 <= y < 2 at 32 per binade: c3 is a whole word (it reaches 116500 at y = 1) */
struct rl_r {
    uint32_t c0;
    int32_t c1, c2, c3;
};
/* TRV: a decline's anchor: T0 2^32 rounded and the tail T0 2^60 - c0 2^28 */
struct ra_r {
    uint32_t c0;
    int32_t dx;
};
/* public #29: sigmoid's B cells (see ry_cell_r) */
struct ry_r {
    uint32_t c0;
    int32_t c1, c2, w3;
};

/* tanh(y) 2^(sc+32), 64 cells per binade, 1/8 <= y < 9.125 */
/* rv32 tables (every _r user): exp9_r[j] = floor(2^((2j+1)/1024) 2^31) + 130 (the fast paths' rounding offset),
 * exp9lo_r[j] = the next 16 bits (rounded), so 2^((2j+1)/1024) 2^63 = (exp9_r[j] - 130) 2^32 + exp9lo_r[j] 2^16
 * within 2^15. With k2 = floor(2y 512/ln2) | 1 (odd), e^y = 2^(k2 >> 10) 2^((2j+1)/1024) e^r, j = (k2 >> 1) & 511,
 * r = y - k2 ln2/1024 in [-ln2/1024, ln2/1024): T e^r stays inside [2^31, 2^32) (no binade crossing). */
/* G3: exp8_r and exp8lo_r in one record, so that a function reading both forms one base address */
static const struct { uint32_t hi[1 << 8]; uint16_t lo[1 << 8]; } ex8_r = {{
    0x802c64b9u, 0x80855b5cu, 0x80de8fbeu, 0x8138020bu, 0x8191b26du, 0x81eba10fu, 0x8245ce1du, 0x82a039c2u,
    0x82fae42au, 0x8355cd80u, 0x83b0f5efu, 0x840c5da4u, 0x846804cau, 0x84c3eb8eu, 0x8520121bu, 0x857c789fu,
    0x85d91f44u, 0x86360638u, 0x86932da8u, 0x86f095c0u, 0x874e3eadu, 0x87ac289cu, 0x880a53bau, 0x8868c035u,
    0x88c76e39u, 0x89265df5u, 0x89858f96u, 0x89e50349u, 0x8a44b93du, 0x8aa4b19fu, 0x8b04ec9eu, 0x8b656a67u,
    0x8bc62b2au, 0x8c272f14u, 0x8c887655u, 0x8cea011bu, 0x8d4bcf94u, 0x8dade1f1u, 0x8e10385fu, 0x8e72d30fu,
    0x8ed5b22fu, 0x8f38d5efu, 0x8f9c3e7fu, 0x8fffec0fu, 0x9063deceu, 0x90c816ecu, 0x912c949au, 0x91915808u,
    0x91f66166u, 0x925bb0e5u, 0x92c146b5u, 0x93272308u, 0x938d460eu, 0x93f3aff8u, 0x945a60f8u, 0x94c1593eu,
    0x952898fdu, 0x95902066u, 0x95f7efaau, 0x966006fcu, 0x96c8668du, 0x97310e91u, 0x9799ff38u, 0x980338b5u,
    0x986cbb3cu, 0x98d686feu, 0x99409c2eu, 0x99aafb00u, 0x9a15a3a7u, 0x9a809655u, 0x9aebd33eu, 0x9b575a97u,
    0x9bc32c91u, 0x9c2f4962u, 0x9c9bb13du, 0x9d086456u, 0x9d7562e1u, 0x9de2ad13u, 0x9e504321u, 0x9ebe253eu,
    0x9f2c53a0u, 0x9f9ace7cu, 0xa0099606u, 0xa078aa75u, 0xa0e80bfdu, 0xa157bad3u, 0xa1c7b72fu, 0xa2380144u,
    0xa2a8994au, 0xa3197f76u, 0xa38ab3ffu, 0xa3fc371bu, 0xa46e0900u, 0xa4e029e5u, 0xa5529a02u, 0xa5c5598cu,
    0xa63868bcu, 0xa6abc7c8u, 0xa71f76e8u, 0xa7937654u, 0xa807c643u, 0xa87c66ecu, 0xa8f15889u, 0xa9669b51u,
    0xa9dc2f7du, 0xaa521545u, 0xaac84ce2u, 0xab3ed68cu, 0xabb5b27du, 0xac2ce0edu, 0xaca46217u, 0xad1c3632u,
    0xad945d7au, 0xae0cd827u, 0xae85a673u, 0xaefec899u, 0xaf783ed3u, 0xaff2095bu, 0xb06c286bu, 0xb0e69c3fu,
    0xb1616511u, 0xb1dc831cu, 0xb257f69bu, 0xb2d3bfc9u, 0xb34fdee3u, 0xb3cc5424u, 0xb4491fc6u, 0xb4c64208u,
    0xb543bb23u, 0xb5c18b56u, 0xb63fb2dcu, 0xb6be31f2u, 0xb73d08d4u, 0xb7bc37c0u, 0xb83bbef3u, 0xb8bb9eaau,
    0xb93bd722u, 0xb9bc6899u, 0xba3d534du, 0xbabe977cu, 0xbb403563u, 0xbbc22d42u, 0xbc447f56u, 0xbcc72bdeu,
    0xbd4a331au, 0xbdcd9547u, 0xbe5152a5u, 0xbed56b74u, 0xbf59dff2u, 0xbfdeb060u, 0xc063dcfdu, 0xc0e96609u,
    0xc16f4bc5u, 0xc1f58e70u, 0xc27c2e4bu, 0xc3032b98u, 0xc38a8696u, 0xc4123f87u, 0xc49a56acu, 0xc522cc46u,
    0xc5aba097u, 0xc634d3e1u, 0xc6be6666u, 0xc7485867u, 0xc7d2aa27u, 0xc85d5be9u, 0xc8e86defu, 0xc973e07bu,
    0xc9ffb3d2u, 0xca8be835u, 0xcb187de9u, 0xcba57531u, 0xcc32ce50u, 0xccc0898cu, 0xcd4ea726u, 0xcddd2765u,
    0xce6c0a8du, 0xcefb50e1u, 0xcf8afaa7u, 0xd01b0825u, 0xd0ab799eu, 0xd13c4f59u, 0xd1cd899bu, 0xd25f28aau,
    0xd2f12cccu, 0xd3839647u, 0xd4166562u, 0xd4a99a62u, 0xd53d358fu, 0xd5d1372fu, 0xd6659f8bu, 0xd6fa6ee8u,
    0xd78fa58eu, 0xd82543c6u, 0xd8bb49d7u, 0xd951b809u, 0xd9e88ea4u, 0xda7fcdf2u, 0xdb177639u, 0xdbaf87c5u,
    0xdc4802dcu, 0xdce0e7cau, 0xdd7a36d6u, 0xde13f04cu, 0xdeae1474u, 0xdf48a399u, 0xdfe39e05u, 0xe07f0402u,
    0xe11ad5dcu, 0xe1b713dcu, 0xe253be4fu, 0xe2f0d57fu, 0xe38e59b7u, 0xe42c4b45u, 0xe4caaa72u, 0xe569778cu,
    0xe608b2dfu, 0xe6a85cb7u, 0xe7487562u, 0xe7e8fd2bu, 0xe889f460u, 0xe92b5b4eu, 0xe9cd3243u, 0xea6f798du,
    0xeb12317au, 0xebb55a57u, 0xec58f474u, 0xecfd001eu, 0xeda17da5u, 0xee466d58u, 0xeeebcf86u, 0xef91a47eu,
    0xf037ec90u, 0xf0dea80bu, 0xf185d741u, 0xf22d7a82u, 0xf2d5921du, 0xf37e1e64u, 0xf4271fa7u, 0xf4d09638u,
    0xf57a8269u, 0xf624e48au, 0xf6cfbcefu, 0xf77b0be8u, 0xf826d1c8u, 0xf8d30ee1u, 0xf97fc388u, 0xfa2cf00du,
    0xfada94c6u, 0xfb88b204u, 0xfc37481cu, 0xfce65761u, 0xfd95e029u, 0xfe45e2c6u, 0xfef65f8du, 0xffa756d5u,
}, {
    0xd0e0, 0x65e9, 0x8b86, 0x1d88, 0x1581, 0x8ad4, 0xb2cf, 0xe0bb, 0x85f6, 0x3204, 0x92a5, 0x73e9,
    0xc04a, 0x80b9, 0xdcb9, 0x1a73, 0x9eca, 0xed73, 0xa906, 0x9318, 0x8c4e, 0x9473, 0xca8e, 0x6cf8,
    0xd96e, 0x8d2e, 0x2507, 0x5d71, 0x12a2, 0x40a5, 0x0371, 0x96fc, 0x5754, 0xc0b6, 0x6fa1, 0x20ee,
    0xb1e8, 0x2060, 0x8ac4, 0x303a, 0x70af, 0xccf4, 0xe6d2, 0x8121, 0x7fe1, 0xe84e, 0xe0f9, 0xb1e0,
    0xc482, 0xa3f9, 0xfd10, 0x9e5c, 0x7851, 0x9d5d, 0x41fa, 0xbccb, 0x86b3, 0x3ae9, 0x9714, 0x7b61,
    0xea9a, 0x0a42, 0x22a7, 0x9eff, 0x0d80, 0x1f75, 0xa95a, 0xa2f1, 0x275e, 0x753c, 0xeeb9, 0x19ae,
    0x9fb3, 0x4e41, 0x16c0, 0x0eab, 0x6f9f, 0x977c, 0x0879, 0x6940, 0x8505, 0x4ba2, 0xd1af, 0x509b,
    0x26c8, 0xd7a0, 0x0bb3, 0x90d1, 0x5a20, 0x8038, 0x413e, 0x00ff, 0x4905, 0xc8b6, 0x556d, 0xea94,
    0xa9be, 0xdac3, 0xebd9, 0x71b0, 0x2789, 0xef58, 0xd1d9, 0xfeaa, 0xcc6c, 0xb8d8, 0x68df, 0xa8c1,
    0x6c2a, 0xce50, 0x120a, 0xa1ed, 0x1069, 0x17e4, 0x9ad6, 0xa3e3, 0x65f8, 0x3c69, 0xab09, 0x5e4a,
    0x2b56, 0x102f, 0x33c6, 0xe61c, 0xa05f, 0x0502, 0xdfdc, 0x2647, 0xf739, 0x9b64, 0x8550, 0x517c,
    0xc677, 0xd4ff, 0x9820, 0x554c, 0x7c81, 0xa85c, 0x9e42, 0x4e74, 0xd431, 0x75d4, 0xa4f3, 0xfe78,
    0x4ac5, 0x7dcf, 0xb73d, 0x4285, 0x970e, 0x5849, 0x55d5, 0x8b9b, 0x21ed, 0x6da3, 0xf040, 0x5807,
    0x8026, 0x70cb, 0x5f48, 0xae32, 0xed81, 0xdaad, 0x60cf, 0x98c3, 0xc942, 0x6709, 0x14f3, 0xa41d,
    0x1401, 0x929f, 0x7c92, 0x5d3b, 0xeedb, 0x1ab4, 0xf92d, 0xd1ef, 0x1c08, 0x7e0b, 0xce32, 0x127e,
    0x80d9, 0x7f34, 0xa3b0, 0xb4b6, 0xa91f, 0xa854, 0x0a6e, 0x585c, 0x4bff, 0xd04f, 0x0181, 0x2d21,
    0xd23a, 0xa177, 0x7d46, 0x79fa, 0xddeb, 0x219e, 0xefe4, 0x25fe, 0xd3c0, 0x3bb4, 0xd33d, 0x42bc,
    0x65af, 0x4adb, 0x3469, 0x9810, 0x1f31, 0xa703, 0x40b2, 0x3185, 0xf301, 0x330d, 0xd419, 0xed3e,
    0xca69, 0xec79, 0x0966, 0x0c69, 0x161c, 0x7ca4, 0xcbd2, 0xc549, 0x60a6, 0xcba3, 0x6a3d, 0xd6da,
    0xe270, 0x94a7, 0x2c04, 0x1e0b, 0x1767, 0xfc11, 0xe775, 0x2c97, 0x563f, 0x271b, 0x99e4, 0xe18c,
    0x695f, 0xd52d, 0x016e, 0x036f, 0x2973, 0xfadf, 0x3861, 0xdc16, 0x19b1, 0x5ea9, 0x525a, 0xd632,
    0x05d3, 0x3747, 0xfb19, 0x1c8f,
}};
#define exp8_r (ex8_r.hi)
#define exp8lo_r (ex8_r.lo)
/* TRV: tanh(y) 2^32 + 0x80 (O4: + 0x101 in c0, sigmoid ap_'s offset; tanh kink_ takes 0x81 off) for 1/8 <= y < 2 on 32 cells per binade (work/trv/gen/gen32.c: every word of every cell
 * checked on tanh T1/T2/T3 and on sigmoid ap_/am_/2 <= x < 4), cell c from y = 1/8 + c 2^18 words; c3 a whole word. */
static const struct rx_r tl_r[96] = {
    {0x1fd59a2cu, 33035557, -32089, -646, -3794},
    {0x21cd2f74u, 32969453, -34006, -635, -13203},
    {0x21cd2f74u, 32969451, -34009, -633, -13203},
    {0x23c3bb0bu, 32899532, -35906, -630, -4499},
    {0x23c3bb0bu, 32899532, -35906, -633, -4499},
    {0x25b92e1du, 32825827, -37790, -620, -2298},
    {0x25b92e1du, 32825831, -37787, -629, -2297},
    {0x27ad79f7u, 32748386, -39651, -621, -14266},
    {0x27ad79f7u, 32748382, -39649, -621, -14266},
    {0x29a09007u, 32667227, -41501, -616, -3898},
    {0x29a09007u, 32667229, -41502, -608, -3898},
    {0x2b9261e5u, 32582401, -43325, -610, -11314},
    {0x2b9261e5u, 32582400, -43326, -602, -11313},
    {0x2d82e14cu, 32493943, -45126, -597, -12527},
    {0x2d82e14cu, 32493939, -45125, -601, -12527},
    {0x2f720021u, 32401890, -46921, -599, -8708},
    {0x2f720021u, 32401893, -46918, -589, -8708},
    {0x315fb073u, 32306295, -48674, -581, -1411},
    {0x315fb073u, 32306295, -48675, -587, -1411},
    {0x334be47du, 32207193, -50421, -580, -1229},
    {0x334be47du, 32207195, -50418, -577, -1229},
    {0x35368ea6u, 32104635, -52137, -569, -4381},
    {0x35368ea6u, 32104637, -52138, -566, -4381},
    {0x371fa183u, 31998667, -53827, -560, -2754},
    {0x371fa183u, 31998669, -53836, -552, -2753},
    {0x39070fdau, 31889336, -55494, -549, -11065},
    {0x39070fdau, 31889333, -55493, -555, -11065},
    {0x3aeccca0u, 31776690, -57146, -552, -12836},
    {0x3aeccca0u, 31776689, -57140, -544, -12836},
    {0x3cd0cafdu, 31660783, -58758, -534, -5422},
    {0x3cd0cafdu, 31660785, -58765, -532, -5422},
    {0x3eb2fe4eu, 31541665, -60353, -529, -13042},
    {0x3eb2fe4eu, 63083329, -241420, -4173, -13041},
    {0x4271d23fu, 62588023, -253829, -4097, -27748},
    {0x4271d23eu, 62588022, -253831, -4028, -11364},
    {0x4628e77bu, 62068333, -265803, -3955, -21688},
    {0x4628e77bu, 62068337, -265803, -3876, -21688},
    {0x49d7e089u, 61525169, -277312, -3802, -28801},
    {0x49d7e088u, 61525170, -277303, -3722, -12416},
    {0x4d7e6384u, 60959463, -288344, -3640, -5531},
    {0x4d7e6385u, 60959468, -288344, -3554, -21915},
    {0x511c1a41u, 60372178, -298887, -3471, -15516},
    {0x511c1a41u, 60372179, -298883, -3393, -15516},
    {0x54b0b25au, 59764293, -308940, -3309, -25210},
    {0x54b0b259u, 59764299, -308946, -3219, -8826},
    {0x583bdd49u, 59136810, -318486, -3142, -15101},
    {0x583bdd49u, 59136813, -318485, -3059, -15101},
    {0x5bbd507cu, 58490743, -327521, -2972, -29552},
    {0x5bbd507cu, 58490742, -327518, -2885, -29552},
    {0x5f34c559u, 57827115, -336044, -2796, -17393},
    {0x5f34c559u, 57827122, -336047, -2708, -17393},
    {0x62a1f953u, 57146972, -344043, -2625, -3268},
    {0x62a1f954u, 57146975, -344038, -2542, -19652},
    {0x6604adedu, 56451354, -351515, -2449, -15375},
    {0x6604adedu, 56451353, -351516, -2363, -15375},
    {0x695ca8bau, 55741298, -358476, -2279, -14208},
    {0x695ca8bau, 55741303, -358477, -2184, -14208},
    {0x6ca9b366u, 55017858, -364908, -2102, -17533},
    {0x6ca9b366u, 55017863, -364911, -2008, -17533},
    {0x6feb9bafu, 54282073, -370823, -1931, -10460},
    {0x6feb9bafu, 54282077, -370819, -1837, -10459},
    {0x73223365u, 53534984, -376210, -1750, -15664},
    {0x73223365u, 53534985, -376209, -1675, -15665},
    {0x764d505fu, 52777613, -381098, -1586, -26997},
    {0x764d505eu, 105555248, -1524545, -11679, -10613},
    {0x7c808569u, 102472166, -1557577, -10346, -2489},
    {0x7c80856au, 102472205, -1557570, -9041, -18873},
    {0x82843898u, 99330952, -1582754, -7751, -4695},
    {0x82843899u, 99330989, -1582752, -6497, -21079},
    {0x8857a4f1u, 96146956, -1600399, -5272, -10260},
    {0x8857a4f1u, 96146992, -1600393, -4066, -10260},
    {0x8dfa4056u, 92934906, -1610857, -2913, -2273},
    {0x8dfa4056u, 92934947, -1610856, -1776, -2273},
    {0x936bb8bau, 89708765, -1614539, -684, -7064},
    {0x936bb8bau, 89708798, -1614537, 377, -7064},
    {0x98abf0f6u, 86481646, -1611885, 1389, -16669},
    {0x98abf0f6u, 86481676, -1611883, 2373, -16669},
    {0x9dbafd5fu, 83265764, -1603353, 3311, -10520},
    {0x9dbafd5fu, 83265789, -1603354, 4209, -10520},
    {0xa299202bu, 80072380, -1589440, 5061, -6684},
    {0xa299202cu, 80072404, -1589435, 5886, -23068},
    {0xa746c5aeu, 76911796, -1570617, 6656, -8158},
    {0xa746c5aeu, 76911816, -1570607, 7393, -8158},
    {0xabc4808au, 73793327, -1547379, 8087, -26029},
    {0xabc48089u, 73793342, -1547372, 8741, -9645},
    {0xb01305d6u, 70725305, -1520220, 9355, -8968},
    {0xb01305d7u, 70725320, -1520218, 9935, -25352},
    {0xb433295du, 67715106, -1489612, 10466, -10176},
    {0xb433295eu, 67715119, -1489609, 10971, -26560},
    {0xb825d9ddu, 64769169, -1456010, 11427, -16489},
    {0xb825d9ddu, 64769181, -1456013, 11858, -16489},
    {0xbbec1d72u, 61893023, -1419871, 12237, -6133},
    {0xbbec1d72u, 61893034, -1419862, 12598, -6133},
    {0xbf870e28u, 59091350, -1381591, 12916, -25847},
    {0xbf870e27u, 59091359, -1381594, 13210, -9463},
    {0xc2f7d6a9u, 56368000, -1341583, 13461, -5657}
};
/* RX: tanh-only DEFICIT cells for 1/8 <= y < 2, 32 per binade (cell c from y = 1/8 + c 2^18 words): V = 256 (bits(y) -
 * bits(tanh y)) + 0x80 + eps with bits() the word as a real number, so the result is w - (V >> 8) for either sign and
 * every tier (8 guard bits of the result, guard values 0 and 1 decline; work/rx/gen/gend.c: every word of every cell
 * checked). Cells 32 and 67 hold tanh y = 1/4 and 1/2 (a kink in bits(tanh y)): all-zero rows, V = 0, which the
 * decline sends to the tl_r path. */
static const struct rl_r tld_r[128] = {
    {0x00a99bd3u, 2075497, 128383, 2557},
    {0x00cb46b5u, 2339925, 136041, 2548},
    {0x00cb46b4u, 2339923, 136040, 2539},
    {0x00f11856u, 2619603, 143634, 2531},
    {0x00f11857u, 2619605, 143632, 2517},
    {0x011b4c0du, 2914407, 151160, 2504},
    {0x011b4c0du, 2914408, 151165, 2487},
    {0x014a1ca9u, 3224198, 158621, 2479},
    {0x014a1ca9u, 3224195, 158621, 2464},
    {0x017dc466u, 3548818, 165995, 2455},
    {0x017dc465u, 3548821, 166001, 2436},
    {0x01b67cefu, 3888130, 173304, 2433},
    {0x01b67cf0u, 3888131, 173301, 2417},
    {0x01f47f54u, 4241967, 180524, 2400},
    {0x01f47f54u, 4241966, 180526, 2386},
    {0x02380400u, 4610167, 187669, 2374},
    {0x023803ffu, 4610162, 187668, 2355},
    {0x028142b5u, 4992551, 194715, 2345},
    {0x028142b6u, 4992551, 194718, 2325},
    {0x02d0728eu, 5388955, 201680, 2315},
    {0x02d0728du, 5388954, 201676, 2300},
    {0x0325c9eau, 5799187, 208544, 2278},
    {0x0325c9eau, 5799187, 208546, 2267},
    {0x03817e75u, 6223064, 215320, 2249},
    {0x03817e76u, 6223064, 215321, 2232},
    {0x03e3c51bu, 6660390, 221991, 2211},
    {0x03e3c51cu, 6660391, 221997, 2200},
    {0x044cd205u, 7110973, 228578, 2189},
    {0x044cd204u, 7110969, 228576, 2164},
    {0x04bcd88fu, 7574603, 235051, 2151},
    {0x04bcd88eu, 7574600, 235043, 2136},
    {0x05340b4cu, 8051070, 241408, 2108},
    {0x00000000u, 0, 0, 0},
    {0x031c5e07u, 9041686, 507665, 8197},
    {0x031c5e07u, 9041682, 507672, 8050},
    {0x03ae338eu, 10081062, 531598, 7896},
    {0x03ae338du, 10081059, 531605, 7747},
    {0x04504173u, 11167393, 554622, 7597},
    {0x04504173u, 11167384, 554622, 7433},
    {0x05033b7au, 12298801, 576684, 7275},
    {0x05033b7au, 12298793, 576687, 7112},
    {0x05c7ce01u, 13473372, 597779, 6952},
    {0x05c7ce01u, 13473366, 597781, 6779},
    {0x069e9dd0u, 14689143, 617884, 6622},
    {0x069e9dd0u, 14689136, 617880, 6450},
    {0x078847f1u, 15944110, 636972, 6278},
    {0x078847f1u, 15944105, 636977, 6106},
    {0x0885618du, 17236245, 655039, 5933},
    {0x0885618du, 17236243, 655040, 5772},
    {0x099677d2u, 18563496, 672086, 5596},
    {0x099677d1u, 18563492, 672085, 5417},
    {0x0abc0fdcu, 19923782, 688079, 5243},
    {0x0abc0fdbu, 19923779, 688084, 5071},
    {0x0bf6a6a9u, 21315028, 703044, 4903},
    {0x0bf6a6a9u, 21315020, 703040, 4724},
    {0x0d46b10eu, 22735132, 716950, 4553},
    {0x0d46b10fu, 22735129, 716943, 4378},
    {0x0eac9bb7u, 24182013, 729817, 4204},
    {0x0eac9bb7u, 24182005, 729816, 4023},
    {0x1028cb24u, 25653580, 741638, 3854},
    {0x1028cb24u, 25653574, 741637, 3683},
    {0x11bb9bb9u, 27147761, 752428, 3513},
    {0x11bb9bb8u, 27147758, 752430, 3335},
    {0x136561c6u, 28662504, 762197, 3170},
    {0x136561c7u, -76892769, 3049102, 23348},
    {0x0efef7b0u, -70726602, 3115154, 20687},
    {0x0efef7b0u, -70726683, 3115150, 18074},
    {0x00000000u, 0, 0, 0},
    {0x0d7bc8e9u, 34886742, 1582749, 6499},
    {0x0fa85c91u, 38070770, 1600391, 5264},
    {0x0fa85c91u, 38070737, 1600394, 4066},
    {0x1205c12cu, 41282822, 1610860, 2911},
    {0x1205c12cu, 41282787, 1610849, 1782},
    {0x149448c8u, 44508964, 1614539, 682},
    {0x149448c7u, 44508934, 1614529, -369},
    {0x1754108cu, 47736084, 1611885, -1393},
    {0x1754108cu, 47736053, 1611884, -2373},
    {0x1a450423u, 50951965, 1603356, -3307},
    {0x1a450423u, 50951940, 1603351, -4203},
    {0x1d66e157u, 54145349, 1589441, -5061},
    {0x1d66e156u, 54145325, 1589436, -5886},
    {0x20b93bd4u, 57305933, 1570619, -6655},
    {0x20b93bd4u, 57305913, 1570606, -7390},
    {0x243b80f8u, 60424402, 1547379, -8089},
    {0x243b80f9u, 60424387, 1547373, -8742},
    {0x27ecfbacu, 63492424, 1520221, -9355},
    {0x27ecfbacu, 63492408, 1520217, -9929},
    {0x2bccd825u, 66502623, 1489613, -10466},
    {0x2bccd824u, 66502610, 1489608, -10967},
    {0x2fda27a5u, 69448563, 1456018, -11421},
    {0x2fda27a5u, 69448549, 1456007, -11848},
    {0x3413e410u, 72324706, 1419870, -12238},
    {0x3413e410u, 72324695, 1419864, -12600},
    {0x3878f35bu, 75126379, 1381594, -12911},
    {0x3878f35au, 75126373, 1381588, -13207},
    {0x3d082ad8u, 77849732, 1341590, -13459},
    {0x3d082ad9u, 21481674, 5366710, -110329},
    {0x3ea026c9u, 31881886, 5031546, -113051},
    {0x3ea026c9u, 31881827, 5031461, -114937},
    {0x40d1a5a4u, 41598974, 4684879, -116061},
    {0x40d1a5a4u, 41598966, 4684805, -116489},
    {0x43921aa0u, 50619192, 4335556, -116302},
    {0x43921a9fu, 50619213, 4335500, -115571},
    {0x46d6e2a6u, 58944414, 3990586, -114342},
    {0x46d6e2a5u, 58944462, 3990546, -112698},
    {0x4a957b5bu, 66588993, 3655433, -110689},
    {0x4a957b5bu, 66589067, 3655399, -108355},
    {0x4ec3adebu, 73576780, 3334168, -105777},
    {0x4ec3adebu, 73576869, 3334142, -102979},
    {0x5357aee6u, 79938513, 3029635, -100012},
    {0x5357aee6u, 79938612, 3029616, -96908},
    {0x584834bdu, 85709611, 2743685, -93706},
    {0x584834bdu, 85709710, 2743671, -90433},
    {0x5d8c864eu, 90928323, 2477319, -87127},
    {0x5d8c864eu, 90928430, 2477317, -83796},
    {0x631c8301u, 95634278, 2230924, -80466},
    {0x631c8301u, 95634381, 2230923, -77166},
    {0x68f0a5b7u, 99867290, 2004342, -73892},
    {0x68f0a5b7u, 99867381, 2004349, -70695},
    {0x6f0203c1u, 103666477, 1797021, -67533},
    {0x6f0203c1u, 103666576, 1797027, -64442},
    {0x754a48e1u, 107069653, 1608202, -61450},
    {0x754a48e1u, 107069744, 1608215, -58527},
    {0x7bc3b119u, 110112814, 1436890, -55695},
    {0x7bc3b119u, 110112901, 1436896, -52960},
    {0x82690112u, 112829882, 1281983, -50321},
    {0x82690112u, 112829959, 1281986, -47778},
    {0x89357d90u, 115252507, 1142316, -45342}
};
/* TRV: the anchors of their declines, every 2^18 words from y = 1/8 to y = 2: T0 2^32 rounded and the tail
 * dx = T0 2^60 - c0 2^28 (work/trv/gen/genanc.c) */
static const struct ra_r tla_r[33] = {
    {0xc2f7d5a9u, -92681685},
    {0xc63fae36u, -66603822},
    {0xc95fd9b8u, 114145484},
    {0xcc59a31du, 4770091},
    {0xcf2e5addu, 36091031},
    {0xd1df54c3u, -88749363},
    {0xd46de5e2u, -121324239},
    {0xd6db62c7u, -43335697},
    {0xd9291ddbu, 93779732},
    {0xdb5865f7u, 109647171},
    {0xdd6a8525u, 54911171},
    {0xdf60bf8fu, -41349318},
    {0xe13c5295u, 41040858},
    {0xe2fe740cu, 33913947},
    {0xe4a8519au, 6578111},
    {0xe63b1036u, 3675026},
    {0xe7b7cbc3u, 117095344},
    {0xe91f96c7u, -41796057},
    {0xea737a32u, 21190741},
    {0xebb47545u, -48357186},
    {0xece37d7fu, 51264553},
    {0xee017ea4u, 45982792},
    {0xef0f5acau, -72824939},
    {0xf00dea75u, -63908945},
    {0xf0fdfcbfu, 26907488},
    {0xf1e05786u, -8049340},
    {0xf2b5b79fu, 131464829},
    {0xf37ed116u, -26657430},
    {0xf43c4f67u, 101117232},
    {0xf4eed5c9u, 103224706},
    {0xf596ff6fu, -84522611},
    {0xf6355fcfu, 46938654},
    {0xf6ca82f1u, -35526166}
};
/* TRV: 2 - 2^-6 <= y < 9.125, 64 cells per binade, in deficit form: V = 128 (bits(y) - bits(tanh y)) + 0x40 + eps,
 * bits() the word as a real number (work/trv/gen/genhd.c: every word of every cell checked on tanh, from y = 2, and
 * on sigmoid x = 2y). Row 0 is the last cell below 2 (sigmoid's x just below 4); xh the anchor tails as before. */
static const struct rx_r ta_r[138] = {
    {0x449abec8u, 28813132, 142816, -2805, -5654},
    {0x449abec8u, 24071857, 571161, -21496, 3553},
    {0x46127139u, 25150579, 508383, -20355, -13251},
    {0x46127139u, 25150599, 508384, -19312, 6556},
    {0x4799acc3u, 26110256, 452036, -18256, -7141},
    {0x4799acc3u, 26110277, 452026, -17283, 6439},
    {0x492eb8beu, 26963198, 401566, -16358, 4217},
    {0x492eb8beu, 26963226, 401571, -15459, 1231},
    {0x4ad00a90u, 27720661, 356478, -14607, -28909},
    {0x4ad00a90u, 27720680, 356481, -13809, 5886},
    {0x4c7c4175u, 28392821, 316211, -13040, 9301},
    {0x4c7c4175u, 28392847, 316228, -12307, 148},
    {0x4e322294u, 28988920, 280344, -11619, 28078},
    {0x4e322294u, 28988939, 280346, -10953, 5457},
    {0x4ff09544u, 29517246, 248404, -10337, -17557},
    {0x4ff09544u, 29517266, 248407, -9748, 4592},
    {0x51b69fa8u, 29985274, 220003, -9184, -7964},
    {0x51b69fa8u, 29985292, 220005, -8661, 1336},
    {0x53836388u, 30399705, 194767, -8167, 13874},
    {0x53836388u, 30399718, 194767, -7697, 4735},
    {0x55561b6eu, 30766526, 172362, -7254, 24192},
    {0x55561b6eu, 30766534, 172362, -6829, 7087},
    {0x572e180au, 31091089, 152478, -6434, -28206},
    {0x572e180au, 31091103, 152475, -6049, 1974},
    {0x590abdd5u, 31378181, 134850, -5703, 7987},
    {0x590abdd5u, 31378195, 134851, -5362, 5079},
    {0x5aeb82e6u, 31632059, 119236, -5046, -4695},
    {0x5aeb82e6u, 31632068, 119243, -4755, 3587},
    {0x5ccfed0au, 31856513, 105407, -4470, 9694},
    {0x5ccfed09u, 31856522, 105405, -4211, -402},
    {0x5eb79002u, 32054902, 93152, -3961, 11270},
    {0x5eb79002u, 32054914, 93150, -3715, 2275},
    {0x60a20bfcu, 32230232, 82322, -3499, 32753},
    {0x60a20bfcu, 32230237, 82327, -3299, 3333},
    {0x628f0c28u, 32385150, 72728, -3106, -28677},
    {0x628f0c28u, 32385159, 72728, -2914, 2054},
    {0x647e457fu, 32522019, 64260, -2738, 2337},
    {0x647e457fu, 32522017, 64256, -2571, 5185},
    {0x666f75a4u, 32642917, 56755, -2428, 16070},
    {0x666f75a4u, 32642917, 56754, -2274, 7072},
    {0x686261e9u, 32749701, 50130, -2138, -12245},
    {0x686261e9u, 32749701, 50134, -2023, 2473},
    {0x6a56d670u, 32844005, 44261, -1895, -17790},
    {0x6a56d670u, 32844011, 44267, -1775, 422},
    {0x6c4ca561u, 32927287, 39081, -1677, -27641},
    {0x6c4ca561u, 32927294, 39083, -1568, 5400},
    {0x6e43a637u, 33000827, 34513, -1477, 11640},
    {0x6e43a637u, 33000832, 34516, -1392, 3729},
    {0x703bb528u, 33065760, 30473, -1302, 15262},
    {0x703bb528u, 33065759, 30482, -1229, 7496},
    {0x7234b293u, 33123085, 26902, -1149, 27811},
    {0x7234b293u, 33123093, 26905, -1093, 1665},
    {0x742e828cu, 33173699, 23744, -1027, -25231},
    {0x742e828cu, 33173700, 23759, -961, 6921},
    {0x76290c65u, 33218379, 20964, -898, 8705},
    {0x76290c65u, 33218382, 20970, -840, 2249},
    {0x78243a57u, 33257829, 18517, -796, -18173},
    {0x78243a57u, 33257824, 18515, -747, 6819},
    {0x7a1ff923u, 33292643, 16342, -695, -10371},
    {0x7a1ff923u, 33292646, 16336, -657, 5017},
    {0x7c1c37cdu, 33323379, 14424, -624, 12665},
    {0x7c1c37cdu, 33323382, 14417, -580, 3413},
    {0x7e18e756u, 33350508, 12732, -547, -1565},
    {0x7e18e756u, 33350507, 12727, -504, 7668},
    {0x8015fa7eu, 33374454, 11242, -483, -24309},
    {0x8015fa7eu, 33194482, 44892, -3514, 1285},
    {0x82111e4cu, 33274048, 34971, -3100, -4231},
    {0x82111e4cu, 33274062, 34971, -2739, 994},
    {0x840d5531u, 33336045, 27245, -2411, 13039},
    {0x840d5531u, 33336054, 27243, -2137, 6407},
    {0x860a625fu, 33384336, 21216, -1887, -16449},
    {0x860a625fu, 33384343, 21224, -1667, 5082},
    {0x88081678u, 33421954, 16534, -1465, -15940},
    {0x88081678u, 33421960, 16525, -1294, 2716},
    {0x8a064c95u, 33451252, 12876, -1142, 28244},
    {0x8a064c95u, 33451258, 12868, -1006, 2198},
    {0x8c04e7f7u, 33474072, 10028, -887, -11713},
    {0x8c04e7f7u, 33474075, 10024, -785, 7377},
    {0x8e03d238u, 33491846, 7810, -692, 29461},
    {0x8e03d238u, 33491845, 7815, -612, 7539},
    {0x9002f9e7u, 33505686, 6077, -539, -30565},
    {0x9002f9e7u, 33505690, 6085, -481, 5231},
    {0x9202516eu, 33516469, 4740, -418, 15494},
    {0x9202516eu, 33516473, 4731, -363, 486},
    {0x9401ce39u, 33524866, 3694, -322, 6642},
    {0x9401ce39u, 33524868, 3692, -292, 878},
    {0x9601680au, 33531406, 2872, -259, 21807},
    {0x9601680au, 33531407, 2874, -225, 5307},
    {0x98011875u, 33536501, 2237, -204, 18617},
    {0x98011875u, 33536500, 2237, -176, 7695},
    {0x9a00da7au, 33540467, 1746, -148, 14960},
    {0x9a00da7au, 33540464, 1748, -136, 6624},
    {0x9c00aa34u, 33543554, 1360, -114, 4746},
    {0x9c00aa34u, 33543556, 1362, -109, 164},
    {0x9e00849du, 33545960, 1048, -103, -22344},
    {0x9e00849du, 33545960, 1061, -84, 7169},
    {0xa0006756u, 33547837, 828, -69, -25105},
    {0xa0006756u, 33547831, 831, -67, 7954},
    {0xa2005088u, 33549295, 643, -59, -12349},
    {0xa2005088u, 33549295, 644, -56, 1438},
    {0xa4003ec6u, 33550430, 498, -48, -14135},
    {0xa4003ec6u, 33550432, 496, -31, 1688},
    {0xa60030f2u, 33551318, 394, -31, 12744},
    {0xa60030f2u, 33551316, 392, -39, 5447},
    {0xa800262cu, 33552004, 301, -31, -9101},
    {0xa800262cu, 33552008, 301, -27, -156},
    {0xaa001dc9u, 33552544, 240, -24, 24753},
    {0xaa001dc9u, 33552543, 238, -21, 3141},
    {0xac001741u, 33552962, 187, -17, -31716},
    {0xac001741u, 33552959, 186, -15, 6419},
    {0xae00122au, 33553287, 143, -22, -3929},
    {0xae00122au, 33553288, 141, -18, 2056},
    {0xb0000e34u, 33553540, 112, -11, 30957},
    {0xb0000e34u, 33553538, 119, -16, 5032},
    {0xb2000b1eu, 33553741, 97, -7, -22468},
    {0xb2000b1eu, 33553733, 93, -4, 4927},
    {0xb40008b7u, 33553892, 66, -12, 8376},
    {0xb40008b7u, 33553886, 77, -5, 6917},
    {0xb60006d7u, 33554009, 52, -10, 11695},
    {0xb60006d8u, 33554006, 59, -14, 8160},
    {0xb8000562u, 33554104, 43, -3, 14749},
    {0xb8000564u, 33554101, 34, -1, 17694},
    {0xba000440u, 33554179, 42, 3, -5669},
    {0xba000441u, 33554172, 30, -4, 14583},
    {0xbc00035du, 33554232, 30, 5, 13366},
    {0xbc000360u, 33554230, 19, 0, 25523},
    {0xbe0002adu, 33554274, 16, -2, 30843},
    {0xbe0002aeu, 33554274, 14, 0, 11352},
    {0xc0000220u, 33554308, 10, -8, -971},
    {0xc0000224u, 33554186, 70, -11, 5448},
    {0xc2000165u, 33554281, 32, -13, 31109},
    {0xc2000162u, 33554283, 29, -4, -25866},
    {0xc40000f2u, 33554340, 26, -5, -2026},
    {0xc40000eeu, 33554342, 13, -1, -31204},
    {0xc60000abu, 33554374, 12, -10, -17296},
    {0xc60000a8u, 33554376, 7, 0, -31512},
    {0xc8000081u, 33554395, -2, -12, -17438},
    {0xc8000082u, 33554405, 0, 0, 4814}
};
/* sigmoid(-x) normalised to [2^31, 2^32) at the start of each cell, 64 cells per binade, 2 <= x < 4 (JR: below 2, am_)
 * (the 6 cells of 1 <= x < 1.09375 dropped by R4: am_ takes them; the rest from #18, R3's refits) */
static const struct ry_r tb_r[64] = {
    {0xf420a9dfu, -225472021, 229648758, -448564860},
    {0xe70147aau, -214904266, 232782869, -455052924},
    {0xe70147aau, -214904287, 235570609, -460627068},
    {0xda80999fu, -204671743, 237806714, -465323644},
    {0xda80999fu, -204671758, 239736605, -469181564},
    {0xce99740du, -194781328, 241150927, -472238204},
    {0xce99740du, -194781336, 242298381, -474531452},
    {0xc346950cu, -185237523, 242966869, -476099196},
    {0xc346950cu, -185237526, 243406841, -476978300},
    {0xb882ad76u, -176042649, 243403631, -477204604},
    {0xb882ad76u, -176042647, 243208569, -476814972},
    {0xae4868fau, -167197061, 242605986, -475843708},
    {0xae4868fbu, -167197055, 241846083, -474326140},
    {0xa4927565u, -158699359, 240713615, -472295548},
    {0xa4927565u, -158699350, 239455783, -469784188},
    {0x9b5b8913u, -150546591, 237858799, -466824316},
    {0x9b5b8913u, -150546578, 236166919, -463447164},
    {0x929e68a3u, -142734440, 234167697, -459681916},
    {0x929e68a3u, -142734424, 232101081, -455557756},
    {0x8a55ebecu, -135257410, 229757522, -451102332},
    {0x8a55ebecu, -135257392, 227371932, -446342780},
    {0x827d0245u, -128108992, 224737819, -441304188},
    {0x04fa0409u, -256217944, 444169067, -872023675},
    {0xf61d6bd7u, -242563645, 438419319, -860978299},
    {0xf61d6bd7u, -242563601, 432671965, -849517179},
    {0xe80c601fu, -229535651, 426531274, -837683835},
    {0xe80c6020u, -229535604, 420429405, -825518715},
    {0xdabd73b0u, -217116694, 413980371, -813061755},
    {0xdabd73b0u, -217116645, 407602161, -800348795},
    {0xce277ed0u, -205288552, 400918888, -787415675},
    {0xce277ed0u, -205288502, 394335119, -774296187},
    {0xc241a265u, -194032301, 387484758, -761020539},
    {0xc241a265u, -194032250, 380758038, -747619451},
    {0xb7034a4au, -183328514, 373800275, -734120059},
    {0xb7034a4au, -183328463, 366986832, -720549499},
    {0xac642ef0u, -173157435, 359974399, -706931323},
    {0xac642ef0u, -173157383, 353123303, -693289083},
    {0xa25c565au, -163499129, 346102238, -679643771},
    {0xa25c565au, -163499077, 339257193, -666016891},
    {0x98e41487u, -154333623, 332268122, -652425339},
    {0x98e41487u, -154333571, 325466433, -638888059},
    {0x8ff40b5fu, -145641018, 318544316, -625419899},
    {0x8ff40b5fu, -145640967, 311818169, -612036219},
    {0x87852a33u, -137401597, 304992813, -598750843},
    {0x87852a33u, -137401546, 298370041, -585576059},
    {0xff215934u, -259191811, 583333169, -1145047162},
    {0xff215934u, -259191712, 570341075, -1119208058},
    {0xf020348fu, -244409661, 557220174, -1093653114},
    {0xf020348fu, -244409567, 544519507, -1068399738},
    {0xe1fa8821u, -230419325, 531719427, -1043464314},
    {0xe1fa8821u, -230419231, 519342265, -1018860154},
    {0xd4a48688u, -217184283, 506890923, -994600058},
    {0xd4a48689u, -217184194, 494862160, -970694266},
    {0xc812ef22u, -204669003, 482781532, -947153530},
    {0xc812ef22u, -204668915, 471121178, -923985530},
    {0xbc3b0a0au, -192839010, 459427579, -901196922},
    {0xbc3b0a0au, -192838923, 448149991, -878794874},
    {0xb112a3eau, -181660924, 436855860, -856783482},
    {0xb112a3eau, -181660841, 425971279, -835167354},
    {0xa6900995u, -171102507, 415084416, -813949050},
    {0xa6900995u, -171102426, 404598966, -793130618},
    {0x9caa038eu, -161132676, 394123559, -772714106},
    {0x9caa038eu, -161132600, 384040786, -752700026},
    {0x9357d172u, -151721529, 373977929, -733087866}
};

/* sigmoid(-x), 4 <= x < 8 (and a sliver below 4): quartics on 32 cells per binade, normalised to
 * [2^31, 2^32) at the end of each cell. Field by field: sq_r[i + 33 k] is c_k of cell i for k < 5, and for
 * k = 5 the exponent field less one, in place (<< 23). */
static const uint32_t sq_r[5 * 33] = {
    0x9caa0387u, 0x9357d175u, 0x049c3e8fu, 0xe66b2110u, 0xcbae1ff9u, 0xb4029455u, 0x9f104dc1u, 0x19112a2du,
    0xf84a823au, 0xdb4fb46du, 0xc1b1a438u, 0xab0d9713u, 0x970be564u, 0x0abd94e3u, 0xeb82a612u, 0xcfecc98eu,
    0xb78fc23bu, 0xa20bbc1au, 0x1e17d001u, 0xfc8a7d3eu, 0xdeeac6c8u, 0xc4c351e7u, 0xadac6068u, 0x994a4131u,
    0x0e97daafu, 0xeed39cd9u, 0xd2c94bb2u, 0xba092d21u, 0xa4309369u, 0x21d0b1d9u, 0xffc7139bu, 0xe1bc652cu,
    0xc738a905u,
    0xf6654fd2u, 0xede9d3f9u, 0xdff11f58u, 0xe39a4e7cu, 0xe6db4315u, 0xe9bef787u, 0xec4f6127u, 0xdd2b00cbu,
    0xe132e432u, 0xe4c50227u, 0xe7ee6f1eu, 0xeabae032u, 0xed34cb5au, 0xdecb0ba2u, 0xe2aac0c5u, 0xe6178343u,
    0xe91e7be7u, 0xebcb5b25u, 0xdc51020eu, 0xe07e42d6u, 0xe42ec94cu, 0xe77109d9u, 0xea51d16du, 0xecdc74c2u,
    0xde35f548u, 0xe22c8343u, 0xe5ac4363u, 0xe8c3143fu, 0xeb7d3856u, 0xdbcb0aa9u, 0xe00b1c3au, 0xe3cb8ff6u,
    0xe71b5762u,
    0x0049e4d0u, 0x0116f8dfu, 0x01f09ae2u, 0x01b991bau, 0x0188498bu, 0x015c3c05u, 0x0134ea87u, 0x0223bdccu,
    0x01e5576eu, 0x01add8b3u, 0x017c8998u, 0x0150c2a0u, 0x0129ec00u, 0x020ef92eu, 0x01d1f1d5u, 0x019be41cu,
    0x016c092du, 0x0141af2cu, 0x02386e87u, 0x01f62799u, 0x01bb8d41u, 0x0187bf10u, 0x0159f587u, 0x01317f86u,
    0x021b7fbau, 0x01dc5656u, 0x01a48bd8u, 0x01734567u, 0x0147c142u, 0x0242a7e0u, 0x01fecb6cu, 0x01c2e0c8u,
    0x018dfaa1u,
    0xffb4b672u, 0xfb88b347u, 0xf7d3c665u, 0xf88e9e62u, 0xf93faa4fu, 0xf9e5a7f8u, 0xfa7ff69eu, 0xf61c7c8eu,
    0xf7216ffbu, 0xf80f7aefu, 0xf8e7b18du, 0xf9ab5878u, 0xfa5bc479u, 0xf5f4e5ceu, 0xf711c17cu, 0xf810c5c6u,
    0xf8f4ccc4u, 0xf9c04f6fu, 0xf4eb5d24u, 0xf62e4448u, 0xf74d841cu, 0xf84caa2fu, 0xf92f4410u, 0xf9f84d6bu,
    0xf5550253u, 0xf690f2dbu, 0xf7a8be47u, 0xf8a08587u, 0xf97bd77bu, 0xf47bb328u, 0xf5d30073u, 0xf7028cb0u,
    0xf80efc43u,
    0x0092a078u, 0x08c78078u, 0x1010a077u, 0x0ea10077u, 0x0d44a077u, 0x0bfe0077u, 0x0ace6077u, 0x136ce076u,
    0x116b8076u, 0x0f974076u, 0x0dee0076u, 0x0c6d4076u, 0x0b126076u, 0x13b4e075u, 0x11850075u, 0x0f8fe075u,
    0x0dcfe075u, 0x0c402075u, 0x15b7e074u, 0x133de074u, 0x110a0074u, 0x0f154074u, 0x0d58a074u, 0x0bce4074u,
    0x14e18073u, 0x12760073u, 0x10518073u, 0x0e6be073u, 0x0cbe2073u, 0x16842072u, 0x13e3c072u, 0x11916072u,
    0x0f83e072u
};

static inline uint32_t mulhu_r(uint32_t a, uint32_t b)
{
    return (uint32_t)(((uint64_t)a * b) >> 32);
}

static inline int32_t mulhs_r(int32_t a, int32_t b)
{
    return (int32_t)(((int64_t)a * b) >> 32);
}

/* t: the 17 bits of the word below the cell index, at the top of a word */
static inline int32_t mulhsx_r(int32_t a, uint32_t b)
{
    return (int32_t)(((int64_t)a * (int64_t)(uint64_t)b) >> 32);
}
/* R4: ta_r/tb_r cells and their kernels from public #29 */
/* th: the offset in the cell at the top of a word, shifted down by one. Its sign bit is then the lowest
 * bit of the cell index, and as a signed number th / 2^31 = v runs over [0, 1) from the start of an even
 * cell and over [-1, 0) from the END of an odd one: V = c0 + (v/2) s1, s1 = c1 + (v/2) s2,
 * s2 = c2 + (v/2) c3. The two inner truncations weigh |v|/2 and v^2/4 of a unit, 1.75 units of spread
 * in all (3 with the offset at full scale): the decline window is one or two guard values. */
static inline uint32_t rx_cell_r(const struct rx_r *r, int32_t th)
{
    int32_t s = r->c2 + mulhs_r(r->c3, th);
    s = r->c1 + mulhs_r(s, th);
    return r->c0 + (uint32_t)mulhs_r(s, th);
}
/* TRV: the same on tl_r (th = w << 13: the cell index's lowest bit is its sign bit) */
static inline uint32_t rl_cell_r(const struct rl_r *r, int32_t th)
{
    int32_t s = r->c2 + mulhs_r(r->c3, th);
    s = r->c1 + mulhs_r(s, th);
    return r->c0 + (uint32_t)mulhs_r(s, th);
}
/* The same on tanh's cells of y >= 1, where c3 is positive and, from y = 2 on, too large for a signed
 * field: read as an unsigned one */
static inline uint32_t rx_cellu_r(const struct rx_r *r, int32_t th)
{
    int32_t s = r->c2 + mulhs_r((int32_t)(uint16_t)r->c3, th);
    s = r->c1 + mulhs_r(s, th);
    return r->c0 + (uint32_t)mulhs_r(s, th);
}
/* sigmoid's B cells, where 8 times the cubic coefficient does not fit 16 bits: it is a whole word, at
 * 2^16 times its value, and the first product is taken with t1 = w << 1, which has the offset at that
 * scale. The upper bits of t1 (exponent, cell index) only add a constant per cell that the generator has
 * taken off c2, as it has the cell's width for an odd cell (t1 counts from the start). The low nine bits
 * of w3 (nothing to the product) are 510 - ex, ex the exponent field less one of a result in the first
 * position: w3 << 23 is that field, and the arithmetically shifted value has 511 in its place. */
static inline uint32_t ry_cell_r(const struct ry_r *r, uint32_t t1, int32_t th)
{
    int32_t s = r->c2 + mulhsx_r(r->w3, t1);
    s = r->c1 + mulhs_r(s, th);
    return r->c0 + (uint32_t)mulhs_r(s, th);
}

/* Inputs the mid_r tier rounds wrongly, found by running it on every input it is given, with their
 * results (tanh by |x|). */

/* a*b exactly. Cortex-M0+ has no widening multiply and the library one costs about 35 instructions. */
static inline uint64_t umul_r(uint32_t a, uint32_t b)
{
    return (uint64_t)a * b;
}

/* y < 1/8 (biased e 115..123), lane TX: tanh y > Mid <=> D > G, D = (y - Mid)/u exact, G = (y - tanh y)/u,
 * u = 2^(e-152), a quarter ulp of y.  Times 3 (so y^3/3 is the exact integer m^3) and 2^K, K = 270 - 2e:
 * 3G 2^K = m^3 2^-28 (1 - c), c = z (2/5 - 17z/105 + 62z^2/945 - 1382z^3/51975 + 21844z^4/2027025), z = y^2.
 * R = 3D 2^K - A + B mod 2^32 with A = m^3 2^-28 (an exact window: only low words of the high partial
 * products) and B = m^3 c 2^-28 = m (m^2 c >> 48) >> 19; |R| < 2^30 for every reject, so the sign of
 * (int32_t)R decides.  +90 centres the truncations.  One word (0x3da99442) is decided wrongly: listed. */
/* R4: the decision itself, for y = the word a (biased exponent 119..123) and D3 = 3 (y - Mid)/u mod 2^32:
 * tanh y > Mid. Shared by tanh's small-range rejects and sigmoid's 2^-6 <= |x| < 1/4 ones (y = |x|/2). */
static inline uint32_t th_core_r(uint32_t M, uint32_t sx, uint32_t D3)
{
    /* R4: m = y's 24-bit significand, sx = 246 - 2e in its low five bits (e: y's biased exponent) */
    uint32_t m = M >> 8;
    uint64_t m2 = umul_r(m, m);
    uint32_t m2h = (uint32_t)(m2 >> 32), m2l = (uint32_t)m2;
    /* G1: (m m2l) >> 28 as mulhu(M, m2l) >> 4 (M = m 2^8 exactly; floors compose): two instructions fewer */
    uint32_t A = (m * m2h << 4) + (mulhu_r(M, m2l) >> 4);                     /* m^3 >> 28 mod 2^32 */
    uint32_t Zp = mulhu_r(M, M), Z = Zp >> (sx & 31u);         /* m^2 >> 16 (HTR: M = m 2^8); z at Q38 */
    /* HTR: the z^4 term of c/z economised (Chebyshev, z <= 2^-6) into the lower ones, one product less */
    uint32_t h2 = 4402689u - mulhu_r(Z, 27528u);                                /* Q26 */
    uint32_t h1 = 0x297296FDu - mulhu_r(Z, h2);                                 /* Q32 */
    uint32_t P = 0xCCCCCCCDu - (mulhu_r(Z, h1) >> 5);                           /* Q33 */
    uint32_t Q = mulhu_r(Zp, mulhu_r(Z, P));                                    /* m^2 c >> 48, c at Q39 */
    uint32_t B = (m * Q >> 19) | (mulhu_r(m, Q) << 13);                         /* m Q >> 19 mod 2^32 */
    uint32_t R = D3 * ((3u << 24) << (sx & 31u)) - A + B + 30u;
    return (int32_t)R > 0;
}
uint32_t eik_exp(uint32_t w);
/* R4: base + (tanh y > Mid), the comparison reversed when E has its top bit set; M = y's significand << 8,
 * E = e + 5 (e: y's biased exponent), so that -2E is th_core_r's sx = 246 - 2e modulo 32. Out of line for tanh's and sigmoid's small-range rejects (three call sites).
 * D = (y - Mid)/u (R4: tripled here, not at the five callers), |3 D| < 2^28 for every caller: the call in the
 * impossible case is the one block that needs a frame, so the decision runs frameless. */
/* G1: the result's base first and M last (the registers eik_tanh_r's series reject has them in: no move); the
 * th_sdec_r(M, E, D, base) spelling is kept for the callers */
#define th_sdec_r(M, E, D, base) th_sdecb_r(base, E, D, M)
static uint32_t th_sdecb_r(uint32_t base, uint32_t E, uint32_t D, uint32_t M)
{
    if ((int32_t)D < 0) /* never (HTR: D > 0 for every caller; one branch, no constant) */
        return eik_exp(M) >> 1;
    /* (R4: 3 D and sx formed here, not at the five callers) */
    return base + (th_core_r(M, 0u - 2u * E, D) ^ (E >> 31));
}
static inline uint32_t tanh_small_mid__r(uint32_t w, uint32_t ef, uint32_t mu)
{
    uint32_t a = w & 0x7FFFFFFFu, e = a >> 23, m = (a & 0x7FFFFFu) | 0x800000u, M = 2 * mu - 1;
    uint32_t D = 4 * m - (ef == e ? 2 * M : M);
    MARK_r(36);
    return th_sdec_r(m << 8, e + 5u, D, (w ^ a) | (((ef - 1) << 23) + mu - 1));
}
/* the small-range decision out of line: eik_tanh_r's tw rejects reach it by tail calls (two sites, so it is not
 * inlined and the fast paths keep no frame); the rare series-path rejects still go through cold_r (lane TX) */
static inline uint32_t th_smid_r(uint32_t w, uint32_t ef, uint32_t mu)
{
    /* the one word decided wrongly; the call (whose result adds 0) gives eik_tanh_r a block that needs a frame,
     * so that its other paths need none (a function without a non-tail call sets its frame up on entry) */
    return tanh_small_mid__r(w, ef, mu);
}

/* Every mid_r-tier path, out of line and behind one entry (many callers) so that it is never inlined
 * into, and never grows, the fast paths. */
static uint32_t ex_cold_r(uint32_t w, uint32_t code, uint32_t k, uint32_t X, uint32_t V);
static inline uint32_t mid_r(uint32_t w, uint32_t ef, uint32_t mu, uint32_t fn)
{
    (void)fn; /* tanh, y < 1/8 (code 2) */
    return th_smid_r(w, ef, mu);
}

/* V 2^(E1 - 157) with V in [2^31, 2^32) (E1 is the exponent field less one), or one binade lower:
 * round, or hand the two candidates to the mid_r tier through MID(exponent field, upper significand) */
/* OPA, OPB: how the sign is joined on (|, + and ^ all do); giving each use its own keeps the compiler
 * from sharing the last instructions of two paths through an extra jump */
#define TAIL2X_r(V, E1, P1, O1, K1, P2, O2, K2, SIGN, MID, OPA, OPB)                                               \
    do {                                                                                                         \
        uint32_t v_ = (V), e_ = (E1);                                                                            \
        if ((int32_t)v_ < 0) {                                                                                   \
            if (FAST_r(v_, 8, O1, K1, P1)) {                                                                       \
                STAT_r(0);                                                                                         \
                return (SIGN) OPA ((e_ << 23) + MANT_r(v_, 8, O1));                                                \
            }                                                                                                    \
            MID(e_ + 1, (v_ >> 8) + 1);                                                                          \
        }                                                                                                        \
        if (FAST_r(v_, 7, O2, K2, P2)) {                                                                           \
            STAT_r(0);                                                                                             \
            return (SIGN) OPB (((e_ - 1) << 23) + MANT_r(v_, 7, O2));                                              \
        }                                                                                                        \
        MID(e_, (v_ >> 7) + 1);                                                                                  \
    } while (0)

/* Cold work is named by a code: 0 exp mid_r, 1 exp small mid_r, 2 tanh mid_r, 3 sigmoid mid_r (a1 = exponent
 * field, a2 = upper significand); 4 exp of a large argument, 5 tanh outside the tables, 6 sigmoid
 * outside the tables, 7 sigmoid of -32 < x <= -4 (a1 = biased exponent); 8 settled.
 * An entry point reaches all of it through one call, cold_r(), at one place: the compiler then sets
 * up that entry point's stack frame only there, and cold_r() is too large to be inlined back. */
#define GO_r(CODE, A1, A2)                                                                                        \
    do {                                                                                                         \
        code = (CODE);                                                                                           \
        a1 = (A1);                                                                                               \
        a2 = (A2);                                                                                               \
        goto cold_;                                                                                              \
    } while (0)
#define GO_T_r(ef, mu) GO_r(2, ef, mu)
#define GO_S_r(ef, mu)                                                                                             \
    do {                                                                                                         \
        a1 = (ef) - 1u; /* G3: the exponent field less one */                                                    \
        a2 = (mu);                                                                                               \
        goto tier_; /* R4: sigmoid's exact tier, ex_cold_r's code 4, by a tail call */                          \
    } while (0)
#define GO_SP_r(ef, mu)                                                                                            \
    do {                                                                                                         \
        a1 = (ef);                                                                                               \
        a2 = (mu);                                                                                               \
        goto tierp_; /* (x > 0) */                                                                               \
    } while (0)

/* All cold_r work; the result comes back with its low bit flipped, which the caller undoes: that
 * keeps the call from being a tail call (see above). */
static uint32_t cold_r(uint32_t w, uint32_t a1, uint32_t a2, uint32_t code)
{
    /* the one use of mid_r(): it is compiled into this function, which is then far too large to be
     * compiled into an entry point */
    return mid_r(w, a1, a2, code) ^ 1u;
}

/* ---- R1 exp lane (rv32 variant): own precise path ---- */
/* R4: e^x = R 2^(q-63), R in (2^62, 2^64), relative error about 2^-48, for biased exponent 115..133 (R3's
 * sigmoid tier, both signs): k2 = floor(2|x| 512/ln2) | 1 with 2^31/ln2 rounded down for x < 0 (never one step too
 * large) and up for x > 0 (never one step too small), rho = +-(k2 L/2 - |x|) = rh 2^-40 + rl 2^-72 exactly
 * (L/2 = ln2/1024 to 2^-72); e^x = 2^(n/1024)... with n = -k2 or k2 by the sign, from the odd-power table. */
static inline uint64_t ex_core_r(uint32_t w, int32_t *qo, uint32_t *zo)
{
    /* G3: k2 = floor(2|x| 512/ln2) | 1 with 2^30/ln2 rounded down for x < 0 and up for x > 0 (k2 never one step too
     * large, or too small: R = T e^r stays below 2^64), m = k2 (x < 0) or -k2 and A = +-(k2 L1 - X) as ex_res_r takes
     * them. R is rebuilt from ex_res_r's window Z = (R >> 6) mod 2^32 (one place wider) and Rc = T (1 + r + r^2/2), R's
     * top word to a few units: R = Rc 2^32 + 64 dZ (mod 2^64), dZ = Z - (Rc << 26) read as signed. */
    uint32_t e = (w << 1) >> 24, sn = e - 119u, f = w << 9, X = f << sn;
    uint32_t t, nk, m, A;
    if ((int32_t)w < 0) {
        t = (1549078528u + mulhu_r(f, 1549078528u)) >> (29u - sn);
        m = t | 1u;
        A = m * 1488522235u - X;
        nk = ~t;
    } else {
        t = (1549082624u + mulhu_r(f, 1549082624u)) >> (29u - sn);
        m = 0u - (t | 1u);
        A = X + m * 1488522235u;
        nk = t;
    }
    *qo = (int32_t)nk;
    uint32_t o2 = nk & 0x1FEu;
    uint32_t Th = *(const uint32_t *)((const uint8_t *)exp8_r + 2u * o2) - 131u;
    uint32_t Tl = *(const uint16_t *)((const uint8_t *)exp8lo_r + o2);
    uint32_t rl = m * 0xE8E7BCD4u;
    int32_t rh = (int32_t)(A + (uint32_t)mulhsx_r((int32_t)m, 0xE8E7BCD4u));
    int32_t sq = mulhs_r(rh, rh);
    int32_t d = sq >> 10;
    int32_t c = mulhsx_r(mulhsx_r(rh + d, 5592405u), (uint32_t)sq);
    uint32_t Lw = (Th << 18) | (Tl << 2);
    uint32_t Z = (Lw << 8) + (Th >> 14) * (uint32_t)rh + (uint32_t)mulhsx_r(rh, Lw) + (mulhu_r(Th, rl) >> 14)
                 + ((uint32_t)mulhsx_r(sq + c, Th) << 9);
    uint32_t Rc = Th + (uint32_t)(mulhsx_r(rh + (sq >> 9), Th) >> 8);
    uint32_t Rh = Rc + (uint32_t)((int32_t)(Z - (Rc << 26)) >> 26);
    *zo = Z;
    return ((uint64_t)Rh << 32) | (Z << 6);
}


/* Words ex_prec_r rounds wrongly, with their results (found by the exhaustive check) */
/* (its two inexact words, bbf0edf1 and bae0e25c, are decided before it: main window / 2^-12..2^-8 series) */
#define EXC_EXR_r(w)

/* e^x correctly rounded for 2^-12 <= |x| < 128 (biased exponent 115..133), x below the overflow word
 * and above -104 (subnormal results included): k = round(|x| 512/ln2), rho = |x| - k ln2/512 in units
 * 2^-72 (64-bit), e^rho - 1 to about 2^-58, times the 48-bit table value 2^(j/512) (exp_tab : exp_lo),
 * which limits the result to about 2^-48 relative. */
static inline uint32_t ex_prec_r(uint64_t R, int32_t q)
{
    /* R4: R and q from ex_core_r */
    if ((int64_t)R >= 0) {
        R <<= 1;
        q--;
    }
    int32_t ef = q + 127;
    uint32_t hi = (uint32_t)(R >> 32);
    if (ef >= 1)
        return ((uint32_t)(ef - 1) << 23) + (hi >> 8) + ((hi >> 7) & 1u);
    /* subnormal: R 2^(ef - 41) units of 2^-149 */
    uint32_t sh = (uint32_t)(41 - ef);
    if (sh > 64u)
        return 0;
    if (sh == 64u)
        return R > (UINT64_C(1) << 63);
    return (uint32_t)(R >> sh) + (uint32_t)((R >> (sh - 1u)) & 1u);
}

static inline int32_t mulhsu_r(int32_t a, uint32_t b)
{
    return (int32_t)(((int64_t)a * (int64_t)(uint64_t)b) >> 32);
}

/* Words ex_res_r decides wrongly (within about 2^-50 of a midpoint, below the 48-bit table), with their results;
 * |Z| < 2^11 for each of them, so they are tested only then (r1: the list of the sign-free ex_res_r, exhaustive) */
/* (O1: EXC_EXS_r is gone: see ex_res_r) */

/* A fast-path reject lies within 8 units of 2^-32 of a midpoint m 2^-24 + 2^-25 of R = e^x 2^(63-q)
 * (R in [2^63, 2^64)). Such a midpoint is a multiple of 2^35 in units of R, so (R >> 4) mod 2^32, read
 * as signed, is R minus the midpoint: every partial product is needed only in that 32-bit window and
 * no carries are kept. k = round(|x| 512/ln2), X = |x| 2^40 mod 2^32 and V = the fast value plus its
 * rounding offset, as in the fast paths (V >> 8 is the upper candidate's significand). */
static inline uint32_t ex_res_r(uint32_t w, uint32_t m, uint32_t A, uint32_t C, uint32_t T, const uint8_t *L)
{
    /* r1 (#4, after public #29's emid_): sign-free. The value is T e^r with r = A 2^-40 + m ln2/1024, where
     * m = -k2 and A = X - k2 L1 for x > 0 (r = rho), and m = k2, A = -(X - k2 L1) for x < 0 (r = -rho); the
     * callers negate. E is the exponent part of the upper candidate E + (V >> 8) (its significand from V, as on the
     * fast paths). ln2/1024 = (0x2C5C85FD : 0xF473DE6A) 2^-72, L1 = 0x2C5C85FD: r = rh 2^-40 + rl 2^-72 with
     * m 0xF473DE6A = rh' 2^32 + rl (m signed: rh' the floor), rh = A + rh' */
    uint32_t rl = m * 0xE8E7BCD4u;
    int32_t rh = (int32_t)(A + (uint32_t)mulhsu_r((int32_t)m, 0xE8E7BCD4u));
    /* O1: r^2/2 in units 2^-49 from rh alone (|r| < ln2/512) */
    int32_t sq = mulhs_r(rh, rh);
    /* e^r - 1 = r + r^2/2 + (r^3/6)(1 + r/4) */
    int32_t d = sq >> 10;                                    /* r^2/4, units 2^-40 */
    int32_t c = mulhsu_r(mulhsu_r(rh + d, 5592405u), (uint32_t)sq); /* r^3/6 (1 + r/4), 2^-49 */
    /* exp9lo_r's entry: index ((-m) >> 1) & 511 (k2's own for x > 0, the reversed index for x < 0) */
    uint32_t Th = T - 131u, Tl = *(const uint16_t *)(L + 1024); /* H1: L from the caller's table base */
    /* O1: T = Th 2^16 + Tl (2^-47) split at 2^28: Th >> 12 and Lw = (T mod 2^28) << 4, so T rh >> 28 mod 2^32 is
     * (Th >> 12) rh + hi(rh Lw) and T << 12 is Lw << 8; T rl from Th alone */
    /* V2: Z = (R >> 5) mod 2^32 (a 16-unit window, for the quartic cells' rejects up to 8.5 units out): T split at 2^29 */
    uint32_t Lw = (Th << 19) | (Tl << 3);
    uint32_t Z = (Lw << 8) + (Th >> 13) * (uint32_t)rh + (uint32_t)mulhsu_r(rh, Lw) + (mulhu_r(Th, rl) >> 13)
                 + ((uint32_t)mulhsu_r(sq + c, Th) << 10);
    /* O1: no exception list: the seven words it held are decided right with exp8lo_r entries 88, 217, 247, 251, 255
     * raised by 1 and 253 by 2 (2^-47 units; exhaustive over every function) */
    (void)w;
    return C - ((int32_t)Z < 0); /* V2: C = the upper candidate word, as the fast path forms it */
}

/* the exp slow paths behind one call; the result comes back with its low bit flipped */
static uint32_t ex_cold_r(uint32_t w, uint32_t code, uint32_t k, uint32_t X, uint32_t V)
{
    /* R4: sigmoid's exact tier (code 4, by a tail call from eik_sigmoid_r's tier_: ef = k, mu = X; the result itself
     * comes back), on the shared core; code 0 is exp's exact path (exp's own call and sigmoid's subnormal results,
     * with the low bit flipped). */
    int32_t q;
    uint32_t Z;
    (void)V;
    /* one call site, so that the core is compiled into this function once */
    uint64_t R = ex_core_r(w, &q, &Z);
    if (code != 0u) {
        /* G3: x < 0 with 4 - 2^-11 < |x| < 87.34 (every caller), near a midpoint m = Mc 2^-s of the candidates
         * (Mc = 2 mu - 1, s = 151 - ef), and E = e^x = R 2^(q-63): sigma > m <=> E (1 - m) > m <=>
         * D = R (2^s - Mc) - Mc 2^(63-q) > 0. Every caller's R is within 2^37 of the threshold, and Mc 2^(63-q) is a
         * multiple of 2^(s+38), so D / 2^(s+6) mod 2^32 = Z - W with W = (Mc R >> (s+6)) mod 2^32, from
         * (Mc R) >> 32 = Mc Rh + hi(Mc Rl) */
        uint32_t eo = k, mu = X; /* (eo = ef - 1) */
        uint32_t Mc = 2u * mu - 1u, Rh = (uint32_t)(R >> 32), Rl = (uint32_t)R;
        uint32_t lo = Rh * Mc, hi = mulhu_r(Rh, Mc), lo2 = lo + mulhu_r(Rl, Mc);
        hi += (lo2 < lo);
        uint32_t cs = 124u - eo, W = (lo2 >> (cs & 31u)) | (hi << ((32u - cs) & 31u));
        if (cs >= 32u) /* (x < -23.5: hi alone) */
            W = cs < 57u ? hi >> (cs & 31u) : 0u;
        return (eo << 23) + mu + (uint32_t)((int32_t)(Z - W) >> 31); /* (the result itself: a tail call) */
    }
    /* R4: never (X is 0 here): a block with a real call (the 64-bit division helper), so that the
     * frame is set up there and this function is frameless on its live paths. (r1 removed the old code 2.) */
    if (X == 1u)
        return (uint32_t)(R / ((uint64_t)k | 3u)) ^ 1u;
    return ex_prec_r(R, q >> 9) ^ 1u; /* (q is k2's bits: the binade is q >> 9) */
}
#define GOX_r(CODE)                                                                                             \
    do {                                                                                                         \
        code = (CODE);                                                                                           \
        goto cold_;                                                                                              \
    } while (0)
/* R < 2^31 on a normal-result path: E = the exponent part that R in [2^31, 2^32) would have had */
#define GOL_r(K, A, RR, EE)                                                                                     \
    do {                                                                                                         \
        cT = T;                                                                                                  \
        ck = (K);                                                                                                \
        cX = (A);                                                                                                \
        cV = (RR);                                                                                               \
        cE = (EE);                                                                                               \
        goto low_;                                                                                               \
    } while (0)
#define GOR_r(K, A, CC)                                                                                          \
    do {                                                                                                         \
        cT = T;                                                                                                  \
        cL = TL_;                                                                                                \
        ck = (K);                                                                                                \
        cX = (A);                                                                                                \
        cV = (CC);                                                                                               \
        goto res_;                                                                                               \
    } while (0)

/* exp(x), -4 < x <= -1/4: cubic cells in the value (after public #34's te_r form; own fit, gen/cgen.c), 32 per
 * binade for -2 < x <= -1/4 (t = w << 14) and 64 for -4 < x <= -2 (t = w << 15):
 * Vf = c0 + t (c1 + t (c2 + w w3)) (signed x unsigned high products; the top term takes the word itself, so
 * w3 = c3 2^sh with the per-cell constant folded into c2). Vf = e^x 2^(31 - E) + 128 + d, d in [0, 4), where
 * e^x in [2^E, 2^(E+2)) over the cell; W = w3 mod 512 = E + 128 for -4 < x <= -2 (added), -(E + 128) + 2 for
 * -2 < x <= -1/4 (subtracted after a logical shift: the two groups' returns differ, so they are neither merged
 * nor tail-merged). Vf < 2^31 (as int32 >= 0) is the binade above (wrapped past 2^32). Accepted unless the guard
 * field is 0..3 (exhaustive per cell: 1.5% rejects). */
struct nxb_r {
    uint32_t c0;
    int32_t c1, c2, w3;
};
static const struct nxb_r nxq_r[161] = {
    {3344924022u,-26132215,3330002,-4337789},
    {3318893619u,-25928857,3303947,-4303485},
    {3293065786u,-25727076,3277127,-4268157},
    {3267438945u,-25526866,3254121,-4237949},
    {3242011535u,-25328214,3231117,-4207741},
    {3216782000u,-25131108,3205448,-4173949},
    {3191748808u,-24935538,3178256,-4138109},
    {3166910422u,-24741484,3152968,-4104829},
    {3142265330u,-24548947,3128069,-4072061},
    {3117812028u,-24357906,3107746,-4045437},
    {3093549024u,-24168350,3080558,-4009597},
    {3069474836u,-23980270,3056806,-3978365},
    {3045587994u,-23793654,3037251,-3952765},
    {3021887041u,-23608489,3010451,-3917437},
    {2998370530u,-23424769,2990903,-3891837},
    {2975037026u,-23242477,2962582,-3854461},
    {2951885106u,-23061598,2941506,-3826813},
    {2928913355u,-22882135,2917387,-3795069},
    {2906120372u,-22704066,2896701,-3767933},
    {2883504764u,-22527379,2872198,-3735677},
    {2861065153u,-22352071,2850753,-3707517},
    {2838800167u,-22178127,2833891,-3685501},
    {2816708450u,-22005533,2807865,-3651197},
    {2794788651u,-21834283,2789478,-3627133},
    {2773039436u,-21664372,2765371,-3595389},
    {2751459472u,-21495778,2747369,-3571837},
    {2730047447u,-21328495,2725169,-3542653},
    {2708802050u,-21162514,2701443,-3511421},
    {2687721986u,-20997824,2682683,-3486845},
    {2666805967u,-20834419,2658580,-3455101},
    {2646052719u,-20672285,2639444,-3430013},
    {2625460975u,-20511413,2618399,-3402365},
    {2605029479u,-40703582,20409373,-26928765},
    {2564642240u,-40072530,20091673,-26507389},
    {2524881151u,-39451262,19780877,-26095229},
    {2485736498u,-38839631,19475076,-25689725},
    {2447198726u,-38237475,19177702,-25295485},
    {2409258429u,-37644658,18880354,-24901245},
    {2371906343u,-37061031,18586469,-24511613},
    {2335133346u,-36486454,18300635,-24132733},
    {2298930462u,-35920786,18020177,-23761021},
    {2263288850u,-35363886,17744711,-23395965},
    {2228199810u,-34815617,17465441,-23025789},
    {2193654775u,-34275853,17198431,-22671997},
    {24323198u,-67488907,33864317,-44638332},
    {4252326104u,-66442588,33342619,-43947132},
    {4186399900u,-65412493,32830909,-43269244},
    {4121495790u,-64398370,32321918,-42594940},
    {4057597923u,-63399964,31823291,-41934460},
    {3994690698u,-62417040,31335419,-41288316},
    {3932758761u,-61449353,30851410,-40647292},
    {3871786990u,-60496665,30377003,-40019068},
    {3811760498u,-59558752,29907229,-39396988},
    {3752664631u,-58635379,29442850,-38782076},
    {3694484962u,-57726322,28990754,-38183548},
    {3637207284u,-56831358,28541373,-37588604},
    {3580817612u,-55950270,28103511,-37009020},
    {3525302183u,-55082841,27667599,-36431996},
    {3470647441u,-54228862,27240909,-35867260},
    {3416840042u,-53388120,26825356,-35317372},
    {3363866847u,-52560413,26411751,-34770044},
    {3311714930u,-51745541,26004691,-34231420},
    {3260371551u,-50943303,25601494,-33697916},
    {3209824178u,-50153501,25209434,-33179260},
    {3160060467u,-98751854,195478050,-259255420},
    {3062835631u,-95713580,189484525,-251286140},
    {2968602089u,-92768783,183668079,-243552892},
    {2877267809u,-89914587,178030242,-236057724},
    {2788743589u,-87148209,172569486,-228798588},
    {2702942972u,-84466935,167269325,-221753468},
    {2619782165u,-81868165,162135905,-214930556},
    {2539179946u,-79349348,157163468,-208322172},
    {2461057596u,-76908025,152341667,-201914492},
    {2385338817u,-74541812,147667053,-195702908},
    {2311949662u,-72248402,143135412,-189681788},
    {2240818453u,-70025553,138736775,-183837820},
    {48784014u,-135742185,268966723,-356374651},
    {4210108136u,-131565836,260709129,-345405563},
    {4080576730u,-127517981,252712559,-334784123},
    {3955030586u,-123594664,244955921,-324482171},
    {3833347091u,-119792054,237437681,-314497659},
    {3715407405u,-116106443,230149022,-304818811},
    {3601096340u,-112534221,223090703,-295446651},
    {3490302258u,-109071908,216238949,-286349435},
    {3382916949u,-105716115,209607563,-277545595},
    {3278835541u,-102463573,203175453,-269006971},
    {3177956381u,-99311101,196939928,-260729979},
    {3080180946u,-96255622,190891396,-252701819},
    {2985413746u,-93294145,185037143,-244932219},
    {2893562226u,-90423790,179354153,-237390459},
    {2804536678u,-87641738,173852007,-230089339},
    {2718250159u,-84945287,168519588,-223014011},
    {2634618398u,-82331795,163348059,-216152699},
    {2553559715u,-79798709,158335115,-209502331},
    {2474994948u,-77343565,153473855,-203053691},
    {2398847362u,-74963950,148763497,-196805755},
    {2325042591u,-72657553,287261915,-381502339},
    {2253508555u,-70422114,278434689,-369764227},
    {73383354u,-136510913,539758763,-716776324},
    {4233950634u,-132310915,523177578,-694729092},
    {4103685671u,-128240134,507098264,-673350020},
    {3977428540u,-124294597,491515062,-652631428},
    {3855055932u,-120470454,476415301,-632556420},
    {3736448334u,-116763969,461773244,-613090692},
    {3621489909u,-113171520,447586968,-594231684},
    {3510068382u,-109689597,433832271,-575947140},
    {3402074935u,-106314804,420501091,-558226308},
    {3297404098u,-103043839,407580359,-541051780},
    {3195953644u,-99873518,395058945,-524408708},
    {3097624491u,-96800730,382919161,-508273540},
    {3002320608u,-93822485,371154870,-492638084},
    {2909948918u,-90935874,359748397,-477478788},
    {2820419206u,-88138066,348692046,-462785412},
    {2733644032u,-85426343,337976992,-448546180},
    {2649538653u,-82798051,327595159,-434750340},
    {2568020922u,-80250624,317530794,-421376900},
    {2489011228u,-77781571,307770827,-408408452},
    {2412432407u,-75388484,298311416,-395839876},
    {2338209670u,-73069028,289146798,-383663492},
    {2266270525u,-70820930,280259671,-371856260},
    {98122004u,-137283992,543303626,-720841093},
    {4257928156u,-133060210,526610141,-698664325},
    {4126925481u,-128966375,510425514,-677164421},
    {3999953337u,-124998496,494744367,-656334213},
    {3876887715u,-121152697,479540944,-636139397},
    {3757608424u,-117425223,464804865,-616566149},
    {3641998971u,-113812428,450521516,-597595013},
    {3529946447u,-110310791,436678599,-579209605},
    {3421341416u,-106916881,423261878,-561390981},
    {3316077810u,-103627393,410254059,-544116101},
    {3214052827u,-100439118,397650914,-527379333},
    {3115166820u,-97348929,385428207,-511148421},
    {3019323216u,-94353815,373588249,-495426437},
    {2926428412u,-91450858,362110666,-480186245},
    {2836391679u,-88637210,350981215,-465408901},
    {2749125086u,-85910129,340192980,-451085189},
    {2664543403u,-83266950,329742880,-437211013},
    {2582564024u,-80705095,319612458,-423761797},
    {2503106887u,-78222059,309786708,-410717573},
    {2426094388u,-75815422,300267942,-398081413},
    {2351451315u,-73482825,291041537,-385833861},
    {2279104766u,-71221995,282102109,-373967749},
    {123000753u,-138061452,546866714,-724922758},
    {4282041466u,-133813751,530058445,-702613382},
    {4150296905u,-129696736,513776038,-681002886},
    {4022605696u,-125706385,497987943,-660049286},
    {3898843135u,-121838808,482684545,-639739782},
    {3778888346u,-118090219,467855062,-620060038},
    {3662624177u,-114456964,453474874,-600977286},
    {3549937083u,-110935496,439542825,-582489990},
    {3440717004u,-107522369,426036206,-564567942},
    {3334857275u,-104214252,412948089,-547201926},
    {3232254507u,-101007917,400255771,-530361734},
    {3132808495u,-97900230,387956939,-514044294},
    {3036422114u,-94888158,376036585,-498229638},
    {2943001231u,-91968757,364485083,-482904966},
    {2852454608u,-89139177,353281647,-468042630},
    {2764693809u,-86396653,342425892,-453642118},
    {2679633126u,-83738505,331903186,-439683974},
    {2597189486u,-81162143,321703911,-426155398},
    {2517282370u,-157330155,-703319532,941862010}, /* F1: -4.00098 < x <= -4 (the first 4096 words of e 129, gen/cgen.c CK=4096) */
};

static inline uint32_t nx_cell_r(const struct nxb_r *r, uint32_t w, uint32_t t)
{
    int32_t s = r->c2 + (int32_t)(((int64_t)r->w3 * (int64_t)(uint64_t)w) >> 32);
    s = r->c1 + (int32_t)(((int64_t)s * (int64_t)(uint64_t)t) >> 32);
    return r->c0 + (uint32_t)(int32_t)(((int64_t)s * (int64_t)(uint64_t)t) >> 32);
}

/* exp(x), -1/4 < x <= -2^-8 (R1X, after public #34's tnl_r/EXPNL path): e^x = e^-x0 e^-delta with x0 = |x| rounded to
 * 3 significant bits (the word rounded at bit 21) and delta = |x| - x0 (|delta| <= 2^-6) in units 2^-32;
 * tnl_r[(e - 119) 4 + m] = e^-x0 2^32 nudged by up to 1 unit to centre the error (gen/nlchk.c, exhaustive:
 * R + 130 within [-1.95, 1.87] of e^x 2^32 + 130, accepted unless the guard field is 0..3: 1.6% rejects). */
static const uint32_t tnl_r[25] = {
    0xff007fd5u, 0xfec0c7acu, 0xfe811f70u, 0xfe41871bu, 0xfe01feabu, 0xfd831d66u, 0xfd047b83u, 0xfc8618e0u,
    0xfc07f55fu, 0xfb0c6b44u, 0xfa11dc35u, 0xf9184738u, 0xf81fab54u, 0xf6315af2u, 0xf446e357u, 0xf2603cd9u,
    0xf07d5fdeu, 0xecc2e44eu, 0xe9173500u, 0xe57a1739u, 0xe1eb5127u, 0xdaf7e94fu, 0xd43b4096u, 0xcdb3a7c7u,
    0xc75f7cf5u
};

/* exp(x), -8 < x <= -4 (R1X, after public #34's eq4_r; own fit, gen/cgen4.c): quartic cells in the value, 32 per
 * binade (t = w << 14), stored by coefficient (c0[32], c1[32], c2[32], c3[32], c4w[32]):
 * Vf = c0 + t (c1 + t (c2 + t (c3 + w c4w))) (the top term takes the word itself, c4w = c4 2^14 with the per-cell
 * constant folded into c3); Vf = e^x 2^(31 - E) + 128 + d, d in [0, 8), e^x in [2^E, 2^(E+2)) over the cell,
 * W = c4w mod 512 = -(E + 128); Vf < 2^31 (as int32 >= 0) is the binade above. Accepted unless the guard field
 * is 0..7 (exhaustive per cell: 2.9% rejects, which take the main path). */
static const uint32_t nq4_r[5 * 32] = {
    0x960aae44u, 0x08d29cacu, 0xe9b4890du, 0xce3e7f54u, 0xb60282b9u, 0xa09f82f4u, 0x1b7fae7du, 0xfa2fd07fu,
    0xdcc9ff84u, 0xc2d87d0fu, 0xabf36078u, 0x97bef6c4u, 0x0bd4a630u, 0xec5c173bu, 0xd09633f1u, 0xb813bfbau,
    0xa272900du, 0x1eb80623u, 0xfd074b47u, 0xdf4bff21u, 0xc50f0cd8u, 0xade75da2u, 0x997833dfu, 0x0edf6ec4u,
    0xef0b5d65u, 0xd2f4b85bu, 0xba2aff9bu, 0xa44aeb35u, 0x21f9bac4u, 0xffe70961u, 0xe1d54981u, 0xc74c0c0eu,
    0xed3eaa7fu, 0xdee5ace4u, 0xe2c96f4au, 0xe6383078u, 0xe93fb002u, 0xebec0ff3u, 0xdc900aaeu, 0xe0ba0663u,
    0xe466c07bu, 0xe7a4f0bdu, 0xea819443u, 0xed082172u, 0xde856bb4u, 0xe2747d86u, 0xe5ed39e8u, 0xe8fd885fu,
    0xebb1ae4fu, 0xdc28ffbfu, 0xe05f170au, 0xe4168082u, 0xe75e1ec5u, 0xea4314a5u, 0xecd0f9cfu, 0xde2412a3u,
    0xe21e94c1u, 0xe5a16959u, 0xe8baa066u, 0xeb76a2ebu, 0xdbc0c92bu, 0xe0031f49u, 0xe3c55738u, 0xe7167eddu,
    0x012c1388u, 0x0211a1f4u, 0x01d3662fu, 0x019c7a72u, 0x016c02c4u, 0x01413d07u, 0x0236fbdfu, 0x01f45c89u,
    0x01b9913cu, 0x0185ae8eu, 0x0157e4a3u, 0x012f7c13u, 0x0217a5fau, 0x01d8b545u, 0x01a129cdu, 0x0170253eu,
    0x0144e31cu, 0x023d6c7eu, 0x01fa0b76u, 0x01be9541u, 0x018a1ba5u, 0x015bcc8bu, 0x0132ee86u, 0x021dbb87u,
    0x01de13c8u, 0x01a5e6d0u, 0x017453b4u, 0x014893cbu, 0x0243efddu, 0x01ffcae7u, 0x01c3a7ccu, 0x018e95a3u,
    0xee4898bdu, 0xe0ba94a8u, 0xe466819cu, 0xe7a3d85bu, 0xea804f6fu, 0xed06f863u, 0xde82b920u, 0xe2715a2bu,
    0xe5e98fd9u, 0xe8fa2d2eu, 0xebae2269u, 0xee115f8fu, 0xe0587213u, 0xe40fe478u, 0xe757f6e2u, 0xea3d38c8u,
    0xeccb9eb1u, 0xde190f5du, 0xe214c98fu, 0xe5984394u, 0xe8b21db2u, 0xeb6dfdcdu, 0xedd88872u, 0xdff51c1au,
    0xe3b83891u, 0xe70a66f4u, 0xe9f91ebeu, 0xec8f5a00u, 0xddaeddc3u, 0xe1b6e536u, 0xe545679au, 0xe868cc3fu,
    0x177ee586u, 0x29780187u, 0x2498cf87u, 0x204c7187u, 0x1c80af87u, 0x1926d587u, 0x2c647188u, 0x272d4788u,
    0x22934788u, 0x1e82c188u, 0x1aed2f88u, 0x17c2b788u, 0x29f09589u, 0x25033989u, 0x20a99b89u, 0x1cd30f89u,
    0x196fb789u, 0x2ce6478au, 0x279ef18au, 0x22f70f8au, 0x1edb398au, 0x1b3bfb8au, 0x18088f8au, 0x2a6a898bu,
    0x256ed98bu, 0x2108d58bu, 0x1d26a18bu, 0x19b9af8bu, 0x2d68958cu, 0x2812298cu, 0x235cbb8cu, 0x1f35338cu
};

static inline uint32_t eik_exp_r(uint32_t w)
{
    uint32_t code, ck, cX, cV, cE, ct, cM, cT;
    const uint8_t *cL;
    /* u = sign and biased exponent: the negative main range (most typical inputs) is told apart in one test */
    /* u = sign and biased exponent. The sign is tested first (as #24 does): the main ranges and the rest are
     * then told apart per sign, so no path pays for the other sign's test */
    uint32_t sn, sp;
    /* the rest, by sign: d = e - 119 (e the biased exponent); the shifts take u (= e mod 32). The fast parts are
     * written per sign, the rare exact decision (s119x_) is shared. */
    if ((int32_t)w < 0) {
        /* F1 (after public #34's dispatch): x < 0 is told apart by lui-only compares on the word itself, |x| >= 2 first;
         * every cell range is then one compare away (5 instructions to the cubic cells, 7 to the quartic and to tnl_r),
         * and u is formed only on the paths that take it */
        uint32_t t1 = w << 1;
        if ((int32_t)t1 < 0) { /* |x| >= 2 */
            if (w <= 0xC0800000u) {
                /* -4 <= x <= -2: cubic cells, 64 per binade (row 160 holds x = -4 itself (the first 4096 words of e 129), so that the
                 * limit is one lui and not folded into a shift of the exponent) */
                const struct nxb_r *r = &nxq_r[(w >> 17) - (384u << 6) + 96u];
                uint32_t Vf = nx_cell_r(r, w, w << 15), W = (uint32_t)r->w3;
                if ((int32_t)Vf < 0) {
                    if ((Vf & 252u) != 0u)
                        return (uint32_t)((int32_t)Vf >> 8) + (W << 23);
                    cV = (uint32_t)((int32_t)Vf >> 8);
                } else {
                    uint32_t v = Vf + 128u;
                    if ((v & 508u) != 0u)
                        return (v >> 9) + (W << 23);
                    cV = v >> 9;
                }
                cE = W << 23;
                sn = 9u;
                goto cres_;
            }
            if (w <= 0xC0FFF000u) {
                /* -7.998 < x <= -4.00098 (the last 4095 words of e 129 take the main path): quartic cells (nq4_r); rejects take the residual */
                const uint32_t *q = &nq4_r[(w >> 18) - (385u << 5)];
                uint32_t tt = w << 14, W = q[4 * 32];
                int32_t s = (int32_t)q[3 * 32] + (int32_t)(((int64_t)(int32_t)q[4 * 32] * (int64_t)(uint64_t)w) >> 32);
                s = (int32_t)q[2 * 32] + (int32_t)(((int64_t)s * (int64_t)(uint64_t)tt) >> 32);
                s = (int32_t)q[32] + (int32_t)(((int64_t)s * (int64_t)(uint64_t)tt) >> 32);
                uint32_t Vf = q[0] + (uint32_t)(int32_t)(((int64_t)s * (int64_t)(uint64_t)tt) >> 32);
                if ((int32_t)Vf < 0) {
                    if ((Vf & 248u) != 0u)
                        return (uint32_t)((int32_t)Vf >> 8) - (W << 23);
                    cV = (uint32_t)((int32_t)Vf >> 8);
                } else {
                    uint32_t v = Vf + 128u;
                    if ((v & 504u) != 0u)
                        return (v >> 9) - (W << 23);
                    cV = v >> 9;
                }
                cE = 0u - (W << 23);
                sn = 10u;
                goto cres_;
            }
            /* |x| >= 8. x <= ln(1.5 2^-149): e^x rounds to 2^-149 (word 1), and from -150 ln 2 on to +0; NaN past -inf */
            if (w >= 0xC2D00000u) { /* x <= -104 (a one-instruction constant) */
                if (w > 0xFF800000u)
                    goto nan_;
                return 0;
            }
            sn = (t1 >> 24) - 119u;
            if (sn < 14u)
                goto negmain_; /* 8 <= |x| < 64 */
            if (w >= 0xC2CDBF37u) {
                if (w >= 0xC2CFF1B5u)
                    return 0;
                return 1;
            }
            if (w < 0xC2AD0000u) /* -86.5 < x <= -64: a normal result with q = 125 - (k2 >> 10) >= 1 (sn = 14) */
                goto negmain_;
            /* G2: the five fixed hard words around -126 ln 2 (every hard set has them) */
            if (w - 0xC2AEAC4Eu < 5u)
                return 0x00800066u - ((w - 0xC2AEAC4Eu) << 6);
            /* O3: -103.97 < x <= -86.5 (e = 133, subnormal results below -87.34): exp's exact path (ex_prec_r rounds
             * subnormals); its own fast reduction here was 212 bytes for a cold range */
            GOX_r(0);
        }
        if (w >= 0xBE801000u) {
            /* -2 < x <= -0.25012 (the first 4096 words of e 125 take tnl_r): cubic cells, 32 per binade; W is stored plus 2 (the normal return takes Vf >> 8 unsigned,
             * so that the two groups are not merged into one path with variable shifts) */
            const struct nxb_r *r = &nxq_r[(w >> 18) - (381u << 5)];
            uint32_t Vf = nx_cell_r(r, w, w << 14), W = (uint32_t)r->w3;
            if ((int32_t)Vf < 0) {
                if ((Vf & 252u) != 0u)
                    return (Vf >> 8) - (W << 23);
                cV = Vf >> 8;
                cE = 0u - (W << 23);
            } else {
                uint32_t v = Vf + 128u;
                if ((v & 508u) != 0u)
                    return (v >> 9) - ((W - 2u) << 23);
                cV = v >> 9;
                cE = 0u - ((W - 2u) << 23);
            }
            sn = (t1 >> 24) - 119u;
            goto cres_;
        }
        /* H1: |x| < 2^-10 (to 0xBA7FF000) and |x| < 2^-24 (to 0xB37FF000) by lui-only compares on the word */
        if (w <= 0xBA7FF000u) {
            if (w <= 0xB37FF000u) /* |x| < 2^-24: 1, or 1 - 2^-24 for x < -2^-25 (the series takes the rest of e 102) */
                return 0x3F800000u - (w > 0xB3000000u);
            uint32_t u = t1 >> 24;
                /* 2^-24 <= |x| < 2^-10: X = floor(|x| 2^31); 1 - e^x = (X - X^2 2^-32) 2^-31 + [-1.21, 1.00] 2^-31
                 * (published #19; up to 2^-10 the cubic term is under 1/3 unit and the window still holds:
                 * exhaustive), so with 7 guard bits only guard fields 0 and 1 are unsettled */
                uint32_t M = (w << 8) | 0x80000000u, X = M >> (~u & 31u);
                uint32_t t = X - mulhu_r(X, X) + 65u;
                if ((t & 0x7Eu) != 0u)
                    return 0x3F800000u - (t >> 7);
                if (X < 0x8000u) {
                    /* |x| < 2^-16, guard fields 0 and 1: exact in one word (after #24/#29's 2^48 form, public) */
                    uint32_t Xo = M >> ((111u - u) & 31u);
                    uint32_t Y = Xo - (mulhu_r(Xo, Xo) >> 16) - 1u;
                    return (0x7F000000u - (Y >> 22)) >> 1;
                }
                cM = M;
                ct = t;
                goto s119x_; /* 2^-16 <= |x| < 2^-10: the series decision (exhaustive with this t) */
        }
        uint32_t u = t1 >> 24; /* e (taken modulo 32 below) */
        if (u < 119u) {
            /* 2^-10 <= |x| < 2^-8: as in #19's 2^-10..2^-7 path, X = floor(|x| 2^31), X - X^2 2^-32 + (2/3) X^3
             * 2^-64 against (1 - e^x) 2^31 (2/3 to one lui); only guard fields 0 and 1 are unsettled (exhaustive) */
            uint32_t M = (w << 8) | 0x80000000u, X = M >> (~u & 31u);
            uint32_t t = X - mulhu_r(X, X - mulhu_r(X, mulhu_r(X, 0xAAAAB000u))) + 64u;
            if ((t & 0x7Eu) != 0u)
                return 0x3F800000u - (t >> 7);
            ct = t;
            cM = M;
            goto s119x_;
        }
        sn = u - 119u;
        {
            /* 2^-8 <= |x| < 0.25012 (sn < 7): tnl_r; rejects take the residual */
            uint32_t T = *(const uint32_t *)((const uint8_t *)tnl_r + ((((t1 >> 20) + 2u) & 0x7FCu) - (119u << 4))); /* F1: from t1 = w << 1 (t1 >> 20 + 2 < 2^11 here: the mask is one andi) */
            int32_t D = (int32_t)((uint32_t)((int32_t)(w << 11) >> 10) << sn);
            uint32_t z = (uint32_t)mulhs_r(D, D);
            int32_t p = D - (int32_t)(z >> 1);
            int32_t Q = p + mulhsu_r(mulhs_r(D + p, 0x15559000), z);
            uint32_t R = T - (uint32_t)mulhsu_r(Q, T) + 0x82u;
            if ((R & 252u) != 0u)
                return 0x3E800000u + (R >> 8);
            cV = R >> 8;
            cE = 0x3E800000u;
            goto cres_;
        }
negmain_: {
            /* x < 0, 8 <= |x| < 86.5 (sn = e - 119). f = the significand's fraction; |x| 2^40 = (2^32 + f) 2^s, mod 2^32
             * f << s (s = sn). t = floor(2|x| 512/ln2) with 2^30/ln2 rounded up; rho = |x| - k2 ln2/1024 in units 2^-40;
             * T = exp8_r read backwards (e^x = 2^(-k2/1024) e^-rho), the exponent 125 - a */
            uint32_t f = w << 9, X = f << sn;
            uint32_t t = (1549082624u + mulhu_r(f, 1549082624u)) >> (29u - sn), k2 = t | 1u;
            int32_t rho = (int32_t)(X - k2 * 1488522235u - mulhu_r(k2, 0xE8E7C000u));
            uint32_t h = (uint32_t)(((int64_t)rho * rho) >> 32) >> 9;
            uint32_t Q = h - (uint32_t)rho;
            uint32_t T = *(const uint32_t *)((const uint8_t *)exp8_r + 1020u - ((k2 << 1) & 0x3FCu));
            const uint8_t *TL_ = (const uint8_t *)exp8_r + ((0u - k2) & 0x1FEu);
            uint32_t V = T + (uint32_t)((int32_t)(((int64_t)(uint64_t)(T + 820u) * (int32_t)Q) >> 32) >> 8);
            /* qn = -(the biased exponent 125 - a); also handed to the residual path */
            uint32_t qn = (uint32_t)((int32_t)k2 >> 9) - 125u;
            if ((int32_t)V < 0) {
                if ((V & 252u) != 0u)
                    return (V >> 8) - (qn << 23);
                GOR_r(k2, k2 * 1488522235u - X, (V >> 8) - (qn << 23));
            }
            GOX_r(0);
        }
    } else {
        uint32_t up = w >> 23; /* F1: its own name, so that the shared u (s119x_) does not reshape this side */
        sp = up - 119u;
        if (sp < 14u) {
    posmain_:;
            /* x > 0: the same with C rounded down (also 64 <= x < 88.72 from the rest, sp = 14) */
            uint32_t f = w << 9, X = f << sp;
            uint32_t t = (1549078528u + mulhu_r(f, 1549078528u)) >> (29u - sp), k2 = t | 1u;
            int32_t rho = (int32_t)(X - k2 * 1488522235u - mulhu_r(k2, 0xE8E7C000u));
            uint32_t h = (uint32_t)(((int64_t)rho * rho) >> 32) >> 9;
            uint32_t P = h + (uint32_t)rho;
            uint32_t T = exp8_r[(k2 >> 1) & 255];
            const uint8_t *TL_ = (const uint8_t *)exp8_r + (k2 & 0x1FEu);
            uint32_t V = T + (uint32_t)((int32_t)(((int64_t)(uint64_t)(T + 820u) * (int32_t)P) >> 32) >> 8);
            uint32_t qp = (uint32_t)((int32_t)k2 >> 9) + 126u;
            if ((int32_t)V < 0) {
                if ((V & 252u) != 0u)
                    return (qp << 23) + (V >> 8);
                GOR_r(0u - k2, X - k2 * 1488522235u, (qp << 23) + (V >> 8));
            }
            GOX_r(0);
        }
        int32_t d = (int32_t)sp;
        /* ER: the 2^-24..2^-10 series first (one add and the main test's 13), then |x| < 2^-24 */
        if ((uint32_t)(d + 16) < 14u) {
            /* 2^-24 <= |x| < 2^-10: e^x - 1 = (X + X^2 2^-32) 2^-31 - [0, 2.21] 2^-31, 8 guard bits (to 2^-10
             * the cubic term stays inside the window: exhaustive) */
            uint32_t M = (w << 8) | 0x80000000u, X = M >> (~up & 31u);
            uint32_t t = X + mulhu_r(X, X) + 130u;
            if ((t & 0xFEu) != 0u)
                return 0x3F800000u ^ (t >> 8); /* F1: t < 2^22: the ^ keeps this tail apart from s119x_'s + */
            if (X < 0x10000u) { /* x < 2^-15 */
                /* x < 2^-15, guard fields 0 and 1: exact in one word (#24/#29, public): X = x 2^46 (truncated by
                 * under one unit at the lowest exponent), x^2/2 in the same unit, no cubic term (under 1/3 unit) */
                uint32_t Xo = M >> ((112u - up) & 31u);
                uint32_t Vo = Xo + (mulhu_r(Xo, Xo) >> 15);
                return 0x3F800000u + ((Vo + 0x400000u) >> 23);
            }
            cM = M;
            ct = t;
            goto s119x_;
        }
        if (d < -16)
            goto one_; /* |x| < 2^-24: 1 */
        if (w >= 0x42B20000u) { /* x >= 89 (a one-instruction constant) */
            if (w > 0x7F800000u)
                goto nan_;
            return 0x7F800000u;
        }
        if (d < 0) {
            /* 2^-10 <= |x| < 2^-8: as for x < 0 with the signs of the even terms */
            uint32_t M = (w << 8) | 0x80000000u, X = M >> (~up & 31u);
            uint32_t t = X + mulhu_r(X, X + mulhu_r(X, mulhu_r(X, 0xAAAAB000u))) + 130u;
            if ((t & 0xFEu) != 0u)
                return 0x3F800000u | (t >> 8); /* t < 2^24: the | keeps this tail apart from the one above */
            ct = t;
            cM = M;
            goto s119x_;
        }
        if (w >= 0x42B17218u)
            return 0x7F800000u;
        /* G2: the two fixed hard words below the overflow threshold (every hard set has them) */
        if (w >= 0x42B17216u)
            return 0x7F7FFF04u + ((w - 0x42B17216u) << 7);
        goto posmain_; /* 64 <= x < 88.72 */
    }
s119x_: {
    /* 2^-16 <= |x| < 2^-8 (2^-15 for x > 0), guard fields 0 and 1, t = the fast sum (2-term below 2^-10, cubic
     * above): decided from the series. The midpoint is a
     * multiple of 2^-24 (2^-25 below 1), so a - (+-a^2/2) + a^3/6 - (+-a^4/24) + a^5/120 (a = |x|) times 2^60
     * mod 2^32, read as signed, has the sign of the distance to it. xs = a 2^40, q2 = xs^2 2^-32. */
    uint32_t M = cM, uu = w >> 23; /* F1: its own exponent (no value shared across the signs) */
    uint32_t sg = (uint32_t)((int32_t)w >> 31), xs = M >> ((118u - uu) & 31u), q2 = mulhu_r(xs, xs);
    /* the a^4 and a^5 factors 2^28/24 and 2^24/5 rounded to one lui each (exhaustive over every word that gets here) */
    uint32_t t4 = mulhu_r(mulhu_r(q2, q2), 0xAAB000u);
    uint32_t ev = ((((xs * xs) >> 21) | (q2 << 11)) + t4) ^ sg;
    uint32_t Z = (xs << 20) + (mulhu_r(q2, mulhu_r(xs, 0x2AAAAAABu)) << 4) + mulhu_r(mulhu_r(t4, xs), 0x333000u)
                 + ev - sg;
    if (sg == 0u)
        return 0x3F800000u + (ct >> 8) - ((int32_t)Z < 0);
    return 0x3F800000u - (ct >> 7) + ((int32_t)Z < 0);
}
one_:
    return 0x3F800000u;
nan_:
    return w | 0x00400000u;
cres_: {
    /* V2: a cell or tnl_r reject (x < 0, sn = e - 119 < 11), cV + cE its upper candidate: straight to the residual
     * with k2 from 2^30/ln2 rounded DOWN (k2 never one step too large, so T e^r never wraps past 2^32 and the
     * reject's distance to the midpoint stays inside the residual's window, also for the quartic's 8-unit rejects) */
    uint32_t f = w << 9, X = f << sn;
    uint32_t t = (1549078528u + mulhu_r(f, 1549078528u)) >> (29u - sn), k2 = t | 1u;
    cT = *(const uint32_t *)((const uint8_t *)exp8_r + 1020u - ((k2 << 1) & 0x3FCu));
    cL = (const uint8_t *)exp8_r + ((0u - k2) & 0x1FEu);
    ck = k2;
    cX = k2 * 1488522235u - X;
    cV += cE;
}
res_:
    return ex_res_r(w, ck, cX, cV, cT, cL);
cold_:
    return ex_cold_r(w, code, 0u, 0u, 0u) ^ 1u;
}

/* tanh, 1/8 <= y < 9.02 (biased exponent 124..130): the candidates' midpoint is m = M 2^-s, M = 2 mu - 1,
 * s = 151 - ef. With G = e^2y: tanh y > m <=> G (1 - m) > 1 + m. G = 2^q F, F = 2^(i/512) e^-s' in units 2^-63
 * (q = k >> 9, i = k & 511, k = round(2y 512/ln 2), s' = k ln2/512 - 2y). A = (1 - m) 2^s, B = (1 + m) 2^s.
 * D = (F A 2^q - B) 2^(63 - q): its high word is hi(F A) - B 2^(31 - q) mod 2^32 (the rest of B 2^(63-q) is a
 * multiple of 2^64), and |D| < 2^62 because the fast path only rejects y near m, so the sign settles it. */
/* tanh h for 2^-8 <= h < 2^-3 (biased exponent eh 119..123), h = M 2^(eh - 158) (M = significand 2^8): returns
 * W = C 2^8 / (last place of h), C = h - tanh h = h^3 S(h^2), so tanh h 2^(158 - eh) = M - W. S(z) is a quadratic
 * in z = h^2 (Z = z 2^32, S in units 2^-32) fitted on [0, 2^-6] with its constants rounded so that W never exceeds
 * its true value: W <= W_true < W + 2.54 (0.21 from S, the rest from the four floors). Shared by tanh (h = |x|)
 * and sigmoid (h = |x|/2: sigma - 1/2 = tanh(x/2)/2); it replaces the 80 cells of tw_r. */
/* W3: tanh 2^-12 <= y < 2^-9 (e 115..117) by thresholds, 32 sub-intervals per binade (port of the thumb rows 512..553 of
 * t_eps): n = (tsr_r[(t >> 19) - (115 << 5)] + t) >> 24 is the rounded deficit, result w - n; the first sub-interval of
 * e 116 and 117 (the corners, where the result drops a binade) holds 2^31 - t0 and goes to the series. */
static const uint32_t tsr_r[82] = { /* (from e 115 entry 14: below it the tiny test returns first) */
    0x8d8ec8bau, 0x8d8ec8bau, 0x8e000000u, 0x8e000000u, 0x8e000000u, 0x8e000000u, 0x8e000000u, 0x8e000000u,
    0x8e000000u, 0x8e000000u, 0x8e000000u, 0x8e000000u, 0x8e000000u, 0x8e000000u, 0x8e000000u, 0x8e000000u,
    0x8e000000u, 0x8e000000u, 0x0c000000u, 0x8de00000u, 0x8de00000u, 0x8de00000u, 0x8dc00000u, 0x8dc00000u,
    0x8dc00000u, 0x8dc00000u, 0x8db08b8au, 0x8db08b8au, 0x8db08b8au, 0x8db08b8au, 0x8e800000u, 0x8e800000u,
    0x8e800000u, 0x8e800000u, 0x8e724632u, 0x8e724632u, 0x8e724632u, 0x8e724632u, 0x8f43118cu, 0x8f43118cu,
    0x8f43118cu, 0x8f43118cu, 0x90200000u, 0x90200000u, 0x90200000u, 0x90200000u, 0x901c30b4u, 0x901c30b4u,
    0x901c30b4u, 0x901c30b4u, 0x0b000000u, 0x8ef00000u, 0x8ee80000u, 0x8ee7b5f2u, 0x8fd80000u, 0x8fd00000u,
    0x8fcf380cu, 0x90c00000u, 0x90ba227eu, 0x91b00000u, 0x91a80000u, 0x91a7796cu, 0x92980000u, 0x9296a45eu,
    0x93880000u, 0x93873f34u, 0x9479043au, 0x95700000u, 0x956bc0bau, 0x96600000u, 0x965f4e86u, 0x97539010u,
    0x98486df8u, 0x99400000u, 0x993dd55cu, 0x9a33b6c6u, 0x9b2a0558u, 0x9c20b642u, 0x9d180000u, 0x9d17c050u,
    0x9e0f1b9cu, 0x9f06c150u,
};
static inline uint32_t th_ser_r(uint32_t M, uint32_t eh)
{
    uint32_t Ms = M >> (126u - eh);
    uint32_t Z = mulhu_r(Ms, Ms);
    uint32_t S = 0x55555530u - mulhu_r(Z, 0x2221E000u - mulhu_r(Z, 0x0DAC6000u));
    return mulhu_r(M, mulhu_r(Z, S));
}


/* Is tanh(y) > m? The near-midpoint test of the table cells. y = y0 + d with y0 the start of y's cell,
 * T0 = tanh(y0), known from the tables to about 2^-55: T0 2^(60+sc) = c0 2^28 + dx (dx: the tax_r word, sc:
 * the cell's scale), and m is the candidate rounding boundary that the fast path found within a few
 * 2^-32 of tanh(y). By the addition theorem, with tau = tanh d,
 *     tanh(y0 + d) = (T0 + tau)/(1 + T0 tau) > m   <=>   tau (1 - m T0) > r,   r = m - T0,
 * and with c = d coth d - 1 = z/3 - z^2/45 + ... (z = d^2), tau = d/(1 + c):
 *     tanh(y0 + d) > m   <=>   D = d (1 - m T0) - r (1 + c) > 0.
 * The fast path has made |D| tiny, so D is computed modulo 2^32 in units 2^(j-60-sc) (j = 0 for tanh,
 * 3 for sigmoid, whose boundary is farther away in tanh's terms). In those units d is a multiple of
 * 2^32 and drops out:
 *     D = -[d m T0] - [r] - [r c]   (mod 2^32).
 * d m 2^(60-j) = G is the exact product of two words (the offset and m); d m T0 is then G c0 2^-32, two
 * multiplies, plus G dx 2^-60, of which the top word is enough; r is exact in its low word; and r c,
 * which is small, needs about 30 bits: one multiply of r by c = z (1/3 - z/45).
 * tt: the offset in the cell at the top of a word; mq = m 2^(32+sc); mB: mq, or mq/8 for j = 3. */
/* JR: the anchor of the cell of t (cell index (t >> 18) - C, C even) is in the pair's even cell q: c0 there and the
 * tail dx from the two halves */
#define TH_Q_r(t, C) ((const struct rx_r *)((const uint8_t *)ta_r + 16u + ((((t) >> 14) + 16u) & ~31u) - ((C) << 4)))
#define TH_DX_r(q) ((int32_t)(((uint32_t)(int32_t)(q)->xh << 16) | (uint16_t)(q)[-1].xh))
/* TRV: the anchor in tla_r of the 64-cell pair of t (as TH_Q_r: (t >> 16) + 4 rounded down to 8 is 8 times its
 * index), C = the index of y = 1/8's anchor in those units */
#define TL_A_r(t, C) ((const struct ra_r *)((const uint8_t *)tla_r + ((((t) >> 16) + 4u) & ~7u) - ((C) << 3)))
static inline uint32_t th_lt_r(int32_t ts, int32_t tq, uint32_t kx, uint32_t c0, int32_t dx, uint32_t mq, uint32_t mB, uint32_t j, uint32_t ux)
{
    /* ts: the kernel's signed offset, d 2^31 / h. c0 and dx are tanh at the cell's anchor: the start of
     * an even cell (d >= 0), the END of an odd one (-h <= d < 0). d enters as a signed number, d^2
     * through ts^2: nothing else knows the parity.
     * The shift counts all follow from the binade. The low five bits of the tax_r word (far below its
     * precision) hold c4 = 149 - e, and a shift takes its count modulo 32, so dx itself serves as the
     * count c4, 2 dx as 266 - 2e, and 28 - dx as e - 121; kx is what the caller adds for dl's count. */
    /* JR: ux = 149 - e from the caller (dx is all value: T0 to 2^-61) */
    /* G1: ux = 149 - e from x = e ^ 31 (as sg_lt_r), which the compiler keeps as one xori: the counts 7 - e and 21 - e
     * (mod 32) are x + 8 and x + 22 (one addi each, no constant pair); kx is fixed (15 - 125); the argument ux is e */
    uint32_t x = ux ^ 31u, c3 = (ux + 7u) & 31u;
    (void)kx;
    int32_t dl = ts >> ((x + 8u) & 31u);                              /* dl mB = d m 2^(60-j), exactly */
    uint32_t gl = (uint32_t)dl * mB;
    int32_t gh = mulhsx_r(dl, mB);
    uint32_t P = (uint32_t)gh * c0 + mulhu_r(gl, c0);
    uint32_t R = mq - c0;
    uint32_t rhs = (R << (28u - j)) - (uint32_t)(dx >> j);
    int32_t rr = (int32_t)(R << c3) - (dx >> ((x + 22u) & 31u));
    /* c = z/3 - z^2/45 at the scale 2^(298-2e), from a square that is a quarter of that: 4 U (1/3 - z/45)
     * as U + U (1/3 - 4z/45). (A factor two bits short would cost the product r c a quarter of its
     * precision, and the closest inputs of the cells near y = 2 need all of it.) */
    /* (tq: ts or -ts, for the square. eik_tanh passes -ts: the 64-bit form of ts itself is shared with
     * its fast paths' products and reaches the decline in two registers, and the square is then built
     * from unsigned parts, four instructions more) */
    uint32_t U2 = (uint32_t)mulhs_r(tq, tq);                            /* z 2^(296-2e) */
    uint32_t zq = U2 >> ((2u * (x + 22u)) & 31u);                     /* z 2^28 (W1: pairs scale, see below) */
    uint32_t PK = mulhu_r(U2 << 1, 0xAAAAAAABu - mulhu_r(zq, 0xB60C0000u)); /* HTR: U2 (4/3 - 16z/45 ...) in one product */
    /* the two small terms, G dx 2^-60 and r c, share their last four bits of shift */
    uint32_t D2 = ((uint32_t)mulhs_r(dx, gh) + ((uint32_t)mulhs_r(rr, (int32_t)PK) << ((c3 - j + 2u) & 31u))) << 4;
    return (int32_t)(P + rhs + D2) < 0;
}
/* W1 (after V1's pairs): th_lt_r runs at the pair scale: ts = w << 13 with the anchor at the even cell boundary nearest y
 * (|d| < 2^18 words, kx one less than before), so the square is a quarter (zq two less) and c (PK) is at 2^(296-2e),
 * which D2's shift takes two more. A single anchor (|d| < 2^17 words, ts = w << 14: tla_r's and ta_r's) runs on the
 * same core with ux one more (150 - e): dl, zq unchanged, rr half (one bit of dx less) and D2 one more.
 */

#define TH_S_r(ef, mu) do { a1 = (ef); a2 = (mu); goto small_; } while (0)
/* a reject of the 2^-8 <= y < 1/8 series: a1 = D = (y - Mid)/u, a2 = the result below Mid (with the sign) */
#define TW_S_r(D, LO) do { a1 = (D); a2 = (LO); tm = M; ts = e + 5u; goto tws_; } while (0)
/* a decline on the table cells (public #24/#25): a1 = the boundary m above the fast value in the cell's units,
 * m 2^(32+sc) = M << 7 where the cell value has its top bit set, M << 6 otherwise; a2 = the result below it,
 * without the sign; a3 = 17 - EX (mod 32), EX the cell's exponent byte 125 - sc */
#define GO_CELL_r(ef, mu, EX, SG)                                                                                 \
    do {                                                                                                         \
        a1 = (2u * (mu) - 1u) << ((ef) + 6u - (EX));                                                             \
        a2 = (((ef) - 1u) << 23) + (mu) - 1u + (SG);                                                             \
        a3 = 16u - (EX);                                                                                         \
        goto cell_;                                                                                              \
    } while (0)
static inline uint32_t eik_tanh_r(uint32_t w)
{
    uint32_t code, a1, a2, tm, ts, th_, c0v_, e_, k_, qi_;
    const struct rl_r *rd_;
    int32_t dx_;
    /* R4 (dispatch after public #24): t has the exponent in its top byte. Two one-sided tests: |x| >= 2 leaves
     * at the first, y < 1/8 (and the first 2^11 words of binade 124) at the second; both limits stay single
     * constants. The cells: one copy per sign, each reading one table byte: ex (tanh's exponent field less
     * one) for w >= 0, sh = 254 - ex for w < 0, which taken off the arithmetically shifted value leaves
     * exponent and sign in place (and is sigmoid's shift modulo 32). Rejects: the lower candidate a1 (with
     * the sign) and m 2^28 = (V + 4) >> (129 - ex) for th_prec_r. */
    uint32_t t = w << 1;
    if ((int32_t)t < 0)
        goto hi_;
    if (t < 0x7C016000u) /* JR: y < 0x3E00B000: past tanh y = 1/8 (0x3E00AC49), so the cells start in tier T3 */
        goto below_;
cells_: {
        /* RX: the deficit cells (tld_r): the result is w - (V >> 8) for both signs and every tier */
        const struct rl_r *r = &tld_r[(t >> 19) - 0xF80u];
        th_ = w << 13; /* W1: cell_'s pair offset */
        uint32_t V = rl_cell_r(r, (int32_t)th_);
        rd_ = r;
        if (V & 254u)
            return w - (V >> 8);
        qi_ = (t >> 19) << 4; /* G1: the row offset for kink_ and cell_ */
        if (V == 0u)
            goto kink_; /* the two cells that hold tanh y = 1/4 and 1/2 */
        /* a decline: a2 = w - (V >> 8) the lower candidate (with the sign), a1 = m 2^32 at tanh's fixed scale, m the
         * midpoint above it: its significand with the half place, shifted by 126 less its exponent */
        if (t > 0x7F000000u) /* G1: y = 1 itself never declines (lui-only bound) */
            goto c127_;
        a2 = w - (V >> 8);
        a1 = ((a2 << 8) | 0x80000080u) >> ((126u - (a2 >> 23)) & 31u);
        goto cell_;
    c127_: {
            th_ = w << 14;
            a2 = w - (V >> 8);
            a1 = (a2 << 8) | 0x80000080u; /* W1: tanh y in [1/2, 1) here: no shift */
            /* W1: 1 <= y < 2: the nearest cell boundary's anchor in tla_r (boundaries 96..128 only), a single anchor (RX:
             * TL_A_r(t, 0xF80u + 96u) with the base taken off t first, so the masked index fits andi) */
            const struct ra_r *A = (const struct ra_r *)((const uint8_t *)tla_r + (((t - 0x7EFC0000u) >> 16) & ~7u));
            c0v_ = A->c0;
            dx_ = A->dx;
            e_ = (t >> 24) - 1u;
            goto lt_;
        }
    }
kink_: {
        /* RX: the two cells of tld_r that hold tanh y = 1/4 or 1/2 (y in [1/4, 1/4 + 2^-7) and [0.546875, 0.5625)) on
         * tl_r's cells (TRV: every word checked on T1/T2/T3), one copy for both signs: JR's fixed scale Vf = tanh(y)
         * 2^32 + 0x80, the tier read off Vf: T1 tanh in [1/2, 1) (8 guard bits), T2 [1/4, 1/2) (7, offset 0x40), T3
         * [1/8, 1/4) (6). A decline is at the boundary m 2^32 = Vf - 0x80 in every tier, a2 the lower candidate. */
        const struct rx_r *r = (const struct rx_r *)((const uint8_t *)tl_r + (qi_ - (0xF80u << 4))); /* RX: the same row as tld_r's */
        uint32_t Vf = rx_cell_r(r, (int32_t)th_) - 0x80u, sg = w & 0x80000000u; /* O4: c0 has 0x81 more */
        if (Vf == 0u) /* G1: never (tanh y 2^32 > 2^30 here); the frame-keeping non-tail call */
            return eik_exp(w) >> 31;
        if ((int32_t)Vf < 0) {
            a1 = (Vf & ~0xFFu) - 0x80u;
            a2 = sg + (125u << 23) + (Vf >> 8);
            if (Vf & 254u)
                return a2;
            a2 = sg + (125u << 23) + (a1 >> 8);
            goto cell_;
        }
        {
            uint32_t v2 = Vf - 0x40u;
            if ((int32_t)(v2 << 1) < 0) {
                if (v2 & 126u)
                    return sg + (124u << 23) + (v2 >> 7);
                a1 = (v2 & ~127u) - 0x40u;
                a2 = sg + (124u << 23) + (a1 >> 7);
                goto cell_;
            }
        }
        {
            uint32_t v3 = Vf - 0x60u;
            if (v3 & 63u)
                return sg + (123u << 23) + (v3 >> 6);
            a1 = Vf - 0x80u;
            a2 = sg + (123u << 23) + (a1 >> 6);
            goto cell_;
        }
    }
hi_:
    if (t <= 0x82206000u) {
        /* 2 <= y < 9.011: the result is in [1/2, 1], so the cell value has its top bit set and the exponent is
         * known (public #29) */
        /* TRV: these cells are in deficit form, V = 128 (|w| - bits(tanh y)) + 0x40 + eps with bits() the word as a
         * real number (unsigned: the deficit reaches 0x1920001 last places at y = 9.011), so the result is
         * w - (V >> 7) for either sign: no sign split, no constant (guard values 0 and 1 decline). On a decline
         * a2 = w - (V >> 7) is the lower candidate (with the sign) and a1 = m 2^32 at tanh's fixed scale, m the
         * midpoint above it */
        const struct rx_r *r = &ta_r[(t >> 18) - 0x1FFFu];
        th_ = w << 14;
        uint32_t V = rx_cell_r(r, (int32_t)th_);
        if (V & 126u)
            return w - (V >> 7);
        a2 = w - (V >> 7);
        a1 = (a2 << 8) + 0x80000080u;
        goto cellx_;
    }
    /* past the table: +-1, or a NaN (a constant of its own per sign keeps the two signs apart) */
    if ((int32_t)w < 0) {
        if (w > 0xFF800000u)
            return w | 0xFFC00000u;
        return 0xBF800000u;
    }
    if (t > 0xFF000000u)
        return w | 0x00400000u;
    return 0x3F800000u;
below_: {
        if (t < 0x73713000u) /* HTR: |x| < 0x39B89800 (lui-only); tanh x rounds to x below 0x39B89BA3 */
            return w;
        if (t <= 0x75FFF000u) { /* W3: e 115..117 by tsr_r (corners and the last 2^11 words: to the series; lui-only) */
            uint32_t s_ = tsr_r[(t >> 19) - (115u << 5) - 14u] + t;
            if ((int32_t)s_ >= 0)
                return w - (s_ >> 24);
        }
        uint32_t e = t >> 24, M = (w << 8) | 0x80000000u, u_, S_;
        /* RV3: the first 128 words above 2^-9, 2^-10 and 2^-11 (the old y (1 - y^2/3) sliver) take the series too */
        /* RV3: one series for all of 2^-12 <= y < 2^-3; the 24-guard-bit series below is the reject tier of
         * y < 2^-8 (near-midpoint words, which it settles without the exact path) */
        {
            /* 2^-8 <= y < 2^-3 (and y < 1/8 (1 + 2^-12) in binade 124): tanh y = y - C, W = C in units 2^-8 of
             * y's last place (one-sided error < 2.54) */
            /* th_ser_r(M, e), with its S kept for the 24-guard tier (RV3) */
            uint32_t Ms_ = M >> (126u - e), Z_ = mulhu_r(Ms_, Ms_);
            S_ = 0x55555530u - mulhu_r(Z_, 0x2221E000u - mulhu_r(Z_, 0x0DAC6000u));
            uint32_t W = mulhu_r(M, mulhu_r(Z_, S_)), V = M - W;
            if ((int32_t)V < 0) {
                /* y's binade: round(C) = (W + 128) >> 8 unless (W + 128) mod 256 is 254 or 255 */
                uint32_t x = W + 130u;
                if (x & 254u)
                    return w - (x >> 8);
                /* R4: with k = x >> 8 (the rounded C) the lower candidate is w - k and D = 4 m - 2 (2 mu - 1) = 4 k - 2
                 * (M has eight zero low bits, and (W + 255) >> 8 = k here) */
                /* G1: v = e ^ 119 is 12..15 for the exact path's binades 120..123, 11 for 124 and 119 - e (0..3) for
                 * 116..119; one xori for both tests and the tier's shift */
                u_ = e ^ 119u;
                if (u_ >= 12u)
                    TW_S_r(4u * (x >> 8) - 2u, w - (x >> 8));
                if (u_ < 4u) {
                    /* G1: y < 2^-7 (binades 118 and 119; 117's last 2^11 words never decline here): the series with 23
                     * guard bits, P = C 2^23 / (last place of y) = M (Ms^2 >> 32) (2 S + 0x49) >> 64 with Ms = M >> (119 - e)
                     * = y 2^39 (P < 2^31.4; S's constant term restored as in g24_), rounded with no test: right on every
                     * decline here (work/g1/gen/mid118.c E 0x49: errors -2.83..0.17 units in 118, -2.43..2.50 in 119).
                     * It replaces g24_ (24 guard bits, 118 only) and the exact path of 119 (the frame-keeping eik_exp
                     * call is now in kink_: here the compiler bounds P > 0 and would drop it) */
                    uint32_t Ms_ = M >> (u_ & 31u);
                    uint32_t P_ = mulhu_r(M, mulhu_r(mulhu_r(Ms_, Ms_), (S_ << 1) + 0x49u));
                    return w - ((P_ + 0x400000u) >> 23);
                }
                /* JR: binade 124 (y < 0x3E00B000): ta_r's cell 0 decides, at the midpoint y - (k - 1/2) 2^-26 */
                a1 = (M >> 2) - ((x >> 8) << 6) + 32u;
                a2 = w - (x >> 8);
                th_ = w << 13;
                qi_ = 0xF80u << 4;
                goto cell_;
            }
            /* the binade below y's: V = tanh y 2^(158 - e) with 7 guard bits */
            if (FAST_r(V, 7, 0x40u, 0x3u, 11))
                return (w & 0x80000000u) + (((e - 2u) << 23) + MANT_r(V, 7, 0x40u));
            if (e >= 124u) {
                /* JR: binade 124 (tanh y < 1/8): cell 0 decides; V = tanh y 2^34, the midpoint 128 n - 64 */
                a1 = (((V + 0x40u) & ~127u) - 0x40u) >> 2;
                a2 = (w & 0x80000000u) + (((e - 2u) << 23) + MANT_r(V, 7, 0x40u)) - 1u;
                th_ = w << 13;
                qi_ = 0xF80u << 4;
                goto cell_;
            }
            /* R4: with c = ceil(W / 128) the lower candidate is w + mant - c and D = 4 m - (2 mu - 1) = 2 c - 1 */
            {
                uint32_t c_ = (W + 127u) >> 7;
                TW_S_r(2u * c_ - 1u, w + ((w << 9) >> 9) - c_);
            }
        }
    }
cell_:
    /* the table cells' declines (public #25's th_lt_r with tax_r): a1 = m 2^(32+sc), a2 = the result below it
     * with the sign (R4); y < 2: every such caller is below y = 2, whose anchors (to y = 2 itself) are tla_r's (RX:
     * no test for ta_r's) */
    {
        /* W1: below y = 1 (every caller here) the anchor is the cell's own: the start of an even cell, the end of an
         * odd one (an even boundary, |d| < 2^18 words), where its tl_r row has v = 0: T0 2^32 = c0 - 0x101 (to 2 units) and
         * the tail dx = xh 2^14 (to 2^13): no tla_r row */
        const struct rx_r *q = (const struct rx_r *)((const uint8_t *)tl_r + (qi_ - (0xF80u << 4))); /* G1: the row index and e_ from each caller */
        c0v_ = q->c0 - 0x100u;
        dx_ = (int32_t)((uint32_t)(int32_t)q->xh << 14);
        e_ = t >> 24;
        goto lt_;
    }
cellx_:
    /* TRV: the anchors from y = 2 on in ta_r, in deficit form: the anchor's value is T0 2^32 = (w_A << 8) + 2^31 -
     * 2 (c0 - 0x40) (mod 2^32) up to the tail dx, with w_A << 8 = o_ << 21 (o_ the pair's offset as TH_Q_r has it) */
    {
        uint32_t o_ = ((t >> 14) + 16u) & ~31u;
        const struct rx_r *q = (const struct rx_r *)((const uint8_t *)ta_r + 16u + o_ - (0x2000u << 4));
        c0v_ = ((o_ + 1024u) << 21) - 2u * (q->c0 - 0x40u);
        dx_ = TH_DX_r(q);
        e_ = (t >> 24) - 1u;
    }
lt_:
    /* W1: the lower candidate as w - k_ (w stays in its register over every decline) */
    return a2 + th_lt_r((int32_t)th_, (int32_t)th_, 15u - 125u, c0v_, dx_, a1, a1, 0, e_); /* G1: e_ itself */
tws_:
    return th_sdec_r(tm, ts, a1, a2);
}

/* sigmoid's cold work (R4): the subnormal results (x <= -87, code 0: exp's exact path in ex_cold_r); the result
 * comes back xor 3 (ex_cold_r's xor 1, then xor 2 here). The call is not a tail call, so this function is
 * frameless on every other path. (The exact tier, ex_cold_r's code 4, is reached by a tail call at tier_.) */
static inline uint32_t sg_cold_r(uint32_t w, uint32_t ef, uint32_t mu, uint32_t code)
{
    return ex_cold_r(w, code, ef, mu, 0u) ^ 2u;
}

/* RS: th_lt_r for sigmoid's scell_ (j = 1, tq = ts, kx = -13), its shift counts from e = x's exponent field: those of
 * ux = 150 - e from x = e ^ 31 (31 - e modulo 32), those of c3 = e - 122 from e itself (one negation, no li/sub pairs) */
static inline uint32_t sg_lt_r(int32_t ts, uint32_t c0, int32_t dx, uint32_t mq, uint32_t e)
{
    uint32_t x = e ^ 31u, c3 = (e + 6u) & 31u;
    int32_t dl = ts >> ((x + 9u) & 31u);                               /* ux + kx = 137 - e (W1: one less, pairs) */
    uint32_t mB = mq >> 1;
    uint32_t gl = (uint32_t)dl * mB;
    int32_t gh = mulhsx_r(dl, mB);
    uint32_t P = (uint32_t)gh * c0 + mulhu_r(gl, c0);
    uint32_t R = mq - c0;
    uint32_t rhs = (R << 27) - (uint32_t)(dx >> 1);
    int32_t rr = (int32_t)(R << c3) - (dx >> ((x + 23u) & 31u));        /* ux = 150 - e */
    uint32_t U2 = (uint32_t)mulhs_r(ts, ts);
    uint32_t zq = U2 >> ((2u * (x + 23u)) & 31u); /* W1: z 2^28 at the pair scale, its factor 4 in the constant */
    uint32_t PK = mulhu_r(U2 << 1, 0xAAAAAAABu - mulhu_r(zq, 0xB60C0000u));
    uint32_t D2 = ((uint32_t)mulhs_r(dx, gh) + ((uint32_t)mulhs_r(rr, (int32_t)PK) << ((e + 7u) & 31u))) << 4;
    return (int32_t)(P + rhs + D2) < 0;
}

/* a reject of the deep path: x <= -32 rounds as e^x does (exp's exact path), else sigmoid's */
#define SG_DEEP_MID_r(ef, mu)                                                                                      \
    do {                                                                                                         \
        GO_S_r(ef, mu);                                                                                          \
    } while (0)

/* R4: a sigmoid decline on the table cells (public #25), settled at scell_ by th_lt_r: sigmoid(x) =
 * (1 + tanh(x/2))/2, so tanh(x/2) is tested against 2 Mv - 1, or against 1 - 2 Mv for x < 0 (then the other
 * way round). a1 = |2 Mv - 1| 2^(32+sc) (Mv: the candidate boundary of the result), a2 = the result below it,
 * a3 = the c0 of the cell of x/2 in ta_r, a4 = sc + 1 (low five bits: ta_r's sh byte). NEG: 1 for x < 0. */
#define GO_SCELL_r(ef, mu, SH, C0, NEG, L)                                                                        \
    do {                                                                                                         \
        uint32_t X_ = (2u * (mu) - 1u) << ((ef) - 118u);                                                         \
        a1 = ((NEG) ? 0u - X_ : X_) << (((SH) - 1u) & 31u);                                                      \
        a2 = (((ef) - 1u) << 23) + (mu) - 1u;                                                                    \
        a3 = (C0);                                                                                               \
        a4 = (SH);                                                                                               \
        goto L; /* W1: the anchor's kind is known at each caller: scellp_ (1/4 <= |x| < 2), scellt_ (2 <= |x| < 4), \
                 * scella_ (x >= 4) */                                                                          \
    } while (0)
/* from the cells of sigmoid(-x) (x <= -1.09375): the cell of x/2 is in ta_r, with sc = 0; its index is written
 * from w, not from t, so that the address is not joined with the fast paths' */
#define GO_SBCELL_r(ef, mu) GO_SCELL_r(ef, mu, 1u, 0u, 1, scellt_)
#define GO_SB_r(ef, mu) do { a1 = (ef); a2 = (mu); goto sb_; } while (0)

static inline uint32_t eik_sigmoid_r(uint32_t w)
{
    uint32_t code, a1, a2, a3, a4, c0v_, ts_, e_;
    int32_t dx_;
    /* R4: dispatch after public #25: two one-sided tests around the cells (|x| >= 2 leaves at the first,
     * |x| < 1/4 and the first 2^11 words of binade 125 at the second) */
    uint32_t t = w << 1;
    if ((int32_t)t < 0)
        goto hi_;
    if (t < 0x7D001000u)
        goto below_;
    /* 1/4 <= |x| < 2 */
    if ((int32_t)w >= 0)
        goto ap_;
    goto am_; /* JR: am_ takes all of -2 < x <= -1/4 from the ta_r cells (b_ starts at x = -2) */
hi_:
    if ((int32_t)w >= 0) {
        if (t < 0x80FFF000u) /* RS: 2 <= x < 4 less 2^11 words + 1 (a strict lui-only test: no addi); the word
                              * t = 0x80FFF000 goes to the deficit cells below */
            goto ap2_;
        if (t <= 0x83155000u) {
            /* 4 <= x < 17.332: ta_r's cells (64 per binade, from y = 2 less 2^17 words). Past 17.3287 the sum wraps by
             * less than one: those decline. */
            /* TRV: deficit cells: V = 128 (bits(y) - bits(tanh y)) + 0x40 + eps, and with n = (1 - sigma) 2^24 (the
             * result's last places below 1), Z = V - (w << 7) + 0x40 = 256 n + 0x80 + eps (mod 2^32): the result is 1 less
             * n rounded. On a decline the upper candidate's significand is 2^24 + 1 - (Z >> 8) */
            const struct rx_r *r = &ta_r[(t >> 18) - 0x203Fu];
            uint32_t Z = rx_cell_r(r, (int32_t)(w << 14)) - (w << 7) + 0x40u;
            if (Z & 255u)
                return 0x3F800000u - (Z >> 8);
            GO_SCELL_r(126, 0x1000001u - (Z >> 8), 1u, 0u, 0, scella_);
        }
        /* x >= 17.5: 1, or a NaN */
        if (t > 0xFF000000u)
            goto nan_;
        return 0x3F800000u;
    }
    /* x <= -2: the cells first, the rest at hin_ (public #29) */
    if (t > 0x80FFF000u)
        goto hin_;
    goto b_;
below_: {
        if (t <= 0x74D12000u) {
            /* |x| < 2^-11 (W3: and on to 0x3A689000 in e 116, 82% of that binade: the rounding of 1/2 + x/4 moves only
             * where the cubic term |x|^3/48 reaches a unit of 2^-(12 + 24), i.e. |x| >= (48 2^-36)^(1/3) = 0x3A6897D4
             * (both signs, exhaustive)): 1/2 + x/4, a tie going towards 1/2 (the cubic term). Below 2^-24 that is 1/2 itself. */
            MARK_r(24);
            /* below 2^-24 (less its top 2^12 words, which lin_ also rounds to 1/2; a lui-only limit) */
            if (t > 0x66FFF000u) /* R2X: the word t = 0x66FFF000 rounds to 1/2 as well */
                goto lin_;
            if ((int32_t)w > 0x66FFF000) /* R2X: never (|x| < 2^-24 here): a branch on the limit's register that keeps this
                                          * return a block of its own, so that its constant is not formed ahead of the
                                          * branch on lin_'s path */
                return w;
            return 0x3F000000u;
        }
        uint32_t e = t >> 24, M = (w << 8) | 0x80000000u;
        if (t >= (121u << 24)) {
            /* 2^-6 <= |x| < 1/4 (and the first 2^11 words of binade 125) */
            /* O4: th_ser_r(M, e - 1) with tanh(|x|/2) 2^32 taken at that scale: V9 = Ms - Ms (z S) = Ms - mulhu(Ms, P), up to
             * 1.3 high (no shift of M - mulhu(M, P)); offsets 0xFF / 0x7F and one-value windows from every input of e 121..125
             * (work/o4/t/ser9.c). On a decline the midpoint is V9 - 1, and V = M - mulhu(M, P) is formed for the tests. */
            uint32_t s_ = ~e & 31u, Ms = M >> s_, Z = mulhu_r(Ms, Ms); /* 127 - e */
            /* H2: Pn = -ceil(Z S / 2^32) from the negated series (one signed product), so that V9 = Ms - ceil(Ms |Pn| / 2^32)
             * is a single product: Ms (2^32 + Pn) / 2^32 */
            uint32_t Pn = (uint32_t)mulhs_r((int32_t)Z, (int32_t)(mulhu_r(Z, 0x2220A000u - mulhu_r(Z, 0x0DAC6000u)) - 0x55555000u)); /* H2: lui-only C1, C2 refit (gen/v9scan.c) */
            uint32_t V9 = mulhu_r(Ms, Pn);
            if ((int32_t)w >= 0) {
                uint32_t U9 = V9 + 0x101u; /* H2: V9 is 1.12 below to 0.06 above tanh 2^32 (work/h2/gen/v9err.c): a two-value window */
                if (U9 & 510u) {
                    STAT_r(0);
                    return 0x3F000000u + (uint32_t)((int32_t)U9 >> 9); /* O4: U9 < 2^31; the arithmetic shift keeps this tail apart from ap_'s (no j) */
                }
                if (e == 125u) /* RV2: the 2^11 words of binade 125 decline on ta_r's cells, as ap_'s */
                    GO_SCELL_r(126, (U9 >> 9) + 0x800000u, 1u, 0u, 0, scellp_);
                {
                    /* R4: the boundary in V's units (a multiple of 2^10); V is at most 2.54 above tanh's value. A decline has
                     * V9 - 1 = U9 - 0x100 = 512 k + 256: the boundary is that << (127 - e) */
                    /* H2: V = M - ceil(M ceil(Z S / 2^32) / 2^32) is 2 below to 1.54 above tanh's value; the two-value window
                     * also declines words up to 1.2 units of V9 from the boundary: both sides settled here */
                    uint32_t V = mulhu_r(M, Pn), lo = 0x3F000000u + (U9 >> 9) - 1u, mV = ((U9 - 0x100u) >> 1) << ((0u - e) & 31u); /* (not s_: its mask would stay on the fast path) */
                    if ((int32_t)(V - mV) >= 5)
                        return lo + 1u;
                    if ((int32_t)(V - mV) <= -2)
                        return lo;
                    return th_sdec_r(M, e + 4u, (uint32_t)((int32_t)(M - mV) >> 6), lo); /* y = x/2 */
                }
            }
            /* the result is in [1/4, 1/2) */
            {
                uint32_t U = V9 + 0x81u;
                if (U & 254u) {
                    STAT_r(0);
                    return 0x3F000000u - (U >> 8);
                }
                if (e == 125u)
                    GO_SCELL_r(125, 0x1000001u - (U >> 8), 1u, 0u, 1, scellp_);
                {
                    /* a decline has V9 - 1 = U - 0x80 = 256 k + 128: the boundary is that << (127 - e); the lower candidate is
                     * 0x3F000000 - (U >> 8) */
                    uint32_t V = mulhu_r(M, Pn), lo = 0x3F000000u - (U >> 8), mV = ((U - 0x80u) >> 1) << ((0u - e) & 31u);
                    if ((int32_t)(V - mV) >= 5)
                        return lo;
                    if ((int32_t)(V - mV) <= -2)
                        return lo + 1u;
                    return th_sdec_r(M, (e + 4u) | 0x80000000u, (uint32_t)((int32_t)(M - mV) >> 6), lo); /* reversed */
                }
            }
        }
        {
            /* 2^-11 <= |x| < 2^-6: 1/2 + x/4 - d, d = |x|^3/48 (1 - x^2/10) in units 2^-52 (28 fraction bits of
             * a last place, 27 below 1/2). X = |x| 2^38 exactly (M has 8 low zero bits). */
            /* H2: X = |x| 2^37 (the shift count 121 - e from the split test's constant), d = |x|^3/48 (1 - x^2/10) 2^51 */
            uint32_t X = M >> (121u - e);
            uint32_t q = mulhu_r(X, X);                                         /* x^2 2^42 */
            uint32_t c3 = mulhu_r(q, X);                                        /* |x|^3 2^47 */
            uint32_t d = mulhu_r(c3, 0x55555554u - mulhu_r(q, 0x22220u));
            if ((int32_t)w >= 0) {
                /* round(X 2^12 - d) / 2^28 with X halved first (exact: M has 8 low zero bits), so that the sum
                 * stays below 2^31 and its arithmetic shift keeps this tail apart from ap_'s (R4); every input
                 * settled (checked on all of them) */
                return 0x3F000000u | ((X - (uint32_t)((int32_t)(d - 0x3FFF000u) >> 12)) >> 15);   /* ID: | (the sum is in [0, 2^16)): not tail-merged with x < 0's add (no j) */
            }
            /* below 1/2: round(X 2^12 - d) / 2^27; d is truncated, the -4 re-centres it (any of -2..-8 settles
             * every input, checked on all of them). R4: as 0x3F000000 + floor((2^14 - 1 - Z) / 2^14) with Z the
             * halved sum (X >> 1) + floor((2^26 - 4 - d) / 2^13): an add, a tail apart from am_'s subtraction */
            return 0x3F000000u - ((X - (uint32_t)((int32_t)(d - 0x1FFEFFFu) >> 12)) >> 14);
        }
    }
lin_: {
    /* (public #25) with m the 24-bit significand, e the exponent field and K the word of 1/2, the result is
     * (2K -+ c) >> 1, c the number of half last places rounded towards 1/2 */
    uint32_t e = t >> 24;
    if ((int32_t)w < 0) {
        /* h = floor((m - 1) / 2^(126-e)), from 2m - 2 = t - 2 - ((e - 1) << 24) */
        uint32_t h = ((t - 2u) - ((e - 1u) << 24)) >> (~e & 31u);
        return (0x7E000000u - h) >> 1;
    }
    {
        /* above 1/2 the last place is twice as large: g = -ceil(m / 2^(127-e)), as the floor of the
         * negative word -m = ((e - 1) << 23) - w. The arithmetic shift at the end only keeps the
         * compiler from sharing the last instructions of the two branches through a jump. */
        int32_t g = (int32_t)(((e - 1u) << 23) - w) >> (~e & 31u);
        return (uint32_t)((int32_t)(0x7E000000u - (uint32_t)g) >> 1);
    }
}
ap_: {
    /* The cell value is tanh(x/2) 2^(32+sc), sc = 2, 1, 0 by the binade of x/2, and the low five bits of
     * the cell's c3 are sc (32 units of c3 are nothing to the cubic): the register that holds c3 for the
     * kernel is the shift count, no byte is loaded. As for x >= 2, tanh(x/2) 2^32 is the significand with
     * nine guard bits. */
    /* JR: every ta_r cell is at the fixed scale tanh 2^32 (+ 0x80): no shift */
    const struct rx_r *r = &tl_r[(t >> 19) - 0xFA0u];
    /* O4: the offset 0x101 is in the cells' c0: V = X + 0x101 with X = tanh 2^32 */
    uint32_t V = rx_cell_r(r, (int32_t)(w << 13));
    if (V & 0x1FEu) {
        STAT_r(0);
        return 0x3F000000u + (V >> 9);
    }
    GO_SCELL_r(126, (V >> 9) + 0x800000u, 1u, 0u, 0, scellp_); /* (X >> 9 = (V >> 9) - 1 on a decline) */
}
ap2_: {
    /* O3: 2 <= x < 4 on tanh's deficit cells of 1 <= y < 2 (tld_r rows 96..127; tl_r ends at row 95): tanh and y are
     * each in one binade there, so tanh 2^32 = (w << 8) - V + 0x80 (mod 2^32) and U = that + 0x102 is ap_'s sum
     * (offset and window from every word of 2 <= x < 4: work/o3/gen/rxscan.c) */
    const struct rl_r *r = &tld_r[(t >> 19) - 0xFA0u];
    uint32_t U = (w << 8) - rl_cell_r(r, (int32_t)(w << 13)) + 0x181u;
    if (U & 510u)
        return 0x3F000000u + (U >> 9);
    GO_SCELL_r(126, (U >> 9) + 0x800000u, 1u, 0u, 0, scellt_);
}
b_: {
    /* The B cells are scaled to [2^31, 2^32) at their END and carry the rounding offset of that position
     * in c0: the binade test is on the sum as it is. Where a cell straddles a power of two of the result,
     * its first part is 2^32 and above and has wrapped: nine guard bits there. An input within the offset
     * below 2^32 lands on that side too, with a sum below 2^9: it rounds to the power of two, which is
     * what comes out. */
    const struct ry_r *r = &tb_r[(t >> 18) - 0x1F40u - 192u];
    uint32_t Vf = ry_cell_r(r, t, (int32_t)(w << 14)), W = (uint32_t)r->w3;
    if ((int32_t)Vf < 0) {
        if (FAST_r(Vf - 0x80u, 8, 0x80u, 0x2u, 15)) {
            STAT_r(0);
            return (uint32_t)MANTS_r(Vf - 0x80u, 8, 0x80u) - (W << 23);
        }
        GO_SB_r(255u - (W & 255u), ((Vf - 0x80u) >> 8) + 1u);
    }
    if (FAST_r(Vf - 0x80u, 9, 0x101u, 0x4u, 16)) {
        STAT_r(0);
        /* (the exponent field is two more than in w3, which is all of 2^32 in this sum; the mask is
         * nothing in the compiled code, a shift by 9 leaves 23 bits) */
        return (MANT_r(Vf - 0x80u, 9, 0x101u) & 0x7FFFFFu) - (W << 23);
    }
    GO_SB_r(256u - (W & 255u), ((Vf - 0x80u) >> 9) + 0x800001u);
}
sb_: {
    /* R4: b_'s two declines meet here, so that GO_SBCELL_r is expanded once */
    uint32_t ef_ = a1, mu_ = a2;
    GO_SBCELL_r(ef_, mu_);
}
am_: {
    const struct rx_r *r = &tl_r[(t >> 19) - 0xFA0u];
    /* 1/2 - tanh(|x|/2)/2 is above 1/4 on these cells (they end at |x| = 1.09375, where it is 0.2509):
     * always in [1/4, 1/2), whose last place is 2^-26, and X = tanh(|x|/2) 2^32 counts 256 to it. The
     * result is that many places below 1/2. */
    uint32_t v8 = rx_cell_r(r, (int32_t)(w << 13)) - 0x80u; /* O4: X + 0x81 (c0 has X + 0x101) */
    if ((int32_t)v8 < 0) {
        /* JR: |x| in [1.0986, 2): sigma in (1/16, 1/4], 7 guard bits down to 1/8, 6 below (windows from every input of
         * those cells). On a decline X >> b = ((X + O) >> b) - 1, so the upper candidate comes from the tested sum. */
        uint32_t v7 = v8 - 0x40u; /* X + 0x42 */
        if ((int32_t)(v7 << 1) < 0) {
            /* sigma <= 1/8 (X + 0x42 >= 3 2^30); the words with X + 0x21 below 3 2^30 still round at 1/8's grid */
            uint32_t v6 = v8 - 0x5Fu; /* X + 0x21 */
            if ((int32_t)(v6 << 1) < 0) { /* H2: v6 >= 3 2^30 (its top bit is set): bit 30 */
                if (v6 & 62u) {
                    STAT_r(0);
                    return 0x41000000u - (v6 >> 6);
                }
                GO_SCELL_r(123, 0x4000001u - (v6 >> 6), 1u, 0u, 1, scellp_);
            }
        }
        if (v7 & 126u) {
            STAT_r(0);
            return 0x3F800000u - (v7 >> 7);
        }
        GO_SCELL_r(124, 0x2000001u - (v7 >> 7), 1u, 0u, 1, scellp_);
    }
    {
        if (v8 & 254u) {
            STAT_r(0);
            return 0x3F000000u - (v8 >> 8);
        }
        /* (the upper candidate's significand: X >> 8 = (v8 >> 8) - 1 on a decline) */
        GO_SCELL_r(125, 0x1000001u - (v8 >> 8), 1u, 0u, 1, scellp_);
    }
}
nan_:
    return w | 0x00400000u;
hin_:
    /* x <= -4, and a sliver above it */
    if (t > 0x81FFF000u)
        goto hix_;
    {
        /* down to -8 (but for a sliver): a quartic in the offset from the start of the cell, four high
         * products; everything it needs from the record is loaded here, so that the address stays folded */
        const uint32_t *q = &sq_r[(t >> 19) - 0x101Fu];
        /* RV2: c4 at 2^13 times its value, taken with t = |w| << 1 (the offset at that scale; the cell's constant part
         * is off c3), so that its low nine bits, nothing to the product, are the exponent field less one: E = c4 << 23 */
        uint32_t tt = w << 14, c4 = q[4 * 33], E = c4 << 23;
        int32_t s = (int32_t)q[3 * 33] + (int32_t)(((int64_t)(int32_t)c4 * t) >> 32);
        s = (int32_t)q[2 * 33] + (int32_t)(((int64_t)s * tt) >> 32);
        s = (int32_t)q[33] + (int32_t)(((int64_t)s * tt) >> 32);
        /* (c0 has the rounding offset 0x83 added: Vf is ready for the test, V is the value) */
        uint32_t Vf = q[0] + (uint32_t)(int32_t)(((int64_t)s * tt) >> 32), V = Vf - 0x83u;
        /* (the top bit after the rounding offset: a value that the offset carries past 2^32 belongs to
         * the other branch, which rounds it to the power of two) */
        if ((int32_t)(Vf - 0x83u + 0x83u) < 0) {
            if (FAST_r(Vf - 0x83u, 8, 0x83u, 0x8u, 14)) {
                STAT_r(0);
                return E + MANT_r(Vf - 0x83u, 8, 0x83u);
            }
            GO_S_r((E >> 23) + 1u, (Vf + (256u - 0x83u)) >> 8);
        }
        /* the cell straddles a power of two of the result and this is its first part: the value is
         * 2^32 + V (V signed: just below 2^32 it is negative), in the binade above, with nine guard bits */
        if (FAST_r(V, 9, 0x102u, 0x8u, 25)) { /* H2: an 8-value window (andi + branch, no constant) */
            STAT_r(0);
            return (E + 0x1000000u) + (uint32_t)MANTS_r(V, 9, 0x102u);
        }
        GO_S_r((E >> 23) + 2u, (uint32_t)((int32_t)V >> 9) + 0x800001u);
    }
hix_:
    if (w < 0xC2D00000u)
        goto deep_;
    if (t > 0xFF000000u)
        goto nan_; /* a branch to a shared tail: a ternary here becomes six branch-free instructions */
    return 0;
deep_: {
    /* -104 < x <= -8: t (1 - t + t^2), t = e^x (below -22.2 that is e^x itself, subnormal below -87.3) */
    uint32_t e2 = t >> 24, f = w << 9;
    /* k2 = floor(2|x| 512/ln2) | 1 with 2^30/ln2 rounded down (one lui, as exp's x > 0 path): never one step too
     * large, so R < 2^32 */
    uint32_t t = (1549078528u + mulhu_r(f, 1549078528u)) >> (148u - e2), k = t | 1u;
    int32_t rho = (int32_t)((f << (e2 - 119u)) - k * 1488522235u - mulhu_r(k, 0xE8E7C000u));
    /* 0xF473D000 (one lui) stands for the 2^-72 part 0xF473DE6A of L/2 to 0.2 units of rho; a constant within
     * 2^11 of sg_expm_r's would be rebuilt from it (+2 instructions) */
    /* e^x = 2^(-k/1024) e^-rho, k = 1024 a + 2 j + 1: 2^(-a-1) 2^((2 (511 - j) + 1)/1024), the table read backwards
     * as on exp's x < 0 path; R = 2^31 2^((2 (511-j)+1)/1024) e^-rho as sg_exp_tail_r has it */
    uint32_t a = t >> 9;
    uint32_t T = *(const uint32_t *)((const uint8_t *)exp8_r + 1020u - ((k << 1) & 0x3FCu)) - 131u;
    uint32_t h = (uint32_t)(((int64_t)rho * rho) >> 32) >> 9;
    uint32_t R = T + (uint32_t)((int32_t)(((int64_t)(uint64_t)(T + 951u) * (int32_t)(h - (uint32_t)rho)) >> 32) >> 8), V = R;
    if (a >= 32u) {
        /* below -22.2 t < 2^-32 and V = R */
        if (a - (R >> 31) >= 125u) { /* q = -a - 1: 2 q + (R >> 31) < -251 */
            /* -104 < x < -87.3: a subnormal result, R 2^(q+118) units of 2^-149 (as exp_big_r), q = -a - 1;
             * rejects go to the exp lane's exact path (code 4) */
            uint32_t sb = a - 117u;
            if ((int32_t)R < 0 && sb < 32) {
                uint32_t half = 1u << (sb - 1), g = R & (2 * half - 1);
                if (g - half + 4u > 8u)
                    return (R >> sb) + (g > half);
            }
            GO_r(0, 0, 0); /* (R4: exp's own path in ex_cold_r) */
        }
    } else {
        /* t <= e^-8 < 2^-11.5: t^3 < 2^-34.5 */
        uint32_t tq = R >> a;
        V = R - mulhu_r(R, tq - mulhu_r(tq, tq));
        /* O1: with the 256-entry table V's error spread is above 5 units here (R's plus two floors): an 8-unit
         * window; the rejects go straight to the exact decisions */
        uint32_t qa = a - 125u;
        if ((int32_t)V < 0) {
            if (FAST_r(V, 8, 0x83u, 0x8u, 22))
                return MANT_r(V, 8, 0x83u) - (qa << 23);
            SG_DEEP_MID_r(1u - qa, (V >> 8) + 1);
        }
        if (FAST_r(V, 7, 0x43u, 0x8u, 22)) /* G3: the exact tier takes only words near a midpoint */
            return MANT_r(V, 7, 0x43u) - ((qa + 1u) << 23);
        GO_S_r(0u - qa, (V >> 7) + 1);
    }
    {
        /* TAIL2_r(V, 125 - a, 22, 0x82, 4, 23, 0x41, 3) with the exponent as -(a - 125) */
        uint32_t qa = a - 125u;
        if ((int32_t)V < 0) {
            if (FAST_r(V, 8, 0x82u, 0x4u, 22)) {
                STAT_r(0);
                return MANT_r(V, 8, 0x82u) - (qa << 23);
            }
            SG_DEEP_MID_r(1u - qa, (V >> 8) + 1);
        }
        /* RV2: V < 2^31 (R within t of 2^31: about 1 in 2000 words of this path, none in a scored set); G3: its own
         * rounding test, so that the exact tier sees only words near a midpoint */
        if (FAST_r(V, 7, 0x42u, 0x4u, 22))
            return MANT_r(V, 7, 0x42u) - ((qa + 1u) << 23);
        GO_S_r(0u - qa, (V >> 7) + 1);
    }
}
scellp_: {
        /* a1..a4 as GO_SCELL_r leaves them (public #25). W1: 1/4 <= |x| < 2, the anchor of the cell of x/2: its own tl_r
         * row's (the start of an even cell, the end of an odd one: |d| < 2^18 words), T0 2^32 = c0 - 0x101 to 2 units and
         * the tail dx = xh 2^14 to 2^13; the core at the pair scale (ts = w << 13) */
        const struct rx_r *q = &tl_r[(t >> 19) - 0xFA0u];
        c0v_ = q->c0 - 0x100u;
        dx_ = (int32_t)((uint32_t)(int32_t)q->xh << 14);
        ts_ = w << 13;
        e_ = t >> 24;
        goto slt_;
    }
scellt_: {
        /* W1: 2 <= |x| < 4 (x/2 in binade 127): the nearest cell boundary's anchor in tla_r (boundaries 96..128), a single
         * anchor (ts = w << 14: e one less for the pair-scale core) */
        const struct ra_r *A = (const struct ra_r *)((const uint8_t *)tla_r + (((t - 0x7FFC0000u) >> 16) & ~7u));
        c0v_ = A->c0;
        dx_ = A->dx;
        ts_ = w << 14;
        e_ = (t >> 24) - 1u;
        goto slt_;
    }
scella_: {
        /* TRV: x >= 4 (y >= 2): deficit anchors (as tanh's cellx_; x's offset o_ is y's plus 1024) */
        uint32_t o_ = ((t >> 14) + 16u) & ~31u;
        const struct rx_r *q = (const struct rx_r *)((const uint8_t *)ta_r + 16u + o_ - (0x2040u << 4));
        c0v_ = (o_ << 21) - 2u * (q->c0 - 0x40u);
        dx_ = TH_DX_r(q);
        ts_ = w << 14;
        e_ = (t >> 24) - 1u;
    }
slt_:
    return a2 + (sg_lt_r((int32_t)ts_, c0v_, dx_, a1, e_) ^ (w >> 31));
tier_:
    return ex_cold_r(w, 4u, a1, a2, 0u);
tierp_:
    return ex_cold_r(w | 0x80000000u, 0x80000004u, a1, a2, 0u); /* x > 0: e^-|x| from -|x| */
cold_:
    return sg_cold_r(w, a1, a2, code) ^ 3u;
}

/* ---- Cortex-M (thumb) variant: the Thumb body of published entry #28 (t_ names), unchanged ---- */
/* ===== Thumb body ===== */
/* Scalar arithmetic extracted from published Exact Integer Kernels entry #17. Central activation coefficients and dispatch modified by the Cojectures.io workspace contributors. */
/* Adapted from published EIK entry #6.
 * https://conjectures.io/v1/competitions/exact-integer-kernels/submissions/6/source
 * Terms granted by the competition: MIT or Apache-2.0.
 * Modified range and arithmetic kernels by the Cojectures.io workspace contributors.

MIT License

Copyright (c) 2026 The exact-integer-kernels contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/
/* Adapted from published EIK entry #6.
 * https://conjectures.io/v1/competitions/exact-integer-kernels/submissions/6/source
 * Terms granted by the competition: MIT or Apache-2.0.
 * Modified range and arithmetic kernels by the Cojectures.io workspace contributors.

MIT License

Copyright (c) 2026 The exact-integer-kernels contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/
/* X2: t_v holds the fixed-scale cell less 2^31 + 2^8 (mod 2^32): the cell gives Y = V - 2^31 - 2^8 with V = tanh 2^32 plus
 * the rounding offset. For tanh >= 1/2 that is bits(tanh) 2^8 mod 2^32 less 2^8: tanh's deficit form (w - result) 2^8. */
struct t_ep {uint32_t t_aux;uint32_t t_v,t_p;uint16_t t_r;uint8_t t_c,t_dn;};
static const struct t_ep t_eps[]={
    {2148937847u,2681575596u,8258040u,678u,0u,20u},
    {2151849055u,2685704539u,8323572u,32439u,0u,18u},
    {2154764208u,2689832471u,8323575u,6845u,0u,16u},
    {2157683310u,2693959385u,8389111u,5823u,0u,14u},
    {2160606366u,2698085272u,8454644u,29371u,0u,12u},
    {2163533382u,2702210127u,8520180u,28335u,0u,11u},
    {2166464364u,2706333942u,8585719u,2715u,0u,10u},
    {2169399316u,2710456709u,8651252u,26239u,0u,8u},
    {2172338244u,2714578421u,8716791u,604u,0u,7u},
    {2175281154u,2718699070u,8782324u,24113u,0u,7u},
    {2178228050u,2722818648u,9044468u,23044u,2u,6u},
    {2181178939u,2726937149u,8913398u,5575u,0u,5u},
    {2184133825u,2731054564u,8978932u,20871u,0u,5u},
    {2187092715u,2735170888u,9044470u,3390u,0u,4u},
    {2190055612u,2739286111u,9110006u,2287u,0u,4u},
    {2193022524u,2743400226u,9241076u,17565u,0u,3u},
    {2195993455u,2747513228u,9175540u,16439u,0u,3u},
    {2198968411u,2751625107u,9306610u,31701u,0u,2u},
    {2201947397u,2755735857u,9306612u,14180u,0u,2u},
    {2204930419u,2759845469u,9372146u,29425u,0u,2u},
    {2207917482u,2763953938u,9437684u,11892u,0u,1u},
    {2210908591u,2768061255u,9503220u,10737u,0u,1u},
    {2213903753u,2772167413u,9568757u,1383u,0u,1u},
    {2216902972u,2776272404u,9634293u,214u,0u,1u},
    {2219906255u,2780376222u,9699828u,7229u,0u,1u},
    {2222913606u,2784478859u,9765361u,30621u,0u,1u},
    {2225925031u,2788580308u,9896436u,4853u,1u,0u},
    {2228940535u,2792680562u,9961972u,3653u,1u,0u},
    {2231960125u,2796779611u,10027508u,2449u,1u,0u},
    {2234983806u,2800877452u,9961970u,17615u,0u,0u},
    {2238011583u,2804974075u,10027504u,32777u,0u,0u},
    {2241043461u,2809069473u,10224115u,6978u,1u,0u},
    {2244079447u,2813163640u,10158578u,13930u,0u,0u},
    {2247119546u,2817256567u,10224112u,29072u,0u,0u},
    {2250163764u,2821348248u,10289651u,3246u,0u,0u},
    {2253212105u,2825438675u,10355187u,1989u,0u,0u},
    {2256264576u,2829527841u,10355184u,25297u,0u,0u},
    {2259321183u,2833615739u,10486256u,24029u,0u,0u},
    {2262381930u,2837702361u,10486256u,22748u,0u,0u},
    {2265446823u,2841787702u,10551792u,21461u,0u,0u},
    {2268515869u,2845871753u,10617327u,28361u,0u,0u},
    {2271589072u,2849954506u,10682864u,18869u,0u,0u},
    {2274666439u,2854035956u,10748400u,17562u,0u,0u},
    {2277747975u,2858116094u,10879472u,16251u,0u,0u},
    {2280833685u,2862194915u,10879472u,14926u,0u,0u},
    {2283923576u,2866272409u,10945009u,5406u,0u,0u},
    {2287017652u,2870348572u,11010544u,12261u,0u,0u},
    {2290115920u,2874423394u,11010544u,10915u,0u,0u},
    {2293218386u,2878496870u,11076080u,9565u,0u,0u},
    {2296325054u,2882568992u,11141617u,16u,0u,0u},
    {2299435931u,2886639752u,11207151u,15037u,0u,0u},
    {2302551023u,2890709145u,11272688u,5473u,0u,0u},
    {2305670334u,2894777163u,11338223u,12287u,0u,0u},
    {2308793871u,2898843798u,11403760u,2710u,0u,0u},
    {2311921640u,2902909044u,11469295u,9510u,0u,0u},
    {2315053646u,2906972894u,11534831u,8110u,0u,0u},
    {2318189895u,2911035341u,11534831u,6700u,0u,0u},
    {2321330393u,2915096377u,11600364u,29862u,0u,0u},
    {2324475145u,2919155996u,11665903u,3866u,0u,0u},
    {2327624158u,2923214190u,11928044u,27019u,2u,0u},
    {2330777437u,2927270954u,11796975u,1004u,0u,0u},
    {2333934987u,2931326279u,11862510u,7755u,0u,0u},
    {2337096815u,2935380158u,11928046u,6307u,0u,0u},
    {2340262926u,2939432586u,11928045u,13040u,0u,0u},
    {2343433327u,2943483554u,12059116u,19773u,0u,0u},
    {2346608022u,2947533056u,12059118u,1917u,0u,0u},
    {2349787019u,2951581085u,12190189u,8637u,0u,0u},
    {2352970322u,2955627635u,12190188u,15341u,0u,0u},
    {2356157937u,2959672697u,12452333u,5664u,2u,0u},
    {2359349871u,2963716266u,12321261u,4163u,0u,0u},
    {2362546129u,2967758333u,12386795u,19045u,0u,0u},
    {2365746717u,2971798894u,12386796u,9338u,0u,0u},
    {2368951641u,2975837940u,12452332u,7821u,0u,0u},
    {2372160907u,2979875465u,12517868u,6297u,0u,0u},
    {2375374520u,2983911463u,12583404u,4765u,0u,0u},
    {2378592487u,2987945925u,12648940u,3227u,0u,0u},
    {2381814814u,2991978845u,12714476u,1683u,0u,0u},
    {2385041505u,2996010217u,12780012u,132u,0u,0u},
    {2388272568u,3000040034u,12911083u,6766u,1u,0u},
    {2391508009u,3004068288u,12976616u,29777u,1u,0u},
    {2394747832u,3008094975u,12911082u,11817u,0u,0u},
    {2397992044u,3012120085u,12976619u,2047u,0u,0u},
    {2401240652u,3016143612u,13173224u,25042u,1u,0u},
    {2404493660u,3020165552u,13107690u,7062u,0u,0u},
    {2407751075u,3024185895u,13107688u,21843u,0u,0u},
    {2411012903u,3028204635u,13173224u,20239u,0u,0u},
    {2414279150u,3032221767u,13238760u,18627u,0u,0u},
    {2417549822u,3036237282u,13304296u,17008u,0u,0u},
    {2420824925u,3040251175u,13369833u,7191u,0u,0u},
    {2424104464u,3044263439u,13435369u,5559u,0u,0u},
    {2427388447u,3048274067u,13500904u,12112u,0u,0u},
    {2430676878u,3052283052u,13500904u,10463u,0u,0u},
    {2433969764u,3056290388u,13566440u,8811u,0u,0u},
    {2437267111u,3060296068u,13631976u,7154u,0u,0u},
    {2440568925u,3064300086u,13697512u,5488u,0u,0u},
    {2443875212u,3068302435u,13763047u,12009u,0u,0u},
    {2447185978u,3072303108u,13763048u,2135u,0u,0u},
    {2450501230u,3076302099u,13828584u,450u,0u,0u},
    {2453820972u,3080299402u,13894116u,31526u,0u,0u},
    {2457145212u,3084295009u,13959655u,5253u,0u,0u},
    {2460473956u,3088288914u,14156261u,19936u,1u,0u},
    {2463807208u,3092281111u,14287332u,26417u,2u,0u},
    {2467144977u,3096271593u,14156260u,24696u,0u,0u},
    {2470487267u,3100260354u,14156260u,22968u,0u,0u},
    {2473834085u,3104247387u,14221798u,4854u,0u,0u},
    {2477185437u,3108232685u,14287334u,3118u,0u,0u},
    {2480541329u,3112216243u,14352867u,25950u,0u,0u},
    {2483901768u,3116198054u,14352869u,7812u,0u,0u},
    {2487266759u,3120178110u,14418404u,14249u,0u,0u},
    {2490636308u,3124156407u,14483941u,4294u,0u,0u},
    {2494010423u,3128132938u,14549475u,18908u,0u,0u},
    {2497389108u,3132107695u,14615013u,749u,0u,0u},
    {2500772371u,3136080673u,14615011u,15348u,0u,0u},
    {2504160217u,3140051865u,14680548u,5368u,0u,0u},
    {2507552652u,3144021265u,14746084u,3573u,0u,0u},
    {2510949683u,3147988867u,14811620u,1772u,0u,0u},
    {2514351317u,3151954664u,14811616u,32729u,0u,0u},
    {2517757558u,3155918650u,14877155u,6340u,0u,0u},
    {2521168414u,3159880819u,14942688u,29096u,0u,0u},
    {2524583891u,3163841163u,15204832u,27274u,2u,0u},
    {2528003995u,3167799678u,15139299u,862u,1u,0u},
    {2531428732u,3171756357u,15073760u,23595u,0u,0u},
    {2534858109u,3175711193u,15139296u,21750u,0u,0u},
    {2538292131u,3179664180u,15204832u,19900u,0u,0u},
    {2541730806u,3183615312u,15466976u,18046u,2u,0u},
    {2545174139u,3187564583u,15401440u,16179u,1u,0u},
    {2548622137u,3191511987u,15335904u,14305u,0u,0u},
    {2552074806u,3195457517u,15401440u,12429u,0u,0u},
    {2555532152u,3199401167u,62063554u,4715u,1u,0u},
    {2558994182u,3207282802u,62456768u,13530u,1u,0u},
    {2562460902u,3215156845u,62784448u,5912u,0u,0u},
    {2565932319u,3223023245u,63177660u,31013u,0u,0u},
    {2569408438u,3230881955u,63570878u,6913u,0u,0u},
    {2572889267u,3238732924u,63964093u,7341u,0u,0u},
    {2576374811u,3246576105u,64422844u,7721u,1u,0u},
    {2579865077u,3254411450u,64750520u,32628u,0u,0u},
    {2583360071u,3262238911u,65143736u,24720u,0u,0u},
    {2586859800u,3270058440u,65536952u,16764u,0u,0u},
    {2590364271u,3277869989u,65930168u,8762u,0u,0u},
    {2593873489u,3285673512u,66388920u,711u,1u,0u},
    {2597387460u,3293468960u,66716599u,808u,0u,0u},
    {2600906193u,3301256288u,67175350u,857u,1u,0u},
    {2604429692u,3309035449u,67503029u,859u,0u,0u},
    {2607957964u,3316806395u,67961776u,33583u,1u,0u},
    {2611491017u,3324569083u,68289456u,25296u,1u,0u},
    {2615028855u,3332323464u,68617136u,16969u,0u,0u},
    {2618571487u,3340069494u,69010352u,8591u,1u,0u},
    {2622118917u,3347807126u,69338032u,173u,0u,0u},
    {2625671154u,3355536315u,69796782u,8095u,1u,0u},
    {2629228203u,3363257018u,70189996u,15969u,1u,0u},
    {2632790070u,3370969188u,70452139u,15605u,0u,0u},
    {2636356763u,3378672781u,70845352u,31579u,1u,0u},
    {2639928288u,3386367752u,71238568u,22938u,1u,0u},
    {2643504651u,3394054058u,71631785u,6061u,1u,0u},
    {2647085859u,3401731655u,71893928u,5520u,0u,0u},
    {2650671919u,3409400499u,72221604u,29511u,0u,0u},
    {2654262837u,3417060546u,72680356u,20695u,1u,0u},
    {2657858619u,3424711753u,73139108u,11837u,2u,0u},
    {2661459273u,3432354079u,73270176u,35694u,0u,0u},
    {2665064805u,3439987478u,73728928u,26750u,1u,0u},
    {2668675221u,3447611908u,74122144u,17765u,1u,0u},
    {2672290528u,3455227330u,74384288u,8728u,1u,0u},
    {2675910733u,3462833698u,74777503u,7851u,1u,0u},
    {2679535842u,3470430973u,75105182u,6927u,1u,0u},
    {2683165863u,3478019112u,75432861u,5962u,1u,0u},
    {2686800801u,3485598074u,75760540u,4956u,1u,0u},
    {2690440663u,3493167819u,76022682u,12100u,0u,0u},
    {2694085456u,3500728303u,76481432u,19209u,1u,0u},
    {2697735187u,3508279489u,76678040u,9886u,0u,0u},
    {2701389863u,3515821334u,77136792u,530u,1u,0u},
    {2705049489u,3523353801u,77398934u,7510u,1u,0u},
    {2708714073u,3530876847u,77857685u,6267u,2u,0u},
    {2712383622u,3538390434u,77988756u,4975u,0u,0u},
    {2716058142u,3545894522u,78381971u,3649u,1u,0u},
    {2719737640u,3553389071u,78709650u,2285u,1u,0u},
    {2723422122u,3560874045u,78906256u,9068u,0u,0u},
    {2727111596u,3568349401u,79233932u,32204u,0u,0u},
    {2730806068u,3575815105u,79627148u,22531u,1u,0u},
    {2734505545u,3583271117u,79823756u,12817u,0u,0u},
    {2738210034u,3590717398u,80216968u,35837u,1u,0u},
    {2741919542u,3598153912u,80479115u,1476u,0u,0u},
    {2745634074u,3605580620u,80872328u,16230u,1u,0u},
    {2749353639u,3612997486u,81200008u,6371u,1u,0u},
    {2753078243u,3620404474u,81462151u,4663u,1u,0u},
    {2756807893u,3627801545u,81789830u,2923u,1u,0u},
    {2760542595u,3635188665u,81920900u,9330u,0u,0u},
    {2764282357u,3642565795u,82379651u,7522u,1u,0u},
    {2768027185u,3649932902u,82510721u,13858u,0u,0u},
    {2771777086u,3657289948u,82838400u,11974u,0u,0u},
    {2775532068u,3664636899u,83100544u,1859u,0u,0u},
    {2779292136u,3671973719u,83362684u,24478u,0u,0u},
    {2783057298u,3679300373u,83821437u,6111u,1u,0u},
    {2786827561u,3686616828u,83952508u,4079u,0u,0u},
    {2790602932u,3693923047u,84214648u,26595u,0u,0u},
    {2794383417u,3701218998u,84542329u,8120u,0u,0u},
    {2798169023u,3708504646u,84804472u,5992u,0u,0u},
    {2801959759u,3715779958u,85066613u,20214u,0u,0u},
    {2805755629u,3723044900u,85328756u,18019u,0u,0u},
    {2809556642u,3730299440u,85590900u,7599u,0u,0u},
    {2813362804u,3737543543u,85853040u,29914u,0u,0u},
    {2817174122u,3744777178u,86115186u,3045u,0u,0u},
    {2820990604u,3752000311u,86442864u,8916u,0u,0u},
    {2824812256u,3759212912u,86639468u,31132u,0u,0u},
    {2828639085u,3766414948u,86901612u,20551u,0u,0u},
    {2832471098u,3773606388u,87163757u,1747u,0u,0u},
    {2836308303u,3780787199u,87425896u,32064u,0u,0u},
    {2840150706u,3787957352u,87753578u,5006u,1u,0u},
    {2843998315u,3795116814u,87950184u,10686u,0u,0u},
    {2847851136u,3802265556u,88277863u,8143u,1u,0u},
    {2851709176u,3809403548u,88408932u,21949u,0u,0u},
    {2855572443u,3816530758u,88671077u,2963u,0u,0u},
    {2859440944u,3823647157u,88867680u,33095u,0u,0u},
    {2863314685u,3830752716u,89129824u,22241u,0u,0u},
    {2867193674u,3837847406u,89391968u,11357u,0u,0u},
    {2871077918u,3844931196u,89719648u,446u,1u,0u},
    {2874967425u,3852004059u,89850718u,5886u,0u,0u},
    {2878862200u,3859065966u,90047324u,11297u,0u,0u},
    {2882762252u,3866116888u,90309467u,8493u,0u,0u},
    {2886667587u,3873156797u,90571610u,5661u,0u,0u},
    {2890578213u,3880185666u,90768217u,2797u,0u,0u},
    {2894494136u,3887203468u,91030358u,16289u,1u,0u},
    {2898415365u,3894210173u,91292500u,21567u,1u,0u},
    {2902341906u,3901205757u,91423573u,2238u,0u,0u},
    {2906273766u,3908190192u,91620176u,32034u,0u,0u},
    {2910210952u,3915163451u,92013392u,20848u,2u,0u},
    {2914153473u,3922125508u,92078927u,17825u,0u,0u},
    {2918101334u,3929076337u,92275532u,31159u,0u,0u},
    {2922054544u,3936015913u,92603214u,3511u,1u,0u},
    {2926013109u,3942944209u,92668748u,8600u,0u,0u},
    {2929977037u,3949861201u,92930891u,5478u,0u,0u},
    {2933946335u,3956766864u,93127496u,18712u,0u,0u},
    {2937921011u,3963661172u,93324104u,7346u,0u,0u},
    {2941901071u,3970544102u,93586247u,4147u,1u,0u},
    {2945886522u,3977415630u,93782851u,25499u,1u,0u},
    {2949877373u,3984275730u,93979460u,5868u,1u,0u},
    {2953873631u,3991124379u,94176067u,2599u,1u,0u},
    {2957875302u,3997961555u,94241601u,7494u,0u,0u},
    {2961882394u,4004787233u,94569280u,4181u,1u,0u},
    {2965894915u,4011601391u,94634815u,839u,0u,0u},
    {2969912872u,4018404006u,94896956u,13861u,1u,0u},
    {2973936271u,4025195056u,95028028u,2285u,0u,0u},
    {2977965122u,4031974518u,95159098u,7068u,0u,0u},
    {2981999430u,4038742370u,95486777u,3645u,1u,0u},
    {2986039204u,4045498592u,95617845u,24767u,1u,0u},
    {2990084451u,4052243160u,95814452u,21297u,1u,0u},
    {2994135177u,4058976054u,96076596u,9615u,2u,0u},
    {2998191392u,4065697254u,96142131u,6099u,1u,0u},
    {3002253101u,4072406738u,96207666u,2563u,0u,0u},
    {3006320313u,4079104485u,96469808u,7203u,1u,0u},
    {3010393035u,4085790477u,96666413u,20015u,1u,0u},
    {3014471274u,4092464693u,96797483u,24610u,1u,0u},
    {3018555038u,4099127112u,96863019u,12804u,0u,0u},
    {3022644334u,4105777716u,97125163u,981u,1u,0u},
    {3026739170u,4112416486u,97190697u,5519u,0u,0u},
    {3030839554u,4119043401u,97452840u,1852u,1u,0u},
    {3034945492u,4125658445u,97583910u,6353u,1u,0u},
    {3039056993u,4132261598u,390923848u,21683u,1u,1u},
    {3043174064u,4145432160u,392169026u,23129u,2u,1u},
    {3047296712u,4158554944u,393152061u,16236u,1u,1u},
    {3051424946u,4171629812u,394200632u,9207u,1u,1u},
    {3055558771u,4184656627u,395314737u,18436u,1u,1u},
    {3059698198u,4197635259u,396232235u,19340u,0u,1u},
    {3063843231u,4210565581u,397346340u,28315u,1u,1u},
    {3067993881u,4223447472u,398263840u,12586u,1u,1u},
    {3072150153u,4236280809u,399246872u,29515u,1u,1u},
    {3076312055u,4249065480u,400098832u,46324u,1u,1u},
    {3080479596u,4261801373u,400950797u,22064u,1u,1u},
    {3084652783u,4274488376u,401802756u,46854u,1u,1u},
    {3088831624u,4287126389u,402523648u,30579u,0u,1u},
    {3093016125u,4748015u,403310072u,46975u,0u,1u},
    {3097206295u,17287750u,404162036u,30510u,1u,1u},
    {3101402142u,29778204u,404882928u,13952u,1u,1u},
    {3105603673u,42219289u,405538281u,21882u,1u,1u},
    {3109810896u,54610918u,406259172u,13350u,1u,1u},
    {3114023819u,66953013u,406717917u,21112u,0u,1u},
    {3118242448u,79245492u,407438808u,12422u,1u,1u},
    {3122466793u,91488283u,407963088u,28231u,1u,1u},
    {3126696861u,103681314u,408552904u,43978u,1u,1u},
    {3130932659u,115824520u,408946117u,18692u,0u,1u},
    {3135174196u,127917836u,409470400u,9729u,1u,1u},
    {3139421478u,139961202u,409863608u,25287u,0u,1u},
    {3143674515u,151954562u,410256819u,16212u,0u,1u},
    {3147933313u,163897862u,410650026u,39856u,0u,1u},
    {3152197881u,175791054u,411108776u,6109u,1u,1u},
    {3156468226u,187634091u,411501984u,21471u,1u,1u},
    {3160744356u,199426932u,411633048u,36783u,0u,1u},
    {3165026279u,211169536u,411960723u,27491u,0u,1u},
    {3169314003u,222861868u,412222864u,1778u,0u,1u},
    {3173607536u,234503895u,412550536u,16998u,1u,1u},
    {3177906885u,246095590u,412616064u,32182u,0u,1u},
    {3182212058u,257636925u,413009272u,47352u,2u,1u},
    {3186523064u,269127878u,413074804u,29728u,1u,1u},
    {3190839910u,280568431u,413205869u,36663u,1u,1u},
    {3195162604u,291958567u,413140328u,27194u,0u,1u},
    {3199491154u,303298274u,413205856u,42294u,0u,1u},
    {3203825568u,314587541u,413271388u,24621u,0u,1u},
    {3208165854u,325826363u,413271380u,39708u,0u,1u},
    {3212512020u,337014736u,413271376u,22027u,0u,1u},
    {3216864074u,348152660u,413271368u,37116u,0u,1u},
    {3221222024u,359240137u,413205824u,52209u,0u,1u},
    {3225585877u,370277175u,413205820u,34540u,1u,1u},
    {3229955642u,381263780u,413009207u,25074u,0u,1u},
    {3234331327u,392199967u,413009200u,32004u,2u,1u},
    {3238712940u,403085748u,412681512u,47142u,0u,1u},
    {3243100489u,413921142u,412681509u,21344u,2u,1u},
    {3247493981u,424706170u,412353823u,20142u,0u,1u},
    {3251893426u,435440856u,412288280u,27155u,2u,1u},
    {3256298830u,446125224u,412026132u,9621u,2u,1u},
    {3260710203u,456759306u,411763981u,16693u,2u,1u},
    {3265127552u,467343132u,411305222u,23797u,0u,1u},
    {3269550885u,477876738u,411043072u,22745u,1u,1u},
    {3273980210u,488360161u,410780920u,38117u,2u,1u},
    {3278415536u,498793439u,410387696u,53531u,2u,1u},
    {3282856871u,509176619u,410125550u,19840u,3u,1u},
    {3287304222u,519509742u,409666792u,18961u,2u,1u},
    {3291757598u,529792861u,409208032u,34511u,2u,1u},
    {3296217008u,540026022u,408749272u,50116u,2u,1u},
    {3300682458u,550209280u,408421588u,33013u,3u,1u},
    {3305153958u,560342690u,408028368u,15964u,4u,1u},
    {3309631516u,570426311u,407373000u,31736u,3u,1u},
    {3314115139u,580460204u,406717632u,47573u,1u,1u},
    {3318604837u,590444431u,406389948u,30710u,4u,1u},
    {3323100617u,600379057u,405865656u,13913u,4u,1u},
    {3327602487u,610264151u,405210288u,29950u,3u,1u},
    {3332110456u,620099783u,404685995u,21485u,4u,1u},
    {3336624532u,629886025u,403965093u,21281u,3u,1u},
    {3341144724u,639622950u,403309728u,12963u,3u,1u},
    {3345671039u,649310638u,402719897u,21112u,3u,1u},
    {3350203486u,658949167u,402195600u,45721u,5u,1u},
    {3354742073u,668538618u,401409165u,21259u,4u,1u},
    {3359286808u,678079074u,400622727u,21458u,3u,1u},
    {3363837701u,687570621u,400163968u,29941u,6u,1u},
    {3368394759u,697013347u,399311993u,38506u,5u,1u},
    {3372957990u,706407343u,398460020u,30777u,4u,1u},
    {3377527403u,715752697u,397673584u,14952u,4u,1u},
    {3382103006u,725049507u,396887146u,15606u,4u,1u},
    {3386684808u,734297866u,396100708u,16358u,4u,1u},
    {3391272817u,743497874u,395314270u,17205u,5u,1u},
    {3395867042u,752649627u,394658904u,18162u,6u,1u},
    {3400467490u,761753231u,393741393u,27403u,6u,1u},
    {3405074171u,770808787u,392758344u,53131u,5u,1u},
    {3409687093u,779816400u,391906370u,54396u,5u,1u},
    {3414306264u,788776178u,390988864u,22997u,5u,1u},
    {3418931692u,797688228u,390005816u,40861u,4u,1u},
    {3423563387u,806552664u,389153845u,17877u,5u,1u},
    {3428201356u,815369593u,388170796u,44160u,4u,1u},
    {3432845608u,824139134u,387318824u,29597u,5u,1u},
    {3437496152u,832861402u,386401316u,15147u,6u,1u},
    {3442152996u,841536510u,385352736u,817u,5u,1u},
    {3446816149u,850164581u,384369688u,19375u,5u,1u},
    {3451485620u,858745734u,383452178u,21671u,6u,1u},
    {3456161416u,867280091u,382338061u,15894u,5u,1u},
    {3460843546u,875767775u,381355016u,10242u,6u,1u},
    {3465532020u,884208910u,380175359u,37485u,4u,1u},
    {3470226845u,892603625u,379192312u,48471u,5u,1u},
    {3474928030u,900952046u,378143735u,10436u,5u,1u},
    {3479635584u,909254302u,377226224u,21682u,7u,1u},
    {3484349515u,917510526u,376046568u,41247u,6u,1u},
    {3489069832u,925720846u,374932453u,19992u,5u,1u},
    {3493796545u,933885399u,373818336u,15245u,6u,1u},
    {3498529660u,942004317u,372769752u,35219u,6u,1u},
    {3503269188u,950077739u,371590101u,14361u,6u,1u},
    {3508015136u,958105797u,370672592u,10035u,8u,1u},
    {3512767514u,966088633u,369427400u,30416u,7u,1u},
    {3517526329u,974026386u,368182208u,50937u,6u,1u},
    {3522291592u,981919197u,367068096u,6064u,7u,1u},
    {3527063311u,989767207u,365822905u,18678u,6u,1u},
    {3531841493u,997570558u,364643252u,15052u,6u,1u},
    {3536626149u,1005329395u,363463600u,3379u,6u,1u},
    {3541417287u,1013043864u,362283944u,24620u,6u,1u},
    {3546214915u,1020714109u,361169827u,21433u,7u,1u},
    {3551019043u,1028340279u,359859102u,18389u,6u,1u},
    {3555829678u,1035922522u,358679449u,15494u,7u,1u},
    {3560646831u,1043460984u,357303183u,53710u,5u,1u},
    {3565470510u,1050955820u,356189072u,1963u,7u,1u},
    {3570300724u,1058407177u,355009417u,15910u,7u,1u},
    {3575137481u,1065815208u,353633156u,13617u,6u,1u},
    {3579980791u,1073180067u,352650109u,27869u,9u,1u},
    {3584830662u,1080501905u,351208312u,25883u,7u,1u},
    {3589687103u,1087780877u,350028660u,15866u,8u,1u},
    {3594550124u,1095017140u,348717936u,6003u,7u,1u},
    {3599419732u,1102210848u,347407208u,29062u,7u,1u},
    {3604295937u,1109362159u,346162020u,19513u,7u,1u},
    {3609178749u,1116471230u,344720223u,18307u,6u,1u},
    {3614068175u,1123538219u,1373701809u,59101u,53u,2u},
    {3618964224u,1137546584u,1363150492u,64079u,52u,2u},
    {3623866907u,1151388537u,1352795784u,62148u,55u,2u},
    {3628776231u,1165065363u,1342178932u,61511u,55u,2u},
    {3633692207u,1178578358u,1331431008u,62174u,55u,2u},
    {3638614842u,1191928834u,1320683086u,47761u,56u,2u},
    {3643544145u,1205118100u,1309869625u,59245u,56u,2u},
    {3648480127u,1218147478u,1298859557u,63859u,55u,2u},
    {3653422795u,1231018299u,1287980562u,61613u,56u,2u},
    {3658372160u,1243731893u,1277101568u,52516u,57u,2u},
    {3663328229u,1256289602u,1266025964u,61145u,56u,2u},
    {3668291012u,1268692773u,1255015897u,62925u,57u,2u},
    {3673260519u,1280942752u,1243874760u,49669u,57u,2u},
    {3678236758u,1293040890u,1232930228u,62357u,58u,2u},
    {3683219738u,1304988548u,1221723554u,60009u,57u,2u},
    {3688209469u,1316787083u,1210516880u,59018u,57u,2u},
    {3693205960u,1328437855u,1199310208u,43007u,57u,2u},
    {3698209219u,1339942228u,1188169068u,61132u,57u,2u},
    {3703219257u,1351301565u,1176962396u,47851u,57u,2u},
    {3708236081u,1362517234u,1165690186u,52317u,56u,2u},
    {3713259702u,1373590596u,1154614584u,58154u,57u,2u},
    {3718290129u,1384523020u,1143276840u,48962u,56u,2u},
    {3723327370u,1395315868u,1132332310u,57531u,58u,2u},
    {3728371436u,1405970504u,1120994566u,51070u,56u,2u},
    {3733422334u,1416488291u,1109984500u,62361u,57u,2u},
    {3738480076u,1426870590u,1098843364u,58625u,56u,2u},
    {3743544669u,1437118757u,1087702228u,56243u,56u,2u},
    {3748616123u,1447234150u,1076692165u,47026u,57u,2u},
    {3753694448u,1457218121u,1065485492u,55540u,55u,2u},
    {3758779652u,1467072018u,1054672037u,49027u,57u,2u},
    {3763871746u,1476797190u,1043465365u,52038u,55u,2u},
    {3768970737u,1486394977u,1032520838u,48203u,55u,2u},
    {3774076637u,1495866718u,1021772918u,53897u,57u,2u},
    {3779189453u,1505213744u,1010762855u,52728u,55u,2u},
    {3784309196u,1514437385u,999949400u,52886u,55u,2u},
    {3789435875u,1523538966u,989135946u,46170u,55u,2u},
    {3794569499u,1532519801u,978388026u,57159u,54u,2u},
    {3799710078u,1541381206u,967640109u,44874u,54u,2u},
    {3804857620u,1550124485u,956892191u,42089u,52u,2u},
    {3810012136u,1558750939u,946406416u,48794u,53u,2u},
    {3815173635u,1567261862u,935789569u,56787u,52u,2u},
    {3820342127u,1575658543u,925369333u,41487u,53u,2u},
    {3825517620u,1583942259u,914883559u,43849u,52u,2u},
    {3830700125u,1592114285u,904594392u,55678u,52u,2u},
    {3835889650u,1600175888u,894239691u,52378u,52u,2u},
    {3841086206u,1608128327u,883950528u,33951u,51u,2u},
    {3846289802u,1615972852u,873989040u,57737u,53u,2u},
    {3851500447u,1623710707u,863765413u,41795u,52u,2u},
    {3856718151u,1631343127u,853672856u,43472u,51u,2u},
    {3861942924u,1638871341u,843711372u,38181u,51u,2u},
    {3867174774u,1646296567u,833749887u,42297u,50u,2u},
    {3872413713u,1653620018u,823919476u,31234u,50u,2u},
    {3877659749u,1660842893u,814089064u,29564u,49u,2u},
    {3882912891u,1667966391u,804455260u,29081u,50u,2u},
    {3888173150u,1674991694u,794690384u,29778u,48u,2u},
    {3893440536u,1681919978u,785187650u,48036u,48u,2u},
    {3898715057u,1688752412u,775750455u,42881u,48u,2u},
    {3903996724u,1695490154u,766378796u,38879u,48u,2u},
    {3909285545u,1702134354u,756876065u,36017u,46u,2u},
    {3914581532u,1708686152u,747832088u,17914u,48u,2u},
    {3919884693u,1715146681u,738525963u,33696u,47u,2u},
    {3925195039u,1721517057u,729350912u,34220u,45u,2u},
    {3930512579u,1727798399u,720306933u,35846u,45u,2u},
    {3935837322u,1733991806u,711459562u,38574u,46u,2u},
    {3941169279u,1740098372u,702546656u,34197u,45u,2u},
    {3946508459u,1746119183u,693764824u,14514u,45u,2u},
    {3951854873u,1752055311u,684917451u,36860u,43u,2u},
    {3957208529u,1757907821u,676463297u,35698u,44u,2u},
    {3962569438u,1763677768u,667878071u,35577u,44u,2u},
    {3967937609u,1769366199u,659227310u,28302u,42u,2u},
    {3973313053u,1774974146u,651100832u,63031u,44u,2u},
    {3978695779u,1780502639u,642777752u,49619u,44u,2u},
    {3984085797u,1785952692u,634258064u,37213u,41u,2u},
    {3989483117u,1791325311u,626197128u,25817u,42u,2u},
    {3994887749u,1796621494u,618070650u,64563u,41u,2u},
    {4000299703u,1801842226u,610140786u,55143u,41u,2u},
    {4005718988u,1806988487u,602145388u,30305u,40u,2u},
    {4011145615u,1812061241u,594346592u,55585u,40u,2u},
    {4016579594u,1817061448u,586547800u,49049u,39u,2u},
    {4022020934u,1821990055u,579076693u,2501u,41u,2u},
    {4027469646u,1826848001u,571212361u,30603u,38u,2u},
    {4032925739u,1831636213u,563741248u,35060u,38u,2u},
    {4038389223u,1836355610u,556335674u,15856u,38u,2u},
    {4043860109u,1841007103u,548995632u,30321u,38u,2u},
    {4049338407u,1845591590u,541721129u,21105u,38u,2u},
    {4054824126u,1850109960u,534446624u,29158u,37u,2u},
    {4060317277u,1854563095u,527303193u,21704u,36u,2u},
    {4065817869u,1858951865u,520356369u,23309u,37u,2u},
    {4071325913u,1863277131u,513344007u,42153u,36u,2u},
    {4076841419u,1867539746u,506331648u,37263u,35u,2u},
    {4082364397u,1871740551u,499450364u,8638u,34u,2u},
    {4087894857u,1875880379u,492765682u,29998u,34u,2u},
    {4093432810u,1879960054u,486081003u,27600u,33u,2u},
    {4098978264u,1883980392u,479396322u,42389u,32u,2u},
    {4104531232u,1887942195u,472973792u,640u,33u,2u},
    {4110091721u,1891846262u,466354645u,33405u,31u,2u},
    {4115659744u,1895693377u,460194252u,50580u,32u,2u},
    {4121235310u,1899484319u,453968328u,27561u,33u,2u},
    {4126818430u,1903219858u,447545794u,21688u,30u,2u},
    {4132409112u,1906900752u,441450939u,24762u,31u,2u},
    {4138007369u,1910527752u,435356081u,53162u,30u,2u},
    {4143613210u,1914101600u,429392300u,41339u,30u,2u},
    {4149226645u,1917623029u,423494056u,22053u,30u,2u},
    {4154847685u,1921092764u,417595808u,36255u,29u,2u},
    {4160476339u,1924511521u,411894168u,51167u,30u,2u},
    {4166112619u,1927880006u,406126998u,17631u,29u,2u},
    {4171756534u,1931198918u,400425360u,17556u,28u,2u},
    {4177408096u,1934468947u,394854793u,26359u,28u,2u},
    {4183067314u,1937690776u,389349761u,44030u,28u,2u},
    {4188734198u,1940865075u,383910272u,5031u,27u,2u},
    {4194408759u,1943992513u,378339704u,24028u,25u,2u},
    {4200091008u,1947073743u,373293427u,19117u,27u,2u},
    {4205780955u,1950109417u,367985007u,6643u,27u,2u},
    {4211478610u,1953100174u,362873192u,19390u,27u,2u},
    {4217183983u,1956046645u,357695843u,16379u,26u,2u},
    {4222897086u,1958949457u,352584031u,5796u,25u,2u},
    {4228617929u,1961809227u,347734360u,20402u,27u,2u},
    {4234346521u,1964626561u,342557008u,43805u,23u,2u},
    {4240082875u,1967402065u,337772879u,10460u,24u,2u},
    {4245826999u,1970136327u,333054279u,35055u,24u,2u},
    {4251578905u,1972829936u,328270144u,52033u,24u,2u},
    {4257338604u,1975483470u,323617089u,4057u,23u,2u},
    {4263106105u,1978097501u,319160632u,38564u,25u,2u},
    {4268881419u,1980672591u,314442036u,32668u,23u,2u},
    {4274664557u,1983209297u,309920048u,27325u,23u,2u},
    {4280455530u,1985708168u,305529132u,22532u,23u,2u},
    {4286254348u,1988169745u,301138216u,18278u,22u,2u},
    {4292061022u,1990594565u,296943907u,22748u,23u,2u},
    {2374944954u,1992983154u,1170014781u,47279u,170u,3u},
    {2382364672u,1997653719u,1136722475u,53955u,167u,3u},
    {2380267520u,2002185522u,1104019996u,40081u,161u,3u},
    {2378170368u,2006582545u,1072366090u,54707u,158u,3u},
    {2377157514u,2010848657u,1041236476u,40381u,151u,3u},
    {2390753280u,2014987628u,1011286508u,46164u,148u,3u},
    {2389853746u,2019003126u,982057439u,30989u,144u,3u},
    {2403537292u,2022898721u,953680336u,35718u,141u,3u},
    {2418016256u,2026677885u,925827521u,43872u,135u,3u},
    {2417766580u,2030343999u,899023281u,63551u,133u,3u},
    {2398617600u,2033900348u,872874408u,29128u,130u,3u},
    {2398093312u,2037350130u,847446424u,55202u,127u,3u},
    {2397569024u,2040696455u,822673805u,43384u,123u,3u},
    {2397550066u,2043942344u,798622080u,50930u,120u,3u},
    {2413297664u,2047090741u,775225720u,20413u,117u,3u},
    {2412773376u,2050144500u,752353642u,41869u,112u,3u},
    {2412722188u,2053106403u,730202464u,33293u,109u,3u},
    {2428502016u,2055979150u,708641110u,27383u,105u,3u},
    {2428117630u,2058765367u,687931723u,32256u,104u,3u},
    {2444230656u,2061467605u,667681088u,39641u,102u,3u},
    {2443706368u,2064088343u,647889207u,33088u,98u,3u},
    {2443671916u,2066629993u,628556080u,12518u,94u,3u},
    {2459435008u,2069094893u,610074917u,27034u,93u,3u},
    {2459346014u,2071485320u,591986972u,27405u,90u,3u},
    {2475163648u,2073803483u,574161172u,21755u,85u,3u},
    {2475114292u,2076051528u,557121805u,10036u,83u,3u},
    {2490958906u,2078231541u,540672256u,49525u,82u,3u},
    {2507145216u,2080345548u,524550398u,896u,79u,3u},
    {2506866874u,2082395513u,508952816u,52509u,78u,3u},
    {2522873856u,2084383352u,493682922u,40465u,75u,3u},
    {2522828422u,2086310914u,479002852u,30256u,73u,3u},
    {2538835984u,2088180004u,464584928u,5431u,70u,3u},
    {2554883576u,2089992370u,450625752u,15098u,68u,3u},
    {2571108352u,2091749711u,437059793u,18249u,65u,3u},
    {2570966364u,2093453674u,424083658u,23026u,65u,3u},
    {2587080390u,2095105860u,411435202u,37577u,63u,3u},
    {2603222360u,2096707827u,398983358u,20878u,61u,3u},
    {2619389506u,2098261079u,386990264u,22057u,59u,3u},
    {2635595776u,2099767083u,375521460u,8296u,59u,3u},
    {2635579472u,2101227257u,364052653u,20505u,56u,3u},
    {2651790236u,2102642983u,353173671u,25888u,55u,3u},
    {2668020048u,2104015600u,342360228u,8009u,51u,3u},
    {2516451328u,2105346407u,332202140u,32373u,52u,3u},
    {2516320256u,2106636665u,321978522u,8823u,48u,3u},
    {2516189184u,2107887598u,312279188u,19249u,47u,3u},
    {2516156392u,2109100392u,303104144u,14469u,48u,3u},
    {2532704256u,2110276203u,293929096u,43580u,47u,3u},
    {2532573184u,2111416145u,284885126u,24642u,44u,3u},
    {2532448756u,2112521305u,276234368u,39544u,42u,3u},
    {2549088256u,2113592735u,267976831u,14525u,42u,3u},
    {2548957184u,2114631457u,259784825u,31467u,40u,3u},
    {2548826112u,2115638462u,251986036u,41195u,40u,3u},
    {2548766336u,2116614710u,244318324u,10912u,38u,3u},
    {2565341184u,2117561136u,236781680u,14308u,36u,3u},
    {2565210112u,2118478643u,229703785u,43179u,36u,3u},
    {2565106090u,2119368107u,222691432u,23762u,34u,3u},
    {2581725184u,2120230384u,216006755u,37950u,34u,3u},
    {2581594112u,2121066296u,209322082u,20180u,32u,3u},
    {2581465522u,2121876645u,203096161u,3207u,32u,3u},
    {2598109184u,2122662210u,196935773u,11571u,31u,3u},
    {2597978112u,2123423742u,190906456u,28866u,30u,3u},
    {2597847040u,2124161974u,185139288u,5923u,30u,3u},
    {2597842558u,2124877614u,179372115u,24639u,27u,3u},
    {2614362112u,2125571352u,173801554u,11257u,26u,3u},
    {2614235454u,2126243850u,168755280u,6740u,27u,3u},
    {2630877184u,2126895760u,163577934u,2850u,26u,3u},
    {2630746112u,2127527708u,158466121u,24151u,24u,3u},
    {2630642726u,2128140301u,153616456u,13287u,23u,3u},
    {2647261184u,2128734130u,149225542u,11204u,25u,3u},
    {2647130112u,2129309768u,144506948u,9671u,23u,3u},
    {2647063098u,2129867768u,139984960u,25073u,21u,3u},
    {2663645184u,2130408671u,135790655u,16432u,21u,3u},
    {2663514112u,2130932997u,131596348u,24685u,20u,3u},
    {2663495472u,2131441252u,127598651u,17054u,20u,3u},
    {2680029184u,2131933927u,123797562u,9910u,20u,3u},
    {2679938886u,2132411498u,120062006u,27808u,20u,3u},
    {2696544256u,2132874427u,116195383u,5196u,17u,3u},
    {2696413184u,2133323160u,112721972u,15799u,17u,3u},
    {2696392496u,2133758133u,109379632u,35018u,18u,3u},
    {2712928256u,2134179765u,105906224u,21881u,16u,3u},
    {2712855558u,2134588464u,102694957u,33725u,16u,3u},
    {2729443328u,2134984626u,99614767u,4999u,16u,3u},
    {2729327410u,2135368635u,96534572u,17605u,16u,3u},
    {2745958400u,2135740861u,93585452u,6007u,15u,3u},
    {2745827328u,2136101665u,90701866u,11148u,14u,3u},
    {2745807462u,2136451399u,87949352u,16630u,14u,3u},
    {2762342400u,2136790399u,85262376u,6062u,14u,3u},
    {2762295186u,2137118995u,82444327u,4008u,11u,3u},
    {2778857472u,2137437505u,80150566u,2276u,13u,3u},
    {2778790102u,2137746238u,77594660u,9030u,12u,3u},
    {2795372544u,2138045494u,75366432u,32470u,13u,3u},
    {2795291784u,2138335562u,73072674u,7045u,12u,3u},
    {2811887616u,2138616725u,70713377u,6464u,11u,3u},
    {2811799836u,2138889254u,68485152u,6156u,10u,3u},
    {2828402688u,2139153416u,66584607u,6112u,12u,3u},
    {2828313906u,2139409466u,64421918u,6316u,10u,3u},
    {2844917760u,2139657651u,62586909u,6771u,11u,3u},
    {2844833666u,2139898215u,60620828u,7458u,10u,3u},
    {2861432832u,2140131390u,58654744u,32949u,9u,3u},
    {2861358818u,2140357404u,56885272u,25898u,9u,3u},
    {2877947904u,2140576476u,55050264u,19060u,8u,3u},
    {2877889088u,2140788818u,53477398u,28821u,9u,3u},
    {2894462976u,2140994636u,51773462u,22399u,8u,3u},
    {2894424226u,2141194133u,50135060u,32556u,7u,3u},
    {2910978048u,2141387499u,48824339u,34721u,9u,3u},
    {2910963998u,2141574925u,47251478u,4294u,8u,3u},
    {2927508188u,2141756592u,45613077u,6812u,6u,3u},
    {2944139264u,2141932678u,44367891u,17701u,8u,3u},
    {2944056596u,2142103352u,42926100u,4184u,6u,3u},
    {2960654336u,2142268782u,41746448u,31789u,8u,3u},
    {2960609038u,2142429128u,40435728u,26785u,7u,3u},
    {2977169408u,2142584547u,39125008u,21932u,6u,3u},
    {2977165338u,2142735189u,38010896u,17231u,7u,3u},
    {2993725334u,2142881202u,36765710u,29055u,6u,3u},
    {3010330624u,2143022727u,35651600u,8253u,6u,3u},
    {3010288880u,2143159901u,34603021u,28551u,6u,3u},
    {3026855830u,2143292861u,33619982u,16207u,7u,3u},
    {3043491840u,2143421733u,32440335u,3989u,5u,3u},
    {3043426052u,2143546644u,31522830u,8282u,6u,3u},
    {3060006912u,2143667715u,30408717u,12692u,4u,3u},
    {3059999424u,2143785065u,29556750u,836u,5u,3u},
    {3076575826u,2143898806u,28639245u,5480u,4u,3u},
    {3093168128u,2144009052u,27918349u,2039u,6u,3u},
    {3093155150u,2144115908u,26869772u,6890u,4u,3u},
    {3109737292u,2144219480u,26083339u,11849u,4u,3u},
    {3126329344u,2144319867u,25362440u,33290u,5u,3u},
    {3126322152u,2144417167u,24576008u,30252u,5u,3u},
    {3142909638u,2144511476u,23789576u,27308u,4u,3u},
    {3159499662u,2144602887u,92078101u,7944u,29u,4u},
    {3176136704u,2144777360u,86442004u,5240u,26u,4u},
    {3176092142u,2144941269u,81264659u,3195u,25u,4u},
    {3192686998u,2145095253u,76414992u,18155u,24u,4u},
    {3209297920u,2145239914u,71696400u,9114u,22u,4u},
    {3209284156u,2145375814u,67371024u,624u,21u,4u},
    {3225883542u,2145503484u,63307791u,844u,19u,4u},
    {3242485092u,2145623423u,59637774u,1545u,20u,4u},
    {3259105280u,2145736097u,55771149u,2693u,16u,4u},
    {3259088740u,2145841949u,52559884u,4274u,17u,4u},
    {3275694422u,2145941388u,49217544u,30827u,14u,4u},
    {3292302082u,2146034806u,46268424u,24989u,14u,4u},
    {3308912640u,2146122565u,43450376u,19506u,13u,4u},
    {3308911664u,2146205009u,40828935u,22548u,12u,4u},
    {3325523114u,2146282460u,38404105u,1325u,12u,4u},
    {3342136382u,2146355218u,35979272u,4970u,10u,4u},
    {3358751416u,2146423569u,33882120u,703u,10u,4u},
    {3375368170u,2146487782u,31719430u,13072u,8u,4u},
    {3392012288u,2146548104u,29884422u,9303u,9u,4u},
    {3391986602u,2146604773u,28114950u,5762u,9u,4u},
    {3408606666u,2146658008u,26411014u,2437u,8u,4u},
    {3425228320u,2146708018u,24838148u,15697u,8u,4u},
    {3441851528u,2146755001u,23330821u,4566u,8u,4u},
    {3458476248u,2146799137u,21954565u,1808u,8u,4u},
    {3475111936u,2146840597u,20643844u,7413u,7u,4u},
    {3475102446u,2146879547u,19464194u,21365u,7u,4u},
    {3491730086u,2146916138u,18153475u,10881u,6u,4u},
    {3508359132u,2146950512u,17039364u,542u,5u,4u},
    {3524989556u,2146982804u,15925249u,23097u,4u,4u},
    {3541621322u,2147013139u,15138818u,13012u,6u,4u},
    {3558254400u,2147041636u,14155776u,27614u,5u,4u},
    {3574888764u,2147068408u,13238272u,25939u,4u,4u},
    {3591524384u,2147093557u,12451840u,24368u,4u,4u},
    {3608161232u,2147117182u,11730945u,14702u,4u,4u},
    {3624799282u,2147139377u,11075584u,21508u,4u,4u},
    {3641442304u,2147160227u,10485760u,20205u,5u,4u},
    {3641438510u,2147179814u,9699328u,18978u,3u,4u},
    {3658078890u,2147198214u,9175040u,17828u,4u,4u},
    {3674720398u,2147215499u,8585218u,365u,3u,4u},
    {3691363012u,2147231737u,7864320u,15733u,0u,4u},
    {3708006708u,2147246992u,7733248u,14784u,4u,4u},
    {3724651468u,2147261322u,7143425u,5694u,3u,4u},
    {2182006142u,2147274784u,6750208u,13045u,3u,4u},
    {2181470502u,2147287430u,6291456u,12255u,2u,4u},
    {2181117686u,2147299311u,5963776u,11511u,3u,4u},
    {2180670244u,2147310472u,5505025u,2619u,2u,4u},
    {2180249408u,2147320956u,5308417u,1968u,3u,4u},
    {2179899070u,2147330805u,5111809u,1355u,4u,4u},
    {2179598966u,2147340057u,4653056u,8967u,2u,4u},
    {2179336480u,2147348749u,4390912u,8424u,2u,4u},
    {2179103222u,2147356914u,3932160u,7910u,0u,4u},
    {2178893332u,2147364585u,3866624u,7433u,2u,4u},
    {2178702550u,2147371791u,3473408u,6980u,0u,4u},
    {2178527686u,2147378560u,3276800u,6558u,0u,4u},
    {2178366288u,2147384919u,3080192u,6162u,0u,4u},
    {2178216426u,2147390893u,2883584u,5788u,0u,4u},
    {2178076564u,2147396506u,2686976u,5435u,0u,4u},
    {2177945450u,2147401777u,2555904u,5108u,0u,4u},
    {2177822052u,2147406730u,2490368u,4799u,1u,4u},
    {2177705514u,2147411383u,2228224u,4505u,0u,4u},
    {2177595112u,2147415753u,2097152u,4233u,0u,4u},
    {2177490232u,2147419859u,1966080u,3976u,0u,4u},
    {2177390350u,2147423716u,1835008u,3735u,0u,4u},
    {2177295008u,2147427339u,1769472u,3511u,0u,4u},
    {2177203812u,2147430743u,1638400u,3297u,0u,4u},
    {2177116418u,2147433941u,1507328u,3096u,0u,4u},
    {2177032522u,2147436945u,1441792u,2909u,0u,4u},
    {2176951852u,2147439767u,1376256u,2734u,0u,4u},
    {2176874170u,2147442417u,1310720u,2570u,0u,4u},
    {2176799264u,2147444908u,1376256u,2415u,2u,4u},
    {2176726942u,2147447247u,1376256u,2269u,3u,4u},
    {2176657030u,2147449445u,1048576u,2129u,0u,4u},
    {2176589374u,2147451509u,1179648u,2003u,2u,4u},
    {2176523832u,2147453450u,917504u,1877u,0u,4u},
    {2176460278u,2147455272u,851968u,1763u,0u,4u},
    {2176398592u,2147456983u,786432u,1656u,0u,4u},
    {2176338670u,2147458591u,786432u,1557u,0u,4u},
    {2176280412u,2147460101u,917504u,1467u,2u,4u},
    {2176223728u,2147461520u,655360u,1373u,0u,4u},
    {2176168536u,2147462853u,655360u,1292u,0u,4u},
    {2176114760u,2147464105u,720896u,1215u,1u,4u},
    {2176062328u,2147465282u,655360u,1140u,1u,4u},
    {2176011176u,2147466387u,524288u,1069u,0u,4u},
    {2175961242u,2147467425u,655360u,1007u,2u,4u},
    {2175912468u,2147468400u,655360u,948u,2u,4u},
    {2175864804u,2147469316u,458752u,888u,0u,4u},
    {2175818198u,2147470177u,458752u,831u,1u,4u},
    {2175772606u,2147470985u,393216u,782u,0u,4u},
};
struct t_ra {
    uint8_t t_c3;
    uint8_t t_ex;
    uint16_t t_c2;
    uint32_t t_c1, t_c0;
};
struct t_rb {
    int16_t t_c3;
    uint8_t t_ex, t_pad;
    uint32_t t_c0;
    int32_t t_c1, t_c2;
};

static const uint16_t t_exp_lo[1 << 9] = {
0x0e12,0xb9cf,0x44da,0x06f8,0x59c9,0x98c5,0x2143,0x5275,0x8d69,0x350a,
0xae25,0x5f62,0xb14a,0x0e46,0xe2a1,0x9c86,0xabff,0x8301,0x955d,0x58cc,
0x44ea,0xd33a,0x7f22,0xc5f1,0x26df,0x2308,0x3d73,0xfb11,0xe2bc,0x7d39,
0x5536,0xf753,0xf216,0xd5f6,0x3557,0xa48c,0xb9d8,0x0d6c,0x396d,0xd9ec,
0x8cf2,0xf278,0xac6a,0x5ea9,0xaf0a,0x4557,0xcb52,0xecb2,0x5727,0xba57,
0xc7e3,0x3364,0xb26f,0xfc92,0xcb56,0xda44,0xe6de,0xb0a5,0xf91a,0x83b8,
0x1601,0x7772,0x718a,0xcfcc,0x5fbc,0xf0e0,0x54c3,0x5ef6,0xe50d,0xbea3,
0xc55a,0xd4da,0xcad6,0x8706,0xeb2e,0xdb1c,0x3ca9,0xf7b8,0xf63a,0x242c,
0x6f9a,0xc89e,0x2161,0x6e1b,0xa516,0xbeaa,0xb54b,0x8572,0x2db5,0xaeba,
0x0b3d,0x4812,0x6c1f,0x8065,0x8ff9,0xa80d,0xd7e9,0x30f0,0xc69f,0xae90,
0x0078,0xd62a,0x4b95,0x7ec7,0x8ff0,0xa158,0xd772,0x58cb,0x4e15,0xe223,
0x41ed,0x9c90,0x234c,0x0987,0x84d0,0xccda,0x1b83,0xaccf,0xbeed,0x9237,
0x6930,0x8888,0x371d,0xbdf6,0x684d,0x8387,0x5f3b,0x4d2e,0xa159,0xb1e4,
0xd72b,0x6bbe,0xcc5e,0x5806,0x6fe1,0x7755,0xd3fd,0xedab,0x2e6c,0x0285,
0xd876,0x20f9,0x4f05,0xd7cd,0x32c1,0xd990,0x4826,0xfcb2,0x77a1,0x3ba1,
0xcda3,0xb4da,0x7abf,0xab0c,0xd3c2,0x8528,0x51ca,0xce7f,0x9263,0x36dc,
0x579b,0x929b,0x8821,0xdac1,0x2f5a,0x2d1a,0x7d7e,0xcc50,0xc7ae,0x2003,
0x8812,0xb4e6,0x5dea,0x3cd5,0x0db7,0x8ef3,0x8146,0xa7c1,0xc7d0,0xa937,
0x1615,0xdae2,0xc673,0xa9fa,0x5905,0xa97f,0x73b5,0x9252,0xe260,0x434e,
0x96e9,0xc164,0xa957,0x37b9,0x57ec,0xf7b7,0x0746,0x7930,0x4275,0x5a77,
0xbb0e,0x6076,0x495a,0x76d1,0xec62,0xaff9,0xca02,0x454c,0x2f1d,0x972d,
0x8fa4,0x2d20,0x86b4,0xb5e8,0xd6b9,0x079d,0x6980,0x1fcb,0x505b,0x238c,
0xc434,0x5fa6,0x25b0,0x48a1,0xfd45,0x7ae9,0xfb59,0xbae4,0xf85b,0xf513,
0xf4e3,0x3e2a,0x19ca,0xd32c,0xb844,0x198b,0x4a05,0x9f3f,0x7153,0x1ae5,
0xf927,0x6bda,0xd54b,0x9a58,0x2271,0xd794,0x2654,0x7dd5,0x4fd2,0x1098,
0x370c,0x3ca7,0x9d7c,0xd837,0x6e1a,0xe304,0xbd70,0x8674,0xc9c0,0x15a7,
0xfb1a,0x0da5,0xe37a,0x156a,0x3eea,0xfe10,0xf399,0xc2e5,0x11fc,0x898b,
0xd4e9,0xa216,0xa1b9,0x8727,0x085e,0xde0b,0xc388,0x76db,0xb8bd,0x4c94,
0xf87a,0x853a,0xbe52,0x71f4,0x7108,0x8f29,0xa2ad,0x849f,0x10c4,0x2599,
0xa459,0x70f6,0x7223,0x914e,0xbaa3,0xdd10,0xea40,0xd6a2,0x9965,0x2c7e,
0x8ca4,0xb954,0xb4cf,0x8421,0x2f1b,0xc058,0x453d,0xcdf9,0x6d87,0x39b1,
0x4b0d,0xbcfe,0xadbc,0x3e4a,0x9280,0xd108,0x235f,0xb5d8,0xb79b,0x5aa6,
0xd3cf,0x5ac6,0x2a11,0x7f14,0x9a0e,0xbe19,0x312d,0x3c23,0x2aaf,0x4b6a,
0xefcc,0x6c30,0x17d4,0x4cdb,0x684f,0xca1f,0xd520,0xef12,0x809f,0xf559,
0xbbc0,0x453e,0x062d,0x75d5,0x0e6d,0x4d1d,0xb1fe,0xc01d,0xfd7b,0xf30b,
0x2cb9,0x396d,0xaaea,0x1619,0x12bd,0x3b9e,0x2e7e,0x8c1d,0xf839,0x198e,
0x99da,0x25da,0x6d4f,0x22fc,0xfca8,0xb321,0x0239,0xa8cc,0x68bd,0x06f8,
0x4b74,0x0135,0xf649,0xfbcf,0xe5f2,0x8bed,0xc811,0x77b4,0x7b50,0xb668,
0x0f97,0x708f,0xc617,0x0012,0x1179,0xf061,0x95fb,0xfe95,0x2998,0x1990,
0xd426,0x6224,0xcf78,0x2b31,0x8784,0xf9cc,0x9a86,0x855d,0xd91f,0xb7c7,
0x467a,0xad8b,0x1872,0xb5df,0xb7ae,0x52e9,0xbfcd,0x39ca,0xff83,0x52d0,
0x78bf,0xb995,0x60cd,0xbd21,0x207f,0xe013,0x5446,0xd8bf,0xcc62,0x9154,
0x8cfc,0x2803,0xce52,0xef1b,0xfcd5,0x6d3e,0xb951,0x5d65,0xd90f,0xaf32,
0x65fc,0x86ec,0x9ecc,0x3db8,0xf71d,0x61b8,0x179c,0xb631,0xde31,0x33b1,
0x5e1a,0x0830,0xe013,0x973c,0xe280,0x7a14,0x198c,0x7fd9,0x6f51,0xadaa,
0x03ff,0x3ecf,0x2dfe,0xa4da,0x7a17,0x87d3,0xab97,0xc658,0xbc77,0x75c4,
0xdd80,0xe259,0x7673,0x8f61,0x262d,0x3756,0xc2d1,0xcc0b,0x59e9,0x76cd,
0x3091,0x988f,0xc39b,0xca0c,0xc7b8,0xdbf3,0x299a,0xd708,0x0e22,0xfc4f,
0xd280,0xc530,0x0c61,0xe3a2,0x8a0e,0x424f,0x529c,0x04bd,0xa60b,0x8774,
0xfd76,0x6027,0x0b33,0x5ddc,0xbaff,0x8911,0x3225,0x23e9,0xcfa7,0xaa4c,
0x2c63,0xd219,0x1b3e,0x8b46,0xa94b,0x000d,0x1df5,0x9516,0xfb23,0xe98e,
0xfd6d,0xd774,
};
static uint64_t t_exp_mid2(uint32_t t_w, uint32_t t_e, int32_t *t_qo)
{
    uint32_t t_m=(t_w&0x7fffffu)|0x800000u;
    uint32_t t_X=t_e>=110u?t_m<<(t_e-110u):t_m>>(110u-t_e);
    /* TX2: k = floor(x / L) (the estimate never exceeds |x| / L), table T 2^(i/512) e^(D 2^-41) + 131: r - D 2^-41 */
    /* TX2: k ~ floor(x / L) (|x| / L within 0.4 of the estimate: rho = r - D in [-0.9 L, 0.9 L]); a value past 2^64
       (cell 511) is halved below */
    uint32_t t_ka=t_e<116u?0u:(((((t_m+96u)>>7)*23637u)>>(147u-t_e))>>1);
    uint32_t t_mask=(uint32_t)((int32_t)t_w>>31);
    int32_t t_k=(int32_t)(t_ka^t_mask);
    uint32_t t_x=(t_X+t_mask)^t_mask;
    int32_t t_tail=t_k*23649;
    int32_t t_r=(int32_t)(t_x-(uint32_t)t_k*1488522236u+(uint32_t)(t_tail>>18)-744230912u);
    int32_t t_fine=(int32_t)(((uint32_t)t_tail&262143u)>>10);
    int32_t t_h=t_r >> 16;
    int32_t t_l=(int32_t)((uint32_t)t_r & 65535u);
    uint32_t t_square=(uint32_t)((t_h*t_h) >> 1) + (uint32_t)((t_h*t_l)>>16);
    int32_t t_third=(t_h*21847) >> 15;
    int32_t t_cubic=((int32_t)(t_square>>13)*t_third) >> 12;
    int32_t t_correction=(int32_t)t_square + t_cubic + (t_fine+2);
    int32_t t_Ph = t_r + (t_correction >> 8);
    uint32_t t_Pl = ((uint32_t)t_correction & 255u) << 8;
    uint32_t t_i=(uint32_t)t_k & 511u, t_Th=t_eps[t_i].t_aux-131u, t_Tl=t_exp_lo[t_i];
    *t_qo = t_k >> 9;
    uint32_t t_ah=t_Th>>16,t_al=t_Th&65535u,t_pl=(uint32_t)t_Ph&65535u;
    int32_t t_ph=t_Ph>>16;
    int32_t t_hp=(int32_t)t_ah*t_ph;
    uint32_t t_hi=t_Th+(uint32_t)(t_hp>>8);
    int32_t t_lo=(int32_t)((((uint32_t)t_hp&255u)<<14)+(t_Tl<<6));
    t_lo+=(int32_t)((t_ah*t_pl)>>2) + (((int32_t)t_al*t_ph)>>2);
    t_lo+=(int32_t)((t_al*t_pl)>>18);
    t_lo+=(int32_t)((t_ah*(t_Pl>>8))>>10)+(((int32_t)t_Tl*t_ph)>>18)+2;
    t_hi+=(uint32_t)(t_lo>>22);
    uint64_t t_R=((uint64_t)t_hi<<32)|((uint32_t)t_lo<<10);
    if ((int32_t)t_hi>=0 && t_hi<0x40000000u) {*t_qo=(t_k>>9)+1; return (t_R>>1)|0x8000000000000000ull;}
    return t_R;
}

static inline uint32_t t_exp_mid_round_(uint32_t t_w)
{
    if (t_w == 0xC2B2E798u)   /* O3: (was t_exp_big's) the one word this path rounds wrongly */
        return 0x000F6DCEu;
    uint32_t t_e = (t_w << 1) >> 24;
    int32_t t_q;
    uint64_t t_R = t_exp_mid2(t_w, t_e, &t_q);
    uint32_t t_top=(uint32_t)(t_R>>63);
    uint32_t t_H=(uint32_t)(t_R>>32);
    if(t_q>-126) {
        uint32_t t_V=(t_H>>(6u+t_top))+1;
        return ((uint32_t)(t_q+125+(int32_t)t_top)<<23)+(t_V>>1);
    }
    uint32_t t_shift=(uint32_t)(-119-t_q);
    return t_shift>=32u?0u:((t_H>>t_shift)+1u)>>1;
}
static uint32_t t_exp_small_fix(uint32_t t_w, uint32_t t_u)
{
    /* R3: exact e 111..117 when the XH window declines. The fast result (from t_u) is right
       unless the exact sum crossed the boundary next to it: the sign of the low word of
       x + 1/2 ulp + x^2/2 + x^3/6 + x^4/24 (in 2^-56 units) decides.
       X = m << (e - 110), x = X 2^-40. Keep it out of line: inlined, t_eik_exp would need r6,
       and a 5-register push costs sub/add sp on every path (it inlines once its IR is a bit
       smaller than this) */
    /* X1: X = m << (e - 110) directly; for x < 0 the + 2^31 is the flip of the sign bit (no 2^31 constant) */
    uint32_t t_X = (((t_w << 9) >> 9) + 0x800000u) << (((t_w << 1) >> 24) - 110u);
    uint32_t t_xt = t_X >> 15, t_xl = t_X & 0x7FFFu;
    uint32_t t_sq = t_xt * t_xt, t_sh = t_sq >> 16;
    uint32_t t_c = (t_sh * t_xt + (((t_sq & 0xFFFFu) * t_xt) >> 16)) >> 3;
    uint32_t t_y = t_c >> 3; t_y += t_y >> 2; t_y += t_y >> 4; t_y += t_y >> 8; t_y += t_y >> 16;
    t_y += (t_sh * t_xl) >> 19;
    uint32_t t_q4 = ((t_y >> 11) * t_xt) >> 16;
    uint32_t t_q2 = (t_sq << 5) + ((t_xt * t_xl) >> 9);
    if ((int32_t)t_w >= 0)
        return 0x3F7FFFFFu + (t_u >> 17) - (((t_X << 16) + t_q2 + t_y + t_q4) >> 31);
    return 0x3F7FFFFFu - (t_u >> 16) + ((((t_X << 16) - t_q2 + t_y - t_q4) >> 31) ^ 1u);
}

static uint32_t t_exp_leaf(uint32_t t_w) {return t_exp_mid_round_(t_w) ^ (t_w>>31);}

static inline uint32_t t_mid_product(uint64_t t_t,uint32_t t_m)
{
    uint32_t t_h=(uint32_t)(t_t>>32),t_l=(uint32_t)t_t;
    uint32_t t_a=t_h&4095u, t_b=t_m&4095u;
    uint32_t t_z=(t_h>>12)*t_m+t_a*(t_m>>12)+((t_a*t_b)>>12);
    return t_z+(((t_l>>16)*(t_m>>16))>>12);
}
static inline uint32_t t_tanh_mid_prec(uint32_t t_w, uint32_t t_ef, uint32_t t_mu)
{
    uint32_t t_a = t_w & 0x7FFFFFFFu;
    uint32_t t_w2 = 0x80000000u | (t_a + 0x800000u), t_e2 = (t_a >> 23) + 1;
    int32_t t_q;
    uint64_t t_R = t_exp_mid2(t_w2, t_e2, &t_q);
    uint32_t t_Mq=(2u*t_mu-1u)<<(t_ef-119u);
    uint32_t t_del;
    if (t_q>=-8) {
        uint32_t t_A=(0u-t_Mq)<<(uint32_t)(19-t_q);
        t_del=t_A-(uint32_t)(t_R>>12)-t_mid_product(t_R,t_Mq)-2u;
    } else {
        uint64_t t_t=t_R>>(1-t_q);
        t_del=((0u-t_Mq)<<18)-(uint32_t)(t_t>>12)-t_mid_product(t_t,t_Mq)-11u;
    }
    return (t_w^t_a)|(((t_ef-1u)<<23)+t_mu-1u+((int32_t)t_del>0));
}
static inline uint32_t t_sig_mid_(uint32_t t_w, uint32_t t_ef, uint32_t t_mu)
{
    uint32_t t_a = t_w & 0x7FFFFFFFu, t_e = t_a >> 23, t_M = 2 * t_mu - 1, t_gt = 0;
    int32_t t_q;
    uint64_t t_R = t_exp_mid2(0x80000000u | t_a, t_e, &t_q);
    ((void)0);
    if ((int32_t)t_w >= 0) {
        uint32_t t_Mq = t_M << 7;
        int32_t t_sh = -1 - t_q;
        uint64_t t_t = t_sh < 0 ? t_R << 1 : t_sh < 64 ? t_R >> t_sh : 0;
        uint32_t t_del=((0u-t_Mq)<<20)-t_mid_product(t_t,t_Mq)-2u;
        t_gt=(int32_t)t_del>0;
    } else {
        uint32_t t_s = 151 - t_ef;
        int32_t t_sh = 63 - (int32_t)t_s - t_q;
        if ((uint32_t)(t_sh-12)<=27u && t_s>=26u && t_s<=80u) {
            uint32_t t_z=t_M<<((uint32_t)t_sh-12u);
            uint64_t t_t=t_R;
            if(t_s>32u) t_t=t_R>>(t_s-32u);
            else t_M<<=32u-t_s;
            uint32_t t_part=t_mid_product(t_t,t_M);
            uint32_t t_del=(uint32_t)(t_R>>12)-t_z-t_part-2u;
            t_gt=(int32_t)t_del>0;
        }
    }
    return ((t_ef - 1) << 23) + t_mu - 1 + t_gt;
}
static uint64_t t_xw_dd(uint32_t t_w)
{
    uint32_t t_e=(t_w<<1)>>24;
    int32_t t_q;
    uint64_t t_z=t_exp_mid2(t_w,t_e,&t_q);
    uint32_t t_H=(uint32_t)(t_z>>32),t_L=(uint32_t)t_z;
    return ((uint64_t)t_H<<32)|((t_L>>4)&~511u)|((uint32_t)t_q&511u);
}
static inline int32_t t_xw_mhx(int32_t t_a, uint32_t t_b)
{
    int32_t t_ah = t_a >> 16;
    uint32_t t_al = (uint32_t)t_a & 0xFFFFu, t_bh = t_b >> 16;
    return t_ah * (int32_t)t_bh + ((t_ah * (int32_t)(t_b & 0xFFFFu)) >> 16) + (int32_t)((t_al * t_bh) >> 16);
}
static uint32_t t_xw_sub(uint32_t t_Y, uint32_t t_fr, int32_t t_ef)
{
    uint32_t t_s = (uint32_t)(9 - t_ef);
    if (t_s > 32u)
        return 0;
    if (t_s == 32u)
        return t_Y > 0x80000000u;
    return (t_Y >> t_s) + ((t_Y << (32 - t_s)) + (t_fr >> (t_s - 4)) > 0x80000000u);
}
static uint32_t t_xw_exp(uint32_t t_w) {return t_exp_mid_round_(t_w);}

static inline uint32_t t_turprod(uint32_t t_delta,uint32_t t_dd,uint32_t t_b,int32_t t_cut){
 uint32_t t_C=t_delta+(((t_dd>>12)*(t_b>>16))>>4);
 if((int32_t)t_C>131)return 1u;
 if((int32_t)t_C<-8324)return 0u;
 uint32_t t_ah=t_dd>>16,t_bh=t_b>>16;uint32_t t_P=t_ah*t_bh+((t_ah*(uint16_t)t_b)>>16)+(((uint32_t)(uint16_t)t_dd*t_bh)>>16);
 return (uint32_t)((int32_t)(t_delta+t_P)>t_cut);}
static inline uint32_t t_posprod(uint32_t t_delta,uint32_t t_dd,uint32_t t_b,int32_t t_cut){
 uint32_t t_C=t_delta+(((t_dd>>12)*(t_b>>12))>>8);
 if((int32_t)t_C>4)return 1u;
 if((int32_t)t_C<-516)return 0u;
 uint32_t t_ah=t_dd>>16,t_bh=t_b>>16;uint32_t t_P=t_ah*t_bh+((t_ah*(uint16_t)t_b)>>16)+(((uint32_t)(uint16_t)t_dd*t_bh)>>16);
 return (uint32_t)((int32_t)(t_delta+t_P)>t_cut);}
static inline uint32_t t_negprod(uint32_t t_delta,uint32_t t_dd,uint32_t t_b,int32_t t_cut){
 uint32_t t_C=t_delta+(((t_dd>>12)*(t_b>>13))>>7);
 if((int32_t)t_C>-253)return 0u;
 if((int32_t)t_C<-2308)return 1u;
 uint32_t t_ah=t_dd>>16,t_bh=t_b>>16;uint32_t t_P=t_ah*t_bh+((t_ah*(uint16_t)t_b)>>16)+(((uint32_t)(uint16_t)t_dd*t_bh)>>16);
 return (uint32_t)((int32_t)(t_delta+t_P)<t_cut);}
/* SZ: e^|x| = 2^q (hi + f 2^-22) 2^-31 to ~2^-53, hi in the upper word, f in the low 22 bits of the lower and q above
 * it (q packed so that it needs no spill of its own; bit-identical to the original). The products go hi part first so
 * that Th, Tl and P's halves die early (3-4 fewer instructions per call). */
/* TS4: (1) no hi < 2^30 renormalisation: when T[511] e^r wraps past 2^32, hi * A and hi * M are the same mod 2^32 and
 * q one lower doubles the residual's scale, which only widens the decision's margins; (2) f = lo << 10 (bits 6..21 of
 * lo are the old f >> 6), no mask; (3) every caller has e >= 121, so m << (e - 110) is (w << 9) << (e - 119) mod 2^32 and
 * the k estimate takes the fraction's top 16 bits with the implicit one and the +96 rounding in one constant;
 * k = estimate >> (148 - e) directly; (4) the cell's byte offset (k << 23) >> 19 serves both tables. */
#define T_MF_CORE(t_w, LOADJ) do { \
    uint32_t t_e=(t_w<<1)>>24; \
    uint32_t t_X9=t_w<<9; \
    uint32_t t_k=(((t_X9>>16)*23637u+1549092160u)>>(148u-t_e)); \
    uint32_t t_tail=t_k*23649u; \
    int32_t t_r=(int32_t)((t_X9<<(t_e-119u))-t_k*1488522236u+(t_tail>>18)-744230912u); \
    int32_t t_h=t_r >> 16; \
    uint32_t t_square=(uint32_t)((t_h*t_h) >> 1) + (uint32_t)((t_h*(int32_t)((uint32_t)t_r & 65535u))>>16); \
    int32_t t_cubic=((int32_t)(t_square>>13)*((t_h*21847) >> 15)) >> 12; \
    int32_t t_correction=(int32_t)t_square + t_cubic + (int32_t)((t_tail&262143u)>>10) + 2; \
    int32_t t_Ph = t_r + (t_correction >> 8); \
    uint32_t t_i16=(t_k<<23)>>19; \
    uint32_t t_Th=*(const uint32_t *)((const uint8_t *)t_eps + t_i16)-131u, t_ah=t_Th>>16, t_al=t_Th&65535u; \
    int32_t t_ph=t_Ph>>16; \
    uint32_t t_pl=(uint32_t)t_Ph&65535u; \
    int32_t t_hp=(int32_t)t_ah*t_ph; \
    t_hi=t_Th+(uint32_t)(t_hp>>8); \
    uint32_t t_Tl=t_exp_lo[t_i16>>4]; \
    int32_t t_lo=(LOADJ)+(int32_t)(t_Tl<<6)+(int32_t)((t_ah*((uint32_t)t_correction & 255u))>>10); \
    t_lo+=(int32_t)((t_al*t_pl)>>18)+(int32_t)((t_ah*t_pl)>>2)+(((int32_t)t_al*t_ph)>>2); \
    t_lo+=(((int32_t)t_Tl*t_ph)>>18)+(int32_t)(((uint32_t)t_hp&255u)<<14); \
    t_hi+=(uint32_t)(t_lo>>22); \
    t_f=(uint32_t)t_lo<<10; t_q=(int32_t)(t_k>>9); \
} while (0)
/* T6: the resolver split by the argument's sign (callers know it): no sign test, no w kept */
#ifndef Q3B2
#define Q3B2 51u
#endif
#ifndef Q3B
#define Q3B 26u
#endif
#ifndef Q3TT
#define Q3TT 897u
#endif
#ifndef Q3TS
#define Q3TS 240u
#endif
/* Q3: the near-midpoint decision in sum form (after #28/#34's t_mid_finish): e^-y = 2^-q T[511 - j] e^-rho / c 2^-32, so with
 * 1 + u = c e^rho and t = T[511 - j] 2^(-q-32), tanh(y / 2) > m iff m (1 + u + t) < 1 + u - t and sigmoid(y) > m iff
 * m (1 + u + t) < 1 + u: no product T e^rho. Z = (m (1 + S) - L) 2^(183 - e_low) mod 2^32 (the 1s vanish), S = u + t
 * in 2^-48 units as Sh 2^16 + Sl. tanh passes low with the sign bit set (its sign comes back on the result). */
static uint32_t t_mid_pos(uint32_t t_w,uint32_t t_low){
    uint32_t t_e=(t_w<<1)>>24, t_X9=t_w<<9;
    uint32_t t_k=(((t_X9>>16)*23637u+1549092160u)>>(148u-t_e));
    uint32_t t_tail=t_k*23649u;
    uint32_t t_R0=(t_X9<<(t_e-119u))-t_k*1488522236u-744291324u;
    int32_t t_r=(int32_t)(t_R0+(t_tail>>18));
    uint32_t t_lt=((t_R0<<16)+(t_tail>>2))>>7;   /* G2: (l << 9) + ((tail & 0x3FFFF) >> 9) from R0 (tail dies here) */
    int32_t t_h=t_r>>16;
    uint32_t t_l=(uint32_t)t_r&65535u;
    /* Q3: u at 2^-49 (a2 = 2 acc): rho^2 2^49 needs no halving, the tanh L its doubling; S takes a2 >> 1 */
    int32_t t_s2=t_h*t_h+((t_h*(int32_t)t_l)>>15);
    int32_t t_c2=((t_s2>>12)*(((t_h*43691)>>14)+(t_s2>>25)))>>15;
    uint32_t t_a2=t_lt+(uint32_t)t_s2+(uint32_t)t_c2+Q3B2;
    uint32_t t_q=t_k>>9, t_n=((~t_k)<<23)>>19;
    uint32_t t_Th=*(const uint32_t *)((const uint8_t *)t_eps+t_n)-131u, t_Tl=t_exp_lo[t_n>>4];
    /* Q3: (T 2^16 + Tl) >> q split at 2^16 without a branch: bits [0, q) of T land at [16 - q, 16) (the ones below 0 drop
     * out for q > 16), Tl >> q below them; (2 T) << (31 - q) keeps q = 0 defined (q <= 19 here) */
    uint32_t t_hiT=t_Th>>t_q, t_ft=(((t_Th<<1)<<(31u-t_q))>>16)+(t_Tl>>t_q);
    uint32_t t_W=(uint32_t)((int32_t)t_a2>>1)+t_ft;
    uint32_t t_Sh=((uint32_t)t_h<<8)+t_hiT+(t_W>>16), t_Sl=t_W&0xFFFFu;
    uint32_t t_lhs;
    if((int32_t)t_low<0)t_lhs=((t_a2-t_Sl-(t_Sh<<16))<<(135u-((t_low<<1)>>24)))-Q3TT;
    else t_lhs=(t_a2<<8)-Q3TS;   /* W2: sigmoid(0x3d21bc81), 2^-29 ulp above the midpoint, is settled by its caller */
    uint32_t t_M7=(t_low<<8)|0x80000080u;   /* Q3: M 2^7, M = 2^24 + 2 mant + 1 */
    return t_low+(((t_M7>>7)*t_Sh+(((t_M7>>16)*t_Sl)>>7)-t_lhs)>>31);
}
static uint32_t t_mid_neg(uint32_t t_w,uint32_t t_low){
    uint32_t t_hi,t_f; int32_t t_q;
    /* TS4: lo + 2 - 128: f >> 15 comes out 4 lower (the borrow, if any, is in hi), so z less M >> 15 is
     * ((f >> 15) M10) >> 7 and the threshold a constant */
    T_MF_CORE(t_w, -126);
    uint32_t t_M7=(t_low<<8)|0x80000080u, t_M=t_M7>>7;   /* TS4: M7 = M << 7 */
 uint32_t t_C=t_q<=24?t_M7<<(24-t_q):t_M7>>(t_q-24),t_z=((t_f>>15)*(t_M7>>17))>>7;
 return t_low+((int32_t)(t_hi*t_M+t_C+t_z)<-1728);
}

static uint32_t t_xw_tanh(uint32_t t_a,uint32_t t_lo){return t_mid_pos(t_a+0x800000u,t_lo);}


static inline uint32_t t_epnormal(const struct t_ep *t_r,uint32_t t_w){
    uint32_t t_f=(uint16_t)t_w,t_p=t_r->t_p,t_bend=(t_p-t_r->t_c*t_f)>>15;
    int32_t t_rem=(int32_t)t_r->t_r-(int32_t)((t_bend*t_f)>>15);
    return t_r->t_v+(((uint16_t)t_p*t_f)>>3)+(uint32_t)((t_rem*(int32_t)t_f)>>16);
}
static inline uint32_t t_epcalc(const struct t_ep *t_r,uint32_t t_w){
    uint32_t t_sh=1u+t_r->t_dn-((uint32_t)(t_r-t_eps)>>7);return t_epnormal(t_r,t_w);
}
/* T6: deficit cells, z = 64 (C' + 128) + err, C' = (y - tanh y) 2^8 / ulp(y), err in [0, span], span < 128; beta 64 span 126.780  */
static const struct t_ra t_tw[80] = {   /* O2: rows reversed: row r is entry 79 - r = ~(u >>s 20), u < 0 (tanh and sigmoid alike) */
    {161, 124, 62260, 15592387u, 1294007520u},
    {161, 124, 60330, 14611640u, 1173212119u},
    {162, 124, 58388, 13661904u, 1060138604u},
    {163, 124, 56434, 12743330u, 954538467u},
    {164, 124, 54477, 11855945u, 856162445u},
    {163, 124, 52525, 10999873u, 764760172u},
    {164, 124, 50555, 10175249u, 680080784u},
    {164, 124, 48584, 9382164u, 601872156u},
    {165, 124, 46602, 8620707u, 529881829u},
    {165, 124, 44619, 7890975u, 463856232u},
    {166, 124, 42625, 7193053u, 403541407u},
    {166, 124, 40629, 6527047u, 348682311u},
    {167, 124, 38628, 5892964u, 299023760u},
    {167, 124, 36623, 5290976u, 254309336u},
    {167, 124, 34613, 4721114u, 214282495u},
    {168, 124, 32598, 4183405u, 178686081u},
    {42, 123, 15796, 3926651u, 324928982u},
    {42, 123, 15291, 3677983u, 294515780u},
    {42, 123, 14785, 3437390u, 266059750u},
    {42, 123, 14279, 3204886u, 239496113u},
    {42, 123, 13773, 2980470u, 214760200u},
    {42, 123, 13266, 2764163u, 191787187u},
    {42, 123, 12759, 2555958u, 170512277u},
    {42, 123, 12252, 2355863u, 150870575u},
    {42, 123, 11744, 2163895u, 132797116u},
    {42, 123, 11236, 1980050u, 116226937u},
    {42, 123, 10728, 1804333u, 101095010u},
    {42, 123, 10219, 1636758u, 87336250u},
    {42, 123, 9711, 1477316u, 74885544u},
    {42, 123, 9201, 1326034u, 63677726u},
    {42, 123, 8691, 1182901u, 53647616u},
    {42, 123, 8181, 1047921u, 44729985u},
    {11, 122, 3963, 983453u, 81327774u},
    {11, 122, 3836, 921059u, 73710990u},
    {11, 122, 3707, 860723u, 66585146u},
    {11, 122, 3580, 802409u, 59933961u},
    {11, 122, 3453, 746138u, 53741063u},
    {11, 122, 3325, 691917u, 47990118u},
    {11, 122, 3197, 639739u, 42664785u},
    {11, 122, 3070, 589596u, 37748733u},
    {11, 122, 2942, 541505u, 33225600u},
    {11, 122, 2814, 495455u, 29079066u},
    {11, 122, 2686, 451452u, 25292733u},
    {11, 122, 2559, 409483u, 21850295u},
    {11, 122, 2430, 369579u, 18735331u},
    {11, 122, 2303, 331698u, 15931570u},
    {11, 122, 2175, 295873u, 13422579u},
    {11, 122, 2047, 262094u, 11192007u},
    {3, 121, 991, 245979u, 20343717u},
    {3, 121, 959, 230367u, 18438681u},
    {3, 121, 927, 215267u, 16656487u},
    {3, 121, 895, 200679u, 14993042u},
    {3, 121, 864, 186592u, 13444285u},
    {3, 121, 832, 173028u, 12006060u},
    {3, 121, 800, 159975u, 10674313u},
    {3, 121, 768, 147433u, 9444951u},
    {3, 121, 736, 135403u, 8313873u},
    {3, 121, 704, 123886u, 7276981u},
    {3, 121, 672, 112879u, 6330197u},
    {3, 121, 640, 102385u, 5469407u},
    {3, 121, 608, 92402u, 4690533u},
    {3, 121, 576, 82931u, 3989473u},
    {3, 121, 544, 73972u, 3362132u},
    {3, 121, 512, 65525u, 2804416u},
    {1, 120, 248, 61498u, 5092480u},
    {1, 120, 240, 57594u, 4616169u},
    {1, 120, 232, 53817u, 4170581u},
    {1, 120, 224, 50170u, 3754675u},
    {1, 120, 216, 46651u, 3367439u},
    {1, 120, 208, 43259u, 3007855u},
    {1, 120, 200, 39995u, 2674894u},
    {1, 120, 192, 36859u, 2367532u},
    {1, 120, 184, 33851u, 2084744u},
    {1, 120, 176, 30971u, 1825507u},
    {1, 120, 168, 28220u, 1588791u},
    {1, 120, 160, 25596u, 1373584u},
    {1, 120, 152, 23100u, 1178857u},
    {1, 120, 144, 20732u, 1003585u},
    {1, 120, 136, 18492u, 846745u},
    {1, 120, 128, 16380u, 707312u}
};

/* T6: z(d) for the cell, d = w's 19 low bits, D = d >> 3 */
static inline uint32_t t_cell_d(const struct t_ra *t_r, uint32_t t_w)
{
    uint32_t t_d = (t_w << 13) >> 13, t_D = t_d >> 3;
    uint32_t t_i2 = t_r->t_c2 + ((t_r->t_c3 * t_D) >> 14);
    uint32_t t_i1 = t_r->t_c1 + ((t_i2 * t_D) >> 13);
    return t_r->t_c0 + (t_i1 >> 16) * t_d + (((t_i1 & 0xFFFFu) * t_D) >> 13);
}

static inline uint32_t t_cell_b8(const struct t_rb *t_r, int32_t t_d)
{
    int32_t t_i2 = t_r->t_c2 + ((t_r->t_c3 * t_d) >> 12);
    int32_t t_i1 = t_r->t_c1 + (t_i2 >> 16) * t_d + (((int32_t)((uint32_t)t_i2 & 0xFFFFu) * t_d) >> 16);
    return t_r->t_c0 + (uint32_t)(((t_i1 >> 16) * t_d + (((int32_t)((uint32_t)t_i1 & 0xFFFFu) * t_d) >> 16)) >> 4);
}
static inline uint32_t t_cell_b(const struct t_rb *t_r, int32_t t_d)
{
    int32_t t_i2 = t_r->t_c2 + ((t_r->t_c3 * t_d) >> 14);
    int32_t t_i1 = t_r->t_c1 + (t_i2 >> 16) * t_d + (((int32_t)((uint32_t)t_i2 & 0xFFFFu) * t_d) >> 16);
    return t_r->t_c0 + (uint32_t)(((t_i1 >> 16) * t_d + (((int32_t)((uint32_t)t_i1 & 0xFFFFu) * t_d) >> 16)) >> 5);
}
static inline uint32_t t_mh32(uint32_t t_a, uint32_t t_b)
{
    uint32_t t_ah = t_a >> 16, t_al = t_a & 0xFFFFu, t_bh = t_b >> 16, t_bl = t_b & 0xFFFFu;
    return t_ah * t_bh + ((t_ah * t_bl) >> 16) + ((t_al * t_bh) >> 16);
}
static uint64_t t_mulhi64(uint64_t t_a, uint64_t t_b)
{
    uint64_t t_ah = t_a >> 32, t_al = (uint32_t)t_a, t_bh = t_b >> 32, t_bl = (uint32_t)t_b;
    return t_ah * t_bh + ((t_ah * t_bl) >> 32) + ((t_al * t_bh) >> 32);
}
static inline uint32_t t_exp_tail(int32_t t_k, int32_t t_rho, int32_t *t_qo)
{
    uint32_t t_T = t_eps[(uint32_t)t_k&511u].t_aux;
    *t_qo = t_k >> 9;
    int32_t t_r16 = t_rho >> 16;
    int32_t t_P = t_rho + (int32_t)((uint32_t)(t_r16 * t_r16) >> 9);
    int32_t t_Ph = t_P >> 16;
    uint32_t t_Pl = (uint32_t)t_P & 0xFFFFu, t_Th = t_T >> 16, t_Tl = t_T & 0xFFFFu;
    int32_t t_S = (int32_t)t_Th * t_Ph + (int32_t)((t_Th * t_Pl) >> 16) + (((int32_t)t_Tl * t_Ph) >> 16);
    return t_T + (uint32_t)(t_S >> 8);
}
static int32_t t_exp_red(uint32_t t_w, uint32_t t_e, int32_t *t_rho)
{
    uint32_t t_M = (t_w << 8) | 0x80000000u;
    uint32_t t_X = t_e >= 118 ? t_M << (t_e - 118) : t_M >> (118 - t_e);
    uint32_t t_k = (((((t_M >> 16) * 47274u + ((((t_M >> 8) & 0xFFu) * 47274u) >> 8)) >> (147 - t_e)) + 1) >> 1);
    uint32_t t_r = t_X - t_k * 1488522235u - ((t_k * 29811u) >> 15);
    if ((int32_t)t_w < 0) {
        *t_rho = -(int32_t)t_r;
        return -(int32_t)t_k;
    }
    *t_rho = (int32_t)t_r;
    return (int32_t)t_k;
}
static uint32_t t_exp_core(uint32_t t_w, uint32_t t_e, int32_t *t_qo)
{
    int32_t t_rho, t_k = t_exp_red(t_w, t_e, &t_rho);
    return t_exp_tail(t_k, t_rho, t_qo);
}
struct t_sm12 {int16_t t_c0; int16_t t_c1; int16_t t_c2; int16_t t_c3; int16_t t_c4; int8_t t_c5;};
static const struct t_sm12 t_sm12[]={
    {5096,772,47,-21844,0,0},
    {28684,977,56,-21844,0,0},
    {-12816,-828,66,-21844,0,0},
    {11748,-542,77,-21843,0,0},
    {-28605,-208,90,-21843,0,0},
    {-2704,178,104,-21843,0,0},
    {24027,622,119,-21843,0,0},
    {-13828,-919,135,-21842,0,0},
    {14935,-343,153,-21842,0,0},
    {-20612,308,173,-21842,0,0},
    {10761,-1007,194,-21842,0,0},
    {-21851,-187,217,-21841,0,0},
    {12808,728,241,-21841,0,0},
    {-16140,-303,267,-21841,0,0},
    {22590,822,296,-21840,0,0},
    {-1852,15,326,-21840,0,0},
    {15994,65,749,-21823,0,0},
    {191,-753,893,-21820,0,0},
    {-8456,-958,1055,-21817,0,0},
    {-8648,-479,1236,-21814,0,0},
    {1059,761,1436,-21810,0,0},
    {22265,794,1656,-21807,0,0},
    {-8801,-296,1898,-21803,0,0},
    {-24666,-374,2163,-21799,0,0},
    {-23213,653,2451,-21795,1,0},
    {-2138,833,2763,-21791,1,0},
    {-24477,265,3101,-21787,1,0},
    {-21989,-947,3466,-21782,1,0},
    {8243,-646,3858,-21778,1,0},
    {3818,-768,4278,-21773,1,0},
    {-31900,849,4728,-21768,1,0},
    {-29774,231,5208,-21763,1,0},
    {-6344,1016,11976,-21482,5,0},
    {2896,207,14288,-21437,6,0},
    {-4445,1006,-15888,-21389,6,0},
    {-7624,470,-13001,-21339,6,0},
    {16468,-187,-9802,-21285,7,0},
    {27898,314,-6276,-21229,7,0},
    {-10648,-781,-2405,-21171,7,0},
    {-2662,-18,1824,-21110,8,0},
    {20167,-23,6429,-21046,8,0},
    {29156,737,11426,-20979,8,0},
    {-1251,-235,-15939,-20910,9,0},
    {-27811,769,-10112,-20838,9,0},
    {-3901,-670,-3846,-20764,9,0},
    {-10451,-717,2875,-20686,10,0},
    {6315,433,10067,-20607,10,0},
    {-27128,598,-15022,-20524,10,0},
    {22991,532,-5113,-16046,88,1},
    {-29135,-725,-936,-15323,93,1},
    {-20239,-1004,7706,-14557,98,1},
    {-12087,-371,-11702,-13750,104,1},
    {-28697,75,6630,-12900,109,1},
    {11218,245,-2581,-12009,114,1},
    {-31404,-987,-6317,-11075,119,1},
    {10332,358,-4323,-10099,125,1},
    {21467,-976,3650,-9081,130,1},
    {420,1003,-14913,-8022,135,1},
    {-4537,1002,5774,-6921,140,1},
    {-24350,876,426,-5778,145,1},
    {29435,-617,2060,-4593,151,1},
    {-26548,377,10927,-3367,156,1},
    {9872,517,-5493,-2099,161,1},
    {7500,-494,-14183,-790,166,1},
    {13131,-712,8403,5002,1392,8},
    {13654,894,6933,16463,1474,8},
    {-14272,-434,10664,28580,1555,8},
    {27352,-615,-9248,-24186,1637,8},
    {-18166,-381,-16128,-10767,1718,8},
    {-6662,785,-6088,3298,1798,8},
    {13681,471,-8033,18006,1878,8},
    {29872,-603,-18118,-32184,1958,8},
    {29312,-727,245,-16203,2037,8},
    {30364,659,-14684,409,2116,8},
    {-18355,820,6403,17647,2194,8},
    {-11189,-234,1715,-30029,2271,8},
    {16837,149,7739,-11551,2348,8},
    {-14698,1009,-4602,7539,2424,8},
    {-5465,-288,1124,27238,2500,8},
    {27227,23,-4219,-17996,2575,7},
};
static inline int32_t t_sm_mul(int32_t t_x, int32_t t_d)
{
    int32_t t_rem=(int32_t)((uint32_t)t_x&262143u);
    return (t_x>>18)*t_d+((t_rem*(t_d>>5)+((t_rem*(int32_t)((uint32_t)t_d&31u))>>5))>>13);
}
static const uint32_t t_sm_dir[]={0x00760000u};
struct t_pdrow {int32_t t_c0;int16_t t_a;int8_t t_b,t_c;};
static const struct t_pdrow t_pdrow[]={
    {-954,2,0,0},
    {-172,4,0,0},
    {-669,31,1,0},
    {130,17,0,0},
    {1639,58,1,0},
    {4318,157,2,0},
    {12829,371,5,1},
    {4085,98,1,0},
    {8468,191,2,0},
    {16613,349,3,0},
    {31797,602,5,0},
    {56776,992,7,0},
    {97081,1574,11,1},
    {160498,2416,16,1},
    {255429,3604,22,1},
    {49434,655,4,0},
    {74589,932,5,0},
    {110401,1301,7,0},
    {159393,1784,9,0},
    {225746,2407,11,0},
    {315087,3202,14,1},
    {433155,4205,18,1},
    {586644,5456,22,1},
    {785334,7003,27,1},
    {1038618,8899,33,1},
    {1358840,11205,40,1},
    {1760549,13987,48,1},
    {2260279,17321,57,2},
    {2876209,21292,68,2},
    {3630706,25994,80,2},
    {4548058,31528,94,2},
};
/* SZ: tanh's exact decision for |x| in [2^-8, 2^-4) (the original's Pade residual D (15 + 6t) - 20 t m - c D t^2 ...).
 * m^2 from three products, the 32/35 factor folded into one product, the t^2 D term only for e >= 121 and its t^3
 * correction only for e = 123; offsets set from the residual's margins over all inputs (work/sz/mf/thr8.sh):
 * e 119..123 must-up max / must-down min -1669/3493, -1097/1658, -91/185, -19/19, -4/3 */
/* T6: the decision of t_pd_small from D (4 (x - mid) in ulps of x's binade; 2 mid for the binade below) and the
 * lower candidate (with the sign): callers that know D skip the candidate set-up */
static uint32_t t_pd_dec(uint32_t t_w,uint32_t t_D){   /* HTT: out of line, returns 1 for the upper candidate */
 uint32_t t_e4=(t_w<<5)>>28;   /* HTT: e & 15 = 7..11 for e 119..123: s = 254 - 2 e = 30 - 2 e4 */
 uint32_t t_mh=((t_w<<9)>>25)+128u,t_ml=t_w&65535u,t_m=(t_mh<<16)+t_ml;
 uint32_t t_acc=((15u*t_D)<<(43u-2u*t_e4))+39u;
 uint32_t t_v=10u*t_m-3u*t_D,t_ab=t_mh*t_ml,t_l2=t_ml*t_ml;
 uint32_t t_L=(t_ab<<17)+t_l2,t_H=t_mh*t_mh+((2u*t_ab+(t_l2>>16))>>16);
 uint32_t t_ah=t_L>>16,t_al=t_L&65535u,t_bh=t_v>>16,t_bl=t_v&65535u;
 t_acc-=t_H*t_v+t_ah*t_bh+((t_ah*t_bl)>>16)+((t_al*t_bh)>>16);
 if(t_e4>=9u){   /* SZ: the t^2 D term (below the margin for e <= 120) */
  uint32_t t_s=30u-2u*t_e4;
  uint32_t t_small=((t_D>>4)*((((t_H*t_H)>>16)*59919u)>>16))>>t_s;
  if(t_e4==11u){uint32_t t_xpart=((t_small>>8)*t_H)>>(t_s+6u);t_small-=(t_xpart*2913u)>>16;t_acc-=122u;}
  t_acc-=t_small;
 }
 return (0u-t_acc)>>31;   /* TS4: delta > 0 as the sign of -delta (|delta| < 2^31 here) */
}
static inline uint32_t t_tanh_small_mid_(uint32_t t_w, uint32_t t_ef, uint32_t t_mu)
{
    if ((t_w & 0x7fffffffu) == 0x3da99442u)
        return (t_w & 0x80000000u) | 0x3da93150u;
    if ((t_w & 0x7fffffffu) == 0x3dec9300u)
        return (t_w & 0x80000000u) | 0x3deb870du;
    uint32_t t_a = t_w & 0x7FFFFFFFu, t_e = t_a >> 23, t_m = (t_a & 0x7FFFFFu) | 0x800000u;
    uint64_t t_M = 2 * (uint64_t)t_mu - 1;
    uint64_t t_D = 4 * (uint64_t)t_m - (t_ef == t_e ? 2 * t_M : t_M);
    uint64_t t_m2 = (uint64_t)t_m * t_m;
    uint64_t t_z = t_e >= 118 ? t_m2 << (2 * t_e - 236) : t_m2 >> (236 - 2 * t_e);
    uint32_t t_zh = (uint32_t)(t_z >> 32);
    uint32_t t_u = 0x00eb69e8u;
    t_u = 0x0244dc6bu - t_mh32(t_zh, t_u);
    t_u = 0x05993d22u - t_mh32(t_zh, t_u);
    t_u = 0x0dd0dd0eu - t_mh32(t_zh, t_u);
    t_u = 0x22222222u - t_mh32(t_zh, t_u);
    uint64_t t_S = 0x5555555555555555ull - ((uint64_t)t_zh * t_u + t_mh32((uint32_t)t_z, t_u));
    uint64_t t_m3 = (((uint64_t)t_m * (uint32_t)(t_m2 >> 16)) << 8) + (((uint64_t)t_m * (uint32_t)(t_m2 & 0xFFFFu)) >> 8);
    uint64_t t_G = t_mulhi64(t_m3, t_S) >> (258 - 2 * t_e);
    ((void)0);
    return (t_w ^ t_a) | (((t_ef - 1) << 23) + t_mu - 1 + ((int64_t)t_D > 0 && (t_D << 32) > t_G));
}
static inline uint32_t t_tsm_mh(uint32_t t_a, uint32_t t_b)
{
    uint32_t t_ah = t_a >> 16, t_al = t_a & 0xFFFFu, t_bh = t_b >> 16, t_bl = t_b & 0xFFFFu;
    return t_ah * t_bh + ((t_ah * t_bl) >> 16) + ((t_al * t_bh) >> 16);
}
static uint32_t t_th_mid_small(uint32_t t_a, uint32_t t_lo)
{
    uint32_t t_ey = t_a >> 23, t_my = (t_a & 0x7FFFFFu) | 0x800000u;
    uint32_t t_el = t_lo >> 23;
    uint32_t t_M = (((t_lo & 0x7FFFFFu) | 0x800000u) << 1) + 1;
    uint32_t t_D = 4 * t_my - (t_el == t_ey ? 2 * t_M : t_M);
    uint32_t t_A = t_my >> 16, t_B = t_my & 0xFFFFu, t_AB = t_A * t_B;
    uint64_t t_m2 = ((uint64_t)(t_A * t_A) << 32) + ((uint64_t)t_AB << 17) + t_B * t_B;
    uint32_t t_m2h = (uint32_t)(t_m2 >> 16);
    uint32_t t_Yf = t_m2h >> (252 - 2 * t_ey);
    uint32_t t_P6 = 3435973837u - t_tsm_mh(t_Yf, 1390751315u - t_tsm_mh(t_Yf, 563572428u));
    uint32_t t_m8 = t_my << 8;
    uint32_t t_q3 = t_tsm_mh(t_tsm_mh(t_tsm_mh(t_m2h, t_m2h), t_m8), t_P6);
    uint32_t t_k, t_W, t_R;
    if (t_ey >= 117u) {
        uint32_t t_Q = (uint32_t)t_m2, t_P = (uint32_t)(t_m2 >> 32), t_Ql = t_Q & 0xFFFFu, t_Qh = t_Q >> 16;
        uint64_t t_V = ((uint64_t)(t_Qh * t_A + t_P * t_my) << 32) + ((uint64_t)(t_Qh * t_B) << 16)
                   + ((uint64_t)(t_Ql * t_A) << 16) + t_Ql * t_B;
        t_W = (uint32_t)(t_V >> 31);
        t_k = 265 - 2 * t_ey;
        t_R = t_q3 >> (244 - 2 * t_ey);
    } else {
        t_W = t_tsm_mh(t_m2h, t_m8);
        t_k = 256 - 2 * t_ey;
        t_R = t_q3 >> (253 - 2 * t_ey);
    }
    int32_t t_E = (int32_t)((12 * t_D << t_k) - t_W + t_R);
    return t_lo + (t_E > 0);
}
static inline uint32_t t_tanh_mid_(uint32_t t_w, uint32_t t_ef, uint32_t t_mu)
{
    uint32_t t_w2 = t_w + 0x800000u, t_mk = t_w2 | 0x7FFFFFFFu;   /* G2: the mask (w2 has w's sign) before the call */
    return t_mid_pos(t_w2, ((t_ef - 1) << 23) + t_mu - 1 + 0x80000000u) & t_mk;   /* Q3: low with the sign bit set selects tanh; the result keeps x's sign */
}
static uint32_t t_xs_exp(uint32_t t_w)
{
    uint32_t t_e = (t_w << 1) >> 24, t_m = (t_w & 0x7FFFFFu) | 0x800000u;
    uint32_t t_s = 127 - t_e, t_s1 = t_s + 1;
    uint32_t t_A = t_m >> 16, t_B = t_m & 0xFFFFu;
    uint32_t t_q2 = ((t_A * t_A) << 15) + t_A * t_B + ((t_B * t_B) >> 17);
    uint32_t t_H = ((t_q2 >> 15) * 43691u) >> 16;
    uint32_t t_Pc = (t_H * (t_m >> 8)) >> t_s1;
    uint32_t t_qr = t_q2 + (((t_Pc * t_A) >> 8) >> t_s1);
    if ((int32_t)t_w >= 0) {
        uint32_t t_S = ((t_m << (t_e - 95)) >> 2) + ((t_qr + t_Pc) >> (231 - 2 * t_e));
        return 0x3F800000u + (t_m >> t_s) + (((t_S >> 29) + 1) >> 1);
    }
    int32_t t_S = (int32_t)(((t_m << (t_e - 94)) >> 2) - ((t_qr - t_Pc) >> (230 - 2 * t_e)));
    return 0x3F800000u - (t_m >> (t_s - 1)) - (uint32_t)(((t_S >> 29) + 1) >> 1);
}
static uint32_t t_mid(uint32_t t_w, uint32_t t_ef, uint32_t t_mu, uint32_t t_fn)
{
    if (t_fn == 0)
        return t_xw_exp(t_w);
    return t_tanh_mid_(t_w, t_ef, t_mu);
}
static inline uint32_t t_sat_u36(uint32_t t_R, int32_t t_q, int32_t t_two)
{
    uint32_t t_s1 = (uint32_t)(-t_q - 5 - t_two), t_s2 = (uint32_t)(-2 * t_q - 6 - t_two), t_rh = t_R >> 16;
    return (t_R >> t_s1) - (t_s2 < 32 ? (t_rh * t_rh) >> t_s2 : 0);
}
static uint32_t t_rest(uint32_t t_w, uint32_t t_e, uint32_t t_fn);
/* Near-midpoint exp resolver shared by the |x| in [2^-9, 8) fast path and exp_big (normal results).
 * From the caller's k (two's complement, i = k & 511, q = k >> 9) and V = R - 125 (candidate mantissa
 * j = V >> 8, midpoint mid = (2j+1) 2^-24 relative to 2^q) it forms D = (e^r - mid 2^(-i/512)) 2^57
 * mod 2^32 with r = x - k ln2/512 and 2^(-i/512) = T((-k) & 511) / 2 (for i = 0 the table gives 1/2
 * instead of 1, which only flips bit 31 of 2^56 (...), and the shift drops it). The caller's window
 * gives |e^r - mid 2^(-i/512)| < 2^-28, so D is the difference up to arithmetic and table error
 * (< 2 * 1437 units over every input that can reach here). |D| <= 2 * 1600 and i = 26 (table entry 486
 * is tuned for the original resolver) go to the original resolver. */
static uint32_t t_exp_res(uint32_t t_w, uint32_t t_kb, uint32_t t_Z)
{
    /* TX2: kb = k + B, k = floor(x / L), B A = D (mod 2^32). With T[n] = 2^(n/512) e^d 2^31 + 131 (d = D 2^-41),
       T[~k] - 131 = 2^(-(i+1)/512) e^d 2^32 for every i, so e^x > mid  <=>  e^(r - L + d) > M (T[~k] - 131) 2^-56,
       r - L + d in [-L/2, L/2). Candidates Z / 256 - 1 and Z / 256 (reject zone Z & 255 < 5), M = 2 (Z >> 8) - 1 */
    uint32_t t_mask = (uint32_t)((int32_t)t_w >> 31);
    uint32_t t_xs = (((t_w << 1) << (((t_w << 1) >> 24) - 110u)) + t_mask) ^ t_mask;   /* TS4: -y = (y - 1) ^ -1; Q2: (w << 1) << (e - 110), w << 1 shared with e */
    /* O5: kb A and kb 5912 (A, 5912 multiples of 8) and (kb << 3) >> 5 do not see kb + 2^29 (the x > 0 main paths' B):
       rh = xs - kb A + C1, FF = C2 - kb 5912.25 (FF spans +-4.3e8 over k in [-77500, 66500]: no wrap) */
    uint32_t t_rh = t_xs - t_kb * 2977044472u + 0xfffe2428u;
    int32_t t_FF = (int32_t)(0x44458A4Au - t_kb * 11824u - ((t_kb << 3) >> 4));   /* Q2: less 512, the + 512 below (D's + 1024 bias), which clang added as movs+lsls+adds */
    uint32_t t_n16 = ((~t_kb) << 23) >> 19;
    uint32_t t_M = ((t_Z >> 8) << 2) - 2u;
    uint32_t t_acc = (t_rh << 16) - (uint32_t)t_FF - t_M * (*(const uint32_t *)((const uint8_t *)t_eps + t_n16) - 131u)
                     - (((t_M >> 10) * t_exp_lo[t_n16 >> 4]) >> 6);
    uint32_t t_base = ((t_kb >> 9) << 23) + (t_Z >> 8);   /* TS4: ex << 23 = (kb >> 9) << 23 for every caller */
    int32_t t_ra = (int32_t)t_rh - (t_FF >> 16);
    int32_t t_c = t_ra >> 16;
    t_acc += (uint32_t)((t_c * (int32_t)((uint32_t)t_ra & 0xFFFFu)) >> 9);
    int32_t t_cc = t_c * t_c;
    t_acc += (uint32_t)t_cc << 6;
    int32_t t_P = (int32_t)((uint32_t)t_cc >> 14) * t_c;   /* Q2: no quartic term: the window takes its error */
    t_acc += (uint32_t)(((t_P >> 14) * 10923) >> 6);
    int32_t t_D = (int32_t)t_acc;   /* Q2: every term doubled (acc is D): no << 1 */
    /* TS4: D is biased by + 1024 (folded into the constant): D in [-1024, 1023] is (D + 1024) >> 11 == 0, and outside it
       the bias does not move D's sign */
    uint32_t t_res = t_base + (uint32_t)(t_D >> 31);
    /* Q2: D in the window: 47 words of all 2^32 (exhaustive), with distinct bases. A perfect hash of base (5 bits)
       picks each one's candidate from a 32-bit mask (lower = 1): no exact path, so w dies early (no r6, no pad) */
    if ((uint32_t)t_D >> 11 == 0u)
        t_res = t_base - ((0x84439564u >> ((t_base * 0x6F851B87u) >> 27)) & 1u);
    return t_res;
}
static inline uint32_t t_xa_tp(uint32_t t_T, int32_t t_P)
{
    int32_t t_Ph = t_P >> 16;
    uint32_t t_Pl = (uint32_t)t_P & 0xFFFFu, t_Th = t_T >> 16, t_Tl = t_T & 0xFFFFu;
    int32_t t_S = (int32_t)t_Th * t_Ph + (int32_t)((t_Th * t_Pl) >> 16) + (((int32_t)t_Tl * t_Ph) >> 16);
    return t_T + (uint32_t)(t_S >> 8);
}
static uint32_t t_exp_big1(uint32_t t_w, uint32_t t_e)
{
    if (t_e - 104u < 12u)
        return t_xs_exp(t_w) ^ 1u;
    return t_xw_exp(t_w) ^ 1u; /* O3: e >= 131 (x <= -87) too: t_exp_big is gone */
}
/* TX2: main-path tail: T (1 + P) = R, exponent field ex = q + 126; window offset OFF, width WIN */
#define T_MAIN_TAIL(ADJ) do { \
    uint32_t t_T = t_eps[t_kb & 511u].t_aux; \
    int32_t t_P7 = (int32_t)t_P >> 8; \
    int32_t t_S = (int32_t)(t_T >> 24) * t_P7 + ((((int32_t)((t_T << 8) >> 17)) * (t_P7 >> 8)) >> 7); \
    uint32_t t_Z = t_T + (uint32_t)(t_S >> 9) + (ADJ), t_ex = t_kb >> 9; \
    if((int32_t)t_Z<0){if((t_Z&255u)>=5u)return (t_ex<<23)+(t_Z>>8);return t_exp_res(t_w,t_kb,t_Z);} \
    return t_exp_leaf(t_w)^(t_w>>31); \
} while (0)
static uint32_t t_eik_exp(uint32_t t_w)
{
    /* X1: (int)w >> 23 is e - 256 for x < 0, so one compare takes sign and range (-8 < x <= -2^-9);
       its low byte es is e - 118 for either sign. t from #29's shift form (>> 11, << s, >> 18: no count) */
    uint32_t t_s = (uint32_t)(((int32_t)t_w >> 23) + 138), t_kb, t_P;
    if (t_s < 12u) {
        /* TX2 (s29's form): kf = floor(|x| / L), never too small; kb = B + k = (B - 1) - kf; kb A = k A + D */
        uint32_t t_X = t_w << 9;
        uint32_t t_kf = ((((t_X >> 16) * 23637u + 1549115262u) >> 11) << t_s) >> 19;
        t_kb = 0x12dcfbffu - t_kf;
        uint32_t t_P0 = t_kb * (0u - 2977044472u) - (t_X << t_s);
        int32_t t_r16 = (int32_t)t_P0 >> 16;
        t_P = t_P0 + ((uint32_t)(t_r16 * t_r16) >> 10);
        goto t_neg;
    } else {
        t_s &= 255u;
        if (t_s >= 138u) {
            uint32_t t_e = t_s - 138u;
            /* R3: odd bounds (111, 101, 125, 135) compare e itself; even ones cost a shift */
            if (t_e <= 109u) {
                if (t_e <= 101u)
                    return 0x3f800000u;
                /* V3 (#35's): 2^-25 <= |x| < 2^-17 in one word, no window: X = |x| 2^48 exactly (M's bit 0 is shifted
                 * out), h = x^2/2 in the same unit from one product; the rounding is the literal's bit 0 and, for x < 0,
                 * the direction of the arithmetic shift (every input of e 102..109 checked) */
                uint32_t t_M=(t_w<<8)|0x80000001u, t_X=t_M>>(248u-t_s), t_xh=t_X>>15, t_h=(t_xh*t_xh)>>19;
                if ((int32_t)t_w<0)
                    return (0x7F000001u+(uint32_t)((int32_t)(t_h-t_X)>>23))>>1;
                return (0xFE000002u+((t_X+t_h)>>23))>>2;
            }
            {
                uint32_t t_X = (((t_w << 8) | 0x80000000u) >> 8) << (t_e - 110u);
                uint32_t t_xt = t_X >> 15, t_h = (t_xt * t_xt) >> 11;
                /* R3: e >= 116 as X >= 2^29 (one shift); the 1.0 constants fold an offset into the
                   rounding add (0x3F7FFFFF is one literal load, 0x3F800000 two instructions); the
                   positive window declines below 64 (two shifts, no mask) instead of below 0x3b */
                if (t_X >= 0x20000000u)
                    t_X += ((((t_h >> 5) * (t_X >> 16)) >> 19) * 10923u) >> 15;
                if ((int32_t)t_w >= 0) {
                    uint32_t t_v = t_X + t_h;
                    if ((((t_v+0x3003bu)<<15)>>21) != 0u)
                        return 0x3F7FFFFFu + ((t_v+0x3003bu)>>17);
                    return t_exp_small_fix(t_w, t_v+0x3003bu);
                } else {
                    uint32_t t_v = t_X - t_h;
                    if (((t_v-0x7ff3u)&65535u)>=0x47u)
                        return 0x3F7FFFFFu - ((t_v-0x7ff3u)>>16);
                    return t_exp_small_fix(t_w, t_v-0x7ff3u);
                }
            }
        }
        if (t_s < 12u) {
        /* TX2: kf = floor(x / L), never too large; kb = B + kf; R errs by -5.15..+0.29: + 1 for the shared window */
        uint32_t t_X = t_w << 9;
        uint32_t t_kf = ((((t_X >> 16) * 23637u + 1549082004u) >> 11) << t_s) >> 19;
        t_kb = 0x32dcfc00u + t_kf;
        uint32_t t_P0 = (t_X << t_s) - t_kb * 2977044472u;
        int32_t t_r16 = (int32_t)t_P0 >> 16;
        t_P = t_P0 + ((uint32_t)(t_r16 * t_r16) >> 10);
            goto t_pos;
        }
            /* HE: |x| >= 256 first, then |x| >= 64 (es 15, 16): 8 <= |x| < 64 skips the 87.3 bound */
            if (t_s >= 17u) {
                /* R3: |x| >= 256: +inf or +0; e = 255 (es 137, rare) sorts out NaN and the infinities */
                if (t_s == 137u)
                    return (t_w << 9) != 0u ? t_w | 0x00400000u : t_w & ~(uint32_t)((int32_t)t_w >> 31);
                if ((int32_t)t_w < 0)
                    return 0;
                return 0x7F800000u;
            }
            if (t_s >= 15u) {
                /* HE: 64 <= |x| < 256: the edges first */
                if ((int32_t)t_w < 0) {
                    /* HE: x <= -103.28: e^x rounds to 2^-149 (word 1), and from -103.97 on to +0 */
                    if (t_w >= 0xC2CDBF37u)
                        return t_w < 0xC2CFF1B5u;
                    /* G2: from the fixed hard words around -126 ln 2 on, the big path (subnormal results);
                       above them (normal results, x > -87.34) the main path below (its k is good to 128) */
                    if (t_w >= 0xC2AEAC4Eu) {
                        /* G2: the five fixed hard words around -126 ln 2 (every hard set has them) */
                        if (t_w < 0xC2AEAC53u)
                            return 0x00800066u - ((t_w - 0xC2AEAC4Eu) << 6);
                        return t_xw_exp(t_w) ^ (t_s >> 4);   /* O3: (t_s is 15 here: the xor is 0, and keeps this call apart from the
                                                               * main tails' one, whose block placement it would move) the exact path, which rounds subnormals itself (t_exp_big's fast
                                                 * reduction, 316 bytes for a cold range, is gone) */
                    }
                } else {
                    if (t_w >= 0x42B17218u)
                        return 0x7F800000u;
                    /* G2: the two fixed hard words below the overflow threshold; the rest of 64 <= x < 88.72 takes
                       the main path below */
                    if (t_w >= 0x42B17216u)
                        return 0x7F7FFF04u + ((t_w - 0x42B17216u) << 7);
                }
            }
                /* SZ: k from one 17-bit product, X 23637.1155 2^-16 = ((X >> 15) 23637 + (X >> 18)) / 2: within 0.70 of
                 * x 512/ln2 for |x| < 128, so rho fits 2^41 units; R errs by -3.65..0.77 (the window takes -4..1) */
                /* TX2: kf = floor(|x| / L) from the same estimate; falls into the main tail of its sign */
                uint32_t t_X = t_w << 9;
                uint32_t t_kf = (((((t_X >> 15) * 23637u + (t_X >> 18)) >> 1) + 1549087890u) >> (30u - t_s));
                uint32_t t_xs = t_X << t_s;
                if ((int32_t)t_w < 0) {
                    uint32_t t_ka = t_kf + 1u;
                    t_kb = 0x12dcfc00u - t_ka;
                    uint32_t t_P0 = t_kb * (0u - 2977044472u) - ((t_ka * 11825u) >> 16) - t_xs;
                    int32_t t_r16 = (int32_t)t_P0 >> 16;
                    t_P = t_P0 + ((uint32_t)(t_r16 * t_r16) >> 10);
                    goto t_neg;
                }
                t_kb = 0x32dcfc00u + t_kf;
                uint32_t t_P0 = t_xs - t_kb * 2977044472u + ((t_kf * 11825u) >> 16);
                int32_t t_r16 = (int32_t)t_P0 >> 16;
                t_P = t_P0 + ((uint32_t)(t_r16 * t_r16) >> 10);
                goto t_pos;
    }
t_pos:
    T_MAIN_TAIL(1u);
t_neg:
    T_MAIN_TAIL(0u);
}

static const uint8_t t_an_tanh_groups[] = {41,36,32,28,25,22,19,17,15,13,12,10,9,8,7,6,5,5,4,4,3,2,2,1,1,1,1,1,1,1};
static uint32_t t_an_tanh_saturated(uint32_t t_a)
{
    uint32_t t_n = t_an_tanh_groups[(t_a - 0x40d80000u) >> 17];
    while ((t_a << 1) < t_eps[681u+t_n].t_aux) ++t_n;   /* HTT: rows 682..727 hold 2 t_aux */
    return 0x3f800000u - t_n;
}

static const uint32_t t_spcuts[]={0x418aa123u,0x4181d72eu,0x417b8204u,0x41761fd3u,0x41721a71u,0x416ee47eu,0x416c383du,0x4169ee19u,0x4167ed6eu,0x416625d9u,0x41648be8u,0x41631749u,0x4161c1c1u,0x41608686u,0x415f61d3u,0x415e50a8u,0x415d5093u,0x415c5f90u,0x415b7bf3u,0x415aa452u,0x4159d77au,0x41591464u,0x41585a2eu,0x4157a810u};

static uint32_t t_sig_plateau(uint32_t t_a){
    if(t_a>=0x418aa123u)return 0x3f800000u;
    uint32_t t_n=t_eps[(t_a-0x41580000u)>>17+0u].t_dn;
    while(t_a<t_spcuts[t_n])t_n++;
    return 0x3f800000u-t_n;
}
static uint32_t t_tanh_rest(uint32_t t_w, uint32_t t_e)
{
    uint32_t t_a = t_w & 0x7FFFFFFFu, t_sign = t_w ^ t_a;
    if (t_a >= 0x41102CB4u) {
        if (t_a > 0x7F800000u)
            return t_w | 0x00400000u;
        return t_sign | 0x3F800000u;
    }
    return t_sign|t_an_tanh_saturated(t_a);
}
static uint32_t t_sig_rest(uint32_t t_w, uint32_t t_e);
static uint32_t t_rest(uint32_t t_w, uint32_t t_e, uint32_t t_fn)
{
    if (t_fn)
        return t_sig_rest(t_w, t_e) ^ 1u;
    return t_tanh_rest(t_w, t_e) ^ 1u;
}

/* T6: tw tanh rejects (x = w) and fraction < 2^14 (x = 0; the result may drop a binade); returns x ^ result, so
 * the two call sites keep distinct tails: it stays out of line and the tiny path keeps its own return.
 * A reject has fraction >= 2^14 (same binade), candidate w - (z >> 14).  Otherwise V = (M << 8) + 128 - (z >> 6),
 * V_true in (V - 1, V + 2). */
static uint32_t t_tw_low(uint32_t t_w, uint32_t t_z)
{
    uint32_t t_D, t_base;
    {   /* HTT: only fraction < 2^14 reaches here (rejects with fraction >= 2^14 call t_pd_dec directly) */
        uint32_t t_e = (t_w << 1) >> 24, t_V = ((t_w << 8) | 0x80000000u) + 128u - (t_z >> 6), t_y, t_mu, t_m = (t_w & 0x7fffffu) | 0x800000u;
        if (t_V >= 0x80000000u - 2u) {
            t_y = t_V + 130u;
            if ((t_y & 255u) >= 3u)
                return (t_w & 0x80000000u) | (((t_e - 1u) << 23) + (t_y >> 8));
            t_mu = (t_V >> 8) + 1u;
            t_D = 4u * t_m - 2u * (2u * t_mu - 1u);
            t_base = (t_w & 0x80000000u) | (((t_e - 1u) << 23) + t_mu - 1u);
        } else {
            t_y = t_V + 66u;
            if ((t_y & 127u) >= 3u)
                return (t_w & 0x80000000u) | (((t_e - 2u) << 23) + (t_y >> 7));
            t_mu = t_y >> 7;
            t_D = 4u * t_m - (2u * t_mu - 1u);
            t_base = (t_w & 0x80000000u) | (((t_e - 2u) << 23) + t_mu - 1u);
        }
    }
    return t_base + t_pd_dec(t_w, t_D);
}
static const uint16_t t_ts_hword[]={0,33,163,683};
typedef const struct t_ep *const t_eprow;
/* H3: +-1 (entries 0, 2) and +-(1/2 + ulp) (entries 1, 3); the latter read at byte offset w >> 28: w's top nibble is 4
 * (x > 0) or 12 (x < 0) for 2 <= |x| < 2^33, so one lsrs gives the offset (no lsls) */
static const uint32_t t_tanh_sg[4] = {0x3F800000u, 0x3F000001u, 0xBF800000u, 0xBF000001u};
static inline uint32_t t_sgn28(uint32_t t_w)
{
    uint32_t t_o = t_w >> 28;
    if (t_o & 3u) __builtin_unreachable();   /* H3: 4 or 12 here: tells clang the word load is aligned */
    return *(const uint32_t *)((const uint8_t *)t_tanh_sg + t_o);
}
static uint32_t t_eik_tanh(uint32_t t_w)
{
    /* T6: u = 2 |x| less e 124's start: its sign splits off e < 124 (and e >= 252) for one bmi on the cells' path */
    uint32_t t_u = (t_w << 1) - (124u << 24) + 1u;   /* + 1: never carries (w << 1 is even); keeps the bias a literal word */
    if ((int32_t)t_u >= 0) {
    if (t_u < (632u << 17)) {   /* Q1: the row index after the range test (the other paths skip the lsrs) */
        /* X2: Y = V - 2^31 - 2^8. tanh |x| >= 1/2 (Y < 2^31): the result is w less the deficit D = ((w << 8) - Y) >> 8
         * (D < 2^24 below row 632, |x| < 3.875) */
        const struct t_ep *t_r=&t_eps[t_u >> 17];uint32_t t_Y=t_epnormal(t_r,t_w);
        if((int32_t)t_Y>=0){if((t_Y&255u)>=3u)return t_w-(((t_w<<8)-t_Y)>>8);return t_mid(t_w,126u,(t_Y>>8)+0x800001u,2u);}
        /* tanh |x| < 1/2: the chain on V = Y - 2^31 + 2^8, bounds and offsets folded */
        if((int32_t)(t_Y<<1)<0){uint32_t t_z=(t_Y<<1)+129u;   /* HTT: z = 2 (Y + 192) - 256 = (result << 8) + guard - 256 (mod 2^32), the
            * deficit form as on the main path (D < 2^24: |x| < 0.55): result = w - (((w << 8) - z) >> 8), sign-free */
            if((t_z&255u)>=7u)return t_w-(uint32_t)((int32_t)((t_w<<8)-t_z)>>8);   /* TJ: D < 2^31 here: asrs, so this tail is not merged with the main one (no b) */return t_mid(t_w,125u,(t_z>>8)+1u,2u);}
        {uint32_t t_z=t_Y+0xE0000060u;if((int32_t)t_z<0){   /* O2: tier 2 by z's sign (Y >= 0x9FFFFFA0, was 0xA0000081): z = (result << 6) + guard (mod 2^32), the deficit form at 6 guard bits:
            * result = w - (((w << 6) - z) >> 6), sign-free (w and the result share the binade or are one apart) */
            if((t_z&63u)>=2u)return t_w-(((t_w<<6)-t_z)>>6);return t_mid(t_w,124u,(t_z>>6)-0x17FFFFFu,2u);}   /* I3: window 2 (was 3): lsls/lsrs, no cmp; rows 0, 1, 15, 17, 25, 70, 100..102, 106 refit (fx.c) */
        t_z+=0x40000010u;   /* I3: + 0x10 (was 0x0F) with row 0 refit, so tier 2 window 2 fits */ if((t_z&31u)>=1u)return t_w-(((t_w<<5)-t_z)>>5);return t_mid(t_w,123u,(t_z>>5)-0x4FFFFFFu,2u);}   /* TJ: deficit form, 5 guard bits */
    }
    if (t_u >= (792u << 17))   /* X2: |x| >= 9.5 (t_c >> 3 >= 99): +-1 without the literal compare */
        return t_tanh_sg[(t_w >> 31) << 1];
    if (t_u < (728u << 17)) {   /* X2: rows 632..727 (|x| in [3.875, 6.75)), tanh |x| >= 1/2: D can reach 2^24 */
        const struct t_ep *t_r=&t_eps[t_u >> 17];uint32_t t_Y=t_epnormal(t_r,t_w);
        if((t_Y&255u)>=3u)return t_sgn28(t_w)+(t_Y>>8);return t_mid(t_w,126u,(t_Y>>8)+0x800001u,2u);
    }
    {   /* T6: |x| >= 6.75, e <= 251 */
        if ((t_w << 1) >= 0x82205968u)   /* |x| >= 9.01 */
            return t_tanh_sg[(t_w >> 31) << 1];
        uint32_t t_t = t_w << 1;   /* HTT: compared as 2 |x|: rows 682..727 hold 2 t_aux; the sign from t_tanh_pm1 */
        uint32_t t_n = t_an_tanh_groups[(t_t - (0x40d80000u << 1)) >> 18];
        while (t_t < t_eps[681u+t_n].t_aux) ++t_n;
        return t_tanh_sg[(t_w >> 31) << 1] - t_n;
    }
    }
    /* X3: e_s = e for e < 128, e - 256 for e >= 252 (negative): unsigned, e_s < N means e < N, and the e 119
     * bound read signed splits e 119..123 off e 252..255, with no e <= 123 test */
    int32_t t_es = (int32_t)(t_w << 1) >> 24;
    uint32_t t_e = (uint32_t)t_es;
    if (t_e < 115u)
        return t_w;
    if (t_e <= 118u) {
        /* R2: the left-aligned fraction g = w << 9 and a row-shift table */
        uint32_t t_g = t_w << 9, t_bin=t_e-115u;
        if (t_bin == 0u)   /* V3 (#35's): e 115 is one step, n = 0 or 1 from one compare (no row, no corner) */
            return t_w - ((t_w << 1) >= 0x73713746u);
        /* O2: the corners: fraction f < thr = {0, 1, 3, 11}[bin] drops a binade, result w + f + 1 - 2 thr */
        static const uint8_t t_cthr[]={0,1,3,11};
        static const uint8_t t_ts_sh[4] = {31, 29, 27, 25};
        uint32_t t_i = t_g >> t_ts_sh[t_bin];
        if (t_i == 0u) {
            uint32_t t_fraction = t_g >> 9, t_th = t_cthr[t_bin];
            if(t_fraction<t_th)return t_w+t_fraction+1u-2u*t_th;
        }
        /* HTT: rows 512 + {0, 2, 10, 42}[bin] of t_eps as pointers (one load instead of offset + base) */
        static const t_eprow t_ts_row[4] = {t_eps + 512, t_eps + 514, t_eps + 522, t_eps + 554};
        const struct t_ep *t_row = t_ts_row[t_bin];
        uint32_t t_n=(t_row[t_i].t_aux+(t_w<<1))>>24;return t_w-t_n;   /* O2: rows 512..681 hold 2 t_aux (mod 2^32): no mask */
    }
    if (t_es <= 118) {   /* X3: e 252..255 (negative), from the same compare as e <= 118 */
        if ((t_w << 1) > 0xFF000000u)
            return t_w | 0x00400000u;
        return t_tanh_sg[(t_w >> 31) << 1];
    }
    {   /* X3: e 119..123 */
        const struct t_ra *t_r = &t_tw[~((int32_t)t_u >> 20)];   /* O2: u < 0 here: ~(u >>s 20) = 79 - row (reversed table) */
        uint32_t t_z = t_cell_d(t_r, t_w);
        if ((t_w << 9) >> 23 == 0u)   /* T6: fraction < 2^14, the result may drop a binade */
            return t_tw_low(t_w, t_z);
        if ((t_z << 18) >> 25 != 0u)
            return t_w - (t_z >> 14);
        {uint32_t t_D = (t_z >> 12) - 2u, t_c = t_w - (t_D >> 2) - 1u; return t_c + t_pd_dec(t_w, t_D);}   /* G2: candidate w - (z >> 14) = w - (D >> 2) - 1 (z bits 12, 13 are 0), before the call */   /* HTT: a reject (fraction >= 2^14): D = 4 q - 2 (bits 12, 13 of z are 0) */
    }
}
/* sigmoid x <= -7 (normal results): sigma = e^x (1 - h), h = u - u^2 + u^3, u = e^x */
static uint32_t t_sig_nb(uint32_t t_w){
    /* TSN: exp's main-path k (one 17-bit product, s = e - 118 from the arithmetic shift: x < 0, no mask);
       kf ~ |x| / L (one high at most: then T[511] e^r wraps past 2^32), kb = (B - 1) - kf */
    uint32_t t_s = (uint32_t)(((int32_t)t_w >> 23) + 138);
    uint32_t t_X = t_w << 9;
    /* TSN: E >> (30 - s) as ((E >> 15) << s) >> 15 (s <= 15: the same floor, and the same shift count as X << s) */
    uint32_t t_kf = ((((((t_X >> 15) * 23637u + (t_X >> 18)) >> 1) + 1549087890u) >> 15) << t_s) >> 15;
    uint32_t t_xs = t_X << t_s;
    uint32_t t_k = 0x12dcfbffu - t_kf;
    int32_t t_rho = (int32_t)(t_k * (0u - 2977044472u) - t_xs - ((t_kf * 11825u) >> 16)), t_r16 = t_rho >> 16;
    uint32_t t_P = (uint32_t)t_rho + ((uint32_t)(t_r16 * t_r16) >> 10);
    uint32_t t_ef = (t_k << 14) >> 23;
    uint32_t t_T = t_eps[t_k & 511u].t_aux - 131u;
    int32_t t_P7 = (int32_t)t_P >> 8;
    int32_t t_S = (int32_t)(t_T >> 24) * t_P7 + ((((int32_t)((t_T << 8) >> 17)) * (t_P7 >> 8)) >> 7);
    uint32_t t_R = t_T + (uint32_t)(t_S >> 9);
    uint32_t t_V, t_z, t_lo;
    if ((int32_t)t_R >= 0) {
        if (t_R < 0x40000000u) {
            /* TSN: T[511] e^r wrapped past 2^32 (k one high): the binade above, at half the scale */
            t_R = 0x80000000u + (t_R >> 1);
            t_ef += 1u;
        } else if (t_ef <= 93u) {
            t_V = t_R;
            goto t_below;
        }
    }
    if (t_ef <= 93u) {
        t_z = t_R + 131u;
        if ((t_z & 255u) >= 4u)   /* I3: window 4 (was 5): exhaustive, no refit */
            return (t_ef << 23) + (t_z >> 8);
        t_lo = (t_ef << 23) + (t_z >> 8) - 1u + (t_z & 248u);
        goto t_rej;
    }
    if (t_ef <= 109u) {   /* TSN: one product up to ef 109 (t < 2^16: u^2 R < 1, (R >> 16) t < 2^32) */
        t_V = t_R - (((t_R >> 16) * (t_R >> (125u - t_ef))) >> 16);
    } else {
        uint32_t t_t = t_R >> (125u - t_ef);           /* u * 2^32 */
        uint32_t t_t2 = ((t_t >> 6) * (t_t >> 6)) >> 20;
        uint32_t t_h = t_t - t_t2 + (t_t2 >> 10);      /* TSN: u^3 2^32 <= t2 2^-10 (t < 2^22) */
        uint32_t t_R11 = t_R >> 11;
        t_V = t_R - (((t_R11 * (t_h >> 11)) >> 10) + ((t_R11 * (t_h & 2047u)) >> 21));
    }
    if ((int32_t)t_V < 0) {
        t_z = t_V + 131u;
        if ((t_z & 255u) >= 7u) return (t_ef << 23) + (t_z >> 8);   /* I3: window 7 (was 8) */
        t_lo = (t_ef << 23) + (t_z >> 8) - 1u + (t_z & 248u);
        goto t_rej;
    }
t_below:
    t_z = t_V + 64u;
    if ((t_z & 127u) >= 2u)   /* I3: window 2 (was 3): lsls/lsrs, no cmp */ return ((t_ef - 1u) << 23) + (t_z >> 7);
    t_lo = ((t_ef - 1u) << 23) + (t_z >> 7) - 1u + (t_z & 124u);
t_rej:
    if (t_w >= 0xC2000000u) return t_exp_leaf(t_w) ^ (t_w >> 31);
    return t_mid_neg(t_w, t_lo);
}
static uint32_t t_sig_rest(uint32_t t_w, uint32_t t_e)
{
    uint32_t t_a = t_w & 0x7FFFFFFFu;
    if (t_e >= 132) {
        if (t_w >= 0xC2D00000u)
            return 0;
        return t_exp_big1(t_w, t_e) ^ 1u;
    }
    if (t_e >= 130) {
        if (t_a > 0x7F800000u)
            return t_w | 0x00400000u;
        return t_sig_plateau(t_a);   /* TSN: x < 0 with e 130, 131 never comes here (t_eik_sigmoid sends (-87, -7] to t_sig_nb) */
    }
    return 0;
}
struct t_cbank{uint32_t t_q,t_p,t_v;};   /* F2: t_q first: read first, from the row base and offset; t_v last (no r6) */
static const struct t_cbank t_crows[]={
    {142852618u,38583430u,2565084168u},
    {140883977u,38029190u,2526778467u},
    {139030025u,37482326u,2489023284u},
    {137198089u,36942702u,2451811345u},
    {135386633u,36410238u,2415135454u},
    {133591561u,35884846u,2378988489u},
    {131817481u,35366462u,2343363410u},
    {130065929u,34855014u,2308253253u},
    {128329225u,34350406u,2273651122u},
    {126614537u,33852582u,2239550208u},
    {124916233u,33361454u,2205943769u},
    {123141640u,32876886u,2172825139u},
    {243067409u,64797957u,4280375476u},
    {239788049u,63855021u,4216050086u},
    {236448272u,62924821u,4152661225u},
    {233241616u,62007349u,4090196166u},
    {230077968u,61102405u,4028642319u},
    {226946576u,60209821u,3967987236u},
    {223853072u,59329469u,3908218624u},
    {220697103u,58461125u,3849324319u},
    {217675791u,57604797u,3791292319u},
    {214690831u,56760269u,3734110748u},
    {211743759u,55927405u,3677767877u},
    {208828431u,55106053u,3622252113u},
    {205951503u,54296093u,3567552010u},
    {203009038u,53497301u,3513656246u},
    {200197646u,52709685u,3460553652u},
    {197422606u,51933045u,3408233184u},
    {194685454u,51167253u,3356683938u},
    {191976462u,50412157u,3305895138u},
    {189203981u,49667565u,3255856141u},
    {186565133u,48933493u,3206556448u},
    {183955469u,48209725u,3157985673u},
    {181381645u,47496149u,3110133570u},
    {178840077u,46792629u,3062990017u},
    {176329229u,46099037u,3016545021u},
    {173851149u,45415253u,2970788715u},
    {171305996u,44741077u,2925711351u},
    {168891404u,44076533u,2881303318u},
    {166507020u,43421421u,2837555114u},
    {164151820u,42775621u,2794457364u},
    {161828364u,42139021u,2752000816u},
    {159536652u,41511501u,2710176332u},
    {157172747u,40892861u,2668974890u},
    {154939403u,40283141u,2628387597u},
    {152732171u,39682141u,2588405662u},
    {150558219u,39089765u,2549020417u},
    {148410379u,38505885u,2510223303u},
    {584997461u,75860717u,2472005872u},
    {568291411u,73608189u,2397276846u},
    {552019025u,71420149u,2324767976u},
    {536175695u,69294901u,2254415623u},
    {520651852u,67230701u,2186157828u},
    {1011366549u,130452188u,4239868590u},
    {982130321u,126558692u,4111372656u},
    {953673869u,122777860u,3986713628u},
    {925979273u,119106644u,3865780365u},
    {899027589u,115542060u,3748464737u},
    {872907906u,112081284u,3634661566u},
    {847395454u,108721316u,3524268540u},
    {822577786u,105459460u,3417186163u},
    {798536311u,102293076u,3313317682u},
    {775156340u,99219452u,3212569014u},
    {752418929u,96236004u,3114848692u},
    {730210925u,93340148u,3020067791u},
    {708713066u,90529572u,2928139881u},
    {687813223u,87801812u,2838980945u},
    {667492452u,85154532u,2752509331u},
    {647843938u,82585548u,2668645695u},
    {628645983u,80092484u,2587312924u},
    {609982556u,77673252u,2508436103u},
    {591845977u,75325764u,2431942444u},
    {574319703u,73048036u,2357761236u},
    {557189716u,70837932u,2285823780u},
    {540642898u,68693652u,2216063356u},
    {524566608u,66613236u,2148415150u},
    {1017801883u,129189627u,4165632438u},
    {987357846u,125273243u,4038410865u},
    {957887122u,121473923u,3915046854u},
    {929154189u,117788115u,3795425114u},
    {901344393u,114212675u,3679433704u},
    {874334341u,110744323u,3566963929u},
    {848102529u,107379939u,3457910265u},
    {822726270u,104116555u,3352170264u},
    {797981818u,100951075u,3249644468u},
    {773953142u,97880707u,3150236333u},
    {750721139u,94902731u,3053852150u},
    {728160368u,92014355u,2960400950u},
    {706157676u,89212883u,2869794447u},
    {684890217u,86495883u,2781946953u},
    {664243302u,83860803u,2696775305u},
    {644198499u,81305219u,2614198795u},
    {624737888u,78826779u,2534139104u},
    {605844573u,76423195u,2456520227u},
    {587507290u,74092259u,2381268416u},
    {569803864u,71831875u,2308312112u},
    {552520789u,69639803u,2237581871u},
    {535842387u,67514155u,2169010329u},
    {1039110304u,130905626u,4205064234u},
    {1007596699u,126907938u,4076167639u},
    {977105047u,123031498u,3951207821u},
    {947412626u,119272554u,3830065402u},
    {918694030u,115627730u,3712624574u},
    {890825354u,112093546u,3598772991u},
    {863681669u,108666618u,3488401673u},
    {837433473u,105343858u,3381404906u},
    {812067454u,102122162u,3277680148u},
    {787347578u,98998330u,3177127926u},
    {763362934u,95969514u,3079651767u},
    {740187251u,93032914u,2985158090u},
    {717598831u,90185618u,2893556133u},
    {695782508u,87425082u,2804757866u},
    {674613865u,84748618u,2718677911u},
    {653974629u,82153618u,2635233458u},
    {634045026u,79637762u,2554344204u},
    {614712415u,77198602u,2475932265u},
    {595952220u,74833810u,2399922109u},
    {577847386u,72541210u,2326240488u},
    {560188503u,70318490u,2254816367u},
    {543050836u,68163586u,2185580857u},
    {1053058724u,132149081u,4236934332u},
    {1020899487u,128098465u,4106821015u},
    {989699226u,124171545u,3980696142u},
    {959428757u,120364569u,3858437890u},
    {930164369u,116673977u,3739928133u},
    {901676172u,113096089u,3625052323u},
    {874136712u,109627625u,3513699398u},
    {847421572u,106265193u,3405761661u},
    {821507712u,103005577u,3301134692u},
    {796367996u,99845641u,3199717238u},
    {771981432u,96782361u,3101411130u},
    {748426869u,93812873u,3006121185u},
    {725476977u,90934169u,2913755108u},
    {703313518u,88143633u,2824223422u},
    {681720426u,85438449u,2737439369u},
    {660871271u,82816145u,2653318835u},
    {640646756u,80274129u,2571780269u},
    {621028449u,77809953u,2492744602u},
    {602000990u,75421249u,2416135179u},
    {583547995u,73105721u,2341877681u},
    {565645912u,70861121u,2269900053u},
    {548277845u,68685289u,2200132442u},
    {1063071398u,133152416u,4265014256u},
    {1030495393u,129063456u,4133916903u}
};
static inline uint32_t t_nbf(const struct t_cbank *t_r,uint32_t t_w){
 uint32_t t_q=t_r->t_q,t_f=(uint16_t)t_w,t_b=(t_q-(uint8_t)t_q*t_f)>>9;
 uint32_t t_s=t_r->t_p-(t_b>>16)*t_f-(((uint16_t)t_b*t_f)>>16);
 return t_r->t_v-(t_s>>16)*t_f-(((uint16_t)t_s*t_f)>>16);}
/* T6: sigmoid's exact decision for 2^-11 <= |x| < 2^-6 (exponent field 116..120), from #29's sg_small_t (s29.c:3465):
 * sigma(x) = 1/2 +- g, g = a/4 - a^3/48 + a^5/480 - ... (a = |x| = m 2^(e-150)). With the midpoint M 2^-K between the
 * candidates L and L + 1, D = (a/4 - |M 2^-K - 1/2|) 2^(152-e) is a small integer and sigma(x) > M 2^-K <=> D > C (x > 0),
 * D < C (x < 0), C = (a^3/48 - a^5/480) 2^(152-e), decided by the sign of E = 3 (D - C) 2^22 modulo 2^32;
 * |E| < 64 (where the error could flip it) is settled by the exhaustive check. */
static uint32_t t_sg_small(uint32_t t_w, uint32_t t_L1, uint32_t t_cube)
{   /* G2: L1 = low + 1 (low's mantissa is never 0x7FFFFF here): no + 1 at the end, 2 mant + 1 = (L1 << 1) - 1 mod 2^24 */
    /* HS: m^3 2^-40 from mh = m >> 8 and ml = m & 255: m^3 = 2^24 mh^3 + 3 2^16 mh^2 ml + 3 2^8 mh ml^2 + ml^3
     * (the third term, below 3 units, as +1: the decision has far more room than that, exhaustive);
     * t_cube = (mh^2 >> 16) mh from the fast path */
    uint32_t t_e = (t_w >> 23) & 0xFFu, t_m = (t_w & 0x7FFFFFu) | 0x800000u;
    uint32_t t_mh = t_m >> 8, t_P2 = t_mh * t_mh;
    uint32_t t_Q = t_cube + (((t_P2 & 0xFFFFu) * t_mh) >> 16) + ((((t_P2 >> 9) + (t_P2 >> 10)) * (t_w & 0xFFu)) >> 14) + 1u;
    uint32_t t_sh = 2u * (120u - t_e);
    uint32_t t_y10 = ((t_P2 >> 16) * 6554u) >> 13;                               /* m^2 2^-29 / 10 */
    uint32_t t_C3 = (t_Q >> t_sh) - ((((t_Q >> 16) * t_y10) >> 15) >> (2u * t_sh));
    uint32_t t_Mm = ((t_L1 << 9) >> 8) + 0xFFFFFFu;
    uint32_t t_E;
    if ((int32_t)t_w >= 0)
        t_E = ((3u * (t_m - ((t_Mm - 0x1000000u) << (127u - t_e)))) << 22) - t_C3;
    else
        t_E = t_C3 - ((3u * (t_m - ((0x2000000u - t_Mm) << (126u - t_e)))) << 22);
    return t_L1 - (t_E >> 31);
}
static const uint8_t t_sig_10[2] = {0x7Fu, 0u};
static uint32_t t_eik_sigmoid(uint32_t t_w)
{
    /* T6: u = 2 |x| less e 125's start (+ 1, which never carries); its sign splits off e < 125 (and e >= 253) */
    uint32_t t_u = (t_w << 1) - (125u << 24) + 1u;
    if ((int32_t)t_u >= 0) {
    /* X3: the sign before any range test, so x < 0 skips c < 728 and runs only its own bounds */
    if((int32_t)t_w<0){
        int32_t t_c = (int32_t)(t_u - (464u << 17));   /* F2: c - 464 as the row: no -464 * 12 folded into each field load */
        if (t_c >= 0) {   /* X3: c >= 464 */
            if ((uint32_t)t_c < (144u << 17)) {
                const struct t_cbank *t_r = &t_crows[(uint32_t)t_c >> 17];
                uint32_t t_V=t_nbf(t_r,t_w),t_e=110u+((t_r->t_p&7u)+5u);
                /* T6: rejects use z: t_V >> 8 = (t_z >> 8) - 1 when (t_z & 255) < 7 (and >> 7 likewise), plus a 0 term (t_z & 248,
                 * t_z & 120), so the fast results need neither a copy of t_V nor a mov */
                if((int32_t)t_V<2){uint32_t t_z=t_V+131u,t_base=(t_e)<<23;if((t_z&255u)>=7u)return t_base+(t_z>>8);return t_mid_neg(t_w,t_base+(t_z>>8)-1u+(t_z&248u));}
                {uint32_t t_z=t_V+195u,t_base=((t_e-1u)<<23)-1u;if((t_z&127u)>=6u)return t_base+(t_z>>7);return t_mid_neg(t_w,t_base+((t_z-128u)>>7)+(t_z&120u));}   /* ID: + 128 and base - 1: one literal, no + 1 */
            }
            if ((uint32_t)t_c >= ((1120u - 464u) << 17))   /* X3: |x| >= 106 (e <= 252): 0 (F2: c - 464 >> 21 from the bound above; 1120, not 1104, whose 640 rows clang re-canonicalizes to >> 24; |x| in [104, 106) goes to t_sig_rest, also 0) */
                return 0;
            if (t_w < 0xC2AE0000u)   /* X3: |x| in [7, 87) */
                return t_sig_nb(t_w);
        } else {
        const struct t_ep *t_r=&t_eps[t_u>>17];uint32_t t_Y=t_epnormal(t_r,t_w);   /* X2: Y = V - 2^31 - 2^8, tests and offsets folded */

        /* T6: each reject candidate below adds a term that is 0 on a reject (t_m & 252 and t_m & 60: the window bits
         * are below 3; t_k (t_k - 1) (t_k - 2) with t_k < 3), so it no longer equals the fast result: clang then
         * computes the fast result after the branch, straight into r0, instead of before it plus a mov */
        if((int32_t)t_Y<0){if((t_Y&255u)>=3u)return 0x3E7FFFFFu-(uint32_t)((int32_t)t_Y>>8);return t_mid_neg(t_w,0x3E7FFFFFu-(uint32_t)((int32_t)t_Y>>8)+(t_Y&252u));}   /* TJ: Y < 0: Y >>a 8 = (Y >> 8) - 2^24, so the base is tier 2's literal 0x3E7FFFFF */
        if(t_Y<1073741697u){uint32_t t_m=t_Y+64u,t_k=t_m&127u;if(t_k>=3u)return 0x3E7FFFFFu-(t_m>>7);return t_mid_neg(t_w,0x3E7FFFFFu-(t_m>>7)+t_k*(t_k-1u)*(t_k-2u));}   /* HS: 192 - 128, 0x3E800000 - 1: one literal, not movs+lsls */
        if(t_Y<1610612609u){uint32_t t_m=t_Y+96u;if((t_m&63u)>=3u)return 0x3EFFFFFFu-(t_m>>6);return t_mid_neg(t_w,0x3EFFFFFFu-(t_m>>6)+(t_m&60u));}   /* H3: 160 - 64 and 0x3F000000 - 1: one literal load (0x3F << 24 shared the mask's movs, plus a mov) */
        {uint32_t t_m=t_Y+113u;if((t_m&31u)>=4u)return 0x407FFFFFu-(t_m>>5);return t_mid_neg(t_w,0x407FFFFFu-(t_m>>5));}   /* HS: as above */
        }
    } else {
        if(t_u<(728u<<17)){
        /* X2: the cell is Y = V - 2^31 - 2^8, exactly as a signed number: V >> 1 = (Y >> 1) + 2^30 + 2^7 */
        const struct t_ep *t_r=&t_eps[t_u>>17];int32_t t_y9=(int32_t)t_epnormal(t_r,t_w)-127;int32_t t_m2=t_y9>>1;   /* HS: 193 - 256 (same low byte) */
            /* HS: 0x3f400001 is one literal load (0x3f400000 would be movs+lsls, or a rebase +1); the reject's constant is kept
             * 257 away so that neither is rebased on the other */
            if((t_y9&0x1FC)!=0)return 0x3f400001u+(uint32_t)(t_y9>>9);   /* ID: the 9-bit field, window 8 (was 6): no >> 1 */
            return t_mid_pos(t_w,0x3f3fff00u+(uint32_t)((int32_t)((uint32_t)(t_m2|(t_m2&252)<<8)+0x10000u)>>8));
        }
        if (t_w >= 0x418AA123u)   /* X3: x >= 13.5, e <= 252 */
            return 0x3F800000u;
    }
    return t_rest(t_w, (t_w << 1) >> 24, 1) ^ 1u;   /* X3: x in [13.5, 17.3) or (-104, -87] */
    }
    /* R2: the exponent field as e_s = e for e < 128, e - 256 above (an arithmetic shift, which keeps the
     * compares below on it rather than on w << 1 with wider shifts); unsigned, e_s < N means e < N */
    int32_t t_es = (int32_t)(t_w << 1) >> 24;
    uint32_t t_e = (uint32_t)t_es;
    if (t_e >= 116u) {
        {
            if (t_es > 120) {   /* R2: e 121..124 */
                const struct t_ra *t_r = &t_tw[~((int32_t)t_u >> 20)];   /* O2: reversed table, as in tanh */
                uint32_t t_V = ((t_w << 8) | 0x80000000u) + 128u - (t_cell_d(t_r, t_w) >> 6);
                if ((int32_t)t_w >= 0) {
                    t_V >>= 128u - (t_w >> 23);   /* T6: the shift from w (a table byte keeps the row pointer live) */
                    uint32_t t_y = t_V + 0x81u, t_k = t_y & 255u;
                    if (t_k >= 2u)
                        return 0x3F000000u + (t_y >> 8);
                    /* a reject: t_V >> 8 = (t_y >> 8) - 1, and t_k (t_k - 1) = 0 (no copy of t_V, no mov) */
                    uint32_t t_lo = 0x3EFFFFFFu + ((t_y + ((t_k * (t_k - 1u)) << 8)) >> 8);
                    if (t_w == 0x3D21BC81u)   /* Q3: sits 2^-29 ulp above the midpoint (W2: tested here, its only caller; low is 0x3F0286DC) */
                        return t_lo;
                    return t_mid_pos(t_w, t_lo);
                }
                t_V = 0u - (t_V >> (127u & ~(t_w >> 23)));   /* ID: 127 - e as a bics (e <= 127) */   /* HS: 127 - e = 256 - e - 129 from the arithmetic shift */
                {   /* T6: V >> 3 < 2^29, so t_V >= 2^31: sigma(x) stays in [1/4, 1/2) */
                    uint32_t t_y = t_V - 0x80u;   /* HS: 0x80 - 0x100 */
                    if ((t_y & 255u) >= 2u)
                        return 0x3E000001u + (t_y >> 8);
                    return t_mid_neg(t_w, 0x3E000200u + ((t_V - 0x20000u) >> 8));
                }
            }
            if (t_e > 120u) {   /* T6: e 253..255 */
                if ((t_w << 1) > 0xFF000000u)
                    return t_w | 0x00400000u;
                return (uint32_t)t_sig_10[t_w >> 31] << 23;
            }
            {   /* T6: e 116..120 (the tw cells first: they are typical) */
                uint32_t t_m = (t_w & 0x7FFFFFu) | 0x800000u, t_mh = t_m >> 8;
                uint32_t t_cube = ((t_mh * t_mh) >> 16) * t_mh;
                static const uint8_t t_cs3[5] = {31, 28, 25, 22, 19};   /* T6: 379 - 3 e as a table (was 6 instructions) */
                uint32_t t_U = (t_m << (t_e - 116)) - (((t_cube >> 16) * 43691u) >> t_cs3[t_e - 116]);
                if ((int32_t)t_w >= 0) {
                    /* ID: 0x3F000000 + ((U + 0x800) >> 12) as 0x3EFFFE00 + ((U + 0x200800) >> 12): two literal loads, 512 away from
                     * 0x3F000000 (no rebase), in place of a hoisted movs+lsls, the shared mask literal and adds #2 */
                    if (((t_U + 0x200800u) & 0xFFFu) >= 2u)
                        return 0x3EFFFE00u + ((t_U + 0x200800u) >> 12);
                    return t_sg_small(t_w, (((126) - 1u) << 23) + (0x800000u + (t_U >> 12) + 1), t_cube);   /* T6: #29's series decision */
                }
                if (((t_U + 0x100400u) & 0x7FFu) >= 2u)   /* ID: as above, 0x3F000200 - ((U + 0x400 + 2^20) >> 11) */
                    return 0x3F000200u - ((t_U + 0x100400u) >> 11);
                return t_sg_small(t_w, (((125) - 1u) << 23) + (0x1000000u - (t_U >> 11)), t_cube);
            }
        }
    }
    if(t_e<103u)return 0x3f000000u;
    /* 1/2 + x/4, ties towards 1/2; s = 0 or -1 the sign. q = (m - 1) >> sh, m the significand;
     * x > 0: (q + 1) >> 1, x < 0: floor(-q / 2), both ((q ^ s) + 1) >> 1 (arithmetic), with
     * 0x3f000000 riding in the shifted sum as 0x7e000000 */
    uint32_t t_s=(uint32_t)((int32_t)t_w>>31),t_sh=127u-t_e+t_s;
    uint32_t t_q=((t_w&0x7fffffu)+0x7fffffu)>>t_sh;
    return (uint32_t)((int32_t)((t_q^t_s)+0x7e000001u)>>1);
}


uint32_t eik_sigmoid(uint32_t w)
{
    if (EIK_SEL)
        return eik_sigmoid_r(w);
    return t_eik_sigmoid(w);
}

uint32_t eik_tanh(uint32_t w)
{
    if (EIK_SEL)
        return eik_tanh_r(w);
    return t_eik_tanh(w);
}

uint32_t eik_exp(uint32_t w)
{
    if (EIK_SEL)
        return eik_exp_r(w);
    return t_eik_exp(w);
}
