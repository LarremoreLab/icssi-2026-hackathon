# CVParsa Codebook
# Last updated: 27 June 2026
# Copyright: [Cevian Labs, Inc](https://cevianlabs.io)

This codebook explains the fields in each `*_cvp.json` file produced by CVParsa. Fields whose names are self-explanatory (e.g., `first_name`, `Title`, `DOI`, `start_year`) are not listed here. Only fields that benefit from definition, derivation notes, value enumerations, or compression-schema documentation are described.

Each `*_cvp.json` file contains the consolidated parse of one academic CV.

---

## 1. Top-level fields

### `ParseTime` *(string)*
The UTC timestamp at which this CV's parse completed, formatted as `"YYYY-MM-DD HH:MM:SS"` (no timezone suffix).

### `pubs_all` *(integer)*
Aggregate publication counts across the full `Publications` list. Counts the total number of publication entries retained after validation and filtering.

### `pubs_journal`, `pubs_proc`, `pubs_chapter`, `pubs_book` *(integer)*
Counts of publication entries by `Type` field:

- `pubs_journal` — entries with `Type == "journal-article"`.
- `pubs_proc` — entries with `Type == "proceedings-article"`.
- `pubs_chapter` — entries with `Type == "book-chapter"` (also includes `"book-section"` when present).
- `pubs_book` — entries with `Type == "book"`.

These four buckets are **disjoint** by construction. Their sum is typically less than `pubs_all` because other publication types are excluded from all four.

---

## 2. `Person`

### `gender` *(string)*
A single-character categorical inference based on publicly available web data: `M` (Man), `W` (Woman), `N` (Nonbinary), `U` (Unclear).

Gender values are inferences, not self-reports, and should be treated as noisy.

### `phd_year` *(integer or null)*
The four-digit year in which the CV owner most recently completed a Ph.D. (or equivalent doctoral degree). Derived from the most recent PhD (or equivalent) entry in `Education[]`. If the degree is recognized by CVParsa as "in progress" based on what is recorded in the CV, then the current year is used. `null` when no Ph.D. entry is found.

### `faculty_year` *(integer or null)*
The four-digit year of the CV owner's first faculty appointment. Derived as the minimum `start_year` across `Employment[]` entries classified as faculty positions. `null` if no faculty position is detected.

---

## 3. `Interests`

### `keywords` *(list of strings)*
A list of up to 7 short scholarly-interest keywords, inferred from explicitly listed interests or from publication titles listed in the CV.

### `summary` *(string)*
A 20–25 word phrase (not a complete sentence) summarizing the CV owner's research interests, as inferred from the contents of the CV.

---

## 4. `Advising`

### `advisors[].type` *(string)*
The kind of advising relationship between the named advisor and the CV owner. No fixed values. Examples include `PhD`, `MS`, `BS`, `Postdoc`, and similar. Treat as a free-form short label.

### `advisors[].year` *(integer or null)*
The four-digit year in which the advising relationship ended — i.e., the year the CV owner completed the degree (or postdoc) supervised by this advisor.

### `advisors[].institution` *(string)*
The standardized institutional affiliation of the advisor at the time of advising, as reported in the CV.

### `advisees[].institution` *(string)*
The institution at which the advisee was supervised. Defaults to `Person.institution` unless the CV explicitly states a different institution for the advisee.

### `advisees[].start_year`, `advisees[].end_year` *(integer or null)*
Integer years marking the start and end (typically graduation year) of the advising relationship. Either or both may be `null` when the CV does not provide the corresponding year; `end_year == null` implies an ongoing advising relationship relative to the date of the CV.

### `advisees[].thesis` *(string or null)*
The title of the advisee's thesis or dissertation, when listed in the CV. Omitted (set to `null` or absent) for postdoc advisees.

### `advisee_count` *(integer)*
The total number of advisees identified in the CV.

---

## 5. `Education[]` and `Employment[]`

### `start_year`, `end_year` *(integer or null)*
Integer years marking the start and end of an identified education or employment entry. Either or both may be `null` when the CV does not provide or imply the year. May be inferred from other constraining information present in the CV.

---

## 6. `Publications[]`

### `Authors[]` *(list of objects)*
The list of authors, in author order. The structure of each author entry depends on the Source for the publication record information:

- **`Source: Crossref`** — `{given, family, sequence}` where `sequence ∈ {"first", "additional"}` (Crossref CSL convention).
- **`Source: OpenAlex`** — `{given, family, particle?, nickname?, ORCID?, OAID?, affiliation?}`. `affiliation` is a list of `{name, ror?}` objects. No `sequence` field.
- **`Source: OpenLibrary`** — `{given, family, particle?, nickname?, OLID?}`. No `sequence` field.
- **`Source: HathiTrust`** — HathiTrust does not overwrite the author list; the entry retains whatever the prior validator produced.
- **`Source: CV`** — no validator matched; the list is whatever was parsed directly from the CV, typically `{given, family}` only.

The order of the list is the publication's canonical author order in all cases.

### `Type` *(string)*
The publication's type within the CVParsa taxonomy. CVParsa normalizes each validator's native type vocabulary into a single closed set. The taxonomy:

**Primary types (retained in output):**
`journal-article`, `proceedings-article`, `book`, `book-chapter`, `book-section`, `posted-content`, `preprint`, `report`, `thesis`, `patent`, `dataset`, `software`, `editorial`, `legal-case`, `unpublished`.

`Type` gives the CVParsa publication taxonomy category for the validator-specific type returned when CVParsa matches a CV publication record against an external database, or, if unmatched externally, the best matching CVParsa category based on the raw text of the bibliographic record identified in the CV. This is the field used to calculate `pubs_journal`, `pubs_proc`, `pubs_chapter`, and `pubs_book`.

