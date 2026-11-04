# Rabbit-Hole Method Reference

Load this when selecting keywords, screening a field, or validating a candidate.

## Keyword shapes

### Prefer
- Complaint spoken aloud: symptom, embarrassment, inconvenience, failed routine.
- Seller-created category coinage: the phrase used to distinguish the new product from the old shelf.
- Mechanism phrase: what physically changes or how the product works.
- Avatar phrase: a specific user identity or situation.
- Feature/benefit phrase that appears verbatim in current ad copy.
- Enemy brand or prescribed drug name when it is specific and emotionally salient.
- Secondary product or mechanism word from a validated operator.

### Avoid
- Invented phrases unsupported by observed copy.
- Diagnoses primarily owned by pharma, clinics, or lead generation.
- Generic retail categories and enemy generic nouns.
- Common verbs/adjectives, gerunds, homographs, and one-edit collisions.
- Product nouns inside an aisle already measured dead under neighboring terms.
- Single-advertiser slogans: they do not prove a field.

Broad promotional terms such as “free shipping,” “shop now,” or discount percentages are doctrine examples, not scheduled starter roots. Begin with specific, verbatim product, problem, mechanism, avatar, or benefit phrases supported by real ad evidence.

## Cheap-screen decision table

| Screen | Reject or defer when… | Why |
|---|---|---|
| History exclusions | measured register/strike covers the token or its aisle | prevents re-spending known-dead surfaces |
| Carry-line check | grep hits are the prior dig and its repeated summaries | low count can mean dead, not virgin |
| Dealer/local producer | the practitioner's noun maps to dealers, farms, workshops, or installers | no launch-operator layer |
| Secondhand | expensive gear is mostly private resale | young cards are listings, not brands |
| Token shape | verbs/adjectives/gerunds/broad nouns dominate | exact-phrase search still fuzzes |
| Edit distance | one spelling edit reaches a common word | fuzzy matching floods the field |
| Service layer | clinic, contractor, gym, or technician earns the purchase | demand exists without a shipped SKU |
| Retail-held/price floor | ads land on Amazon/Walmart or product is near sub-$10 | retailer/commodity economics, not a cloneable operator |
| Catalogue/path | unrelated SKUs or generic catalogue titles dominate | fresh ads can hide a general store |
| Volume | counter is extremely broad or sub-floor | broad reads show canopy; thin reads lack operators |
| Persona | distinctive titled identity repeats across hosts | re-skins pass date gates by construction |
| Host count | high young ratio comes from one or two hosts | incumbent activity masquerades as entrant growth |
| B2B/OEM | manufacturer advertises wholesale/private-label supply | not a DTC operator |

## Five-gate decision table

| Gate | Pass | Kill / downgrade | Critical caveat |
|---|---|---|---|
| Recency | oldest same-product ad ≤28 days | any older same-product ad | derive from host-pure page/domain history, not field view |
| Live volume | ≥5 live own-host ads | fewer than 5 | filter token fuzz and unrelated cards |
| Cadence | new ads every 1–3 days | >~10-day gap | capped reads can hide ads: cadence pass is stronger than kill |
| Delivery | low-impression share roughly 2–43% on cohorts ≥5 days | roughly 65–81% | capped reads bias low-impression upward: fail is stronger than pass |
| Store/SKU age | store-to-first-ad gap <~60 days | ≥180 days; 60–180 borderline | many same-day SKUs suggest rebuild/import; non-Shopify is unknown |

## Evidence discipline

- Ads Library counters are query evidence, not field truth.
- Deduplicate cards by Library ID.
- Preserve complete outbound paths; hostname-only analysis loses product identity.
- An oldest visible ad is a lower bound on age because Meta's record can forget.
- A partition result is a floor until attributed to the target host.
- Re-fetch product catalogues before using old swipe stock; products and stores decay or pivot.
- A failed established operator can confirm demand but is not an early product entry.
- A product validated in one geography cannot inherit another geography's spend thresholds.
