
import {
  KnowledgeResponse,
  KnowledgeSource
} from "./types";

const BASE_URL = (
  process.env.KNOWLEDGE_BRAIN_URL ||
  "http://127.0.0.1:8000"
).replace(/\/+$/, "");

const TIMEOUT_MS = Number(
  process.env.KNOWLEDGE_TIMEOUT_MS || 30000
);

const TOP_K = Math.min(
  10,
  Math.max(1, Number(process.env.KNOWLEDGE_TOP_K || 5))
);

export async function askKnowledgeBrain(
  question: string
): Promise<KnowledgeResponse> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const response = await fetch(`${BASE_URL}/ask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify({
        question,
        top_k: TOP_K
      }),
      signal: controller.signal
    });

    if (!response.ok) {
      throw new Error(
        `Knowledge Brain returned HTTP ${response.status}`
      );
    }

    const data: unknown = await response.json();

    if (
      typeof data !== "object" ||
      data === null ||
      !("answer" in data) ||
      typeof data.answer !== "string" ||
      !("grounded" in data) ||
      typeof data.grounded !== "boolean"
    ) {
      throw new Error("Knowledge Brain returned an invalid response.");
    }

    const raw = data as {
      question?: string;
      answer: string;
      grounded: boolean;
      sources?: Array<{
        title?: string;
        url?: string;
        excerpt?: string;
        score?: number;
      }>;
    };

    const sources: KnowledgeSource[] = Array.isArray(raw.sources)
      ? raw.sources
          .filter((source) => typeof source.url === "string" && source.url.length > 0)
          .map((source) => ({
            title: source.title || "Help-center article",
            url: source.url!,
            excerpt: source.excerpt || "",
            score: typeof source.score === "number" ? source.score : 0
          }))
      : [];

    return {
      question: raw.question || question,
      answer: raw.answer,
      grounded: raw.grounded && sources.length > 0,
      sources
    };
  } finally {
    clearTimeout(timeout);
  }
}
