import type { Connector, ConnectorRecord, SyncMode } from "./types.js";

export abstract class BaseConnector implements Connector {
  abstract name: string;
  abstract listObjects(): Promise<string[]>;
  abstract read(
    object: string,
    cursor: string | null
  ): Promise<{ records: ConnectorRecord[]; nextCursor: string | null }>;

  async sync(object: string, mode: SyncMode, cursor: string | null) {
    const effectiveCursor = mode === "full" ? null : cursor;
    return this.read(object, effectiveCursor);
  }
}
