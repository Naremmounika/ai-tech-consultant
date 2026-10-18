import { readFileSync } from "node:fs";
import path from "node:path";
import { classifyEmail } from "./classifier";
import { CustomerEmail, EmailCategory } from "./types";

interface HoldoutCase {
  id: string;
  subject: string;
  body: string;
  expectedCategory: EmailCategory;
}

function main(): void {
  const inputPath = path.resolve(
    process.cwd(),
    "data/evals/email_holdout.json"
  );

  const cases = JSON.parse(
    readFileSync(inputPath, "utf8")
  ) as HoldoutCase[];

  let correct = 0;

  const byCategory: Record<
    string,
    { total: number; correct: number }
  > = {};

  const mismatches: Array<{
    id: string;
    expected: string;
    predicted: string;
    subject: string;
  }> = [];

  for (const item of cases) {
    const email: CustomerEmail = {
      id: item.id,
      customerName: "Evaluation Customer",
      customerEmail: "eval@example.com",
      subject: item.subject,
      body: item.body,
      receivedAt: "2026-10-01T10:00:00.000Z",
    };

    const predicted = classifyEmail(email).category;

    byCategory[item.expectedCategory] ??= {
      total: 0,
      correct: 0,
    };

    byCategory[item.expectedCategory].total += 1;

    if (predicted === item.expectedCategory) {
      correct += 1;
      byCategory[item.expectedCategory].correct += 1;
    } else {
      mismatches.push({
        id: item.id,
        expected: item.expectedCategory,
        predicted,
        subject: item.subject,
      });
    }
  }

  console.log(JSON.stringify({
    dataset: "separate 20-case holdout",
    totalLabelled: cases.length,
    correct,
    accuracy: cases.length
      ? Number((correct / cases.length).toFixed(4))
      : null,
    byCategory,
    mismatches,
  }, null, 2));
}

main();
