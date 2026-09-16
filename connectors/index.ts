import { SalesforceConnector } from "./salesforce.js";
import { HubSpotConnector } from "./hubspot.js";
import type { Connector } from "./types.js";

export function getConnector(name: string): Connector {
  switch (name) {
    case "salesforce":
      return new SalesforceConnector();
    case "hubspot":
      return new HubSpotConnector();
    default:
      throw new Error(`Unknown connector: ${name}`);
  }
}

export * from "./types.js";
export * from "./salesforce.js";
export * from "./hubspot.js";
