"""Pain-signal phrase library.

Each category gets a weight. A thread earns the weight once per distinct phrase
it contains, so a post that says "I've tried everything", "I'm at my wits end"
and "I wish there was something" scores in three categories.

Phrases are matched case-insensitively against normalised text (curly quotes
straightened, apostrophes optional), so "ive tried everything" and
"I've tried everything" both hit.
"""

# --- Signals in the post itself ------------------------------------------------

PAIN_CATEGORIES = {
    # The gap: people asking for something that doesn't exist yet.
    "wish_for_solution": {
        "weight": 4.0,
        "phrases": [
            "i wish there was", "i wish there were", "i wish someone would",
            "i wish someone made", "i wish i could just", "if only there was",
            "if only there were", "why is there no", "why isn't there",
            "why is there not", "why doesn't anyone make", "why does nobody make",
            "why hasn't anyone", "someone should make", "someone should invent",
            "someone needs to make", "someone needs to invent", "no one makes",
            "nobody makes", "does anything exist", "does something exist",
            "is there a product", "is there an app", "is there a tool",
            "is there a device", "is there anything that", "is there anything out there",
            "there has to be a better way", "there's got to be a better way",
            "there must be a better way", "there has to be something",
            "can't find anything that", "cant find anything that",
            "can't find a single", "nothing on the market",
            "i would pay", "i'd pay", "id pay anything", "i'd pay anything",
            "would pay good money", "take my money", "shut up and take my money",
            "i would buy", "i'd buy", "would happily pay",
        ],
    },
    # Exhausted options: the market's current answers are failing them.
    "tried_everything": {
        "weight": 3.0,
        "phrases": [
            "i've tried everything", "tried everything", "tried literally everything",
            "tried every", "tried all the", "tried so many", "tried countless",
            "nothing has worked", "nothing works", "nothing seems to work",
            "nothing is working", "nothing helps", "nothing has helped",
            "nothing ever works", "none of it works", "none of them work",
            "none of it has helped", "didn't work for me", "doesn't work for me",
            "made it worse", "only made it worse", "only temporary relief",
            "temporary relief", "temporary fix", "band-aid", "bandaid solution",
            "keeps coming back", "always comes back", "comes right back",
            "spent thousands", "spent hundreds", "spent so much money",
            "wasted so much money", "wasted money on", "waste of money",
            "seen multiple doctors", "seen so many doctors", "every doctor",
            "been to every", "multiple specialists", "seen specialists",
            "dermatologist said", "doctor just", "doctors just", "out of options",
            "running out of options", "last resort", "my last hope",
        ],
    },
    # Raw emotional intensity: how badly this bothers them.
    "desperation": {
        "weight": 3.0,
        "phrases": [
            "i can't take this anymore", "i cant take this anymore",
            "i can't take it anymore", "can't do this anymore", "cant do this anymore",
            "at my wits end", "at my wit's end", "i'm desperate", "im desperate",
            "so desperate", "desperate for", "please help", "begging for help",
            "ruining my life", "ruined my life", "destroying my life",
            "taking over my life", "controls my life", "i'm losing my mind",
            "losing my mind", "driving me insane", "driving me crazy",
            "making me miserable", "so miserable", "i'm miserable",
            "i just want to feel normal", "just want to be normal",
            "i'm so tired of", "im so tired of", "sick and tired of",
            "i give up", "about to give up", "ready to give up",
            "i don't know what else to do", "i dont know what else to do",
            "i'm at a loss", "at a complete loss", "i've had enough",
            "can't live like this", "cant live like this", "can't keep living like this",
            "i hate my", "i hate how", "i'm crying", "cried myself", "in tears",
            "breaking down", "mental breakdown", "affecting my job",
            "affecting my work", "affecting my relationship", "affecting my marriage",
            "ruining my relationship", "can't sleep because", "no quality of life",
            "for years now", "suffered for years", "struggling for years",
            "dealt with this for years", "my whole life", "since i was a kid",
        ],
    },
    # Uneducated on the true cause: room for a mechanism / education angle.
    "unknown_cause": {
        "weight": 3.0,
        "phrases": [
            "no idea why", "no idea what's causing", "no idea what is causing",
            "can't figure out why", "cant figure out why", "can't figure out what",
            "what's causing this", "what is causing this", "what could be causing",
            "what causes this", "root cause", "nobody knows why", "no one knows why",
            "doctors don't know", "doctors dont know", "doctor doesn't know",
            "doctors can't figure", "no one can tell me", "nobody can tell me",
            "tests came back normal", "everything came back normal",
            "bloodwork came back normal", "blood work was normal",
            "told me it's just", "told me its just", "told it's normal",
            "said it's normal", "said its just", "it's all in my head",
            "all in my head", "dismissed me", "dismissed by", "brushed off",
            "brushed me off", "doesn't take me seriously", "don't take me seriously",
            "undiagnosed", "misdiagnosed", "no diagnosis", "can't get a diagnosis",
        ],
    },
    # Unspoken problems: embarrassing, isolating, under-served.
    "unspoken": {
        "weight": 2.5,
        "phrases": [
            "nobody talks about", "no one talks about", "why does no one talk about",
            "why doesn't anyone talk about", "too embarrassed", "so embarrassed",
            "embarrassing to admit", "embarrassed to ask", "ashamed to",
            "i'm ashamed", "never told anyone", "can't tell anyone",
            "can't talk to anyone about", "no one to talk to", "feel so alone",
            "feel alone in this", "thought i was the only one", "am i the only one",
            "is it just me", "no one understands", "nobody understands",
            "using a throwaway", "throwaway account", "throwaway because",
        ],
    },
    # Active help-seeking: lower weight, but marks intent to act.
    "help_seeking": {
        "weight": 1.5,
        "phrases": [
            "how do i fix", "how do i stop", "how do i get rid of", "how to get rid of",
            "how do i deal with", "how do you deal with", "how to deal with",
            "how do i cope", "how do i make it stop", "any advice", "any tips",
            "any suggestions", "what actually works", "what finally worked",
            "what worked for you", "what helped you", "does anyone else",
            "anyone else deal with", "anyone else struggle", "anyone else have",
            "anyone have experience", "need help with", "looking for a solution",
            "looking for something", "recommendations for",
        ],
    },
}

