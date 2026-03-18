/**
 * WASM worker
*/

import { MessageType } from '../index';
import config from '../../../config.json';
import * as IDS from './ids';
import * as API from './api';
import type { ApiCallPayload, WorkerRequest } from "$src/types/wasm";

let pyodide: any = null;
let ready = false;

self.addEventListener('message', async (event: MessageEvent<WorkerRequest>) => {
    console.log("[worker] Received message:", event.data);
    const { type, payload, id } = event.data;

    try {
        switch (type) {
            case MessageType.INIT:
                await initEnvironment();
                self.postMessage({
                    type: MessageType.READY,
                    payload: { success: true },
                    id
                });
                break;

            case MessageType.API_CALL: {
                if (!ready) {
                    throw new Error('[worker] Pyodide not initialized');
                }
                if (!payload) {
                    throw new Error('[worker] Missing payload for API call');
                }
                const result = await handleApiCall(payload as ApiCallPayload);
                self.postMessage({
                    type: MessageType.API_RESPONSE,
                    payload: result,
                    id
                });
                break;
            }

            default:
                throw new Error(`[worker] Unknown message type: ${type}`);
        }
    } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        const stack = error instanceof Error ? error.stack : undefined;
        self.postMessage({
            type: MessageType.ERROR,
            payload: {
                message,
                stack
            },
            id
        });
    }
});

async function initEnvironment() {
    if (ready) return;

    // Load Pyodide
    const scriptUrl = new URL('/pyodide/pyodide.mjs', import.meta.url);
    const { loadPyodide } = await import(scriptUrl.href);
    pyodide = await loadPyodide({
        convertNullToNone: true
    });

    // Load required packages
    await pyodide.loadPackage('micropip');
    await pyodide.loadPackage('numpy');

    const micropip = pyodide.pyimport('micropip');

    // Install IfcOpenShell wheel
    await micropip.install(config.wasm.wheel_url);

    // Install IfcTester dependencies
    await micropip.install(config.wasm.odfpy_url);
    await pyodide.loadPackage("shapely");

    // Install IfcTester
    const ifctesterManifest = await fetch('/worker/generated/ifctester.json').then((response) => {
        if (!response.ok) {
            throw new Error(`[worker] Failed to load IfcTester wheel manifest: ${response.status} ${response.statusText}`);
        }
        return response.json() as Promise<{ wheel_url: string }>;
    });
    await micropip.install(ifctesterManifest.wheel_url);

    // Initialize IDS and API
    await API.init(pyodide);
    await IDS.init(pyodide);

    console.log("[worker] Environment initialized");

    ready = true;
}

async function cleanupEnvironment() {
    ready = false;
    pyodide = null;
    console.log("[worker] Closed environment");
}

async function handleApiCall({ method, args = [] }: ApiCallPayload) {
    if (method === 'internal.cleanup') {
        await cleanupEnvironment();
        return true;
    }

    if (method in API.API) {
        return await (API.API as Record<string, (...params: unknown[]) => unknown>)[method](...args);
    }
    if (method in IDS.API) {
        return await (IDS.API as Record<string, (...params: unknown[]) => unknown>)[method](...args);
    }
    throw new Error(`[worker] Unknown API method: ${method}`);
}
