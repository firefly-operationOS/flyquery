# Semantic Types

Every column ingested by flyquery is classified with a **semantic
type** in addition to its storage **data type**. The storage type
(`VARCHAR`, `DOUBLE`, `TIMESTAMP`, …) tells you how Postgres stores
the value; the semantic type tells you what the value **means**.

Two `DOUBLE` columns can be `amount` versus `percentage` versus
`rate` -- the SDK, the explainer, and the chart-hint heuristic
format them very differently.

## Where the type comes from

The `DescribeAgent` (Stage 7 of the ingestion pipeline) inspects
each column's sample values and table context and assigns one of
the labels below. The agent prompt lives in
[`src/flyquery/resources/prompts/describe.yaml`](../src/flyquery/resources/prompts/describe.yaml)
-- tune it without redeploying.

Persistence: `flyquery_schema_objects.governance_json.semantic_type`
(JSONB). The schema-objects controller exposes it via
`GET /api/v1/tables/{table_id}/objects`.

## The taxonomy

| Group         | Label              | When to use                                    |
|---------------|--------------------|------------------------------------------------|
| Text          | `text`             | short labels / captions                        |
|               | `name`             | person or organization name                    |
|               | `description`     | long narrative, multi-sentence                  |
|               | `tag`              | open categorical                                |
|               | `enum`             | closed-set categorical                          |
|               | `language_code`    | ISO 639 (`en`, `es`)                           |
| Identifiers   | `identifier`       | UUID / surrogate / generic ID                  |
|               | `code`             | business codes (SKU, ISIN, GICS)               |
|               | `tax_id`           | national tax / VAT / company-reg IDs           |
|               | `iban`             | bank-account IBANs                              |
|               | `version`          | SemVer / CalVer / build numbers                |
| Quantities    | `integer`          | arbitrary integers                              |
|               | `count`            | counts of discrete things                       |
|               | `decimal`          | arbitrary decimals                              |
|               | `score`            | composite KPI / risk / sentiment                |
|               | `ratio`            | 0-1 unitless fractions                          |
|               | `percentage`       | 0-100 values labelled %                         |
|               | `rate`             | interest / FX / discount rates                  |
| Money         | `amount`           | monetary WITHOUT currency column                |
|               | `currency`         | monetary WITH currency column                   |
|               | `currency_code`    | ISO 4217                                        |
| Time          | `date`             | calendar date                                   |
|               | `datetime`         | timestamp with time                             |
|               | `time`             | clock time without date                         |
|               | `year`             | year only                                       |
|               | `quarter`          | `Q1 2024` / `2024-Q1`                          |
|               | `month`            | month bucket                                    |
|               | `week`             | ISO week                                        |
|               | `duration`         | minutes / days / months span                    |
|               | `timezone`         | IANA timezone string                            |
| Boolean       | `boolean`          | true / false                                    |
|               | `flag`             | active / inactive, on / off                     |
| Contact       | `email`            | email address                                   |
|               | `phone`            | phone number                                    |
|               | `url`              | web URL                                         |
|               | `image_url`        | image URL                                       |
|               | `file_path`        | FS / object-store path                          |
| Geo           | `address`          | multi-field street address                      |
|               | `city`             | city name                                       |
|               | `state`            | state / province                                |
|               | `postal_code`      | ZIP / postcode                                  |
|               | `country`          | country name                                    |
|               | `country_code`     | ISO 3166                                        |
|               | `region`           | multi-country (EMEA, APAC)                      |
|               | `industry_sector`  | NACE / NAICS / GICS                             |
|               | `geo_coordinate`   | lat / lon                                       |
| Tech          | `ip_address`       | IPv4 / IPv6                                     |
|               | `json`             | structured JSON blob                            |
| Default       | `unknown`          | truly uncertain                                 |

## Adding a new type

1. Add the label to `SemanticType` Literal in
   [`describe_agent.py`](../src/flyquery/core/agents/describe_agent.py).
2. Add a row to the rules table in `describe.yaml`.
3. Bump the `version` field in `describe.yaml`.
4. The grounding agent + explainer pick it up automatically -- no
   migration needed (lives in `governance_json` JSONB).
