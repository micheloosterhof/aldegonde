// ABOUTME: Compiled base_0-free walk scorer with a per-word Caesar shift of the
// ABOUTME: plaintext: scores many sigmas against one set of letter perms and a schedule.

#include <stdint.h>
#include <string.h>

#ifndef M
#define M 29
#endif

// The cipher this scores, `walk_shift_verifier_check.py`:
//
//     c_j = base_w( g_(j mod 5)( p_j + s_w ) ),  base_{w+1} = base_w o g_((L-1) mod 5) o sigma
//
// so with u = base_0^-1(c) the plaintext is g_j^-1( M_w^-1( u ) ) - s_w, and the only
// change from walk_score_kernel is one more table index: by_phase[j][s][y] holds
// log f( g_j^-1(y) - s ). Windows are scored independently with their own free base
// and combine as their maximum. The greedy one-to-one assignment is always run.
void score_sigmas_shifted(const int8_t *letter_perms, // 5 x M
                          const int8_t *sigmas,       // n_sigma x M
                          int n_sigma,
                          const int8_t *runes,        // ciphertext, windows concatenated
                          const int32_t *word_lens,   // word lengths, windows concatenated
                          const int8_t *word_shifts,  // s_w per word, same layout
                          const int32_t *window_words, // words per window
                          int n_windows,
                          const float *logf,          // M log-frequencies
                          float *out)                 // n_sigma scores
{
    static float by_phase[5][M][M];
    int8_t ginv[5][M];
    float flat = 0.0f;
    for (int x = 0; x < M; x++) flat += logf[x] / M;
    for (int j = 0; j < 5; j++)
        for (int x = 0; x < M; x++)
            ginv[j][letter_perms[j * M + x]] = (int8_t)x;
    for (int j = 0; j < 5; j++)
        for (int s = 0; s < M; s++)
            for (int y = 0; y < M; y++) {
                int p = ginv[j][y] - s;
                if (p < 0) p += M;
                by_phase[j][s][y] = logf[p];
            }

    for (int si = 0; si < n_sigma; si++) {
        const int8_t *sigma = sigmas + si * M;
        int8_t step_inv[5][M];
        for (int a = 0; a < 5; a++)
            for (int x = 0; x < M; x++)
                step_inv[a][letter_perms[a * M + sigma[x]]] = (int8_t)x;

        float best = -1e30f;
        const int8_t *rune = runes;
        const int32_t *len = word_lens;
        const int8_t *shift = word_shifts;
        for (int w = 0; w < n_windows; w++) {
            float table[M][M];
            float seen[5][M];
            int8_t m_inv[M];
            int n_runes = 0;
            memset(table, 0, sizeof table);
            for (int u = 0; u < M; u++) m_inv[u] = (int8_t)u;
            for (int k = 0; k < window_words[w]; k++, len++, shift++) {
                int L = *len;
                int s = *shift;
                int phases = L < 5 ? L : 5;
                for (int j = 0; j < phases; j++)
                    for (int u = 0; u < M; u++)
                        seen[j][u] = by_phase[j][s][m_inv[u]];
                for (int j = 0; j < L; j++, rune++) {
                    float *row = table[*rune];
                    const float *add = seen[j % 5];
                    for (int u = 0; u < M; u++) row[u] += add[u];
                }
                n_runes += L;
                const int8_t *st = step_inv[(L - 1) % 5];
                for (int u = 0; u < M; u++) m_inv[u] = st[m_inv[u]];
            }
            // greedy one-to-one assignment of u to c: base_0 is a bijection
            float total = 0.0f;
            int c_used[M] = {0}, u_used[M] = {0};
            for (int k = 0; k < M; k++) {
                float top = -1e30f;
                int top_c = 0, top_u = 0;
                for (int c = 0; c < M; c++) {
                    if (c_used[c]) continue;
                    for (int u = 0; u < M; u++)
                        if (!u_used[u] && table[c][u] > top) {
                            top = table[c][u];
                            top_c = c;
                            top_u = u;
                        }
                }
                total += top;
                c_used[top_c] = u_used[top_u] = 1;
            }
            float score = (total - n_runes * flat) / n_runes;
            if (score > best) best = score;
        }
        out[si] = best;
    }
}
