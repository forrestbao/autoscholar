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
    730.0963418006897,
    786.0850782871246,
    458.1646556854248,
    263.9219160079956
  ],
  "std_fit_time": [
    19.511536884353994,
    24.62287742091309,
    39.994328956358565,
    138.10951300718418
  ],
  "mean_score_time": [
    54.150642204284665,
    51.54488458633423,
    42.13119487762451,
    25.22088475227356
  ],
  "std_score_time": [
    6.243268583868012,
    3.9268922580311725,
    3.1277043678466767,
    6.936906162257738
  ],
  "param_C": [
    1.0,
    10.0,
    100.0,
    1000.0
  ],
  "param_kernel": [
    "rbf",
    "rbf",
    "rbf",
    "rbf"
  ],
  "params": [
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
    },
    {
      "C": 1000.0,
      "kernel": "rbf"
    }
  ],
  "split0_test_precision": [
    0.6666666666666666,
    0.4925373134328358,
    0.5068493150684932,
    0.5211267605633803
  ],
  "split1_test_precision": [
    0.9,
    0.5,
    0.4823529411764706,
    0.46511627906976744
  ],
  "split2_test_precision": [
    0.7333333333333333,
    0.609375,
    0.5287356321839081,
    0.5180722891566265
  ],
  "split3_test_precision": [
    0.6470588235294118,
    0.5625,
    0.5180722891566265,
    0.5
  ],
  "split4_test_precision": [
    0.7368421052631579,
    0.4675324675324675,
    0.47619047619047616,
    0.4367816091954023
  ],
  "mean_test_precision": [
    0.7367801857585139,
    0.5263889561930607,
    0.5024401307551949,
    0.4882193875970353
  ],
  "std_test_precision": [
    0.08901507825798935,
    0.05195591965413303,
    0.020237580032811286,
    0.03253451221758174
  ],
  "rank_test_precision": [
    1,
    2,
    3,
    4
  ],
  "split0_test_recall": [
    0.09090909090909091,
    0.3,
    0.33636363636363636,
    0.33636363636363636
  ],
  "split1_test_recall": [
    0.07894736842105263,
    0.30701754385964913,
    0.35964912280701755,
    0.3508771929824561
  ],
  "split2_test_recall": [
    0.102803738317757,
    0.3644859813084112,
    0.42990654205607476,
    0.40186915887850466
  ],
  "split3_test_recall": [
    0.08870967741935484,
    0.2903225806451613,
    0.3467741935483871,
    0.3225806451612903
  ],
  "split4_test_recall": [
    0.125,
    0.32142857142857145,
    0.35714285714285715,
    0.3392857142857143
  ],
  "mean_test_recall": [
    0.09727397501345107,
    0.3166509354483586,
    0.36596727038359467,
    0.35019526953432034
  ],
  "std_test_recall": [
    0.015805278838989873,
    0.02597789664096239,
    0.03301747738831584,
    0.027362586905109756
  ],
  "rank_test_recall": [
    4,
    3,
    1,
    2
  ],
  "split0_test_f1": [
    0.16,
    0.37288135593220345,
    0.4043715846994535,
    0.4088397790055249
  ],
  "split1_test_f1": [
    0.14516129032258063,
    0.3804347826086956,
    0.41206030150753764,
    0.4
  ],
  "split2_test_f1": [
    0.18032786885245902,
    0.456140350877193,
    0.47422680412371127,
    0.45263157894736844
  ],
  "split3_test_f1": [
    0.15602836879432624,
    0.3829787234042554,
    0.41545893719806765,
    0.39215686274509803
  ],
  "split4_test_f1": [
    0.21374045801526717,
    0.380952380952381,
    0.40816326530612246,
    0.38190954773869346
  ],
  "mean_test_f1": [
    0.1710515971969266,
    0.3946775187549457,
    0.42285617856697855,
    0.4071075536873369
  ],
  "std_test_f1": [
    0.024193103298595274,
    0.03092199605320287,
    0.025952931325693884,
    0.024431199165352285
  ],
  "rank_test_f1": [
    4,
    3,
    1,
    2
  ]
}
0.42285617856697855     {'C': 100.0, 'kernel': 'rbf'}
```