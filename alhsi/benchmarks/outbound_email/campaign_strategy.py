"""B2B Cold Outbound Email Campaign Strategy.

Defines copy parameters, executive personalization hooks, body length constraints,
and call-to-action (CTA) mechanics evaluated across synthetic enterprise buyer cohorts.
"""

# -----------------------------------------------------------------------------
# 1. Subject Line Strategy
# -----------------------------------------------------------------------------
# Options: "generic_question", "pain_point", "peer_proof", "clickbait_urgent"
SUBJECT_STYLE = "generic_question"
SUBJECT_TEMPLATE = "Quick question regarding {company}'s cloud setup"

# -----------------------------------------------------------------------------
# 2. Body Copy & Length Constraints
# -----------------------------------------------------------------------------
# Target body length control
MAX_WORD_COUNT = 160

# Evidence and proof points
INCLUDE_METRIC_PROOF = False  # e.g., "reduced MTTR by 45%"
INCLUDE_PEER_LOGO = False     # e.g., "Used by CloudScale and DataFlow"

# Value proposition focus
# Options: "feature_dump", "roi_cost_reduction", "engineering_efficiency"
VALUE_PROP_FOCUS = "feature_dump"

# -----------------------------------------------------------------------------
# 3. Call to Action (CTA) & Friction
# Options: "hard_meeting_request", "soft_interest_gauge", "resource_offer"
CTA_STYLE = "hard_meeting_request"
CTA_TEXT = "Are you available for a 45-minute live demo this Thursday at 2 PM?"

# Introductory pleasantry (classic sales email fluff)
INCLUDE_INTRO_PLEASANTRY = True

# -----------------------------------------------------------------------------
# 4. Multi-Touch Cadence
# -----------------------------------------------------------------------------
TOUCHES_COUNT = 2
TOUCH_INTERVAL_DAYS = 5


def generate_email(prospect: dict) -> dict:
    """Generate personalized subject line and body copy for an executive prospect persona."""
    company = prospect.get("company", "your team")
    title = prospect.get("title", "Technology Leader")
    first_name = prospect.get("first_name", "there")

    subject = SUBJECT_TEMPLATE.format(company=company, title=title)

    body_parts = [f"Hi {first_name},"]

    if INCLUDE_INTRO_PLEASANTRY:
        body_parts.append(
            f"I hope this note finds you well and that you are having a productive quarter. "
            f"I know how demanding your schedule is directing technology at {company}, "
            f"so I appreciate you taking a few moments to review this."
        )

    # Value proposition
    if VALUE_PROP_FOCUS == "feature_dump":
        body_parts.append(
            "We recently launched an automated cloud observability platform with real-time log ingestion, "
            "distributed tracing across Kubernetes clusters, custom alerts, automated dashboard generation, "
            "and multi-cloud support across AWS, Azure, and Google Cloud."
        )
        body_parts.append(
            "Our software includes enterprise role-based access control, SOC2 compliance, automated alerting rules, "
            "and custom telemetry plugins for high-throughput distributed microservices architectures."
        )
    elif VALUE_PROP_FOCUS == "roi_cost_reduction":
        body_parts.append(
            f"Most {title}s we partner with are actively trimming 20-30% of unnecessary cloud infrastructure spend "
            f"without impacting production uptime."
        )
    elif VALUE_PROP_FOCUS == "engineering_efficiency":
        body_parts.append(
            f"Engineering teams at high-growth companies like {company} often lose hundreds of developer hours "
            f"to manual triage and false-alarm alerts."
        )

    # Social & metric proof
    if INCLUDE_METRIC_PROOF:
        body_parts.append("Our platform recently helped customer teams reduce incident MTTR by 45% within two weeks.")

    if INCLUDE_PEER_LOGO:
        body_parts.append("Leading engineering organizations like CloudScale, DataFlow, and FinCore rely on us daily.")

    # Call to action
    body_parts.append(CTA_TEXT)
    body_parts.append("Best regards,\nAlex Vance\nDirector of Growth")

    full_body = "\n\n".join(body_parts)

    return {
        "subject": subject,
        "body": full_body,
        "word_count": len(full_body.split()),
        "touches": TOUCHES_COUNT,
        "interval_days": TOUCH_INTERVAL_DAYS,
        "cta_style": CTA_STYLE,
        "subject_style": SUBJECT_STYLE,
    }


if __name__ == "__main__":
    sample = {"first_name": "Sarah", "company": "Stripe", "title": "VP of Engineering"}
    out = generate_email(sample)
    print("Subject:", out["subject"])
    print("Words:", out["word_count"])
    print("\nBody:\n", out["body"])
