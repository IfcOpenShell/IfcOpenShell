export type WorkerMessageType =
    | "init"
    | "api_call"
    | "ready"
    | "api_response"
    | "error"
    | "disposed";

export type WorkerRequest = {
    type: WorkerMessageType;
    payload?: Record<string, unknown>;
    id: string;
};

export type WorkerResponse = {
    type: WorkerMessageType;
    payload?: Record<string, unknown>;
    id: string;
};

export type ApiCallPayload = {
    method: string;
    args?: unknown[];
};
