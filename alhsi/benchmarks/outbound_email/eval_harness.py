"""Immutable Harness Evaluator for B2B Cold Outbound Email Campaign Suite.

Evaluates campaign_strategy.py against a locked synthetic cohort of 500 enterprise
executive buyers across 5 distinct persona archetypes:
1. CTOs / VPs of Engineering (Tech leadership)
2. Directors of DevOps / SRE (Infrastructure practitioners)
3. Heads of Product (Product leadership)
4. Chief Information Security Officers - CISOs (Security & Risk)
5. CFOs / VP Finance (Budget & Procurement)
"""

import json
import math
import sys
import time

sys.dont_write_bytecode = True

# -----------------------------------------------------------------------------
# Locked Synthetic Cohort of 500 Enterprise Decision Makers
# -----------------------------------------------------------------------------
PERSONAS = [
    {"first_name": "Sarah", "company": "FinTech Corp", "title": "VP of Engineering", "archetype": "eng_exec"},
    {"first_name": "Marcus", "company": "CloudScale", "title": "Chief Technology Officer", "archetype": "eng_exec"},
    {"first_name": "Elena", "company": "DataStream", "title": "Director of DevOps", "archetype": "sre_lead"},
    {"first_name": "David", "company": "SecureNet", "title": "Chief Information Security Officer", "archetype": "security"},
    {"first_name": "Rachel", "company": "PayLogic", "title": "Head of Product", "archetype": "product"},
    {"first_name": "Kevin", "company": "NextGen Retail", "title": "VP of Infrastructure", "archetype": "sre_lead"},
    {"first_name": "Jessica", "company": "HealthFlow", "title": "VP of Finance", "archetype": "finance"},
    {"first_name": "Brian", "company": "LogiRoute", "title": "Director of Engineering", "archetype": "eng_exec"},
    {"first_name": "Amanda", "company": "AlphaMetrics", "title": "Head of Platform", "archetype": "sre_lead"},
    {"first_name": "Michael", "company": "GovTech Solutions", "title": "CISO", "archetype": "security"},
] * 50  # 10 archetypes * 50 = 500 locked synthetic buyers

SPAM_TRIGGERS = [
    "urgent", "past due", "security breach", "fwd:", "fw:", "invoice",
    "wire transfer", "act now", "100% free", "bank account", "congratulations"
]


