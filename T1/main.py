from os import path
from time import time
from lsh import TextLSH, LSH
from loader import write_examples


_DIR = path.dirname(__file__)
_DATA_FILE = 'tweets_2022_abril_junio.csv'
_DATA_PATH = path.join(_DIR, 'data', _DATA_FILE)
_OUTPUT_FILE = 'match_samples.json'


def main():
    text_lsh = TextLSH(0.5, 6, 32)
    author_lsh = LSH(0.5, 54)
    start = time()
    text_lsh.populate_table(_DATA_PATH)
    author_lsh.populate_table(text_lsh.table)
    print(f'Finished finding matches in {time() - start}.')
    print('Finding tweets and writing sample file...')
    write_examples(_OUTPUT_FILE, _DATA_PATH, author_lsh.get_match_samples(3))
    print(f'Samples writen to {_OUTPUT_FILE}')


if __name__ == "__main__":
    main()
