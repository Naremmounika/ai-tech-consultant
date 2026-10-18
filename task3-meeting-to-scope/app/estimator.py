import re


ESTIMATION_RULES = [
    (("payment", "checkout", "billing", "subscription"), 20),
    (("integration", "third-party", "api connection", "webhook"), 16),
    (("dashboard", "admin panel", "admin area", "admin management"), 20),
    (("booking", "appointment", "calendar", "scheduling"), 18),
    (("login", "authentication", "registration", "member account"), 12),
    (("migration", "import existing data", "data transfer"), 16),
    (("email notification", "email reminder", "notifications", "reminders"), 8),
    (("multilingual", "multi-language", "multiple languages", "language support", "translation", "english and spanish"), 14),
    (("favorites list", "favourites list", "save services", "saved services"), 8),
    (("mobile responsive", "responsive design", "mobile-friendly", "responsive website"), 10),
    (("seo", "search engine optimization", "search engine optimisation"), 6),
    (("contact form", "inquiry form", "enquiry form", "lead form"), 5),
    (("content page", "about page", "services page", "landing page"), 6),
    (("analytics", "reporting"), 8),
    (("search", "filter", "directory"), 14),
]


def estimate_feature(feature: dict) -> dict:
    """Estimate effort from feature wording using transparent rules."""
    text = (
        f"{feature.get('name', '')} "
        f"{feature.get('description', '')}"
    ).lower()

    base_hours = 8
    matched_rule = "general feature"

    for keywords, hours in ESTIMATION_RULES:
        if any(keyword in text for keyword in keywords):
            base_hours = hours
            matched_rule = ", ".join(keywords)
            break

    low_hours = round(base_hours * 0.75, 1)
    high_hours = round(base_hours * 1.5, 1)

    return {
        **feature,
        "estimated_hours": float(base_hours),
        "low_hours": low_hours,
        "high_hours": high_hours,
        "estimation_basis": matched_rule,
    }


def estimate_scope(features: list[dict]) -> dict:
    estimates = [
        estimate_feature(feature)
        for feature in features
    ]

    total = sum(item["estimated_hours"] for item in estimates)
    low = sum(item["low_hours"] for item in estimates)
    high = sum(item["high_hours"] for item in estimates)

    contingency_percent = 15
    total_with_contingency = round(
        total * (1 + contingency_percent / 100), 1
    )

    return {
        "features": estimates,
        "feature_count": len(estimates),
        "estimated_hours": round(total, 1),
        "low_hours": round(low, 1),
        "high_hours": round(high, 1),
        "contingency_percent": contingency_percent,
        "estimated_hours_with_contingency": total_with_contingency,
        "note": (
            "Rule-based preliminary estimates. Validate scope, "
            "dependencies, integrations, and acceptance criteria "
            "with a human before committing to a schedule."
        ),
    }
