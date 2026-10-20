# SEEK jobs scraper (Python) - seek.com.au and seek.co.nz job ads API

Scrape job ads from SEEK Australia and SEEK New Zealand with Python, using the [SEEK Jobs Scraper](https://apify.com/rel8ble/seek-jobs-scraper) on Apify. Pass keywords, locations and filters (or SEEK search URLs); get back one clean JSON row per job: title, company, location, salary as written and as numbers, work type, on-site/hybrid/remote, classification, listing date and URL, plus the full description and company profile if you want them.

> Disclosure: I built this actor; it's a paid tool on Apify ($0.80 per 1,000 jobs).

It reads the same JSON the SEEK site loads, over plain HTTP (no browser, no login), 100 jobs per request. SEEK caps any one search at 550 jobs; the actor splits big searches by category, work type and arrangement and merges them, so a search with 8,877 jobs returned 8,539 in testing (96%) in about 80 seconds.

## Why use it

- **Hiring-signal lead generation.** A company advertising for three payroll officers is a prospect for payroll software. Run your keywords daily with `postedWithinDays: 1` and push new ads, with the company website attached, to your CRM.
- **Recruitment market mapping.** `company` vs `advertiserName` tells you whether an ad is a direct employer or an agency.
- **Salary benchmarking.** `salaryMin` / `salaryMax` / `salaryPeriod` parsed from the ads that publish pay (about half).
- **Job boards and aggregators.** Stable SEEK job ids for deduplication, no 550-job cutoff.

## Quick start (Python)

```bash
pip install apify-client
```

```python
from apify_client import ApifyClient

client = ApifyClient("<YOUR_APIFY_TOKEN>")

run = client.actor("rel8ble/seek-jobs-scraper").call(run_input={
    "searchQueries": ["data engineer", "data analyst"],
    "locations": ["Sydney NSW", "All Melbourne VIC"],
    "country": "AU",
    "workArrangements": ["hybrid", "remote"],
    "postedWithinDays": 7,
    "maxItems": 200,
})

for job in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(job["company"], "|", job["title"], "|", job["location"], "|", job.get("salaryText"))
```

Get your token at https://console.apify.com/settings/integrations.

## Quick start (Node.js)

```js
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: '<YOUR_APIFY_TOKEN>' });
const run = await client.actor('rel8ble/seek-jobs-scraper').call({
    country: 'NZ',
    classification: 'Healthcare & Medical',
    searchQueries: ['nurse'],
    maxItems: 0,          // 0 = everything, deep search goes past SEEK's 550 cap
});
const { items } = await client.dataset(run.defaultDatasetId).listItems();
console.log(items.map((j) => `${j.company}: ${j.title} (${j.location})`));
```

## Full example: hiring-signal report

[`example.py`](example.py) pulls this week's ads for your keywords, writes `seek_jobs.csv`, and prints the companies hiring the most, how many ads come from agencies, the remote/hybrid share and the published AUD salary range.

```bash
pip install -r requirements.txt
set APIFY_TOKEN=<YOUR_APIFY_TOKEN>        # export APIFY_TOKEN=... on macOS/Linux
python example.py "payroll officer" "data engineer"
```

## What the input accepts

| Field | Default | Description |
|---|---|---|
| `searchQueries` | - | Keywords, one search each. Empty = all jobs matching the filters |
| `locations` | whole country | As SEEK writes them: `Sydney NSW`, `All Melbourne VIC`, `Auckland`, a suburb or a postcode |
| `country` | `AU` | `AU` (seek.com.au) or `NZ` (seek.co.nz) |
| `classification` | `any` | One of SEEK's 30 categories, e.g. `Healthcare & Medical` |
| `workTypes` | all | `fulltime`, `parttime`, `contract`, `casual` |
| `workArrangements` | all | `onsite`, `hybrid`, `remote` |
| `postedWithinDays` | 0 (any) | 1, 3, 7, 14, 31 |
| `salaryMin` / `salaryMax` | 0 | In the unit set by `salaryType` (`annual`, `monthly`, `hourly`) |
| `sort` | `relevance` | `relevance` or `date` |
| `maxItems` | 100 | Max jobs per search; 0 = all |
| `deepSearch` | true | Split searches above 550 jobs so nothing is cut off |
| `includeDetails` | false | Full description, expiry, screening questions, company profile (one extra request per job) |
| `startUrls` | - | SEEK search URLs, job URLs or bare job ids |

## Sample output

A real row from a 12 Oct 2026 run (`data engineer`, Sydney NSW, details on; long texts trimmed):

```json
{
  "id": "95195166",
  "title": "Research Data Storage Specialist",
  "company": "The University of Sydney",
  "advertiserName": "The University of Sydney",
  "location": "Sydney NSW",
  "area": "New South Wales NSW",
  "countryCode": "AU",
  "workType": "Full time",
  "workArrangement": "Hybrid",
  "isRemote": false,
  "salaryText": "$152,045 to $160,430 + 17% Superannuation",
  "salaryMin": 152045,
  "salaryMax": 160430,
  "salaryCurrency": "AUD",
  "salaryPeriod": "year",
  "classification": "Information & Communication Technology",
  "subclassification": "Database Development & Administration",
  "teaser": "Support pivotal research infrastructure systems that enable world-class research at the University of Sydney.",
  "listedAt": "2026-10-12T01:01:13.000Z",
  "isSponsored": false,
  "url": "https://www.seek.com.au/job/95195166",
  "companyWebsite": "http://sydney.edu.au/",
  "companyIndustry": "Education, Training & Professional Development",
  "companyRating": 3.2,
  "sourceQuery": "data engineer",
  "sourceLocation": "Sydney NSW"
}
```

Fill rates on an 8,539-job run (`nurse`, all of Australia): id, title, company, location, work type, work arrangement, classification, listing date and URL 100%; bullet points 70%; salary text 53%; parsed salary numbers 43%. With details on (301-job run): description 100%; company industry 34%; company website 27% (company fields exist only for employers with a SEEK profile). Fields SEEK does not publish are `null`, never guessed.

## Price and limits

- **$0.80 per 1,000 jobs** (one result = one job ad, description and company profile included). A 550-job search costs $0.44. Duplicates and failed requests are not charged.
- Apify's free plan includes $5 of monthly credit, enough for about 6,000 jobs a month.
- 550 jobs per single search is SEEK's own limit; deep search returned 96% of an 8,877-job total in testing.
- Locations must be ones SEEK recognises; an unknown location returns 0 jobs and the run summary says so.
- Ads live about 30 days, so `postedWithinDays` above 31 has no effect.
- Only the public job ad and company profile are read. No applicant or recruiter contact data is collected.
- Details cost one request per job: about 160 jobs a minute instead of several thousand.

## Links

- Apify Store: https://apify.com/rel8ble/seek-jobs-scraper
- Apify Python client: https://docs.apify.com/api/client/python

## License

MIT for the code in this repo. The actor itself is a paid Apify tool.
