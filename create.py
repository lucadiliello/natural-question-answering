import json
import os
import random
import re
import csv
from argparse import ArgumentParser, Namespace
from typing import Dict, List, Union

from compressed_dictionary import CompressedDictionary
from tqdm import tqdm


FORMATS = ['jsonl', 'tsv', 'compressed-dictionary']
TAG_RE = re.compile(r'<[^>]+>')


def create_example(question, long_answer, document_text, label):
    """ Create a single example. """
    start_token, end_token = long_answer['start_token'], long_answer['end_token']
    answer = TAG_RE.sub('', " ".join(document_text[start_token: end_token])).strip()
    return {'question': question, 'answer': answer, 'label': label}


def create_examples(input_example: Dict) -> Union[List[Dict], Dict, None]:
    """ Transform an input example of the Natural Questions dataset to an entry
    of the Natural Question Answering dataset.
    """
    document_text = input_example['document_text'].split(" ")
    annotations = input_example['annotations']
    question = input_example['question_text']
    long_answer_candidates = input_example['long_answer_candidates']

    for annotation in annotations:
        if annotation['yes_no_answer'] == "NONE":
            long_answer = annotation['long_answer']
            if long_answer['candidate_index'] != -1:
                yield create_example(question, long_answer, document_text, True)

    # avoid picking correct answer for negative example
    positive_annotations_indexes = set(annotation['long_answer']['candidate_index'] for annotation in annotations)
    all_indexes = set(range(len(long_answer_candidates)))
    choices = list(all_indexes - positive_annotations_indexes)

    for random_negative_answer in random.sample(choices, k=min(len(annotations), len(choices))):
        long_answer = input_example['long_answer_candidates'][random_negative_answer]
        if long_answer['start_token'] < long_answer['end_token']:
            yield create_example(question, long_answer, document_text, False)


def read_and_create(args: Namespace):
    """ Read from input file line-by-line and create examples. """
    random.seed(1337)  # reproducibility
    assert os.path.isfile(args.input_file), f"input file {args.input_file} does not exist"

    with open(args.input_file) as fi:    
        for line in tqdm(fi.readlines(), desc="Processing dataset"):
            input_example = json.loads(line)
            for example in create_examples(input_example):
                if example['question'] and example['answer']:
                    yield example


def main(args: Namespace):

    if args.format == 'compressed-dictionary':
        res = CompressedDictionary()
        for i, example in enumerate(read_and_create(args)):
            res[i] = example
        res.dump(args.output_file)
    elif args.format == 'jsonl':
        with open(args.output_file, "w") as fo:
            for example in read_and_create(args):
                fo.write(json.dumps(example) + "\n")
    elif args.format == 'tsv':
        with open(args.output_file, "w") as fo:
            reader = csv.writer(fo, delimiter="\t", quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for example in read_and_create(args):
                reader.writerow([example['question'], example['answer'], example['label']])
    else:
        raise ValueError(f"format {args.format} not recognized, use one of {FORMATS}")


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-i', '--input_file', type=str, required=True)
    parser.add_argument('-o', '--output_file', type=str, required=True)
    parser.add_argument('--format', choices=FORMATS, default='jsonl')
    args = parser.parse_args()
    main(args)
