# Step 1
## Get Annotation from mendeley
1. Configure ``config.yaml``, and run the following command:
```
python extract_annot.py
```

## Highlight pdf with ML model
1. Configure ``config.py`` for path settings.
2. Run ``highlights.py``, this generates tsv dataset for training from highlighted pdf (or mendeley)
```
python highlights.py
```
**Note:** Mendeley use a different coordinate than the pymupdf, conversion is done when add highlights to the pdf file.

2. Concatenate the tsv to generate the final file. (change accordingly as **dataset_folder** and **train_tsv_file** in ``config.py``)
```
cat dataset/*.tsv > all.tsv
```
3. Run ``model.py`` to train the model. This generate two pickle file, one is **preprocessed_file** for the preprocessed dataset, the other is **model_file** for the saved model.
```
python model.py
```
4. Run ``main.py`` to use the trained model to identify highlights and add to the pdf. To use a pre-trained model, unzip the ``model.zip`` and put the pickle as **model_file** in the ``config.py``.
```
python main.py
```

## Cross validation results
```
{
  "mean_fit_time": [
    331.70669651031494,
    584.4845421791076,
    786.8646607398987,
    793.0170915603637
  ],
  "std_fit_time": [
    5.549939933329034,
    2.043943807365307,
    22.537849270777848,
    69.14977394966095
  ],
  "mean_score_time": [
    36.99736890792847,
    56.5459858417511,
    62.55118737220764,
    43.47189927101135
  ],
  "std_score_time": [
    3.1186122386885553,
    7.02968559668811,
    5.468647161074893,
    14.767032651899706
  ],
  "params": [
    {
      "C": 0.01,
      "kernel": "rbf"
    },
    {
      "C": 0.1,
      "kernel": "rbf"
    },
    {
      "C": 1.0,
      "kernel": "rbf"
    },
    {
      "C": 10.0,
      "kernel": "rbf"
    }
  ],
  "split0_test_precision": [
    0.0,
    0.0,
    0.5833333333333334,
    0.48214285714285715
  ],
  "split1_test_precision": [
    0.0,
    0.0,
    0.6428571428571429,
    0.5
  ],
  "split2_test_precision": [
    0.0,
    0.0,
    0.4,
    0.3442622950819672
  ],
  "split3_test_precision": [
    0.0,
    0.0,
    0.9166666666666666,
    0.515625
  ],
  "split4_test_precision": [
    0.0,
    0.0,
    0.625,
    0.5588235294117647
  ],
  "mean_test_precision": [
    0.0,
    0.0,
    0.6335714285714286,
    0.4801707363273178
  ],
  "std_test_precision": [
    0.0,
    0.0,
    0.1657601195509948,
    0.07254165704284628
  ],
  "rank_test_precision": [
    3,
    3,
    1,
    2
  ],
  "split0_test_recall": [
    0.0,
    0.0,
    0.06666666666666667,
    0.2571428571428571
  ],
  "split1_test_recall": [
    0.0,
    0.0,
    0.08108108108108109,
    0.2702702702702703
  ],
  "split2_test_recall": [
    0.0,
    0.0,
    0.039603960396039604,
    0.2079207920792079
  ],
  "split3_test_recall": [
    0.0,
    0.0,
    0.11,
    0.33
  ],
  "split4_test_recall": [
    0.0,
    0.0,
    0.08928571428571429,
    0.3392857142857143
  ],
  "mean_test_recall": [
    0.0,
    0.0,
    0.07732748448590034,
    0.2809239267556099
  ],
  "std_test_recall": [
    0.0,
    0.0,
    0.023500209887134145,
    0.048627269201165085
  ],
  "rank_test_recall": [
    3,
    3,
    2,
    1
  ],
  "split0_test_f1": [
    0.0,
    0.0,
    0.11965811965811965,
    0.3354037267080745
  ],
  "split1_test_f1": [
    0.0,
    0.0,
    0.14400000000000002,
    0.3508771929824562
  ],
  "split2_test_f1": [
    0.0,
    0.0,
    0.07207207207207207,
    0.25925925925925924
  ],
  "split3_test_f1": [
    0.0,
    0.0,
    0.19642857142857142,
    0.40243902439024387
  ],
  "split4_test_f1": [
    0.0,
    0.0,
    0.15625,
    0.4222222222222223
  ],
  "mean_test_f1": [
    0.0,
    0.0,
    0.13768175263175264,
    0.3540402851124512
  ],
  "std_test_f1": [
    0.0,
    0.0,
    0.04114698119569067,
    0.05715239948503746
  ],
  "rank_test_f1": [
    3,
    3,
    2,
    1
  ]
}
```