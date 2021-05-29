# Highlight pdf with ML model

1. Configure and run ``highlights.py``, this generates tsv dataset for training from highlighted pdf (or mendeley)
```
python highlights.py
```
2. Concatenate the tsv to generate the final file
```
cat datasets/*.tsv > all.tsv
```
3. Configure and run ``model.py`` to train the model
```
python model.py
```
4. Configure and run ``main.py`` to use the trained model to identify highlights and add to the pdf.
```
python main.py
```