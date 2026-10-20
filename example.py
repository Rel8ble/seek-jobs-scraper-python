"""Hiring-signal report from SEEK (seek.com.au / seek.co.nz) with the SEEK Jobs Scraper on Apify.

Pulls the last week's job ads for your keywords, saves them to seek_jobs.csv, and
prints: the companies hiring the most, how many ads come from agencies, the
remote/hybrid share and the published salary range.

Usage:
    pip install -r requirements.txt
    set APIFY_TOKEN=<YOUR_APIFY_TOKEN>      (export on macOS/Linux)
    python example.py "payroll officer" "data engineer"
"""
import csv
import os
import sys
from collections import Counter

from apify_client import ApifyClient

ACTOR_ID = "rel8ble/seek-jobs-scraper"
COUNTRY = "AU"          # or "NZ"
DAYS = 7

token = os.environ.get("APIFY_TOKEN", "<YOUR_APIFY_TOKEN>")
queries = sys.argv[1:] or ["payroll officer", "data engineer"]

client = ApifyClient(token)
run = client.actor(ACTOR_ID).call(run_input={
    "searchQueries": queries,
    "country": COUNTRY,
    "postedWithinDays": DAYS,
    "maxItems": 0,          # everything; deep search goes past SEEK's 550 cap
    "includeDetails": False,
})
jobs = list(client.dataset(run["defaultDatasetId"]).iterate_items())
jobs = [j for j in jobs if j.get("id")]   # drop the RUN_SUMMARY row if present
print(f"{len(jobs)} ads in the last {DAYS} days for {queries}\n")

fields = ["id", "title", "company", "advertiserName", "location", "area", "workType",
          "workArrangement", "salaryText", "salaryMin", "salaryMax", "salaryPeriod",
          "classification", "subclassification", "listedAt", "url", "sourceQuery"]
with open("seek_jobs.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    w.writeheader()
    w.writerows(jobs)

companies = Counter(j["company"] for j in jobs if j.get("company"))
agency = sum(1 for j in jobs if j.get("advertiserName") and j.get("company")
             and j["advertiserName"] != j["company"])
flexible = sum(1 for j in jobs if j.get("workArrangement") in ("Hybrid", "Remote"))
paid = [j for j in jobs if j.get("salaryMin") and j.get("salaryPeriod") == "year"]

print("Top employers this week:")
for name, n in companies.most_common(10):
    print(f"  {n:3d}  {name}")
print(f"\n{agency} of {len(jobs)} ads were placed by an agency rather than the employer")
print(f"{flexible} of {len(jobs)} ads are hybrid or remote")
if paid:
    lo = min(j["salaryMin"] for j in paid)
    hi = max(j.get("salaryMax") or j["salaryMin"] for j in paid)
    print(f"Published annual salary range on {len(paid)} ads: ${lo:,.0f} - ${hi:,.0f}")

print("\nSaved seek_jobs.csv")
