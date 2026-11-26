/* Exact inference in C: the same output bits as `exactrt`, the proved Lean runtime.
 *
 * The specification is `ContractExact.lean` (with `ExactToolkit/` and FloatLib); this library
 * follows it, and is tested bit for bit against `exactrt`. Values are binary32 words handled with
 * integer arithmetic only. Model files are `.exrt`, the format read by `exactrt`
 * (`Runtime.lean`). */
#ifndef EXACT_H
#define EXACT_H

#include <stddef.h>
#include <stdint.h>

typedef uint32_t er_word;

/* Layer tags, as in `.exrt` files. */
enum er_tag {
    ER_LINEAR = 1,
    ER_GEMM = 2,
    ER_CONV = 3,
    ER_DEPTHWISE = 4,
    ER_BN = 5,
    ER_MAXPOOL = 6,
    ER_AVGPOOL = 7,
    ER_RMSNORM = 8,
    ER_LAYERNORM = 9,
    ER_SAVE = 10,
    ER_ADDSAVED = 11,
    /* Version 2 */
    ER_CONV2 = 12,       /* general convolution: strides, padding per side, dilation, groups */
    ER_DEPTHWISE2 = 13,  /* general depthwise convolution */
    ER_CONVT = 14,       /* transposed convolution */
    ER_MAXPOOL2 = 15,    /* general pooling: windows, strides, padding, ceil mode */
    ER_AVGPOOL2 = 16,
    ER_ATTENTION = 17,
    ER_SILU = 18,
    ER_LSTM = 19,
    ER_GRU = 20,
    ER_LASTSTEP = 21
};

/* The newest `.exrt` version this library reads (it also reads version 1, tags 1 to 11). */
#define ER_VERSION 2

/* A tensor inside the model file: `n` little-endian words from `p`, read in place (no copy, so
 * weights can stay in flash). */
typedef struct {
    const uint8_t *p;
    uint32_t n;
} er_tensor;

/* One layer: its tag, its parameters in file order, and up to eight tensors.
 *
 *   tag           param[0..]                                  t[0..]
 *   linear        rows inW outW relu                          weights bias
 *   gemm          m k n                                       a
 *   conv          cin h w cout kh kw stride pad relu          weights bias
 *   depthwise     cin h w kh kw stride pad relu               weights bias
 *   bn            relu c hw                                   scale shift
 *   maxpool       c h w k
 *   avgpool       c h w k
 *   rmsnorm       rows n eps                                  g
 *   layernorm     rows n eps                                  g b
 *   save
 *   addSaved      relu
 *   conv2         cin h w cout kh kw sH sW padT padL padB padR dilH dilW groups relu
 *                                                             weights bias
 *   depthwise2    cin h w kh kw sH sW padT padL padB padR dilH dilW relu
 *                                                             weights bias
 *   convT         cin h w cout kh kw sH sW padT padL padB padR dilH dilW groups outPadH outPadW relu
 *                                                             weights bias
 *   maxpool2      c h w kh kw sH sW padT padL padB padR ceilMode countIncludePad
 *   avgpool2      as maxpool2
 *   attention     T heads d causal                            wq bq wk bk wv bv wo bo
 *   silu
 *   lstm          T inW H                                     wih whh bih bhh (4 gate blocks)
 *   gru           T inW H                                     wih whh bih bhh (3 gate blocks)
 *   lastStep      T n
 */
typedef struct {
    uint32_t tag;
    uint32_t param[18];
    er_tensor t[8];
    uint32_t out_size; /* values this layer outputs */
} er_layer;

#define ER_MAX_LAYERS 64
#define ER_ERROR_LEN 160

typedef struct {
    uint32_t input_size;
    uint32_t output_size;
    uint32_t layer_count;
    er_layer layers[ER_MAX_LAYERS];
} er_model;

/* Reads a model file in place, with every size check of `exactrt`. Returns 0, or -1 with the
 * reason in `error` (the same wording as `exactrt`). */
int er_model_parse(const uint8_t *bytes, size_t len, er_model *m, char error[ER_ERROR_LEN]);

