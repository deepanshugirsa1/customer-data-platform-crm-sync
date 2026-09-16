/**
 * Writes connector output to JSONL for the Python sync orchestrator.
 * Simulates Airbyte "destination" handoff without requiring Airbyte runtime.
 */
import { writeFileSync, mkdirSync } from "node:fs";
import { getConnector } from "./index.js";

const source = process.argv[2] ?? "salesforce";
const object = process.argv[3] ?? "leads";
const outDir = process.argv[4] ?? "data/raw";

mkdirSync(outDir, { recursive: true });
const connector = getConnector(source);
const { records, nextCursor } = await connector.read(object, null);
const path = `${outDir}/${source}_${object}.jsonl`;
writeFileSync(path, records.map((r) => JSON.stringify(r)).join("\n") + "\n");
writeFileSync(
  `${outDir}/${source}_${object}.state.json`,
  JSON.stringify({ source, object, cursor: nextCursor }, null, 2)
);
console.log(`Wrote ${records.length} records to ${path}`);
