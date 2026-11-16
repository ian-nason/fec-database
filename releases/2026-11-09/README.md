# FEC snapshot validation

This bundle verifies a separately downloaded, closed FEC DuckDB snapshot. It does not contain the database or the large raw FEC inputs, and it is not an offline or one-command source rebuild. Source URLs are mutable; the source lock identifies the exact bytes used for this snapshot. A future download from the same URL may differ.

1. Create a Python virtual environment and install `requirements.txt`.
2. Download `fec.duckdb` from the same immutable dataset revision as this bundle.
3. Run `python verify_snapshot.py /path/to/fec.duckdb`.

Verification reads every byte for SHA-256, then every source-table row for typed fingerprints. It can take substantial time. It uses one thread, a 1 GiB memory limit, no external access and no disk spill. Increase `--memory-limit` only when you have sufficient memory. It opens the database read-only and refuses a WAL. It does not run the expensive contribution views.

## Fingerprint algorithm

Using exactly DuckDB 1.5.5, serialize the full typed row, in stored column order and including `cycle`, with `to_json(t)`. Compute `sha256` of that JSON. Split its 64 hexadecimal digits into four consecutive 16-digit unsigned 64-bit limbs. For each table/cycle, store the row count and four exact sums, accumulated as signed 128-bit integers. All sums are decimal **strings** in JSON, to preserve integers above JavaScript's safe-number range. Nulls, typed dates, DOUBLE serialization, column order, and multiplicity are significant. Row order is not. These multiset fingerprints are not a proof of injectivity or an exact row-by-row diff; the whole-file SHA-256 independently identifies the delivered artifact.

The verifier checks table schemas, complete cycle fingerprints, base null statistics, metadata counts, dictionary schema and unchanged view SQL. Dictionary statistics/examples for three contribution views are explicitly unavailable. It does not prove source content is factually correct or perform fresh source retrieval and parsing.

The source lock records official source/header URLs, SHA-256 identities, byte sizes and acquisition times, available/expected-absent outcomes, the 2022 shard equivalence, amendment filtering and standalone correction. The ZIP contains code, tests, documentation and the original MIT license. `bundle-files.json` hashes every other file in the ZIP and intentionally does not hash itself; the dataset provenance hashes the entire ZIP. Neither embeds its own future repository commit ID.

## Use restrictions

Underlying FEC government records are public domain for copyright purposes. Contributor names and addresses may not be sold or used commercially or to solicit contributions/donations. See the [FEC guidance](https://www.fec.gov/updates/sale-or-use-contributor-information/). The MIT license covers the code, not a waiver of these restrictions.