/* Word `i` of a tensor. */
static inline er_word er_at(er_tensor t, uint32_t i)
{
    const uint8_t *q = t.p + 4 * (size_t)i;
    return (er_word)q[0] | (er_word)q[1] << 8 | (er_word)q[2] << 16 | (er_word)q[3] << 24;
}

/* FNV-1a over the output words, as `hashWords` in `exactrt`. */
uint32_t er_hash(const er_word *v, size_t n);

/* ---- Exact dot products (FloatLib's `dot`, rounded to nearest-even) ---- */

/* Limbs of the fixed-point accumulator: two's complement, least significant bit 2^-298 (the
 * smallest product of two binary32 values). Products reach bit 553; the rest is carry headroom. */
#define ER_ACC_LIMBS 20

/* An exact sum of products, with FloatLib's exceptional-value state. */
typedef struct {
    uint32_t limb[ER_ACC_LIMBS];
    er_word snan, qnan;     /* the first signalling and quiet NaN, already quieted */
    uint8_t have_snan, have_qnan;
    uint8_t pos_inf, neg_inf;
    uint8_t invalid;        /* 0 · ∞ seen */
    uint8_t all_neg_zero;   /* every term so far was a negative zero */
} er_acc;

void er_acc_init(er_acc *a);
/* Adds the exact product `x · y` (left operand first, for NaN priority). */
void er_acc_add(er_acc *a, er_word x, er_word y);
/* The exact total rounded once to binary32, nearest-even. */
er_word er_acc_round(const er_acc *a);

/* ReLU on a word: negative non-NaN values (including -0) become +0. */
er_word er_relu(er_word w);
/* `a < b` as binary32 values (false if either is NaN). */
int er_less(er_word a, er_word b);

/* ---- Single operations: correctly rounded, nearest-even, FloatLib's NaN choice ---- */

er_word er_add(er_word x, er_word y);
er_word er_sub(er_word x, er_word y);
er_word er_mul(er_word x, er_word y);
er_word er_div(er_word x, er_word y);
er_word er_fma(er_word x, er_word y, er_word z); /* x · y + z, one rounding */
er_word er_maximum(er_word x, er_word y);        /* IEEE maximum: NaN wins, max(-0, +0) = +0 */
er_word er_nat(uint32_t n);                      /* n as binary32 */
/* Correctly rounded logistic sigmoid `1 / (1 + e^-x)` and `tanh x`: the nearest binary32 value,
 * ties to even. NaNs are quieted (sign and payload kept); tanh(±∞) = ±1, tanh(±0) = ±0,
 * σ(+∞) = 1, σ(−∞) = +0, σ(±0) = 1/2. */
er_word er_sigmoid(er_word x);
er_word er_tanh(er_word x);
/* Correctly rounded `e^x` (the spec's `expW`, FloatLib's `CorrectlyRounded.exp`): the nearest
 * binary32 value, ties to even, +∞ when that would exceed the largest finite value. NaNs are
 * quieted (sign and payload kept); exp(+∞) = +∞, exp(−∞) = +0, exp(±0) = 1. */
er_word er_exp(er_word x);

/* ---- Layers ---- */

/* `Y[i, j] = act(Σ_t X[i, t] · W[j, t] + b[j])`. */
void er_linear(uint32_t rows, uint32_t in_w, uint32_t out_w, int relu, const er_word *x,
               er_tensor w, er_tensor b, er_word *y);
/* `C[i, j] = Σ_t A[i, t] · B[t, j]`, `A` from the model (`m × k`), `B` the activation (`k × n`). */
void er_gemm(uint32_t m, uint32_t k, uint32_t n, er_tensor a, const er_word *b, er_word *c);

/* A convolution's shape (NCHW, one image); `cout` is unused by depthwise convolutions. */
typedef struct {
    uint32_t cin, h, w, cout, kh, kw, stride, pad;
} er_conv_shape;

/* Output size along one axis: `(in + 2·pad − k) / stride + 1`. */
uint32_t er_conv_out(uint32_t in, uint32_t k, uint32_t stride, uint32_t pad);
/* `out[o, y, x] = act(Σ_{c, dy, dx} in[c, …] · w[o, c, dy, dx] + b[o])`, zero padding. */
void er_conv2d(const er_conv_shape *s, int relu, const er_word *in, er_tensor w, er_tensor b,
               er_word *out);