### `Misc` *(string)*
Free-form leftover bibliographic information that did not map cleanly to one of the structured fields. Typical contents: page ranges (e.g., `"44989-45037"`), volume and issue numbers, conference dates, locations, and similar miscellanea. Content is not validated or structured.

### `Source` *(string)*
The provenance of the canonical bibliographic record for this entry. Indicates which external validator (if any) matched and overwrote the fields. Values:

`Crossref` -- Matched and overwritten by Crossref.
`OpenAlex` -- Matched and overwritten by OpenAlex.
`OpenLibrary` -- Matched and overwritten by OpenLibrary (typically books).
`HathiTrust` -- Matched and overwritten by HathiTrust (typically older books/periodicals).
`CV` -- No validator matched; record fields reflect what was extracted directly from the CV.

`Source` is also the key signal for interpreting the `Authors[]` schema (see above).

### `ISBN-13`, `ISBN-10` *(string)*
International Standard Book Numbers for books and book-chapters. Present either when CVParsa identifies an ISBN number in the CV itself, or when a validator (Crossref, OpenAlex, OpenLibrary) returned a valid ISBN.

### `Preprint-Server`, `Preprint-DOI`, `Preprint-ID` *(string)*
Present either when CVParsa identifies preprint information in a particular bibliographic record in the CV or when such information is returned by an external validator. When a publication has both a peer-reviewed version of record and an associated preprint, CVParsa keeps the version of record as the canonical entry (`DOI`, `Venue`, etc.) and stores the preprint information in these tagged fields. They may also appear on standalone preprint entries (`Type: preprint` or `posted-content`).

- `Preprint-Server` — short name of the preprint server (e.g., `arXiv`, `bioRxiv`, `SSRN`, `NBER`, `medRxiv`).
- `Preprint-DOI` — the preprint's DOI (e.g., `10.48550/arXiv.2306.12345` for arXiv, `10.2139/ssrn.XXXX` for SSRN, `10.3386/wXXXX` for NBER).
- `Preprint-ID` — the preprint's native identifier (arXiv ID, bioRxiv DOI, SSRN ID, NBER working-paper number, etc.).

---

## 7. `OpenAlex-metadata`

