package main

import (
	"strings"
)

func iterngrams(runes []rune, length int, cut int) [][]rune {
	N := len(runes)
	ngrams := make([][]rune, 0)

	if cut == 0 {
		for i := 0; i < N-length+1; i++ {
			ngrams = append(ngrams, runes[i:i+length])
		}
	} else if cut <= length && cut > 0 {
		for i := cut - 1; i < N-length+1; i += length {
			ngrams = append(ngrams, runes[i:i+length])
		}
	}

	return ngrams
}

func ngrams(runes []rune, length int, cut int) [][]rune {
	return iterngrams(runes, length, cut)
}

func digraphs(runes []rune, cut int) [][]rune {
	return ngrams(runes, 2, cut)
}

func trigraphs(runes []rune, cut int) [][]rune {
	return ngrams(runes, 3, cut)
}

func tetragraphs(runes []rune, cut int) [][]rune {
	return ngrams(runes, 4, cut)
}

func bigrams(runes []rune, cut int) [][]rune {
	return ngrams(runes, 2, cut)
}

func trigrams(runes []rune, cut int) [][]rune {
	return ngrams(runes, 3, cut)
}

func quadgrams(runes []rune, cut int) [][]rune {
	return ngrams(runes, 4, cut)
}

func ngramDistribution(runes []rune, length int, cut int) map[string]int {
	ngrams := iterngrams(runes, length, cut)
	frequencies := make(map[string]int)
	for _, ngram := range ngrams {
		key := string(ngram)
		frequencies[key]++
	}
	return frequencies
}

func ngramPositions(runes []rune, length int, cut int) map[string][]int {
	positions := make(map[string][]int)
	ngrams := iterngrams(runes, length, cut)
	for i, ngram := range ngrams {
		key := string(ngram)
		positions[key] = append(positions[key], i)
	}
	return positions
}