/* Channel `c` of the output uses only input channel `c` and its own `kh × kw` filter. */
void er_depthwise(const er_conv_shape *s, int relu, const er_word *in, er_tensor w, er_tensor b,
                  er_word *out);
/* Batch norm at inference: `act(x · s[ch] + t[ch])` with one rounding, `c` channels of `hw`. */
void er_scale_shift(int relu, uint32_t c, uint32_t hw, const er_word *x, er_tensor s, er_tensor t,
                    er_word *y);
/* Residual add: `act(a[i] + b[i])`. */
void er_add_relu(int relu, size_t n, const er_word *a, const er_word *b, er_word *y);
/* Max and average pooling over `k × k` windows with stride `k`. */
void er_maxpool(uint32_t c, uint32_t h, uint32_t w, uint32_t k, const er_word *in, er_word *out);
void er_avgpool(uint32_t c, uint32_t h, uint32_t w, uint32_t k, const er_word *in, er_word *out);
/* RMS norm and layer norm over `rows` rows of `n` values: exact statistics when every value is
 * finite and eps > 0, otherwise FloatLib's staged binary32 steps. */
void er_rmsnorm(uint32_t rows, uint32_t n, er_word eps, const er_word *x, er_tensor g, er_word *y);
void er_layernorm(uint32_t rows, uint32_t n, er_word eps, const er_word *x, er_tensor g,
                  er_tensor b, er_word *y);
/* SiLU: `x · σ(x)`, one rounding after the correctly rounded sigmoid. */
void er_silu(size_t n, const er_word *x, er_word *y);
/* LSTM and GRU layers: `T` steps of `inW` inputs (`x` is `T × inW`), hidden size `H`, zero
 * initial state; every step's hidden state goes to `y` (`T × H`). Weights as PyTorch's:
 * `wih` is `G·H × inW`, `whh` `G·H × H`, `bih` and `bhh` `G·H`, gates `i f g o` (LSTM, G = 4) or
 * `r z n` (GRU, G = 3). The LSTM keeps its cell state in `c` (`H` words of scratch). */
void er_lstm(uint32_t steps, uint32_t in_w, uint32_t hid, const er_word *x, er_tensor wih,
             er_tensor whh, er_tensor bih, er_tensor bhh, er_word *y, er_word *c);
void er_gru(uint32_t steps, uint32_t in_w, uint32_t hid, const er_word *x, er_tensor wih,
            er_tensor whh, er_tensor bih, er_tensor bhh, er_word *y);
/* The last of `T` rows of `n` words. */
void er_last_step(uint32_t steps, uint32_t n, const er_word *x, er_word *y);

/* General convolution and pooling geometry (`ConvShape`, `ConvTShape`, `PoolShape`): `cin` is the
 * channel count (`c` for pooling), strides, dilations and padding per axis and side; `groups`,
 * `out_pad_*` (transposed convolution), `ceil_mode` and `count_include_pad` (pooling) are used only
 * by the layers they belong to. Shapes must be valid (the model reader checks them). */
typedef struct {
    uint32_t cin, h, w, cout, kh, kw, stride_h, stride_w, pad_t, pad_l, pad_b, pad_r, dil_h, dil_w,
        groups, out_pad_h, out_pad_w, ceil_mode, count_include_pad;
} er_geom;

/* Output sizes: convolution `(h + padT + padB − ekh) / strideH + 1`; transposed convolution
 * `strideH·(h − 1) + outPadH + ekh − padT − padB`; pooling ONNX's floor or ceil rule. */
uint32_t er_geom_conv_ho(const er_geom *s);
uint32_t er_geom_conv_wo(const er_geom *s);
uint32_t er_geom_convt_ho(const er_geom *s);
uint32_t er_geom_convt_wo(const er_geom *s);
uint32_t er_geom_pool_ho(const er_geom *s);
uint32_t er_geom_pool_wo(const er_geom *s);
/* Grouped, strided, padded, dilated convolution; weights `cout × (cin/groups) × kh × kw`. */
void er_conv2d_general(const er_geom *s, int relu, const er_word *in, er_tensor w, er_tensor b,
                       er_word *out);