Validation metadata dict returned by [OpenAlex](https://docs.openalex.org/api-entities/works/work-object) for matched publications, compressed in-place to reduce file size. Each sub-field is described against its OpenAlex source.

### `type` *(string)*
OpenAlex's native publication type (its `type` field on the Work object). Independent of CVParsa's top-level `Type` field (CVParsa taxonomy). Values OpenAlex emits include: `article`, `review`, `book`, `book-chapter`, `reference-entry`, `proceedings-article`, `preprint`, `report`, `dissertation`, `dataset`, `software`, `letter`, `editorial`, `erratum`, `peer-review`, `paratext`, `standard`, `poster`, `presentation`, `map`, `other`. See [OpenAlex Work types](https://api.openalex.org/works?group_by=type) for the live distribution.

### `cited_by_count` *(integer)*
OpenAlex's count of works that cite this publication, summed across all OpenAlex sources at the time of querying. See [OpenAlex `cited_by_count`](https://docs.openalex.org/api-entities/works/work-object#cited_by_count).

### `fwci` *(float or null)*
Field-Weighted Citation Impact — the ratio of this work's citation count to the average citation count of works in the same year and field. A value of 1.0 is the field average; 2.0 means twice the field average. `null` if OpenAlex could not compute it. See [OpenAlex `fwci`](https://docs.openalex.org/api-entities/works/work-object#fwci).

### `primary_topic` *(list or null)*, `topics` *(list of lists)*
OpenAlex assigns each work a `primary_topic` plus a ranked list of related `topics`, all drawn from OpenAlex's hierarchical topic taxonomy (~4,500 topics, ~250 subfields, ~25 fields, 4 domains). CVParsa compresses both:

- `primary_topic` — `[topic_id_slug, display_name, score, [domain_id, field_id, subfield_id]]` (4-element list; `null` if OpenAlex did not assign one).
- `topics` — `[[topic_id_slug, score], ...]` (list of 2-element lists). Entries with `score ≤ 0.05` are dropped.

**Note:** `primary_topic` is **removed** from `topics` after extraction, so the two are disjoint. To reconstruct the full ranked topic list, prepend `primary_topic` to `topics`. See [OpenAlex topics](https://docs.openalex.org/api-entities/topics).

### `keywords` *(list of lists)*
OpenAlex-derived subject keywords for this work (distinct from `Interests.keywords` at the CV level). Compressed as `[[keyword_slug, score], ...]` where `score` is a float. Only keywords with `score > 0.3` are retained. See [OpenAlex keywords](https://docs.openalex.org/api-entities/keywords).

### `oa_id` *(string)*
The OpenAlex Work ID, with the URL prefix stripped (e.g., `W2741809807` rather than `https://openalex.org/W2741809807`). Reconstruct the full URL by prefixing `https://openalex.org/`. See [OpenAlex IDs](https://docs.openalex.org/how-to-use-the-api/get-single-entities#the-openalex-id).

### `oa_status` *(string)*
Open-access status of the work. Values:

`closed` -- Not openly accessible.
`green` -- Author-posted self-archived copy (e.g., institutional repository, preprint server).
`gold` -- Published in a fully open-access journal.
`hybrid` -- OA article in an otherwise subscription journal.
`bronze` -- Freely readable on publisher site without a clear OA license.
`diamond` -- Gold OA without article processing charges.
`unknown` -- OpenAlex could not determine the status.

See [OpenAlex OA status](https://docs.openalex.org/api-entities/works/work-object#oa_status).

### `institutions_ror` *(list of strings)*
A deduplicated flat list of [ROR](https://ror.org/) IDs (with the `https://ror.org/` prefix stripped) for all institutions affiliated with any author on this work, as recorded by OpenAlex. CVParsa flattens the OpenAlex per-author institution lists into a single set of distinct ROR IDs to save space. The per-author affiliation structure is **lost** in this compression; if needed, query OpenAlex directly using `oa_id`.

### `counts_by_year` *(list of lists)*
Yearly citation counts for this work. CVParsa compresses OpenAlex's list of `{year, cited_by_count}` objects into list-of-lists form: `[[year, count], ...]` where both elements are integers. Years with zero citations are preserved when OpenAlex returns them. See [OpenAlex `counts_by_year`](https://docs.openalex.org/api-entities/works/work-object#counts_by_year).

### `mesh_major`, `mesh_minor` *(list of lists)*
MeSH (Medical Subject Headings) terms assigned to this work, split by `is_major_topic` flag from OpenAlex's MeSH records. Both fields are compressed as `[[mesh_ui, mesh_name], ...]` lists of 2-element string lists, deduplicated. When OpenAlex provides a MeSH qualifier (e.g., Descriptor/Qualifier pair), CVParsa concatenates the qualifier onto the descriptor with a slash: `mesh_ui` becomes `"D001/Q002"` and `mesh_name` becomes `"DescriptorName/QualifierName"`. Present primarily on biomedical publications. See [MeSH](https://www.nlm.nih.gov/mesh/meshhome.html).

---

## 8. `Crossref-metadata`

Validation metadata dict returned by [Crossref](https://api.crossref.org) for matched publications. Note that Crossref and OpenAlex are independent sources; their citation counts and subject classifications will not match.

### `is-referenced-by-count` *(integer)*
Crossref's count of other Crossref-indexed works that cite this DOI. This is **not** the same as OpenAlex's `cited_by_count` — Crossref only counts citations from Crossref-deposited references, so it generally undercounts relative to OpenAlex.

### `references-count` *(integer)*
The number of outbound references this work has deposited in Crossref (i.e., works that this paper cites). A value of 0 may indicate either no references or that the publisher did not deposit references.

### `subject` *(list of strings)*
A list of Crossref subject category strings drawn from the [Crossref Scholarly Subject Categories taxonomy](https://api.crossref.org/categories) (e.g., `"Computer Science Applications"`, `"General Materials Science"`). Assigned by Crossref based on the publication venue, not the article content; coverage is uneven.

### `funder` *(list of objects)*
A list of funder objects acknowledged on the work, as deposited by the publisher. CVParsa preserves the Crossref structure: `[{name, DOI, award: [...]}, ...]` where `name` is the funder's display name, `DOI` is the Crossref Funder DOI (links to [Open Funder Registry](https://search.crossref.org/funding)), and `award` is a list of grant/award identifier strings.

### `language` *(string)*
ISO 639-1 two-letter language code for the work's primary language (e.g., `"en"`, `"de"`), as deposited by the publisher.

### `license` *(list of objects)*
A list of license objects associated with the work, each typically containing `URL` (license URL), `start` (effective date), `delay-in-days` (embargo length), and `content-version` (e.g., `vor` for version of record, `am` for accepted manuscript). The CVParsa pipeline preserves the Crossref structure verbatim.

### `container-title`, `short-container-title` *(string)*
The publication venue's full title and abbreviated title, respectively, as recorded in Crossref. For journal articles, these are the journal name and ISO 4 abbreviation; for proceedings articles, the proceedings series name and abbreviation. Generally redundant with the canonical `Venue` field but preserved for downstream tools that key on Crossref's exact strings.

### `alternative-id` *(list of strings)*
A list of alternative identifier strings the publisher deposited alongside the DOI. Contents vary: publisher-internal manuscript IDs, PII codes for Elsevier articles, journal-internal article numbers, etc. No fixed schema.

---

## 9. `OpenLibrary-metadata`

Validation metadata dict returned by [OpenLibrary](https://openlibrary.org/developers/api) for matched books. Present only when OpenLibrary, rather than Crossref or OpenAlex, was the canonical source.

### `key` *(string)*
The OpenLibrary Work key, of the form `/works/OL12345W`. Reconstruct the full URL by prefixing `https://openlibrary.org`.

### `subject` *(list of strings)*
A list of OpenLibrary subject tags. CVParsa truncates this list to the **first 10** items as returned by OpenLibrary (which orders them by an internal relevance metric). Subjects are folksonomic and uneven in quality (mixing topical, geographic, temporal, and form-based tags).

### `ia` *(list of strings)*
A list of [Internet Archive](https://archive.org) item identifiers for digitizations of this work held by IA. CVParsa truncates to the **first 5**. To resolve, prefix `https://archive.org/details/`.

---

## 10. `HathiTrust-metadata`

Validation metadata dict returned by [HathiTrust](https://www.hathitrust.org/bib_api) for matched books. Present only when HathiTrust returned a good match to a given book entry.

### `htid` *(string)*
The HathiTrust volume ID (a.k.a. `htid`) identifying a specific digitized volume (not the bibliographic record itself). Format is `<source>.<barcode>`, e.g., `mdp.39015012345678`. Resolve via `https://catalog.hathitrust.org/Record/<recordURL_id>` for the record or `https://babel.hathitrust.org/cgi/pt?id=<htid>` for the volume.

### `fromRecord` *(string)*
The HathiTrust bibliographic record ID (an integer string) from which this volume's metadata was drawn. A single bibliographic record can be associated with multiple physical/digital volumes (different printings, editions, etc.); `fromRecord` identifies the parent record, while `htid` identifies the specific volume CVParsa matched.

### `enumcron` *(string)*
Volume/issue enumeration and chronology string, when HathiTrust has parsed one out of the holdings record. Examples: `"v.3 1987"`, `"no.42 (Spring 1990)"`. Empty or absent for monographs and for multi-volume sets HathiTrust has not enumerated. See [HathiTrust Bib API](https://www.hathitrust.org/bib_api).

---

## 11. `Grants`

Each entry in `Grants[]` describes one grant, gift, or funded-project arrangement listed on the CV. CVParsa validates each entry against external grant databases (NSF Award Search, NIH RePORTER, USAspending.gov, UKRI Gateway to Research, and the EU CORDIS / EURIO Knowledge Graph) when the funder can be routed to a supported agency. On a successful match, validator-canonical fields overwrite CV-extracted values; on a miss, the CV-extracted values are preserved verbatim. The `Source` field (below) is the key signal for interpreting every other field on the record.

**What appears in `Grants` (inclusion / exclusion).** The `Grants` array is restricted to the CV owner's **own awarded research funding** (broadly construed to include non-STEM external funding such as artistic commissions and funded humanities mechanisms). The following are deliberately excluded:
- honors, prizes, medals, memberships, named-scholar/recognition titles, and best-paper / service / teaching / achievement awards (recognition, not funding);
- pre-career student scholarships (merit, tuition, study-abroad, doctoral scholarships) and program participation lines (summer institutes/seminars, REU as a participant);
- faculty appointments (e.g., named chairs / professorships) and internal-support mechanisms that are not competitive project funding: start-up funds, summer salary, course buyout, lectureship/outreach funds, pedagogy/publication/development funds, and book/publication subventions (subsidies);
- grant-review-panel / advisory-committee service lines; and research costs paid out of the owner's own endowed professorship/chair (self-funded);
- patents (captured by the publications module, not Grants);
- gifts with no stated dollar amount;
- travel grants/awards/funds; and visiting-scholar / visiting-fellow / residency positions that are short-term or carry no funds (a *funded* visiting researcher position or scholarly residency is kept and typed `fellowship`; artistic commissions and arts residencies are kept under `other`);
- awards (most often fellowships) where the CV owner is the mentor/supervisor of the recipient rather than the recipient themselves (e.g., a trainee's fellowship the owner mentored);
- submitted, declined, withdrawn, and unsuccessful proposals (only awarded items appear), and empty parser-artifact records.

These exclusions keep funding analyses focused on the owner's own awarded research support. The honor-vs-grant boundary for Source:CV records is enforced by a post-classification refinement stage (`GRANTS_OTHER_RESCUE_SPEC.md`); some *funded* honors/awards may still pass through pending a future dedicated honors/awards extraction.

### `Source` *(string)*
The provenance of the canonical grant record. Indicates which external validator (if any) matched and overwrote the fields. Values:

`NSF` -- Matched against the [NSF Award Search API](https://www.research.gov/awardapi-service/v1/awards.json).
`NIH` -- Matched against the [NIH RePORTER v2 API](https://api.reporter.nih.gov/).
`USASpending` -- Matched against the [USAspending.gov API](https://api.usaspending.gov/) (federal grants and contracts identified by FAIN / Award ID; covers DoD sub-agencies, NASA, DOE, DARPA, ARPA-E, and other publishing federal funders).
`UKRI` -- Matched against the [UKRI Gateway to Research (GTR-2) API](https://gtr.ukri.org/resources/api.html) (UK Research and Innovation councils: EPSRC, BBSRC, MRC, ESRC, AHRC, NERC, STFC, Innovate UK).
`CORDIS` -- Matched against the EU [CORDIS / EURIO Knowledge Graph](https://cordis.europa.eu/datalab/sparql) (SPARQL endpoint; European Commission research funding: ERC, Horizon Europe, H2020, and Marie Skłodowska-Curie Actions). Matching is **organisation-anchored** (CORDIS/EURIO exposes only organisation nodes, no individual investigators) — the same class as USASpending — so the CV owner's identity is corroborated by their institution's participation rather than by name, a weaker signal than the NSF/NIH/UKRI person-level matches (see `CV Owner.source` and the cross-cutting note).
`CV` -- No external validator matched (or no validator was applicable); the record reflects what was extracted directly from the CV. (Exception: a few `CV` records carry validator-resolved `Funder Details`/`Grant Details` from an institution-level NSF award — see the "Institution-level awards" cross-cutting note below.)

`Source` is also the key signal for interpreting `Funder`, `Funder Details`, and `Grant Details` (see below) — each agency populates these fields with its own canonical attribute set.

### `Funder` *(string)*
The funder's canonical short code (or display name when no short code applies). The value's shape depends on `Source`:

- **`Source: NSF`** — `"NSF"`.
- **`Source: NIH`** — the awarding Institute/Center code (e.g., `"NIGMS"`, `"NHLBI"`, `"NCI"`, `"NIAID"`); see the [NIH ICs list](https://www.nih.gov/institutes-nih/list-nih-institutes-centers-offices) for the canonical name mapping.
- **`Source: USASpending`** — the awarding top-level agency abbreviation (e.g., `"DOD"`, `"NASA"`, `"DOE"`); for sub-agency context (e.g., AFOSR, ARO, ONR, DARPA, ARPA-E), see `Funder Details.awarding_sub_agency_*`.
- **`Source: UKRI`** — the awarding council short code (`"EPSRC"`, `"BBSRC"`, `"MRC"`, `"ESRC"`, `"AHRC"`, `"NERC"`, `"STFC"`), or `"Innovate UK"` for innovation-channel funding, or `"UKRI"` for cross-council awards.
- **`Source: CORDIS`** — always `"CORDIS"` (the canonical short code for the EU framework-programme funder). The specific programme/agency (ERC, MSCA, etc.) is not separately encoded here; the project acronym appears in `Funder Details.acronym`.
- **`Source: CV`** — the funder name extracted from the CV, preserved verbatim. May be a full agency name (`"National Science Foundation"`), an acronym (`"NSF"`), a private foundation (`"Howard Hughes Medical Institute"`), an industry sponsor, an internal institutional source (`"Mathematical Institute, University of Oxford"`), or any other free-form string. Not standardized.

### `Validator` *(string or null)*
The external validation database this grant was **routed to** for verification, regardless of whether a match was ultimately found. One of `NSF`, `NIH`, `USASpending`, `UKRI`, `CORDIS`, or `null` (the grant could not be routed to any supported database — e.g., private foundations, university/internal awards, industry, or unsupported foreign funders).

This is the companion to `Source`: `Validator` records *which database the grant's funder maps to*, while `Source` records *whether a match was found there*. The combinations:

- `Source == Validator` — the database was queried and matched.
- `Source == "CV"`, non-null `Validator`, **no** `Validation Note` — the database was queried but found no confident match.
- `Source == "CV"`, non-null `Validator`, **with** a `Validation Note` — the database was *not* queried, because the grant's type (fellowship/travel/gift) is not indexed there (see `Validation Note` below).
- `Source == "CV"`, `Validator == null` — the grant was never routable to any supported database.

To compute a per-database validation **success** rate, use `Validator == X` **and no `Validation Note`** as the denominator (the grants actually tested against X) and `Source == X` as the numerator; counting `Validation Note` records in the denominator would understate the rate by including grants that were never queried.

Routing is **validator-level, not agency-level**: every federal agency without its own API — DOE, DOD, NASA, USDA, EPA, etc. — routes to `USASpending`, so they all read `Validator == "USASpending"`; the specific awarding agency (when known) is in `Funder` / `Funder Details`. EU funders (ERC, MSCA, Horizon) read `CORDIS`.

(Replaces the former `Funder Hint` field — the raw CV-extracted agency token — which is now internal-only.)

### `Validation Note` *(string; present only when applicable)*
Present **only** on records whose funder routes to a validator (`Validator` is non-null) but whose grant *type* means the record was never queried against that validator — agency/funder databases index awarded research grants, not these instrument types. Absent on all other records. The value is one of a strict, closed vocabulary, so the field can be parsed programmatically:

`Not validated: fellowships are not indexed in the validator's database`
`Not validated: travel awards are not indexed in the validator's database`
`Not validated: gifts are not indexed in the validator's database`

The note names the *type* exclusion; the database itself is in `Validator`. It disambiguates the two reasons a `Source: CV` record can carry a non-null `Validator`: a record **with** a `Validation Note` was never queried (the validator structurally cannot hold this grant type), whereas one **without** a note was queried and simply not matched. Most type-excluded records (declined/submitted proposals, gifts, non-PI fellowships and travel awards) are dropped from the user-facing output entirely; the records that retain a `Validation Note` are predominantly own-fellowships, where the CV owner is the credited fellow/PI.

### `Funder Sector` *(string)*
A derived, closed-taxonomy classification of the funder's sector, for downstream analysis. One of:

`government` -- Any governmental funder: US federal research agencies (NSF/NIH/DOD/NASA/DOE/HHS/…), US state/local government, and foreign or supranational government bodies (UKRI, ERC/EU, DFG, …).
`foundation` -- Private philanthropy and nonprofits: foundations, charitable trusts, endowments, and professional societies/associations — including *corporate* foundations (e.g., the Shell Oil Company Foundation).
`industry` -- For-profit corporations, identified by corporate-form suffixes (`Inc`, `Corp`, `LLC`, `Pharmaceuticals`, …) or a curated company-name gazetteer (Google, Pfizer, IBM, …).
`academic` -- Universities, colleges, and internal institutional funds.
`unknown` -- No resolvable funder signal.

Derived from the authoritative funder token plus `Funder`.

### `Grant Number` *(string)*
The canonical award identifier. The format depends on `Source`:

- **`Source: NSF`** — 7-digit NSF Award ID (e.g., `"2420950"`).
- **`Source: NIH`** — canonical core project number (e.g., `"R01CA123456"`, `"U24GM132013"`); CVParsa strips the support-year prefix (`5`, `1`, `2`, `3`, `4`) and amendment suffix (`-03A1`, `-01S2`) from CV-extracted forms to produce the canonical 8–11-character identifier.
- **`Source: USASpending`** — the FAIN (for assistance awards) or Award ID (for contracts) as recorded in USAspending. Examples: `"W911NF2420199"` (ARO assistance), `"N000142212482"` (ONR), `"FA95501610516"` (AFOSR Minerva), `"DESC0016140"` (DOE-SC).
- **`Source: UKRI`** — the RCUK Project Reference. Modern forms: `"EP/V046713/1"` (EPSRC), `"BB/T012345/1"` (BBSRC), `"MR/V001234/1"` (MRC). Legacy forms also supported: `"MC_UU_12025/2"` (legacy MRC), `"BBS/E/W/10963A02"` (legacy BBSRC), `"RES-000-22-1234"` (legacy ESRC), `"G0900700"` (legacy MRC G-number), `"PP/E001025/1"` (legacy PPARC/STFC), `"UKRI12345678"` (modern UKRI unified).
- **`Source: CORDIS`** — the EU grant-agreement number (EURIO `identifier`): a 6–9-digit integer with no prefix. H2020 awards use 6 digits (e.g., `"683289"`); Horizon Europe uses 9 digits (e.g., `"101012345"`).
- **`Source: CV`** — the grant number as listed in the CV, preserved verbatim. May contain typos, partial numbers, or non-standard formats. May be the empty string when the CV does not state a grant number.

### `Title` *(string)*
The grant's title. On a successful external match (NSF/NIH/USASpending/UKRI/CORDIS), CVParsa overwrites with the canonical title from the validator (NSF `title`, NIH `project_title`, USAspending `Award Description`, UKRI `project.title`, CORDIS EURIO project `title`). On a `Source: CV` record, the CV-stated title is preserved verbatim.

**Exception:** when a match is anchored purely by grant-number corroboration (low title similarity, but the canonical grant number matches), CVParsa **preserves the CV-stated title** rather than overwriting with the validator's title. This honors the CV author's framing of sub-project facets within large prime awards — common for NIH supplements (type-3) and NSF sub-projects, where the parent award's title may not describe the CV author's specific contribution. The `Grant Number` is still canonicalized and the rest of the record is validator-sourced.

### `Type` *(string)*
The grant's funding-mechanism category within the CVParsa grant taxonomy. CVParsa normalizes each validator's native mechanism vocabulary into a single closed set. On a successful match the category is taken from the validator's own classification; if unmatched, CVParsa assigns the best category inferred from the CV record's text. The taxonomy:

`research-grant` -- A competitive project grant (the most common category; e.g., NSF standard / continuing grants, NIH R-series, USAspending project grants, UKRI research grants).
`cooperative-agreement` -- An award where the funder takes a substantial programmatic role (e.g., NSF cooperative agreements, NIH U-series).
`contract` -- A procurement / deliverable contract (e.g., USAspending definitive contracts and orders, NIH N-series, industry research contracts).
`fellowship` -- An individual fellowship or career-development award held by the CV owner (e.g., NIH F- and K-series, NSF GRFP, UKRI Fellowship, Sloan, dissertation and postdoctoral fellowships).
`training-grant` -- An institutional training grant awarded to an organization to train people (e.g., NIH T-series, UKRI Training Grant / Studentship).
`center-program` -- A center, program-project, or programme grant (e.g., NIH P-series, UKRI Programme Grant, NSF centers, COBRE cores).
`gift` -- A philanthropic gift, not in any agency grants database; retained only when it states a dollar amount. Always `Source: CV`.
`other` -- A real funded arrangement that is none of the above (e.g., internal seed awards, equipment funds, publication subventions).
`unknown` -- No usable signal (rare).

### `Subtype` *(string)*
A CVParsa-derived refinement of `Type` for subcategories that benefit from distinct treatment. Present only when CVParsa detects a recognizable subtype. Closed set:

`grfp` -- NSF Graduate Research Fellowship Program award; validated against NSF Award Search by direct award-number lookup only.
`sbir` -- Small Business Innovation Research award.
`sttr` -- Small Business Technology Transfer award.
`fellowship` -- Non-GRFP fellowships and career awards (e.g., university Hooke Research Fellowship, Sloan Fellowship). Routed as unroutable when no recognizable agency.
`travel` -- Travel grants, conference attendance funding, visiting-scholar stipends. Not typically in agency databases.

When `Subtype` is absent, the record's `Type` value is sufficient categorization.

### `Funded Amount` *(integer)*
The amount funded, in `Currency` units. Always a whole number (dollars, pounds, or euros, never cents/pence). On successful external match, derived from the canonical validator field (NSF `estimatedTotalAmt`; NIH summed `award_amount` across all fiscal-year records of a multi-FY award; USAspending `Award Amount`; UKRI sum of `fund.valuePounds.amount` across all linked funds; CORDIS the EURIO project total contribution). On `Source: CV`, the amount is parsed from the CV-stated value to an integer; `null` when the CV does not state an amount. A stated `0` is likewise normalized to `null`, since a zero amount is treated as no funding.

### `Currency` *(string)*
ISO 4217 three-letter code for the `Funded Amount`. Validator-canonical on match (`"USD"` for NSF/NIH/USASpending; `"GBP"` for UKRI; `"EUR"` for CORDIS); CV-stated otherwise (typical values: `"USD"`, `"GBP"`, `"EUR"`). `null` when the CV does not state a currency and no validator matched.

### `Year Start`, `Year End` *(integer)*
The integer years bounding the funding period. Validator-canonical on match:

- **NSF** — extracted from `startDate` / `expDate` (MM/DD/YYYY).
- **NIH** — extracted from `project_start_date` / `project_end_date` (ISO format); for multi-FY awards, the full span across all FYs.
- **USASpending** — extracted from `period_of_performance_start_date` / `period_of_performance_current_end_date`.
- **UKRI** — preferentially from `project.start` / `project.end` (epoch milliseconds), falling back to the earliest `fund.start` and latest `fund.end` across linked funds when the project record has null inline dates (common for Fellowships, Studentships, and some Research Grants).
- **CORDIS** — the four-digit year parsed from the EURIO project `startDate` / `endDate`.
- **`Source: CV`** — extracted from the CV. May be `null` if the CV does not state the relevant year.

### `Funder Details` *(object)*
A dict of canonical funder-level attributes (about the funder itself; not specific to the award). Shape depends on `Source`:

- **`Source: NSF`** — `{directorate, division, directorate_name, division_name, program}`. The administrative organizational unit within NSF (e.g., `directorate: "MPS"`, `division: "DMS"`, `program: "Algebra and Number Theory"`).
- **`Source: NIH`** — institute/IC and funding-mechanism context, including `institute`, `ic_code`, `ic_long_name`, `activity_code`, `study_section_name`, `mechanism`, and fiscal-year flags. The `activity_code` (e.g., `"R01"`, `"K99"`, `"U24"`) identifies the funding mechanism within the NIH portfolio.
- **`Source: USASpending`** — agency tree + funding flow, including `awarding_agency_name`, `awarding_sub_agency_name`, `awarding_sub_agency_abbr`, `funding_agency_name`, `funding_sub_agency_name`. USAspending distinguishes the *awarding* agency (who issued the award) from the *funding* agency (whose appropriations paid for it); these are usually the same but can differ for inter-agency transfers.
- **`Source: UKRI`** — `{lead_council}` — UKRI council short code. Cross-council co-funded projects are denoted by the lead council; co-funder details are not currently populated.
- **`Source: CORDIS`** — `{project_uri, acronym}` — the EURIO project URI (a stable CORDIS identifier resolving to the project's knowledge-graph node) and the project's short acronym (e.g., `"RustBelt"`).
- **`Source: CV`** — normally absent; **exception:** institution-level NSF awards (GRFP / EPSCoR) populate this even under `Source: CV` — see the "Institution-level awards" cross-cutting note.

### `Grant Details` *(object)*
A dict of canonical award-level attributes (specific to this grant). Shape depends on `Source`:

- **`Source: NSF`** — `{start_date, end_date, activeAwd, transType, cfdaNumber, awardeeName}`. `activeAwd` is `"true"` or `"false"`; `transType` is the NSF mechanism class (e.g., `"Standard Grant"`, `"Continuing Grant"`, `"Cooperative Agreement"`); `cfdaNumber` is the federal CFDA assistance listing number; `awardeeName` is the host institution as recorded by NSF.
- **`Source: NIH`** — `{core_project_num, full_project_num, project_url, project_start_date, project_end_date, awardee_org, sub_project_id, is_subaward}`. Includes the canonical NIH identifiers, project period, recipient organization, and a `is_subaward` flag indicating whether this is a type-3 supplement to a parent grant.
- **`Source: USASpending`** — `{award_type, recipient_name, recipient_uei, generated_internal_id, base_obligation_date, period_of_performance_start, period_of_performance_current_end, description, place_of_performance_*}`. `award_type` is the USAspending category (`"PROJECT GRANT (B)"`, `"COOPERATIVE AGREEMENT (C)"`, `"DEFINITIVE CONTRACT (D)"`, etc.); `recipient_uei` is the Unique Entity ID at SAM.gov.
- **`Source: UKRI`** — `{project_uuid, project_url, grant_category, status, lead_organisation_dept}`. `project_uuid` is the UKRI Gateway-to-Research project identifier; `project_url` is a deep link to the public-facing project page (e.g., `https://gtr.ukri.org/projects?ref=EP/V046713/1`); `grant_category` is one of `"Research Grant"`, `"Fellowship"`, `"Studentship"`, `"Training Grant"`, `"Programme Grant"`, or similar UKRI taxonomy values; `status` is `"Active"` or `"Closed"`; `lead_organisation_dept` is the lead institution's department/school name.
- **`Source: CORDIS`** — `{start_date, end_date, project_uri}`. `start_date` / `end_date` are the full EURIO project dates (the basis for `Year Start` / `Year End`); `project_uri` is the EURIO project node identifier (also echoed in `Funder Details`).
- **`Source: CV`** — normally absent; same institution-level GRFP/EPSCoR exception as `Funder Details` (with award dates cleared).

### `CV Owner` *(object)*
The CV owner's role and identity on this grant, structured as `{full_name, grant_role, affiliation, email, source}`:

- `full_name` — the CV owner's name (matches `Person.full_name`).
- `grant_role` — the CV owner's role on this grant, **standardized to a closed 7-token set**: `"PI"` (Principal Investigator), `"co-PI"` (Co-Principal Investigator), `"MPI"` (Multiple / Multi-PI — co-equal lead PIs), `"co-I"` (Co-Investigator, non-PI; also a bare "Investigator"), `"Site/Sub PI"` (PI of a site, subaward, or subcontract), `"Senior Personnel"` (NSF-style senior / key personnel), and `"Other"` (any other, unstated, or missing role). The many free-text variants seen in CVs and validator records — casing, spelling, `"Principal Investigator"` ↔ `"PI"`, `"Co-Investigator"`, `"Subcontract PI"`, etc. — are mapped to these tokens; combined values resolve to the highest leadership tier present (e.g. `"PI/co-PI"` → `PI`, `"Co-PI/MPI/Co-Is"` → `MPI`). When the validator's role assignment differs from the CV-stated role, the CV-stated role wins (and is then normalized).
- `affiliation` — the CV owner's institutional affiliation at the time of the award (typically derived from `Person.institution` or the contemporaneous `Employment[]` entry).
- `email` — the CV owner's email at the time of the award, if available from the validator. Currently populated only for NSF matches (where it appears alongside the PI list); empty string otherwise.
- `source` — provenance of this dict's authority. `"NSF"` / `"NIH"` / `"UKRI"` means the validator confirmed the CV owner is a named *person* on the award (these are the person-level validators, which expose individual-investigator records). `"CV"` means the role is from the CV alone, with no external person-level confirmation. This `"CV"` case covers: `Source: CV` records; grants matched only by their award number, where the validator did not list the owner among the named investigators; and **all `Source: USASpending` and `Source: CORDIS` matches** — both are *organisation-anchored* validators (USAspending indexes only the prime recipient organisation; CORDIS/EURIO exposes only organisation nodes), so they can confirm the owner's *institution* participated but never that the owner personally was a named investigator. See the cross-cutting note below.

### `Collaborators` *(list of objects)*
A list of named collaborators on the grant, each represented as `{full_name, grant_role, affiliation, email, source}`. The CV owner is **never** included in this list (the CV owner appears separately as `CV Owner`). For the person-level validators (NSF / NIH / UKRI), a successful match makes this list the **union** of (a) canonical investigators from the validator and (b) any CV-only co-investigators / senior personnel the CV listed but the validator did not. The organisation-anchored validators (USASpending, CORDIS) contribute **no** validator collaborators — they expose no investigator records — so on those matches the list is exactly the CV-listed collaborators. Per-entry fields:

- `full_name` — collaborator's full name. Validator-canonical when present.
- `grant_role` — same standardized 7-token closed set as `CV Owner.grant_role` (above), normalized the same way.
- `affiliation` — collaborator's home institution; not standardized.
- `email` — collaborator's email if available from the validator. **Omitted entirely** (the key is dropped from the object) when null or empty, rather than carried as an empty string.
- `source` — `"NSF"` / `"NIH"` / `"UKRI"` when the collaborator was confirmed by that (person-level) validator; `"CV"` for CV-only entries. The organisation-anchored validators contribute no validator collaborators, so on `Source: USASpending` and `Source: CORDIS` matches every collaborator is a CV-named person with `source: "CV"`.

On `Source: CV` records, all collaborators have `source: "CV"`.

### `Grant Publications` — *not present in output*
Reserved for possible future use. No validator currently provides grant-publication links, and **this field does not appear in the consolidated `cvp.json` output**. It is noted here only to record its reserved status; downstream consumers should not expect it.

### `Misc` *(string)*
Free-form leftover bibliographic / contextual information that did not map cleanly into one of the structured fields. Typical contents: award notes ("New Horizons grant"), grant_role qualifiers ("Subaward Lead"), the verbatim CV award title when overwritten by a more canonical validator title, or other ancillary text. Content is not validated or structured.

### Cross-cutting notes for the `Grants` section

**Trust-the-CV philosophy.** CVParsa's grant validators preserve the CV author's framing where it does not conflict with verifiable facts. The CV-stated `grant_role` always wins over a validator-derived role. When a grant is matched by its award number alone (its title did not closely match the validator's record), the CV-stated title is kept rather than overwritten, so the sub-project facets of large prime awards remain legible. On a successful match, `Type` is set from the validator's funding-mechanism classification, since the validator is authoritative about mechanism; when no validator matched, `Type` is inferred from the CV text. `Subtype` remains CV-derived and is preserved unchanged.

**One record per award (consolidation).** Each distinct award appears at most once per CV. When a CV lists the same grant more than once — a repeated entry, a base award together with a supplement, or the same award described two slightly different ways — those records are consolidated into a single entry. In that case `Funded Amount` reflects the funder-reported total for the award (which already incorporates any supplemental funding), **not** the sum of the duplicate listings, so award dollars are not double-counted. Genuinely distinct awards are kept separate even when their titles are similar — including sequentially numbered or phased awards (e.g., Phase I vs. Phase II of an SBIR/STTR award, or successive annual cohorts of a program) and the several awards that can share one solicitation or program number. Consolidation operates within a single CV only: an award listed on two different people's CVs is retained on each.

**Multi-agency CVs.** A single CV may have grants from multiple supported agencies (e.g., a UK PI with EPSRC + NSF + NIH awards, or an EU PI with ERC + Horizon awards). Each grant is validated independently against its routed agency; cross-agency interaction is limited to ensuring the per-CV cv_owner record reflects the strongest available validator source.

**Person-level vs organisation-anchored validators.** NSF, NIH, and UKRI expose individual-investigator records, so a confident match can corroborate the CV owner and co-investigators by name — `CV Owner.source` and `Collaborators[].source` then carry the validator's name. USAspending and CORDIS are *organisation-anchored*: they index only the recipient / participant organisations, with no individual-person records. On those matches CVParsa still canonicalizes the grant (title, number, amount, dates), but it cannot confirm individual people, so `CV Owner.source` stays `"CV"` and no validator collaborators are added.

**Institution-level awards: enriched but CV-sourced.** A small number of records carry `Source: "CV"` yet still have populated `Funder Details` / `Grant Details`. This occurs when a CV grant number resolves (via NSF `id_lookup`) to an **institution-level** NSF award — e.g. the Graduate Research Fellowship Program (GRFP) or an EPSCoR Research Infrastructure award — where one federal award covers many people at an institution and the named PI is the program's institutional director, not the CV owner. CVParsa attaches the resolved award's `Funder Details` / `Grant Details` for reference but **deliberately keeps `Source: "CV"`**: the CV-stated scalar fields (`Funder`, `Grant Number`, `Funded Amount`, `Year Start/End`, `Type`) are preserved rather than overwritten, and the institution-level dates are cleared from `Grant Details`. Interpretation: the award is real and externally resolvable, but its attribution to the CV owner is CV-asserted (e.g. administering a sub-portion), not validator-confirmed — so it is correctly counted as `CV`, not `NSF`. This is the one case where populated `Funder Details`/`Grant Details` under `Source: "CV"` is expected, not a mismatch.

**Known recall limits.** Some legitimate awards are not findable in any database — most commonly: sub-PI roles at non-prime institutions (the validator only indexes the prime recipient), classified-budget IC awards (NSA Mathematics Sciences Program, DIA / CIA / NRO / NGA academic engagement), institutional pots not indexed at individual-PI level (UKRI Impact Acceleration Accounts), and sparse CV records (blank title + null year + typo'd grant number). All such cases fall through cleanly as `Source: "CV"` with all CV-stated metadata preserved.

**Zero false positives is the precision target.** All five validators (NSF / NIH / USASpending / UKRI / CORDIS) are designed and tuned for zero false positives in production. The cost is that recall is below 100% — missing real matches is preferred to confidently asserting an incorrect match. Records that the validators cannot match with high confidence fall back to `Source: "CV"` rather than being assigned a guess.

---

## 12. Cross-cutting fields

### `institution`, `university` *(string)*
Standardized institution name. This field is present on `Person`, `Education[]`, `Employment[]`, `Advising.advisors[]`, and `Advising.advisees[]`. Standardization handles common abbreviations, aliases, historical names, or local-language forms, and maps strings to a canonical English-language display name — e.g., `"CU Boulder"` → `"University of Colorado, Boulder"`. These are **human-readable canonical names**, not Wikidata QIDs or ROR IDs, and are most accurate for common institutions. If no standardization is known, the original CV-derived string is given here.