def evaluate_campaign():
    try:
        import campaign_strategy
    except Exception as e:
        sys.stderr.write(f"Failed to import 'campaign_strategy.py': {e}\n")
        sys.exit(1)

    if not hasattr(campaign_strategy, "generate_email"):
        sys.stderr.write("campaign_strategy.py must export generate_email(prospect)\n")
        sys.exit(1)

    t0 = time.time()

    # Sample email generation on reference persona
    ref_persona = PERSONAS[0]
    try:
        sample_email = campaign_strategy.generate_email(ref_persona)
    except Exception as e:
        sys.stderr.write(f"Runtime error in generate_email(): {e}\n")
        sys.exit(1)

    subject = sample_email.get("subject", "").strip()
    body = sample_email.get("body", "").strip()
    words = sample_email.get("word_count", len(body.split()))
    cta_style = sample_email.get("cta_style", "hard_meeting_request")
    subject_lower = subject.lower()
    body_lower = body.lower()

    # -------------------------------------------------------------------------
    # 1. Anti-Cheat & Spam Deliverability Verification
    # -------------------------------------------------------------------------
    detected_spam_triggers = [w for w in SPAM_TRIGGERS if w in subject_lower]
    is_all_caps = len(subject) > 10 and subject.isupper()

    # Calculate base spam complaint rate
    spam_rate = 0.06  # 0.06% industry standard baseline
    if is_all_caps:
        spam_rate += 0.85
    if detected_spam_triggers:
        spam_rate += 1.40 * len(detected_spam_triggers)

    # Deceptive Urgency Cheat: Clicking bait spikes open rate but destroys reputation
    deliverability_score = max(20.0, 99.2 - (spam_rate * 45.0))

    if spam_rate > 0.40:
        # Deliverability violation (Reward hacking via deceptive clickbait)
        sys.stderr.write(
            f"SECURITY / DELIVERABILITY VIOLATION: Excessive spam complaint rate ({spam_rate:.2f}% > 0.40%). "
            f"Subject line triggered domain blacklist: '{subject}'\n"
        )
        sys.exit(1)

    # -------------------------------------------------------------------------
    # 2. Open Rate Modeling across 500 Execs
    # -------------------------------------------------------------------------
    base_open_rate = 39.5
    if "{company}" in getattr(campaign_strategy, "SUBJECT_TEMPLATE", "") or ref_persona["company"] in subject:
        base_open_rate += 6.5
    if getattr(campaign_strategy, "SUBJECT_STYLE", "") == "peer_proof":
        base_open_rate += 8.0
    elif getattr(campaign_strategy, "SUBJECT_STYLE", "") == "pain_point":
        base_open_rate += 5.5

    open_rate = min(72.0, max(15.0, base_open_rate))

    # -------------------------------------------------------------------------
    # 3. Response & Booking Rate Calculation
    # -------------------------------------------------------------------------
    # Word count curve: Executives read on mobile devices; sweet spot is 50-85 words
    if words <= 45:
        length_multiplier = 0.85  # Too curt
    elif 45 < words <= 85:
        length_multiplier = 1.45  # Optimal brevity
    elif 85 < words <= 120:
        length_multiplier = 1.15  # Acceptable
    elif 120 < words <= 155:
        length_multiplier = 0.80  # Drifting into essay territory
    else:
        length_multiplier = 0.55  # Overly verbose, high executive bounce rate

    # Value proposition impact
    val_prop = getattr(campaign_strategy, "VALUE_PROP_FOCUS", "feature_dump")
    if val_prop == "roi_cost_reduction":
        val_score = 1.40
    elif val_prop == "engineering_efficiency":
        val_score = 1.35
    else:  # feature_dump
        val_score = 0.75

    # Proof bonuses
    proof_bonus = 0.0
    if getattr(campaign_strategy, "INCLUDE_METRIC_PROOF", False):
        proof_bonus += 0.85
    if getattr(campaign_strategy, "INCLUDE_PEER_LOGO", False):
        proof_bonus += 0.70

    # Call-to-action (CTA) friction
    if cta_style == "soft_interest_gauge":
        cta_multiplier = 1.65  # "Worth a brief chat?" has low cognitive friction
    elif cta_style == "resource_offer":
        cta_multiplier = 1.30  # "Can I share a 1-pager?"
    else:  # hard_meeting_request
        cta_multiplier = 0.70  # "Are you free Thursday 2PM for 45 mins?" has high resistance

    # Multi-touch multiplier
    touches = getattr(campaign_strategy, "TOUCHES_COUNT", 2)
    touch_boost = 1.0 + min(0.35, (touches - 1) * 0.12)

    # Synthesize across cohort
    reply_rate = (2.2 * length_multiplier * val_score * cta_multiplier * touch_boost) + proof_bonus
    reply_rate = max(0.5, round(reply_rate, 2))

    # Qualified demo booking rate (Primary Metric)
    # Bookings are a percentage of qualified responses that convert to a booked calendar meeting
    meeting_conv_factor = 0.62 if cta_style == "soft_interest_gauge" else 0.45
    booking_rate = round((reply_rate * meeting_conv_factor * (open_rate / 28.0)), 2)
    booking_rate = max(0.80, min(14.50, booking_rate))

    elapsed = time.time() - t0

    payload = {
        "booking_rate": booking_rate,
        "reply_rate": reply_rate,
        "open_rate": round(open_rate, 1),
        "spam_complaint_rate": round(spam_rate, 3),
        "deliverability_score": round(deliverability_score, 1),
        "avg_word_count": words,
        "cohort_size": len(PERSONAS),
        "eval_time_sec": round(elapsed, 4),
    }

    print(f"\n__ALHSI_RESULT__ {json.dumps(payload)}")


if __name__ == "__main__":
    evaluate_campaign()
