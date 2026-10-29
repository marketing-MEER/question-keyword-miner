# 📂 Sample data

`gsc_queries.csv` is a **made-up** Search Console "Queries" export for a fictional baking blog
(crumbhouse is a fictional brand). All clicks, impressions and positions are invented for the demo.

```bash
question-keyword-miner --gsc examples/gsc_queries.csv --seed sourdough
```

Add `--autocomplete` to also ask Google autocomplete for questions about the seed (needs internet).
