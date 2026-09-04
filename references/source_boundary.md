# Source Boundary

Allowed inputs:

- User-provided or user-authorized long-form daily market and point-in-time fundamental data.
- Public Factors Directory pages and academic references linked by individual factor pages.

Formula source:

- The 241 formulas reproduce public mathematical definitions documented by Factors Directory: https://factors.directory/en.
- The implementation is bundled as local NumPy/Pandas modules and does not require another factor Skill or source repository at runtime.
- This repository does not copy website pages, long-form descriptions, branding assets, hosted datasets, private API responses, or credentials.

Data boundary:

- The runtime does not download market or fundamental data.
- Financial fields must be aligned by their actual availability date before use.
- Users are responsible for data licensing, field definitions, price adjustment, universe construction, and trading-calendar conventions.

Not included:

- Materialized production factor datasets or historical backtest artifacts.
- Empirical factor directions, IC or ICIR results, performance claims, or trading recommendations.
- Any affiliation, authorization, or official partnership with Factors Directory.
