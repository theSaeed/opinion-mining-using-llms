# Opinion Mining Using Pre-Trained LLMs

This is the official repository of the paper:
> **Opinion Mining Using Pre-Trained Large Language Models: Identifying the Type, Polarity, Intensity, Expression, and Source of Private States** <br>
> The 2024 Joint International Conference on Computational Linguistics, Language
Resources and Evaluation (LREC-COLING 2024) <br>
> Saeed Ahmadnia, Arash Yousefi Jordehi, Mahsa Hosseini Khasheh Heyran, Seyed Abolghasem Mirroshandel, Owen Rambow

## Dataset

### Dependencies
* Python 3.6 or higher
* NLTK 3.8

Please install all dependencies using the following command in your terminal:

```
pip install -r requirements.txt
```

### Cleaner Script

1. Please download the original MPQA dataset from [http://mpqa.cs.pitt.edu/corpora/mpqa_corpus/mpqa_corpus_2_0/](http://mpqa.cs.pitt.edu/corpora/mpqa_corpus/mpqa_corpus_2_0/).
2. Unzip it and move `database.mpqa.2.0/` to the `dataset/` directory.
3. Run the following commands:
```
cd dataset
sh clean.sh
```
4. The cleaned version of the dataset will be available at `dataset/MPQA2.0_cleaned.json`. You can also find each fold's training-validation-test split of each task in [dataset/folds/](dataset/folds/).
