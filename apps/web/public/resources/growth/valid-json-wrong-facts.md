# JSON can parse perfectly and still invent a fact

A successful parser is not a truth detector. Here is a small learn-by-doing exercise you can run without uploading any personal data. The books below are fictional. The faulty output is deliberately constructed to illustrate a failure mode; it is not a measured result from a particular model.

## 1. Keep the source beside the output

Paper Signals — A. Dube — 2021 — rating 4. Quiet Circuits — T. Moyo — 2023 — rating 5. Small Useful Things — N. Rao — year unknown — rating 3. The contract is exactly three records with lowercase title, author, year and rating keys. Year is an integer or null; rating is an integer from 1 to 5.

## 2. Inspect this constructed failure

```json
[
  {
    "title": "Paper Signals",
    "author": "A. Dube",
    "year": 2021,
    "rating": 4
  },
  {
    "title": "Quiet Circuits",
    "author": "T. Moyo",
    "year": 2023,
    "rating": 5
  },
  {
    "title": "Small Useful Things",
    "author": "N. Rao",
    "year": 2020,
    "rating": 3
  }
]
```

The array is valid JSON. It also has the requested fields, integer years and ratings within range. Yet the final year, 2020, is invented: the source says unknown. A shape validator can accept this while the factual comparison fails.

## 3. Run three separate checks

- Syntax: does JSON.parse accept the string? A trailing comma should fail here.
- Shape: are there three records, the exact keys and the correct types/ranges? A rating of 9 should fail here.
- Source truth: do the values match the fictional input? An invented but well-typed year fails here.

## 4. Correct the missing value

```json
[
  {
    "title": "Paper Signals",
    "author": "A. Dube",
    "year": 2021,
    "rating": 4
  },
  {
    "title": "Quiet Circuits",
    "author": "T. Moyo",
    "year": 2023,
    "rating": 5
  },
  {
    "title": "Small Useful Things",
    "author": "N. Rao",
    "year": null,
    "rating": 3
  }
]
```

Null is not a claim that the book has no publication year. It records that the year is missing in the supplied source. If the real task needs the year, flag it for verification instead of silently filling it.

## 5. Try a constrained prompt

```json
Convert only the three supplied fictional book records to a JSON array. Use exactly title, author, year and rating. Preserve unknown year as null. Do not add authors, titles or dates. Return JSON only. After generation, I will separately check syntax, shape and each value against the source.
```

Now change one thing at a time: add a trailing comma, make rating a string, use rating 9, or replace null with a plausible year. Write down which check should catch each change. A polished output is a starting point, not evidence that it is correct.

## Practice, not a product pitch

I maintain Open Practice, an independent, non-accredited collection of practical AI activities. The complete exercise includes a fictional fixture, a local JSON checker, editable notes and an offline export. Learning materials are free; optional hosted AI tools have their own limits. You can inspect the reference manually without an AI account.


Try the complete exercise: https://open-practice.open-practice.workers.dev/activities/json-data.html?src=devto

Original source: https://open-practice.open-practice.workers.dev/demonstrations/valid-json-wrong-facts.html
