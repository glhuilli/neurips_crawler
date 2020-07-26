# neurips_crawler

Get all NeurIPS papers for input years.

This code is inspired on @benhamner's [NeurIPS 2015 crawler](https://github.com/benhamner/nips-2015-papers).

To use this script you should first setup a Virtual Environment, and run

```bash
pip install -r requirements.txt
```

Then you can run the code below to start crawling all PDFs from every NeurIPS conference from year `from_year` to year `to_year`. The output will be stored in `./output` (default) folder. And the execution logs will be stored in `crawler_log.txt` (default).

```bash
python src/neurips_crawler.py --from_year=1998 --to_year=2018 --output=./output/ --log=./crawler_log.txt
```

For each conference year, the script will create a folder inside `--output` where all papers will be stored together with a `jsons` file with each paper's metadata collected from the website. If a folder for a given year is available, it will be assumed that the year was already processed and skip to the next one. Logs will be available in both the console and a log file.

Any entry on the `jsons` file will look like this:

```
{
  "id": "755b0ec5-8636-50cc-9c95-e9f7d11e3a47",
  "title": "Efficient Algorithms for Non-convex Isotonic Regression through Submodular Optimization",
  "pdf_name": "7286-efficient-algorithms-for-non-convex-isotonic-regression-through-submodular-optimization.pdf",
  "abstract": "We consider the minimization of submodular functions subject to ordering constraints. We show that this potentially non-convex optimization problem can be cast as a convex optimization problem on a space of uni-dimensional measures, with ordering constraints corresponding to first-order stochastic dominance.  We propose new discretization schemes that lead to simple and efficient algorithms based on zero-th, first, or higher order oracles;  these algorithms also lead to improvements without isotonic constraints. Finally,   our experiments  show that non-convex loss functions can be much more robust to outliers for isotonic regression, while still being solvable in polynomial time.",
  "authors": [
    {
      "id": "francis-bach-6335",
      "name": "Francis Bach"
    }
  ]
}
```

If you want to retry a given year (e.g. some papers failed to download), you can use the `--force` option. 



The script was formatted using `mypy`, `yapf`, `isort`, and `pylint`.

Note that downloading the whole NeurIPS/NIPS period (1988 - 2018) could be a large set of files (e.g. The period 1988 to 2018 is ~8.8Gb). Also, note that this code will only work as long as NeurIPS organizers keep the website unchanged.
