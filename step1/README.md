# Step 1
## Get Annotation from mendeley
1. Configure ``config.yaml``, and run the following command:
```
python extract_annot.py
```
This generates ``annot.json``.

2. Download the pdfs based on the url provided in ``annot.json``.
```
python download_pdf.py
```

## Highlight pdf with ML model
1. Configure ``config.py`` for path settings.
2. Run ``highlights.py``, this generates tsv dataset for training from highlighted pdf (or mendeley)
```
python highlights.py
```
**Note:** Mendeley use a different coordinate than the pymupdf, conversion is done when add highlights to the pdf file.

3. Concatenate the tsv to generate the final file. (change accordingly as **dataset_folder** and **train_tsv_file** in ``config.py``)
```
cat dataset/*.tsv > all.tsv
```
4. Run ``model.py`` to train the model. This generate two pickle file, one is **preprocessed_file** for the preprocessed dataset, the other is **model_file** for the saved model.
```
python model.py
```
5. Run ``main.py`` to use the trained model to identify highlights and add to the pdf. To use a pre-trained model, unzip the ``model.zip`` and put the pickle as **model_file** in the ``config.py``.
```
python main.py
```

## Cross validation results
```
{
  "mean_fit_time": [
    592.6879759788513,
    793.6028532981873,
    889.7929029464722,
    493.7695357322693
  ],
  "std_fit_time": [
    11.811757432118068,
    17.667785477508808,
    41.18594713784361,
    58.32348975481459
  ],
  "mean_score_time": [
    49.614366722106936,
    58.97617592811584,
    58.76612429618835,
    36.940512323379515
  ],
  "std_score_time": [
    6.683141009265396,
    4.573166242806917,
    2.3147609558065065,
    11.254476825042842
  ],
  "param_C": [
    0.1,
    1.0,
    10.0,
    100.0
  ],
  "param_kernel": [
    "rbf",
    "rbf",
    "rbf",
    "rbf"
  ],
  "params": [
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
    },
    {
      "C": 100.0,
      "kernel": "rbf"
    }
  ],
  "split0_test_precision": [
    0.0,
    0.6923076923076923,
    0.5352112676056338,
    0.5054945054945055
  ],
  "split1_test_precision": [
    0.0,
    1.0,
    0.6440677966101694,
    0.5694444444444444
  ],
  "split2_test_precision": [
    0.0,
    0.4166666666666667,
    0.4507042253521127,
    0.4186046511627907
  ],
  "split3_test_precision": [
    0.0,
    0.875,
    0.43037974683544306,
    0.3953488372093023
  ],
  "split4_test_precision": [
    0.0,
    0.75,
    0.4057971014492754,
    0.42857142857142855
  ],
  "mean_test_precision": [
    0.0,
    0.7467948717948718,
    0.4932320275705268,
    0.4634927733764943
  ],
  "std_test_precision": [
    0.0,
    0.19622087006428166,
    0.08708337990301543,
    0.06460331567068255
  ],
  "rank_test_precision": [
    4,
    1,
    2,
    3
  ],
  "split0_test_recall": [
    0.0,
    0.07563025210084033,
    0.31932773109243695,
    0.3865546218487395
  ],
  "split1_test_recall": [
    0.0,
    0.07142857142857142,
    0.30158730158730157,
    0.3253968253968254
  ],
  "split2_test_recall": [
    0.0,
    0.04504504504504504,
    0.2882882882882883,
    0.32432432432432434
  ],
  "split3_test_recall": [
    0.0,
    0.11382113821138211,
    0.2764227642276423,
    0.2764227642276423
  ],
  "split4_test_recall": [
    0.0,
    0.07964601769911504,
    0.24778761061946902,
    0.26548672566371684
  ],
  "mean_test_recall": [
    0.0,
    0.07711420489699079,
    0.2866827391630276,
    0.31563705229224964
  ],
  "std_test_recall": [
    0.0,
    0.02198530685189649,
    0.024118529711483604,
    0.043018226805795194
  ],
  "rank_test_recall": [
    4,
    3,
    2,
    1
  ],
  "split0_test_f1": [
    0.0,
    0.13636363636363635,
    0.39999999999999997,
    0.4380952380952381
  ],
  "split1_test_f1": [
    0.0,
    0.13333333333333333,
    0.41081081081081083,
    0.41414141414141414
  ],
  "split2_test_f1": [
    0.0,
    0.08130081300813008,
    0.3516483516483516,
    0.36548223350253806
  ],
  "split3_test_f1": [
    0.0,
    0.20143884892086333,
    0.3366336633663366,
    0.3253588516746411
  ],
  "split4_test_f1": [
    0.0,
    0.144,
    0.3076923076923077,
    0.3278688524590164
  ],
  "mean_test_f1": [
    0.0,
    0.1392873263251926,
    0.3613570267035613,
    0.37418931797456956
  ],
  "std_test_f1": [
    0.0,
    0.03818757592813054,
    0.03879268302220046,
    0.0453562562371348
  ],
  "rank_test_f1": [
    4,
    3,
    2,
    1
  ]
}
```