/* The same with `cout = groups = cin` (the shape's own `cout` and `groups` are ignored). */
void er_depthwise_general(const er_geom *s, int relu, const er_word *in, er_tensor w, er_tensor b,
                          er_word *out);
/* ONNX ConvTranspose: each output the exact dot of the taps that reach it, plus the bias;
 * weights `cin × (cout/groups) × kh × kw`. */
void er_conv_transpose(const er_geom *s, int relu, const er_word *in, er_tensor w, er_tensor b,
                       er_word *out);
/* Max (IEEE maximum) and average (exact sum, then division) over each window's image cells;
 * padding is never a value. */
void er_maxpool_general(const er_geom *s, const er_word *in, er_word *out);
void er_avgpool_general(const er_geom *s, const er_word *in, er_word *out);

/* Attention over `T` tokens of `heads · d` channels (`Layer.attention`): projections, exact-dot
 * scores (`causal`: −∞ above the diagonal), softmax with the correctly rounded exp, exact-dot mix,
 * output projection. `t` holds wq bq wk bk wv bv wo bo; `work` needs
 * `er_attention_work_words` words. */
size_t er_attention_work_words(uint32_t steps, uint32_t heads, uint32_t d);
void er_attention(uint32_t steps, uint32_t heads, uint32_t d, int causal, const er_word *x,
                  const er_tensor t[8], er_word *y, er_word *work);

/* ---- SHA-256 ---- */

typedef struct {
    uint32_t h[8];
    uint64_t len;
    uint8_t buf[64];
} er_sha256_ctx;

void er_sha256_init(er_sha256_ctx *c);
void er_sha256_update(er_sha256_ctx *c, const void *data, size_t n);
void er_sha256_final(er_sha256_ctx *c, uint8_t out[32]);
void er_sha256(const void *data, size_t n, uint8_t out[32]);
/* SHA-256 of words as little-endian bytes (as a .f32 file holds them). */
void er_sha256_words(const er_word *v, size_t n, uint8_t out[32]);

/* ---- Signed run records (Ed25519) ---- */

#define ER_RECORD_MAX 1024 /* longest signed text */

/* A key pair from a 32-byte secret seed; `sk` holds the seed and then `pk`. */
void er_keypair(const uint8_t seed[32], uint8_t pk[32], uint8_t sk[64]);
int er_sign(const uint8_t sk[64], const uint8_t *msg, size_t n, uint8_t sig[64]);
/* 0 if `sig` is `pk`'s signature of `msg`. */
int er_verify(const uint8_t pk[32], const uint8_t *msg, size_t n, const uint8_t sig[64]);

void er_hex(const uint8_t *b, size_t n, char *out);   /* out: 2n + 1 chars */
int er_unhex(const char *s, uint8_t *b, size_t n);    /* exactly 2n lowercase hex digits */

/* What a run record states. */
typedef struct {
    char engine[32];
    uint8_t model[32], input[32], output[32]; /* SHA-256 of model file, input file, output words */
    uint32_t samples;
    uint32_t hash; /* the FNV hash `exactrt` prints */
} er_record;

/* Writes the record, signed with `sk`, as text into `out`. */
int er_record_write(const er_record *r, const uint8_t sk[64], char *out, size_t cap);
/* Reads a record and checks its signature against the key it names (returned in `pk`); the
 * caller decides whether it trusts that key. */
int er_record_read(const char *text, er_record *r, uint8_t pk[32], char error[ER_ERROR_LEN]);

/* ---- Running a model ---- */

/* Words of scratch memory `er_model_run` needs. */
size_t er_model_scratch_words(const er_model *m);

/* Runs `samples` consecutive inputs through the model, writing `samples · output_size` words.
 * Returns 0, or -1 with the reason in `error` (e.g. a layer type not implemented yet). */
int er_model_run(const er_model *m, const er_word *inputs, uint32_t samples, er_word *outputs,
                 er_word *scratch, size_t scratch_words, char error[ER_ERROR_LEN]);

#endif
