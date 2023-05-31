import numpy as np
from loader import load_tweets
from hashlib import sha1
from functools import reduce
from struct import unpack
from random import sample
from scipy.integrate import quad as integrate


_PRIME = np.uint64((1 << 61) - 1)
_MAX_SIZE = np.uint64((1 << 32) - 1)


def hash(value: bytes) -> int:
    return unpack('<I', sha1(value).digest()[:4])[0]


def false_positive_probability(s: int, b: int, r: int):
    def probability(x):
        return 1 - (1 - x**r)**b
    a, _ = integrate(probability, 0.0, s)
    return a


def false_negative_probability(s: int, b: int, r: int):
    def probability(x):
        return 1 - (1 - (1 - x**r)**b)
    a, _ = integrate(probability, s, 1.0)
    return a


class LSH:

    def __init__(self, s: float, num_perm: float):
        self.table = {}
        self.bands, self.rows = self._generate_params(s, num_perm)
        self.permutations = self._generate_permutations(self.bands * self.rows)

    def _generate_params(self, s, num_perm):
        # https://github.com/ekzhu/datasketch/blob/master/datasketch/lsh.py
        min_error = float("inf")
        opt = (0, 0)
        for b in range(1, num_perm+1):
            max_r = int(num_perm / b)
            for r in range(1, max_r+1):
                fp = false_positive_probability(s, b, r)
                fn = false_negative_probability(s, b, r)
                error = fp + fn
                if error < min_error:
                    min_error = error
                    opt = (b, r)
        return opt

    def _generate_permutations(self, n_perms):
        return np.array(
            [
                (
                    np.random.randint(1, _PRIME, dtype=np.uint64),
                    np.random.randint(0, _PRIME, dtype=np.uint64)
                )
                for _ in range(n_perms)
            ],
            dtype=np.uint64
        ).T

    def min_hash(self, values):
        h_values = np.array(values, dtype=np.uint64)
        a, b = self.permutations
        perms = np.tile(h_values, (self.bands * self.rows, 1)).T
        insize_perms = np.bitwise_and(((perms * a + b) % _PRIME).T, _MAX_SIZE)
        return insize_perms.T.min(axis=0)

    def add_to_table(self, key, value):
        if key not in self.table.keys():
            self.table[key] = {value}
            return
        self.table[key].add(value)

    def populate_table(self, query):
        for key, value in query.items():
            signature = self.min_hash(np.array(list(value), dtype=np.uint64))
            for i in range(self.bands):
                self.add_to_table(
                    hash(
                        reduce(
                            lambda x, y: x + y,
                            signature[i * self.rows: (i + 1) * self.rows]
                        )
                    ),
                    key
                )

    def get_match_samples(self, n: int) -> list[tuple[str, str]]:
        samples = []
        candidates = [
            match
            for match in filter(lambda x: len(x) >= 2, self.table.values())
        ]
        for match in sample(candidates, n):
            samples.append(tuple(sample(list(match), 2)))
        return samples


class TextLSH(LSH):

    def __init__(self, s: float, k: int, num_perm: int):
        super().__init__(s, num_perm)
        self.shingle_len: int = k
        self.shingle_top_pos: int = 0
        self.shingle_pos: dict[str, int] = {}

    def shingle(self, text: str):
        text_len = len(text)
        if text_len < self.shingle_len:
            return (text)
        return list(
            text[i: i + self.shingle_len + 1]
            for i in range(0, text_len - self.shingle_len + 1)
        )

    def shingle_order(self, shingle: str):
        try:
            return self.shingle_pos[shingle]
        except KeyError:
            self.shingle_pos[shingle] = self.shingle_top_pos
            self.shingle_top_pos += 1
            return self.shingle_top_pos - 1

    def encode_text(self, text: str):
        encoding = np.array(
            list(map(lambda x: self.shingle_order(x), self.shingle(text))),
            dtype=np.uint64
        )
        return encoding

    def hash_tweet(self, author: str, text: str):
        signature = self.min_hash(self.encode_text(text))
        for i in range(self.bands):
            self.add_to_table(
                author,
                hash(
                    reduce(
                        lambda x, y: (x + y) % _PRIME,
                        signature[i * self.rows: (i + 1) * self.rows]
                    )
                )
            )

    def populate_table(self, file_path):
        for author, text in load_tweets(file_path):
            self.hash_tweet(author, text)
