"""Everything you'd want to tune lives here: searches, scoring weights, filters."""

# How far back to look (days). Overridable with --days.
DEFAULT_DAYS = 30

# Jobs scoring below this are dropped. Overridable with --min-score.
DEFAULT_MIN_SCORE = 20

# Score tiers shown in the report.
TIERS = [
    (70, "Superpower match"),
    (50, "Strong fit"),
    (30, "Worth a look"),
    (20, "Stretch"),
]

# ---------------------------------------------------------------------------
# Searches run against Indeed (via JobSpy) and the search-capable remote boards.
# The first block is the "bread and butter" profile; the rest are secondary.
# ---------------------------------------------------------------------------
PRIMARY_SEARCHES = [
    "direct response copywriter",
    "conversion copywriter",
    "dtc copywriter",
    "health copywriter",
    "wellness copywriter",
    "copywriter",
    "senior copywriter",
]
SECONDARY_SEARCHES = [
    "short form video copywriter",
    "creative strategist",
    "growth marketing",
    "ecommerce manager",
    "content creator copywriter",
    "email copywriter",
    "ad copywriter",
    "marketing copywriter",
    "content writer",
    "content strategist",
    "content marketing manager",
    "email marketing manager",
    "retention marketing",
    "lifecycle marketing",
    "social media manager",
    "paid social",
    "ugc creator",
    "brand writer",
    "scriptwriter",
]

# ---------------------------------------------------------------------------
# Scoring. Title matches count more than description matches. Each keyword
# counts once. Final score is clamped to 0-100.
# ---------------------------------------------------------------------------
TITLE_WEIGHTS = {
    # core: Superpower-style copy roles
    "copywriter": 45,
    "copy writer": 45,
    "copy lead": 40,
    "head of copy": 40,
    "copy chief": 40,
    "direct response": 20,
    "conversion": 10,
    "response copy": 10,
    "scriptwriter": 25,
    "script writer": 25,
    "vsl": 20,
    # secondary roles from the shortlist
    "creative strategist": 35,
    "growth marketing": 25,
    "growth marketer": 25,
    "ecommerce manager": 20,
    "e-commerce manager": 20,
    "content creator": 20,
    "content writer": 15,
    "brand writer": 25,
    "email marketing": 15,
    "lifecycle": 10,
    "performance creative": 20,
    # adjacent roles: same skill set, slightly different title
    "writer": 20,
    "content strategist": 20,
    "content marketing": 20,
    "content": 8,
    "storyteller": 15,
    "retention": 15,
    "crm": 8,
    "paid social": 15,
    "social media": 12,
    "ugc": 15,
    "creative": 10,
    "cro": 12,
    "marketing manager": 10,
    "marketing": 5,
    "brand": 5,
}

DESC_WEIGHTS = {
    # the Superpower profile: persuasion copy for health / DTC
    "direct response": 12,
    "direct-response": 12,
    "sales page": 8,
    "landing page": 5,
    "vsl": 8,
    "video sales letter": 8,
    "advertorial": 8,
    "conversion": 4,
    "dtc": 8,
    "d2c": 8,
    "direct-to-consumer": 8,
    "direct to consumer": 8,
    "ecommerce": 4,
    "e-commerce": 4,
    "shopify": 4,
    "health": 6,
    "wellness": 8,
    "supplement": 8,
    "longevity": 8,
    "telehealth": 6,
    "nutrition": 4,
    "founder": 3,
    "hooks": 5,
    "ugc": 5,
    "meta ads": 5,
    "facebook ads": 5,
    "tiktok": 4,
    "short-form": 4,
    "short form": 4,
    "email": 2,
    "portfolio": 2,
}

# Penalties: roles that look like "writer" but aren't the persuasion-copy kind,
# or that you've already ruled out (SEO-heavy, AI training gigs, etc.).
TITLE_PENALTIES = {
    "technical writer": -60,
    "technical author": -60,
    "grant writer": -60,
    "proposal writer": -50,
    "rfp": -50,
    "medical writer": -40,
    "regulatory": -40,
    "legal": -30,
    "seo": -20,
    "intern": -30,
    "internship": -30,
    "ai trainer": -80,
    "annotation": -80,
    "annotator": -80,
    "data entry": -80,
    "transcription": -80,
    "rater": -60,
    "evaluator": -60,
    "engineer": -40,
    "developer": -40,
    "nurse": -60,
    "physician": -60,
}

# ---------------------------------------------------------------------------
# BS / scam filter. Any match in title, company or description drops the job.
# ---------------------------------------------------------------------------
RED_FLAGS = [
    "commission only",
    "commission-only",
    "100% commission",
    "unlimited earning potential",
    "be your own boss",
    "mlm",
    "network marketing",
    "multi-level marketing",
    "starter kit",
    "pay for training",
    "training fee",
    "contact us on telegram",
    "via telegram",
    "via whatsapp",
    "on whatsapp",
    "reshipping",
    "package forwarding",
    "check deposit",
    "wire transfer",
    "forex",
    "earn $500 a day",
    "work from home and earn",
    "paid per video",
    "paid per vid",
    "paid per view",
    "pay per view",
]

