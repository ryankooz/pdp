"""Subreddit packs grouped by life area.

Discovery searches all of Reddit by default. Packs narrow it to communities
where people vent about a specific kind of problem. Mix and match with
`--pack health --pack body` or pass your own with `--subreddit`.
"""

PACKS = {
    "health": [
        "ChronicPain", "ChronicIllness", "IBS", "GERD", "Constipation", "SIBO",
        "tinnitus", "insomnia", "sleep", "migraine", "Allergies", "Sinusitis",
        "POTS", "cfs", "Fibromyalgia", "Hashimotos", "thyroidhealth", "diabetes",
        "Gout", "kidneystones", "Hemorrhoids", "Interstitialcystitis", "lowerbackpain",
        "sciatica", "Posture", "Dentistry", "TMJ", "Bruxism", "Visualsnow",
        "dryeyes", "Floaters", "HealthAnxiety", "longcovid", "Perimenopause",
        "Menopause", "PCOS", "endometriosis", "Hyperhidrosis", "Sweatypalms",
        "Snoring", "sleepapnea", "Narcolepsy", "Vertigo", "Neuropathy",
    ],
    "body": [
        "HairLoss", "tressless", "FemaleHairLoss", "SkincareAddiction", "acne",
        "Rosacea", "eczema", "Psoriasis", "keratosispilaris", "Melasma",
        "Hidradenitis", "bodyodor", "Halitosis", "loseit", "PetiteFitness",
        "intermittentfasting", "Weightlosstechniques", "BingeEatingDisorder",
        "Lipedema", "Cellulite", "Posture", "flatfeet", "Plantarfasciitis",
        "Gynecomastia", "LooseSkin", "stretchmarks",
    ],
    "mental": [
        "Anxiety", "depression", "ADHD", "adhdwomen", "socialanxiety", "OCD",
        "BPD", "CPTSD", "selfimprovement", "getdisciplined", "productivity",
        "decidingtobebetter", "lonely", "Procrastination", "burnout",
        "overthinking", "ADHD_Programmers", "Agoraphobia",
    ],
    "family": [
        "Parenting", "toddlers", "beyondthebump", "NewParents", "breastfeeding",
        "sleeptrain", "Mommit", "daddit", "AgingParents", "CaregiverSupport",
        "dementia", "Autism_Parenting", "ADHDparenting", "infertility",
        "TryingForABaby", "BabyBumps", "stepparents", "Divorce", "raisedbynarcissists",
    ],
    "relationships": [
        "relationship_advice", "dating_advice", "marriage", "DeadBedrooms",
        "AskMen", "AskWomen", "AskMenOver30", "AskWomenOver30", "AskWomenOver40",
        "LongDistance", "ExNoContact", "socialskills", "MakeNewFriendsHere",
    ],
    "work": [
        "careerguidance", "jobs", "antiwork", "WorkReform", "recruitinghell",
        "nursing", "Teachers", "Residency", "medicine", "Pharmacy", "Paramedics",
        "Truckers", "Construction", "electricians", "Plumbing", "KitchenConfidential",
        "TalesFromRetail", "sysadmin", "ITCareerQuestions", "cscareerquestions",
        "Accounting", "Lawyertalk", "RealEstate", "Serverlife", "BarBattlestations",
        "remotework", "freelance", "overemployed",
    ],
    "money": [
        "personalfinance", "povertyfinance", "Debt", "StudentLoans", "Frugal",
        "budget", "financialindependence", "smallbusiness", "Entrepreneur",
        "ecommerce", "sweatystartup", "Landlord", "Insurance", "HealthInsurance",
    ],
    "home": [
        "HomeImprovement", "homeowners", "DIY", "Plumbing", "HVAC", "Mold",
        "pestcontrol", "bedbugs", "Roaches", "landscaping", "lawncare",
        "CleaningTips", "declutter", "organization", "Apartmentliving",
        "HomeMaintenance", "Noise",
    ],
    "pets": [
        "dogs", "Dogtraining", "puppy101", "reactivedogs", "DogAdvice", "cats",
        "CatAdvice", "AskVet", "Pets", "horses", "Aquariums",
    ],
    "age": [
        "college", "GradSchool", "teenagers", "AskOldPeople", "retirement",
        "over60", "Millennials", "GenX", "AskMenOver30", "AskWomenOver40",
    ],
    # Where people say what they don't say out loud: rich in Level 3-4 pain.
    "venting": [
        "offmychest", "TrueOffMyChest", "Vent", "self", "confession", "lonely", "disability",
        "TwoXChromosomes", "AskMenAdvice", "SingleParents", "ChronicIllness", "AskWomenOver30",
    ],
    "lifestyle": [
        "Cooking", "MealPrepSunday", "EatCheapAndHealthy", "running",
        "bodyweightfitness", "Fitness", "xxfitness", "cycling", "travel",
        "solotravel", "digitalnomad", "vandwellers", "malefashionadvice",
        "femalefashionadvice", "BuyItForLife", "gadgets", "techsupport",
        "Gaming", "GirlGamers", "bald",
    ],
}


def resolve(packs, extra):
    """Return a de-duplicated subreddit list from pack names plus extra names."""
    subs = []
    for name in packs or []:
        if name == "all":
            for group in PACKS.values():
                subs.extend(group)
        elif name in PACKS:
            subs.extend(PACKS[name])
        else:
            raise SystemExit(f"Unknown pack '{name}'. Choose from: {', '.join(PACKS)} or all")
    subs.extend(s.removeprefix("r/") for s in extra or [])
    seen, out = set(), []
    for s in subs:
        if s.lower() not in seen:
            seen.add(s.lower())
            out.append(s)
    return out
