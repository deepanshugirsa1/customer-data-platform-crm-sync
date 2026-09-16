import { BaseConnector } from "./base.js";
import type { ConnectorRecord } from "./types.js";

/** Mock Salesforce connector — swap HTTP calls for live OAuth in production. */
export class SalesforceConnector extends BaseConnector {
  name = "salesforce";

  async listObjects(): Promise<string[]> {
    return ["leads", "accounts", "contacts"];
  }

  async read(object: string, cursor: string | null) {
    const now = new Date().toISOString();
    const records: ConnectorRecord[] = [
      {
        id: `sf-${object}-001`,
        object,
        source: this.name,
        payload: {
          Email: "alex@acme.io",
          Company: "Acme",
          Phone: "+1-415-555-0100",
          Status: "Open",
        },
        updatedAt: now,
      },
      {
        id: `sf-${object}-002`,
        object,
        source: this.name,
        payload: {
          Email: "jordan@globex.com",
          Company: "Globex",
          Phone: "+1-628-555-0199",
          Status: "Working",
        },
        updatedAt: now,
      },
    ];
    const filtered = cursor
      ? records.filter((r) => r.updatedAt > cursor)
      : records;
    return { records: filtered, nextCursor: now };
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const c = new SalesforceConnector();
  c.read("leads", null).then((r) => console.log(JSON.stringify(r, null, 2)));
}
