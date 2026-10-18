export type EmailCategory =
  | "technical_support"
  | "billing"
  | "account_management"
  | "sales"
  | "feature_request"
  | "other";

export type EmailPriority = "low" | "medium" | "high" | "urgent";

export type Sentiment = "positive" | "neutral" | "negative";

export type ReviewReason =
  | "billing_or_payment_dispute"
  | "account_security"
  | "legal_or_compliance"
  | "angry_customer"
  | "insufficient_knowledge"
  | "high_impact_issue";

export interface CustomerEmail {
  id: string;
  customerName: string;
  customerEmail: string;
  subject: string;
  body: string;
  receivedAt: string;
}

export interface EmailClassification {
  category: EmailCategory;
  priority: EmailPriority;
  sentiment: Sentiment;
  summary: string;
  requiresHumanReview: boolean;
  reviewReasons: ReviewReason[];
}

export interface KnowledgeSource {
  title: string;
  url: string;
  excerpt: string;
  score: number;
}

export interface KnowledgeResponse {
  question: string;
  answer: string;
  sources: KnowledgeSource[];
  grounded: boolean;
}

export interface DraftReply {
  subject: string;
  body: string;
  usedKnowledge: boolean;
  sourceUrls: string[];
  requiresHumanReview: boolean;
  reviewReasons: ReviewReason[];
}

export interface ProcessedEmail {
  email: CustomerEmail;
  classification: EmailClassification;
  knowledgeAnswer: string;
  sources: KnowledgeSource[];
  draft: DraftReply;
  status: "draft_ready" | "needs_human_review" | "failed";
  error?: string;
}
