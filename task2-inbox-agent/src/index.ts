
import "dotenv/config";

import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

import { sampleEmails } from "./sampleEmails";
import { processBatch } from "./workflow";

async function main(): Promise<void> {
  const limitArgument = process.argv.find((arg) =>
    arg.startsWith("--limit=")
  );

  const limit = limitArgument
    ? Number(limitArgument.split("=")[1])
    : sampleEmails.length;

  if (!Number.isInteger(limit) || limit < 1) {
    throw new Error("--limit must be a positive integer.");
  }

  const emails = sampleEmails.slice(
    0,
    Math.min(limit, sampleEmails.length)
  );

  console.log(`Inbox Agent: processing ${emails.length} email(s)...`);

  const results = await processBatch(emails);

  const summary = {
    totalEmails: results.length,
    categories: {} as Record<string, number>,
    priorities: {} as Record<string, number>,
    sentiments: {} as Record<string, number>,
    statuses: {} as Record<string, number>,
    requiringHumanReview: 0,
    usingKnowledgeBrain: 0,
    withSources: 0,
    failed: 0
  };

  for (const result of results) {
    const category = result.classification.category;
    const priority = result.classification.priority;
    const sentiment = result.classification.sentiment;

    summary.categories[category] =
      (summary.categories[category] || 0) + 1;

    summary.priorities[priority] =
      (summary.priorities[priority] || 0) + 1;

    summary.sentiments[sentiment] =
      (summary.sentiments[sentiment] || 0) + 1;

    summary.statuses[result.status] =
      (summary.statuses[result.status] || 0) + 1;

    if (result.draft.requiresHumanReview) {
      summary.requiringHumanReview++;
    }

    if (result.draft.usedKnowledge) {
      summary.usingKnowledgeBrain++;
    }

    if (result.sources.length > 0) {
      summary.withSources++;
    }

    if (result.status === "failed") {
      summary.failed++;
    }
  }

  const outputDirectory = path.join(process.cwd(), "outputs");
  await mkdir(outputDirectory, { recursive: true });

  const outputPath = path.join(
    outputDirectory,
    "processed_emails.json"
  );

  await writeFile(
    outputPath,
    JSON.stringify(
      {
        generatedAt: new Date().toISOString(),
        summary,
        results
      },
      null,
      2
    ),
    "utf8"
  );

  console.log("\n=== Inbox Agent Summary ===");
  console.log(JSON.stringify(summary, null, 2));
  console.log(`\nDetailed results saved to: ${outputPath}`);

  if (process.argv.includes("--eval")) {
    console.log(
      "\nNote: these are operational metrics, not measured " +
      "classification accuracy. Accuracy requires manually " +
      "labelled expected answers for each email."
    );
  }
}

main().catch((error: unknown) => {
  console.error(
    "Inbox Agent failed:",
    error instanceof Error ? error.message : error
  );
  process.exitCode = 1;
});
