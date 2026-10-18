import {
  CustomerEmail,
  EmailClassification,
  EmailCategory,
  EmailPriority,
  Sentiment,
  ReviewReason
} from "./types";

function includesAny(text: string, terms: string[]): boolean {
  return terms.some((term) => text.includes(term));
}

export function classifyEmail(email: CustomerEmail): EmailClassification {
  const text = `${email.subject} ${email.body}`.toLowerCase();

  let category: EmailCategory = "other";

  // Specific categories first to avoid broad keyword conflicts.
  if (
    includesAny(text, [
      "invoice", "billing", "charged", "payment", "refund",
      "subscription", "renewal", "overcharged", "credit card",
      "receipt", "payment method", "billing details",
      "plan cancellation", "cancel my plan", "cancelling my plan",
      "canceling my plan", "chargeback", "payment dispute"
    ])
  ) {
    category = "billing";
  } else if (
    includesAny(text, [
      "hacked", "unauthorized access", "unauthorised access",
      "security breach", "data breach", "account compromised",
      "stolen password", "someone accessed my account",
      "password", "login", "log in", "sign in", "account access",
      "reset my account", "two-factor", "two factor",
      "security code", "verification code", "verification process",
      "account email", "profile information", "profile details",
      "change phones", "device change", "locked",
      "unexpected account change"
    ])
  ) {
    category = "account_management";
  } else if (
    includesAny(text, [
      "feature request", "would like a feature", "please add",
      "it would be helpful", "suggestion", "integration request",
      "new feature", "feature improvement", "search filters",
      "reporting filters", "bulk-editing", "accessibility customization",
      "accessibility filters", "csv export", "export to csv",
      "export functionality", "add the ability", "support for",
      "would like the ability", "could you add", "request a feature"
    ])
  ) {
    category = "feature_request";
  } else if (
    includesAny(text, [
      "pricing", "price", "plan options", "demo", "sales",
      "purchase", "buy a plan", "upgrade plan", "upgrade options",
      "free trial", "trial availability", "business inquiry",
      "enterprise", "larger organization", "franchise",
      "considering the platform", "evaluating the platform",
      "trial account", "sales team", "schedule a demo",
      "multiple locations"
    ])
  ) {
    category = "sales";
  } else if (
    !includesAny(text, [
      "getting started", "how do i get started",
      "getting started guide", "general question"
    ]) &&
    includesAny(text, [
      "error", "bug", "not working", "website", "domain",
      "dashboard", "customize", "customise", "font", "colors",
      "colours", "page", "email notification", "configuration",
      "configure", "settings", "template", "loading", "broken"
    ])
  ) {
    category = "technical_support";
  }

  let priority: EmailPriority = "medium";

  if (
    includesAny(text, [
      "site is down", "website is down", "data breach",
      "hacked", "unauthorized access", "unauthorised access",
      "security breach", "all members affected"
    ])
  ) {
    priority = "urgent";
  } else if (
    includesAny(text, [
      "urgent", "asap", "immediately", "production is down",
      "cannot access my business", "can't access my business",
      "business is losing", "deadline today"
    ])
  ) {
    priority = "high";
  } else if (
    includesAny(text, [
      "when convenient", "just wondering", "general question",
      "feature suggestion", "no rush"
    ])
  ) {
    priority = "low";
  }

  const negativeTerms = [
    "angry", "frustrated", "disappointed", "terrible",
    "unacceptable", "ridiculous", "complaint", "furious",
    "waste of time", "cancel immediately", "very upset"
  ];

  const positiveTerms = [
    "thank you", "thanks", "great service", "appreciate",
    "excellent", "happy with", "well done"
  ];

  let sentiment: Sentiment = "neutral";

  if (includesAny(text, negativeTerms)) {
    sentiment = "negative";
  } else if (includesAny(text, positiveTerms)) {
    sentiment = "positive";
  }

  const reviewReasons = new Set<ReviewReason>();

  if (
    category === "billing" ||
    includesAny(text, [
      "chargeback", "dispute this charge", "refund my money",
      "double charged", "charged twice", "payment dispute"
    ])
  ) {
    reviewReasons.add("billing_or_payment_dispute");
  }

  if (
    includesAny(text, [
      "hacked", "unauthorized access", "unauthorised access",
      "security breach", "stolen password", "account compromised",
      "data breach", "someone accessed my account"
    ])
  ) {
    reviewReasons.add("account_security");
  }

  if (
    includesAny(text, [
      "lawsuit", "legal action", "lawyer", "attorney",
      "regulator", "gdpr complaint", "privacy violation"
    ])
  ) {
    reviewReasons.add("legal_or_compliance");
  }

  if (sentiment === "negative") {
    reviewReasons.add("angry_customer");
  }

  if (
    priority === "urgent" ||
    includesAny(text, [
      "all customers affected", "data loss", "lost all my data",
      "entire website unavailable", "production outage"
    ])
  ) {
    reviewReasons.add("high_impact_issue");
  }

  const reasons = [...reviewReasons];

  const summary = email.body
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, 220);

  return {
    category,
    priority,
    sentiment,
    summary,
    requiresHumanReview: reasons.length > 0,
    reviewReasons: reasons
  };
}
