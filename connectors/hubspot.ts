import { BaseConnector } from "./base.js";
import type { ConnectorRecord } from "./types.js";

/** Mock HubSpot connector — mirrors Airbyte HubSpot source shape. */
export class HubSpotConnector extends BaseConnector {
  name = "hubspot";

  async listObjects(): Promise<string[]> {
    return ["contacts", "companies", "deals"];
  }

  async read(object: string, cursor: string | null) {
    const now = new Date().toISOString();
    const records: ConnectorRecord[] = [
      {
        id: `hs-${object}-001`,
        object,
        source: this.name,
        payload: {
          email: "alex@acme.io",
          company: "Acme Inc",
          phone: "4155550100",
          lifecycleStage: "lead",
        },
        updatedAt: now,
      },
      {
        id: `hs-${object}-002`,
        object,
        source: this.name,
        payload: {
          email: "sam@initech.com",
          company: "Initech",
          phone: "5105550144",
          lifecycleStage: "opportunity",
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
