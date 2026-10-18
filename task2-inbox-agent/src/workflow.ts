
import {
  CustomerEmail,
  ProcessedEmail,
  ReviewReason,
  KnowledgeResponse,
} from "./types";

import { classifyEmail } from "./classifier";
import { askKnowledgeBrain } from "./knowledgeClient";
import { generateDraftReply } from "./responseGenerator";

export async function processEmail(
  email: CustomerEmail
): Promise<ProcessedEmail> {
  const classification = classifyEmail(email);

  const needsKnowledge =
    classification.category === "technical_support" ||
    classification.category === "account_management" ||
    classification.category === "feature_request" ||
    classification.category === "other";

  let knowledgeAnswer = "";
  let sources: ProcessedEmail["sources"] = [];
  let knowledge: KnowledgeResponse | null = null;
  let error: string | undefined;

  if (needsKnowledge) {
    try {
      knowledge = await askKnowledgeBrain(
        `Customer question: ${email.body}\nEmail subject for context: ${email.subject}`
      );

      knowledgeAnswer = knowledge.answer;
      sources = knowledge.sources;
    } catch (err) {
      error = err instanceof Error
        ? err.message
        : "Unknown Knowledge Brain error";
    }
  }

  const draft = generateDraftReply(
    email,
    classification,
    knowledge
  );

  if (error) {
    const extraReason: ReviewReason = "insufficient_knowledge";

    if (!draft.reviewReasons.includes(extraReason)) {
      draft.reviewReasons.push(extraReason);
    }

    draft.requiresHumanReview = true;
  }

  const status: ProcessedEmail["status"] =
    error
      ? "failed"
      : draft.requiresHumanReview
        ? "needs_human_review"
        : "draft_ready";

  return {
    email,
    classification,
    knowledgeAnswer,
    sources,
    draft,
    status,
    ...(error ? { error } : {})
  };
}

export async function processBatch(
  emails: CustomerEmail[]
): Promise<ProcessedEmail[]> {
  const results: ProcessedEmail[] = [];

  // Sequential processing avoids overwhelming the local API.
  for (const email of emails) {
    results.push(await processEmail(email));
  }

  return results;
}
