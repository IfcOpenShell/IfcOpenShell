/**
 * WASM module
 * Exposes an API that abstracts the underlying WASM thread
 */

import hyperid from "hyperid";
import EventEmitter from "eventemitter3";
import type { WorkerResponse } from "$src/types/wasm";

// Message types
export const MessageType = {
    // Initialize the WASM module
    INIT: 'init',

    // API call
    API_CALL: 'api_call',

    // Ready to serve API calls
    READY: 'ready',

    // API response
    API_RESPONSE: 'api_response',

    // Error
    ERROR: 'error',

    // WASM module disposed
    DISPOSED: 'disposed'
} as const;

type PendingMessage = {
    resolve: (value?: unknown) => void;
    reject: (reason?: unknown) => void;
};

type WasmReadyState = boolean | Promise<boolean>;

class WASMModule extends EventEmitter {
    id = hyperid();
    ready: WasmReadyState = false;
    worker: Worker | null = null;
    pendingMessages = new Map<string, PendingMessage>();

    async init() {
        if (this.ready === true) return;
        if (this.ready instanceof Promise) return this.ready;

        this.worker = new Worker(new URL('./worker/worker.ts', import.meta.url), {type: 'module'});

        this.worker.onmessage = (event: MessageEvent<WorkerResponse>) => {
            this._handleWorkerMessage(event.data);
        };

        this.worker.onerror = (error: ErrorEvent) => {
            console.error('[WASM] Web worker error:', error);
            this._rejectPendingMessages(error);
        };

        this.ready = this._sendMessage(MessageType.INIT)
            .then(() => true)
            .catch((error) => {
                console.error('[WASM] Failed to initialize:', error);
                this.ready = false;
                throw error;
            });

        return this.ready;
    }

    async _sendMessage(type: string, payload: Record<string, unknown> = {}): Promise<unknown> {
        const worker = this.worker;
        if (!worker) throw new Error('Worker not initialized');

        const id = this.id();

        return new Promise((resolve, reject) => {
            this.pendingMessages.set(id, { resolve, reject });
            
            worker.postMessage({
                type,
                payload,
                id
            });
        });
    }

    _handleWorkerMessage({ type, payload, id }: WorkerResponse) {
        const pendingMessage = this.pendingMessages.get(id);
        
        if (!pendingMessage) {
            console.warn('[WASM] Received response for unknown message ID:', id);
            return;
        }

        this.pendingMessages.delete(id);
        const { resolve, reject } = pendingMessage;

        switch (type) {
            case MessageType.READY:
                this.emit(MessageType.READY);
                resolve();
                break;
            case MessageType.API_RESPONSE:
                resolve(payload);
                break;
            case MessageType.ERROR: {
                const message =
                    payload && typeof payload === "object" && "message" in payload
                        ? String(payload.message)
                        : "Unknown worker error";
                reject(new Error(message));
                break;
            }
            default:
                console.warn('[WASM] Unknown message type:', type);
                reject(new Error(`Unknown message type: ${type}`));
        }
    }

    _rejectPendingMessages(error: unknown) {
        for (const { reject } of this.pendingMessages.values()) {
            reject(error);
        }
        this.pendingMessages.clear();
    }

    async _apiCall(method: string, ...args: unknown[]) {
        if (!this.ready) await this.init();

        const result = await this._sendMessage(MessageType.API_CALL, { method, args });
        return result;
    }

    /**
     * Get all entity classes in a given IFC schema
     */
    async getAllEntityClasses(schema: string) {
        return this._apiCall('getAllEntityClasses', schema);
    }

    /**
     * Get all data types in a given IFC schema
     */
    async getAllDataTypes(schema: string) {
        return this._apiCall('getAllDataTypes', schema);
    }

    /**
     * Get predefined types for a given IFC entity
     */
    async getPredefinedTypes(schema: string, entity: string) {
        return this._apiCall('getPredefinedTypes', schema, entity);
    }

    /**
     * Get all attributes for a given IFC entity
     */
    async getEntityAttributes(schema: string, entity: string) {
        return this._apiCall('getEntityAttributes', schema, entity);
    }

