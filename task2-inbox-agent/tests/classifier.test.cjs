const test = require("node:test");
const assert = require("node:assert/strict");
const { classifyEmail } = require("../dist/classifier.js");

function email(subject, body) {
  return {
    id: "TEST-001",
    customerName: "Test Customer",
    customerEmail: "test@example.com",
    subject,
    body,
    receivedAt: "2026-10-01T10:00:00.000Z",
  };
}

test("classifies technical support", () => {
  const result = classifyEmail(
    email("Website error", "My website is not working.")
  );
  assert.equal(result.category, "technical_support");
});

test("classifies billing", () => {
  const result = classifyEmail(
    email("Invoice problem", "I was charged twice.")
  );
  assert.equal(result.category, "billing");
});

test("classifies account management", () => {
  const result = classifyEmail(
    email("Password reset", "I cannot log in.")
  );
  assert.equal(result.category, "account_management");
});

test("classifies sales", () => {
  const result = classifyEmail(
    email("Pricing information", "Please send your pricing options.")
  );
  assert.equal(result.category, "sales");
});

test("classifies feature requests", () => {
  const result = classifyEmail(
    email("New feature", "Please add a CSV export feature.")
  );
  assert.equal(result.category, "feature_request");
});

test("classifies general messages", () => {
  const result = classifyEmail(
    email("Getting started", "Where can I find the help documentation?")
  );
  assert.equal(result.category, "other");
});

test("marks an outage as urgent", () => {
  const result = classifyEmail(
    email("Site is down", "Our entire website is down.")
  );
  assert.equal(result.priority, "urgent");
});

test("flags an account security concern for review", () => {
  const result = classifyEmail(
    email("Account hacked", "Someone accessed my account without permission.")
  );
  assert.equal(result.requiresHumanReview, true);
  assert.ok(result.reviewReasons.includes("account_security"));
});

test("flags a payment dispute for review", () => {
  const result = classifyEmail(
    email("Payment dispute", "I dispute this charge.")
  );
  assert.equal(result.requiresHumanReview, true);
  assert.ok(result.reviewReasons.includes("billing_or_payment_dispute"));
});

test("detects negative sentiment", () => {
  const result = classifyEmail(
    email("Complaint", "I am frustrated and disappointed.")
  );
  assert.equal(result.sentiment, "negative");
  assert.equal(result.requiresHumanReview, true);
});

test("detects positive sentiment", () => {
  const result = classifyEmail(
    email("Thank you", "Thank you for the excellent service.")
  );
  assert.equal(result.sentiment, "positive");
});

test("returns a concise summary", () => {
  const body = "  I need help with my website.  ";
  const result = classifyEmail(email("Help", body));
  assert.equal(result.summary, "I need help with my website.");
});

test("returns a review reasons array", () => {
  const result = classifyEmail(email("Question", "General inquiry."));
  assert.ok(Array.isArray(result.reviewReasons));
});

test("does not flag a neutral general question automatically", () => {
  const result = classifyEmail(
    email("Question", "Where can I find general documentation?")
  );
  assert.equal(result.requiresHumanReview, false);
});

test("flags legal concerns for human review", () => {
  const result = classifyEmail(
    email("Legal action", "I may take legal action over this privacy violation.")
  );
  assert.equal(result.requiresHumanReview, true);
  assert.ok(result.reviewReasons.includes("legal_or_compliance"));
});

test("preserves the expected category vocabulary", () => {
  const valid = [
    "technical_support",
    "billing",
    "account_management",
    "sales",
    "feature_request",
    "other",
  ];

  const result = classifyEmail(email("Question", "Hello."));
  assert.ok(valid.includes(result.category));
});