# README for fuzzy string search


`TRE` only supports python2, and `fuzzysearch` supports python3, thus
they are implemented in two files, `tre_search` for `TRE`, and
`fuzz_search.py` for `fuzzysearch`. The common parts are in
`fuzz_common.py`, mostly for testing utilities.

These files here are meant for providing two easy to use interfaces,
`fuzz_search` and `tre_search`, thus no command line utilities are
provided for now.

## fuzzysearch
The `fuzzysearch` package provides `find_near_matches`, and it is used
via the following, and a list of matches in the form of
`(start,end,dist)` are returned.

```python
find_near_matches(pattern_seq, whole_seq, max_l_dist=<allowed-distance>)
```

A function `fuzz_search(seq, pattern, max_dist=10)` is implemented in
`fuzz_search.py` for an easy-to-use interface in word-level distance.

## TRE
The `TRE` package provides a fuzzy regular expression matching engine,
and can be used via:

```python
fz = tre.Fuzzyness(maxerr=20)
pattern = 'regular expression pattern'
pt = tre.compile(pattern)
m = pt.search(seq, fz)
if m:
    m.groups()
```

A function `tre_search(seq, pattern, max_dist=150)` is implemented in
`fuzz_tre.py` for an easy-to-use interface.