# Offshore outsourcing / VA shops: low pay, not the roles you're after.
# Matched as substrings of company + title (lowercase).
OFFSHORE_FLAGS = [
    "outsourc", "bpo", "virtual assistant", "general va", "with english",
    "offshore", "nearshore", "talent pool", "manpower pooling", "pooling",
]

# Companies to always skip (lowercase). Add anything that wastes your time.
COMPANY_BLOCKLIST = {
    "outlier",
    "dataannotation",
    "data annotation",
    "remotasks",
    "scale ai",
    "appen",
    "telus international",
    "cemspace",
}

# ---------------------------------------------------------------------------
# Remote verification. A job must be clearly remote and not hybrid/on-site.
# ---------------------------------------------------------------------------
NOT_REMOTE_PHRASES = [
    "hybrid",
    "on-site",
    "onsite",
    "in-office",
    "in office",
    "in-person",
]
# These only count when found in the description (remote postings often say
# "on-site offsites" etc., so we look for stronger phrasing there).
NOT_REMOTE_DESC_PHRASES = [
    "this is a hybrid",
    "hybrid role",
    "hybrid schedule",
    "hybrid position",
    "this role is hybrid",
    "this is an on-site",
    "this role is on-site",
    "this is an onsite",
    "this role is onsite",
    "on-site position",
    "onsite position",
    "days a week in the office",
    "days per week in the office",
    "days a week in our office",
    "days per week in our office",
    "must be able to commute",
    "not a remote",
    "not remote",
]

# You're in the US: a location must mention one of US_OK, be a US city/state
# ("Austin, TX"), or say "remote" without naming a NON_US_ONLY region.
# Anything else (e.g. "Sri Lanka", "Berlin") is dropped.
US_OK = [
    "anywhere", "worldwide", "global", "united states", "north america",
    "americas", "us", "usa", "u.s.",  # us/usa/u.s. are matched as whole words
]
NON_US_ONLY = [
    "europe", "emea", "eu only", "uk", "united kingdom", "germany", "france",
    "spain", "poland", "portugal", "netherlands", "india", "philippines",
    "pakistan", "nigeria", "latam", "latin america", "south america",
    "brazil", "mexico", "argentina", "colombia", "apac", "asia", "australia",
    "new zealand", "canada", "singapore", "japan", "south africa",
    "ukraine", "sri lanka", "indonesia", "malaysia", "vietnam", "thailand",
    "kenya", "egypt", "turkey", "romania", "serbia", "ireland", "israel",
]

# ---------------------------------------------------------------------------
# Company job boards: health, wellness and DTC brands in Superpower's lane.
# Pulled straight from their own Ashby / Greenhouse / Lever boards, so these
# are first-party listings (no reposts, no ghost jobs). Only remote roles are
# kept. All slugs verified live; add more as you find them.
# ---------------------------------------------------------------------------
COMPANY_BOARDS = [
    # (display name, ats, slug)
    ("Superpower", "ashby", "superpower"),
    ("Eight Sleep", "ashby", "eightsleep"),
    ("WHOOP", "ashby", "whoop"),
    ("Headway", "ashby", "headway"),
    ("Tonal", "ashby", "tonal"),
    ("Winona", "ashby", "winona"),
    ("Oura", "greenhouse", "oura"),
    ("AG1", "greenhouse", "ag1"),
    ("Hone Health", "greenhouse", "honehealth"),
    ("Seed Health", "greenhouse", "seed"),
    ("Ritual", "greenhouse", "ritual"),
    ("Momentous", "greenhouse", "momentous"),
    ("Maven Clinic", "greenhouse", "mavenclinic"),
    ("Parsley Health", "greenhouse", "parsleyhealth"),
    ("Prenuvo", "greenhouse", "prenuvo"),
    ("Ezra", "greenhouse", "ezra"),
    ("Liquid I.V.", "greenhouse", "liquidiv"),
    ("Olipop", "greenhouse", "olipop"),
    ("Future", "greenhouse", "future"),
    ("Peloton", "greenhouse", "peloton"),
    ("Manscaped", "greenhouse", "manscaped"),
    ("ThirdLove", "greenhouse", "thirdlove"),
    ("Glossier", "greenhouse", "glossier"),
    ("Grüns", "greenhouse", "gruns"),
    ("Tia", "greenhouse", "tia"),
    ("Ro", "lever", "ro"),
    ("Everlywell", "lever", "everlywell"),
    ("Viome", "lever", "viome"),
    ("Lifeforce", "lever", "lifeforce"),
]