# --- Signals in the comments ------------------------------------------------------

# Commenters saying "this is me too": proves the problem is shared, not a one-off.
AGREEMENT_PHRASES = [
    "same here", "me too", "same for me", "same with me", "same exact",
    "exact same", "same thing happens", "same thing happened", "same problem",
    "same issue", "same boat", "in the same boat", "this is me", "literally me",
    "this is exactly", "i could have written this", "could have written this myself",
    "you just described", "you described my", "i feel this", "i feel you",
    "thought i was the only one", "glad i'm not the only one", "glad im not the only one",
    "not the only one", "you're not alone", "youre not alone", "you are not alone",
    "i have the same", "i've had the same", "i had the same", "dealing with the same",
    "going through the same", "struggling with the same", "ugh same", "omg same",
    "following", "commenting to follow", "following for answers", "following this",
    "remindme", "remind me!", "saving this", "bump",
]

# Commenters telling their own story: depth of pain across many people.
STORY_PHRASES = [
    "i've been dealing", "ive been dealing", "i've had this", "ive had this",
    "i've struggled", "i struggled with", "for years i", "years ago i",
    "my experience", "in my experience", "i've been through", "i went through",
    "when i had", "i suffered", "i've suffered", "it took me", "i spent",
    "i tried", "i've tried", "ive tried",
]

# Someone claiming a fix exists. Many of these = the problem is less untapped
# (or there's a known fix the market hasn't packaged well). Reported, not penalised hard.
SOLUTION_CLAIM_PHRASES = [
    "what worked for me", "what finally worked", "finally found", "finally fixed",
    "fixed it for me", "fixed my", "cured my", "cured it", "solved it", "solved my",
    "game changer", "game-changer", "life changer", "life-changing", "changed my life",
    "holy grail", "100% fixed", "completely gone", "never looked back",
]

# Captures what people tried, e.g. "I've tried melatonin, magnesium and CBD".
TRIED_PATTERN = (
    r"\b(?:i(?:'ve|ve| have)? (?:tried|used|taken|been on|done)|tried|tested)\s+"
    r"([^.!?\n;:()]{3,120})"
)

# Default search seeds for discovery. Each is searched as an exact phrase.
# The strongest "gap" and "exhausted" phrases come first.
DISCOVERY_SEEDS = [
    "i wish there was",
    "why is there no",
    "someone should invent",
    "i would pay anything",
    "i've tried everything",
    "nothing has worked",
    "at my wits end",
    "i can't take this anymore",
    "ruining my life",
    "doctors can't figure out",
    "tests came back normal",
    "nobody talks about",
    "thought i was the only one",
    "how do i fix",
    "has anyone found a solution",
    "spent thousands",
    "keeps coming back",
    "is there anything that actually works",
]


# --- Your own phrases ---------------------------------------------------------------
# Lines in pain-finder/my_phrases.txt like "desperation: i feel like im dying"
# are added to that category (or to agreement / stories / fix_claims) at startup.

def _load_user_phrases():
    from pathlib import Path
    path = Path(__file__).resolve().parent.parent / "my_phrases.txt"
    if not path.exists():
        return
    extra = {"agreement": AGREEMENT_PHRASES, "stories": STORY_PHRASES, "fix_claims": SOLUTION_CLAIM_PHRASES}
    for n, line in enumerate(path.read_text().splitlines(), 1):
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        cat, sep, phrase = line.partition(":")
        cat, phrase = cat.strip(), phrase.strip().lower()
        if not sep or not phrase:
            raise SystemExit(f"{path}:{n}: expected 'category: phrase'")
        if cat in PAIN_CATEGORIES:
            PAIN_CATEGORIES[cat]["phrases"].append(phrase)
        elif cat in extra:
            extra[cat].append(phrase)
        else:
            raise SystemExit(f"{path}:{n}: unknown category '{cat}'. Use one of: "
                             + ", ".join(list(PAIN_CATEGORIES) + list(extra)))


_load_user_phrases()
