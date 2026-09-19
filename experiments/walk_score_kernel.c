// ABOUTME: Compiled inner loop of the base_0-free walk verifier: scores many sigmas
// ABOUTME: against one set of letter perms over several ciphertext windows.

#include <stdint.h>
#include <string.h>

#define M 29

// Writes one score per sigma, in nats per rune above the flat baseline. A window's
// score is the greedy one-to-one assignment of u to c on the table S[c][u], which
// accumulates log f( g_j^-1 M_w^-1 (u) ) over the positions carrying ciphertext
// rune c. Windows combine as their maximum, or (sum_windows) as their rune-weighted
// mean, which credits a key for every window it gets right.
void score_sigmas(const int8_t *letter_perms, // 5 x M, position j uses perm j % 5
                  const int8_t *sigmas,       // n_sigma x M
                  int n_sigma,
                  const int8_t *runes,        // ciphertext runes, windows concatenated
                  const int32_t *word_lens,   // word lengths, windows concatenated
                  const int32_t *window_words, // words per window
                  int n_windows,
                  const float *logf,          // M log-frequencies
                  int sum_windows,
                  float *out)                 // n_sigma scores
{
    float by_phase[5][M];
    float flat = 0.0f;
    for (int x = 0; x < M; x++) flat += logf[x] / M;
    for (int j = 0; j < 5; j++)
        for (int x = 0; x < M; x++)
            by_phase[j][letter_perms[j * M + x]] = logf[x];

    for (int s = 0; s < n_sigma; s++) {
        const int8_t *sigma = sigmas + s * M;
        int8_t step_inv[5][M];
        for (int a = 0; a < 5; a++)
            for (int x = 0; x < M; x++)
                step_inv[a][letter_perms[a * M + sigma[x]]] = (int8_t)x;

        float best = -1e30f;
        float gained = 0.0f;
        int all_runes = 0;
        const int8_t *rune = runes;
        const int32_t *len = word_lens;
        for (int w = 0; w < n_windows; w++) {
            float table[M][M];
            float seen[5][M];
            int8_t m_inv[M];
            int n_runes = 0;
            memset(table, 0, sizeof table);
            for (int u = 0; u < M; u++) m_inv[u] = (int8_t)u;
            for (int k = 0; k < window_words[w]; k++, len++) {
                int L = *len;
                int phases = L < 5 ? L : 5;
                for (int j = 0; j < phases; j++)
                    for (int u = 0; u < M; u++)
                        seen[j][u] = by_phase[j][m_inv[u]];
                for (int j = 0; j < L; j++, rune++) {
                    float *row = table[*rune];
                    const float *add = seen[j % 5];
                    for (int u = 0; u < M; u++) row[u] += add[u];
                }
                n_runes += L;
                const int8_t *si = step_inv[(L - 1) % 5];
                for (int u = 0; u < M; u++) m_inv[u] = si[m_inv[u]];
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
            gained += total - n_runes * flat;
            all_runes += n_runes;
        }
        out[s] = sum_windows ? gained / all_runes : best;
    }
}