    /**
     * Get applicable property sets for a given IFC entity
     */
    async getApplicablePsets(schema: string, entity: string, predefinedType = '') {
        return this._apiCall('getApplicablePsets', schema, entity, predefinedType);
    }

    /**
     * Get standard material categories
     */
    async getMaterialCategories() {
        return this._apiCall('getMaterialCategories');
    }

    /**
     * Get standard classification systems
     */
    async getStandardClassificationSystems() {
        return this._apiCall('getStandardClassificationSystems');
    }

    /**
     * Load an IFC file. Returns a unique ID for the loaded file.
     */
    async loadIfc(ifcData: number[] | Uint8Array | ArrayBuffer) {
        return this._apiCall('loadIfc', ifcData);
    }

    /**
     * Unload an IFC file
     */
    async unloadIfc(ifcId: string) {
        return this._apiCall('unloadIfc', ifcId);
    }

    /**
     * Audit a loaded IFC file against IDS specifications
     */
    async auditIfc(ifcId: string, idsData: ArrayBuffer | Uint8Array | number[]) {
        const idsBytes = idsData instanceof ArrayBuffer ? new Uint8Array(idsData) : idsData;

        return this._apiCall('auditIfc', ifcId, Array.from(idsBytes));
    }

    // IDS API Methods

    /**
     * Create a new IDS instance
     */
    async createIDS() {
        return this._apiCall('createIDS');
    }

    /**
     * Open an existing IDS from XML string
     */
    async openIDS(idsXml: string, validate = false) {
        return this._apiCall('openIDS', idsXml, validate);
    }

    /**
     * Create a specification
     */
    async createSpecification(options: Record<string, unknown> = {}) {
        return this._apiCall('createSpecification', options);
    }

    /**
     * Create an entity facet
     */
    async createEntityFacet(clause: string, options: Record<string, unknown> = {}) {
        return this._apiCall('createEntityFacet', clause, options);
    }

    /**
     * Create an attribute facet
     */
    async createAttributeFacet(clause: string, options: Record<string, unknown> = {}) {
        return this._apiCall('createAttributeFacet', clause, options);
    }

    /**
     * Create a property facet
     */
    async createPropertyFacet(clause: string, options: Record<string, unknown> = {}) {
        return this._apiCall('createPropertyFacet', clause, options);
    }

    /**
     * Create a material facet
     */
    async createMaterialFacet(clause: string, options: Record<string, unknown> = {}) {
        return this._apiCall('createMaterialFacet', clause, options);
    }

    /**
     * Create a classification facet
     */
    async createClassificationFacet(clause: string, options: Record<string, unknown> = {}) {
        return this._apiCall('createClassificationFacet', clause, options);
    }

    /**
     * Create a part-of facet
     */
    async createPartOfFacet(clause: string, options: Record<string, unknown> = {}) {
        return this._apiCall('createPartOfFacet', clause, options);
    }

    /**
     * Validate an IDS object
     */
    async validateIDS(idsObj: Record<string, unknown>) {
        return await this._apiCall('validateIDS', idsObj);
    }

    /**
     * Export IDS instance to XML string
     */
    async exportIDS(idsObj: Record<string, unknown>) {
        return this._apiCall('exportIDS', idsObj);
    }

    async _cleanupWorker() {
        return this._apiCall('internal.cleanup', {});
    }

    /**
     * Cleanup resources
     */
    async dispose() {
        if (this.worker) {
            await this._cleanupWorker();
            this.worker.terminate();
            this.worker = null;
        }
        this.ready = false;
        this._rejectPendingMessages(new Error('WASM module disposed'));
        this.emit(MessageType.DISPOSED);
    }
}

// Export singleton instance
const wasm = new WASMModule();

export const {
    init,
    getAllEntityClasses,
    getAllDataTypes,
    getPredefinedTypes,
    getEntityAttributes,
    getApplicablePsets,
    getMaterialCategories,
    getStandardClassificationSystems,
    loadIfc,
    unloadIfc,
    auditIfc,
    createIDS,
    openIDS,
    createSpecification,
    createEntityFacet,
    createAttributeFacet,
    createPropertyFacet,
    createMaterialFacet,
    createClassificationFacet,
    createPartOfFacet,
    validateIDS,
    exportIDS,
    dispose
} = wasm;

export default wasm;
