export type SyncMode = "full" | "incremental";

export interface ConnectorRecord {
  id: string;
  object: string;
  source: string;
  payload: Record<string, unknown>;
  updatedAt: string;
}

export interface SyncState {
  source: string;
  object: string;
  cursor: string | null;
  lastSyncedAt: string | null;
}

export interface Connector {
  name: string;
  listObjects(): Promise<string[]>;
  read(object: string, cursor: string | null): Promise<{
    records: ConnectorRecord[];
    nextCursor: string | null;
  }>;
}
