# Natural Question Answers

This dataset is an adaptation of the well known [Natural Questions](https://github.com/google-research-datasets/natural-questions) dataset released by the Google team. This version is created to be used as a benchmark in Question Answering systems.


## Creation

This dataset has been created by taking a positive and a negative question-answer pair from each query-document pair in the original dataset. In particular, for each query-document, one or a few positive examples `(question, long_sentence)` has been created by taking all the `long_sentences` in the annotations. Negative examples has been created in a similar way, taking random `long_sentence`s without annotations pointing to them. Annotations containing only `boolean` answers has been discarded.


## Statistics

The resulting training labels are more balanced that the original dataset or ASNQ. The following table contains the statistics for the publicy available train and dev sets.

|  Set  | Examples | Positive | Negative |
|-------|----------|----------|----------|
| Train | 443292   | 144807   | 298485   |
| Dev   | 57478    | 18697    | 38781    |


## Usage

Download and decompress the original natural-questions dataset. Then run install the necessary libraries with:

```sh
pip install compressed-dictionary tqdm
```

And run the dataset creation with:
```bash
python create.py -i <input-natural-question> -o <output-file> --format <jsonl|tsv|compressed-dictionary>
```
This should take only a few minutes on an average machine.

[`compressed-dictionary`](https://github.com/lucadiliello/compressed-dictionary) is our technology to store dataset as compressed python dictionaries to save memory when training because data are decompressed on-the-fly.
