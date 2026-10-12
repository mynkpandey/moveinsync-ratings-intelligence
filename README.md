# MoveInSync Ratings Intelligence

## Overview
This project analyzes Google Play Store reviews for MoveInSync to identify user pain points, investigate rating trends, and recommend data-driven product and engineering improvements.

## Dataset Summary
- Collected reviews: 24,315
- Cleaned reviews: 24,305
- Average rating: 3.61/5
- Low-rated reviews (1–2 stars): 7,517
- Share of 1–2 star reviews: 30.93%

## Key Findings
- Cab tracking and GPS complaints are prominent in historical low-rated reviews.
- Scheduling and booking reliability are recurring concerns.
- Login and registration issues are prominent in the recent review window.
- App reliability issues include reports of slowness and malfunctioning features.
- Average rating fell from approximately 4.02 in May 2026 to 3.56 in June, then recovered to approximately 4.01 in July.

## Recommended Actions
1. **P0 — Scheduling and booking:** Investigate failed bookings, pickup-time mismatches, and unfulfilled trips.
2. **P0 — Cab tracking and GPS:** Investigate stale location updates, inaccurate ETAs, and tracking failures.
3. **P1 — Login and OTP:** Measure OTP delivery failures and authentication completion rates.
4. **P1 — App reliability:** Correlate crashes, latency, and errors with release versions.
5. **P1 — Safety and support:** Improve safety escalation and complaint resolution.

## Methodology
1. Collect publicly accessible Google Play reviews using `google-play-scraper`.
2. Clean and validate review records with Pandas.
3. Extract 1–2 star reviews.
4. Categorize complaints using keyword-based, multi-label classification.
5. Analyze recent issues, monthly ratings, and app-version comparisons.
6. Investigate rating anomalies and propose measurable engineering fixes.
7. Present results in a Streamlit dashboard.

## Technology Stack
Python, Pandas, NumPy, google-play-scraper, Streamlit, Plotly.

## Run Locally
Install dependencies:

```bash
pip install pandas numpy google-play-scraper streamlit plotly
```

Launch the dashboard from the project root:

```bash
python -m streamlit run app.py
```

## Limitations
Issue categories are keyword-based and can overlap. Reviews are self-selected and do not represent every user. Rating changes and app-version differences indicate investigation leads, not proven causes. Validate recommendations using crash logs, backend telemetry, trip outcomes, release records, and version-level exposure data.

## Future Work
- Automate review collection and dashboard refresh.
- Add NLP-based complaint classification.
- Correlate reviews with production telemetry.
- Monitor issue rates and release quality over time.