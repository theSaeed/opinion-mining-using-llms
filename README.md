# Opinion Mining Using Pre-Trained LLMs

This is the official repository of the paper:
> **Opinion Mining Using Pre-Trained Large Language Models: Identifying the Type, Polarity, Intensity, Expression, and Source of Private States** [[Paper]](https://aclanthology.org/2024.lrec-main.1093.pdf) [[ACL Anthology]](https://aclanthology.org/2024.lrec-main.1093/) <br>
> _The 2024 Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING 2024)_ <br>
> Saeed Ahmadnia, Arash Yousefi Jordehi, Mahsa Hosseini Khasheh Heyran, Seyed Abolghasem Mirroshandel, Owen Rambow

## Dataset

### Dependencies
* Python 3.7 or higher
* NLTK 3.8

Please install all dependencies using the following command in your terminal:

```
pip install -r dataset/requirements.txt
```

### Cleaner Script

1. Please download the original MPQA dataset from [http://mpqa.cs.pitt.edu/corpora/mpqa_corpus/mpqa_corpus_2_0/](http://mpqa.cs.pitt.edu/corpora/mpqa_corpus/mpqa_corpus_2_0/).
2. Unzip it and move `database.mpqa.2.0/` to the `dataset/` directory.
```
tar -xzf mpqa_2_0_database.tar.gz -C dataset/
rm mpqa_2_0_database.tar.gz 
```
3. Run the following commands:
```
cd dataset
sh clean.sh
```
4. The cleaned version of the dataset will be available at `dataset/MPQA2.0_cleaned.json`. You can also find each fold's training-validation-test split of each task in [dataset/folds/](dataset/folds/).

## Cite Us

```bibtex
@inproceedings{ahmadnia-etal-2024-opinion-mining,
    title = "Opinion Mining Using Pre-Trained Large Language Models: Identifying the Type, Polarity, Intensity, Expression, and Source of Private States",
    author = "Ahmadnia, Saeed and Yousefi Jordehi, Arash and Hosseini Khasheh Heyran, Mahsa and Mirroshandel, SeyedAbolghasem and Rambow, Owen",
    booktitle = "Proceedings of the 2024 Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING 2024)",
    month = may,
    year = "2024",
    address = "Torino, Italia",
    publisher = "ELRA and ICCL",
    url = "https://aclanthology.org/2024.lrec-main.1093",
    pages = "12481--12495",
}
```
