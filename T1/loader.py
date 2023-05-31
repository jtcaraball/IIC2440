from csv import reader
from typing import Generator
from json import dumps


def load_tweets(file_path: str) -> Generator[tuple[str, str], None, None]:
    with open(file_path, 'r') as file:
        row_reader = reader(file)
        next(row_reader, None)
        for line in row_reader:
            yield line[2], line[3]


def get_tweets(
    file_path: str,
    matches: list[tuple[str, str]]
) -> dict[str, dict[str, list[str]]]:
    tweets = {}
    authors = []
    for match in matches:
        auth_1, auth_2 = match
        tweets[auth_1] = []
        tweets[auth_2] = []
        authors.extend([auth_1, auth_2])

    for author, tweet in load_tweets(file_path):
        if author in authors:
            tweets[author].append(tweet)

    return {
        f'match-{i}': {
            f'{match[0]}': tweets[match[0]],
            f'{match[1]}': tweets[match[1]]
        }
        for i, match in enumerate(matches)
    }


def write_examples(
    output_name: str,
    file_path: str,
    matches: list[tuple[str, str]]
):
    examples = get_tweets(file_path, matches)
    exapmples_json = dumps(examples, indent=2)
    with open(output_name, 'w') as file:
        file.write(exapmples_json)
