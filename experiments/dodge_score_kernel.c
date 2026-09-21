// ABOUTME: Compiled inner loop of the dodge-aware scorer: scores every odometer dial
// ABOUTME: pair against one keyed alphabet and schedule, tracking the preventer's skips.

#include <stdint.h>
#include <string.h>

#ifndef M
#define M 29
#endif

#ifndef MAX_WINDOWS
#define MAX_WINDOWS 2048
#endif

#ifndef MAX_WORDS
#define MAX_WORDS 4096
#endif

#ifndef MAX_RUNES
#define MAX_RUNES 20480
#endif

// The cipher this scores:
//
//     c_j = ( K[ (pos_K(p_j) + a_w + S_k) mod M ] + b_w ) mod M
//
// with the doublet preventer moving the clock, so k is NOT the position. The kernel
// never has to know where the preventer fired: it cuts the stream into short windows,
// treats each window's starting clock phase as one of five unknowns, and alternates
//
//   1. build the score table summing all five phases, or the chosen ones;
//   2. greedy one-to-one assignment for the free bijection on the ciphertext;
//   3. with that fixed, score each window at each phase and keep the best.
//
// `logtab[k][t][z]` is log f of the plaintext implied by ciphertext-candidate z at
// clock phase k under total inner shift t, so the per-position inner loop is one
// rotated vector add. The caller builds it once per (alphabet, schedule) and the
// kernel sweeps every dial pair against it.
//
// Scores come back in nats per rune above the flat baseline, as walk_score_kernel does.
void score_dials(const float *logtab,      // 5 x M x M
                 const int8_t *dials,      // n_dials x 2, each (a0, b0)
                 int n_dials,
                 const int8_t *runes,      // ciphertext, words concatenated
                 const int32_t *word_lens, // word lengths
                 int n_words,
                 int window,               // runes per window
                 int passes,
                 float *out)               // n_dials scores
{
    int n_runes = 0;
    for (int w = 0; w < n_words; w++) n_runes += word_lens[w];
    int n_windows = (n_runes + window - 1) / window;
    if (n_windows > MAX_WINDOWS) n_windows = MAX_WINDOWS;

    float flat = 0.0f;
    for (int k = 0; k < M; k++) flat += logtab[0 * M * M + 0 * M + k] / M;

    // Bail rather than overrun: the caller slices the corpus, so these bounds are
    // generous for any window the sweep uses.
    if (n_words > MAX_WORDS || n_runes > MAX_RUNES) {
        for (int d = 0; d < n_dials; d++) out[d] = -1e30f;
        return;
    }

    // per-rune word index, so the dial walk does not need the word loop inside
    int16_t owner[MAX_RUNES];
    for (int w = 0, i = 0; w < n_words; w++)
        for (int j = 0; j < word_lens[w]; j++, i++) owner[i] = (int16_t)w;

    for (int d = 0; d < n_dials; d++) {
        int a0 = dials[d * 2], b0 = dials[d * 2 + 1];

        // the odometer: a advances every word, b only when a wraps
        int8_t wa[MAX_WORDS], wb[MAX_WORDS];
        int a = a0, b = b0;
        for (int w = 0; w < n_words; w++) {
            wa[w] = (int8_t)a;
            wb[w] = (int8_t)b;
            a = (a + 1) % M;
            if (a == 0) b = (b + 1) % M;
        }

        int phase[MAX_WINDOWS];
        for (int m = 0; m < n_windows; m++) phase[m] = -1; // -1 seeds all five

        float total = 0.0f;
        for (int pass = 0; pass < passes; pass++) {
            float table[M][M];
            memset(table, 0, sizeof table);
            for (int m = 0; m < n_windows; m++) {
                int lo = m * window;
                int hi = lo + window;
                if (hi > n_runes) hi = n_runes;
                int first = phase[m] < 0 ? 0 : phase[m];
                int last = phase[m] < 0 ? 4 : phase[m];
                float share = phase[m] < 0 ? 0.2f : 1.0f;
                for (int ph = first; ph <= last; ph++)
                    for (int i = lo; i < hi; i++) {
                        int w = owner[i];
                        int k = (ph + i - lo) % 5;
                        const float *src = logtab + (k * M + wa[w]) * M;
                        float *row = table[runes[i]];
                        int rot = wb[w];
                        // row[y] += logtab[k][a_w][(y - b_w) mod M]
                        for (int y = 0; y < M; y++) {
                            int z = y - rot;
                            if (z < 0) z += M;
                            row[y] += share * src[z];
                        }
                    }
            }

            // greedy one-to-one assignment: the free bijection is a permutation
            int8_t chosen[M];
            int c_used[M] = {0}, y_used[M] = {0};
            total = 0.0f;
            for (int step = 0; step < M; step++) {
                float top = -1e30f;
                int top_c = 0, top_y = 0;
                for (int c = 0; c < M; c++) {
                    if (c_used[c]) continue;
                    for (int y = 0; y < M; y++)
                        if (!y_used[y] && table[c][y] > top) {
                            top = table[c][y];
                            top_c = c;
                            top_y = y;
                        }
                }
                total += top;
                c_used[top_c] = y_used[top_y] = 1;
                chosen[top_c] = (int8_t)top_y;
            }
            if (pass + 1 == passes) break;

            // refit each window's phase against the bijection just chosen
            for (int m = 0; m < n_windows; m++) {
                int lo = m * window;
                int hi = lo + window;
                if (hi > n_runes) hi = n_runes;
                float best = -1e30f;
                int arg = 0;
                for (int ph = 0; ph < 5; ph++) {
                    float sum = 0.0f;
                    for (int i = lo; i < hi; i++) {
                        int w = owner[i];
                        int k = (ph + i - lo) % 5;
                        int z = chosen[runes[i]] - wb[w];
                        if (z < 0) z += M;
                        sum += logtab[(k * M + wa[w]) * M + z];
                    }
                    if (sum > best) {
                        best = sum;
                        arg = ph;
                    }
                }
                phase[m] = arg;
            }
        }
        out[d] = (total - n_runes * flat) / n_runes;
    }
}
