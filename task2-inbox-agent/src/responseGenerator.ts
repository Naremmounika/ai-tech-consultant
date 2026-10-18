
import {
  CustomerEmail,
  DraftReply,
  EmailClassification,
  KnowledgeResponse,
  ReviewReason
} from "./types";

export function generateDraftReply(
  email: CustomerEmail,
  classification: EmailClassification,
  knowledge: KnowledgeResponse | null
): DraftReply {
  const reasons = new Set<ReviewReason>(
    classification.reviewReasons
  );

  const needsKnowledge =
    classification.category === "technical_support" ||
    classification.category === "account_management" ||
    classification.category === "feature_request" ||
    classification.category === "other";

  const canUseKnowledge =
    needsKnowledge &&
    knowledge !== null &&
    knowledge.grounded &&
    knowledge.sources.length > 0;

  let body: string;

  if (classification.reviewReasons.includes("account_security")) {
    body =
      `Hi ${email.customerName},\n\n` +
      "Thank you for reporting this. We take account-security concerns seriously. " +
      "Your message needs to be reviewed by our support team so they can verify " +
      "the situation and advise you on the appropriate next steps. " +
      "Please do not send passwords or verification codes by email.\n\n" +
      "Regards,\nSupport Team";
  } else if (
    classification.category === "billing" ||
    classification.reviewReasons.includes("billing_or_payment_dispute")
  ) {
    body =
      `Hi ${email.customerName},\n\n` +
      "Thank you for contacting us about your billing concern. " +
      "Our support team needs to review the details before confirming any " +
      "charges, adjustments, or refund eligibility. We have prepared your " +
      "message for human review.\n\n" +
      "Regards,\nSupport Team";
  } else if (
    classification.reviewReasons.includes("legal_or_compliance")
  ) {
    body =
      `Hi ${email.customerName},\n\n` +
      "Thank you for bringing this matter to our attention. " +
      "We have flagged your message for review by the appropriate team. " +
      "They will assess the details before providing a substantive response.\n\n" +
      "Regards,\nSupport Team";
  } else if (canUseKnowledge && knowledge) {
    const sourceList = knowledge.sources
      .map((source) => `- ${source.title}: ${source.url}`)
      .join("\n");

    body =
      `Hi ${email.customerName},\n\n` +
      "Thank you for contacting support.\n\n" +
      `${knowledge.answer}\n\n` +
      (sourceList ? `Helpful documentation:\n${sourceList}\n\n` : "") +
      "If this does not resolve the issue, please reply with any relevant " +
      "details so our support team can investigate further.\n\n" +
      "Regards,\nSupport Team";

    if (classification.reviewReasons.includes("angry_customer")) {
      body =
        `Hi ${email.customerName},\n\n` +
        "I'm sorry this has been frustrating. Thank you for explaining " +
        "what happened.\n\n" +
        `${knowledge.answer}\n\n` +
        (sourceList ? `Helpful documentation:\n${sourceList}\n\n` : "") +
        "Our team can review any remaining issues if you reply with further details.\n\n" +
        "Regards,\nSupport Team";
    }
  } else {
    reasons.add("insufficient_knowledge");

    body =
      `Hi ${email.customerName},\n\n` +
      "Thank you for contacting us. We need to confirm a few details " +
      "before providing an accurate answer. Your message has been flagged " +
      "for support-team review rather than providing unverified instructions.\n\n" +
      "Regards,\nSupport Team";
  }

  const sourceUrls = canUseKnowledge && knowledge
    ? [...new Set(knowledge.sources.map((source) => source.url))]
    : [];

  return {
    subject: `Re: ${email.subject}`,
    body,
    usedKnowledge: canUseKnowledge,
    sourceUrls,
    requiresHumanReview: reasons.size > 0,
    reviewReasons: [...reasons]
  };
}
