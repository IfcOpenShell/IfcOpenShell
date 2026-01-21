import { io } from 'socket.io-client';
import type { Socket } from 'socket.io-client';
import { IFCModels } from './api.svelte';
import * as IDS from './ids.svelte';
import { error, success } from '../utils/toast.svelte';
import hyperid from 'hyperid';
import type { AuditReport, AuditReportData } from "$src/types/report";

// Bonsai connection state
type BonsaiState = {
    enabled: boolean;
    port: string | null;
    socket: Socket | null;
    connected: boolean;
    auditing: boolean;
};

type PendingAudit = {
    resolve: (value: string | null) => void;
    reject: (reason?: unknown) => void;
};

type AuditResultPayload = {
    id?: string;
    json_report?: string;
    html_report?: string;
};

type AuditErrorPayload = {
    id?: string;
    error?: string;
};

export const Bonsai: BonsaiState = $state({
    enabled: false,
    port: null,
    socket: null,
    connected: false,
    auditing: false
});

const id: () => string = hyperid();
const pendingAudits = new Map<string, PendingAudit>();

// Check for Bonsai server port in URL parameters
const urlParams = new URLSearchParams(window.location.search);
const serverPort = urlParams.get('bonsai_server');

if (serverPort) {
    Bonsai.enabled = true;
    Bonsai.port = serverPort;
}

/**
 * Connect to Bonsai server
 */
export const connect = () => new Promise<void>((resolve, reject) => {
    if (!Bonsai.port) {
        resolve();
        return;
    }
    
    try {
        Bonsai.socket = io(`ws://127.0.0.1:${Bonsai.port}/ifctester`, {
            transports: ['websocket'],
            reconnection: false,
            timeout: 5000
        });
        
        Bonsai.socket.on('connect', () => {
            Bonsai.connected = true;
            success('Connected to Bonsai');
            resolve();
        });
        
        Bonsai.socket.on('disconnect', () => {
            Bonsai.connected = false;
        });
        
        Bonsai.socket.on('connect_error', (err: Error) => {
            Bonsai.connected = false;
            error(`Failed to connect to Bonsai: ${err.message}`);
            reject(err);
        });
        
        Bonsai.socket.on('audit_result', handleAuditResult);
        Bonsai.socket.on('error', handleAuditError);
        
    } catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        error(`Failed to connect to Bonsai: ${message}`);
        reject(err);
    }
});

/**
 * Disconnect from Bonsai server
 */
export const disconnect = () => {
    if (Bonsai.socket) {
        Bonsai.socket.disconnect();
        Bonsai.socket = null;
        Bonsai.connected = false;
        success('Disconnected from Bonsai');
    }
};

/**
 * Run audit using current IDS document against Bonsai's IFC model
 * @returns {Promise<string|null>} Returns audit ID when completed, null if failed
 */
export const runAudit = async () => {
    if (!Bonsai.socket || !Bonsai.connected || !IDS.Module.activeDocument) {
        return null;
    }
    
    try {
        Bonsai.auditing = true;
        
        const activeDoc = IDS.Module.documents[IDS.Module.activeDocument];
        if (!activeDoc) throw new Error('No active IDS document');
        
        // Convert IDS document to XML string
        const idsXml = await IDS.exportActiveDocument();
        if (!idsXml) {
            throw new Error('Failed to export IDS document');
        }
        
        const requestId = id();
        const socket = Bonsai.socket;
        if (!socket) {
            throw new Error('Bonsai socket not connected');
        }
        
        return new Promise<string | null>((resolve, reject) => {
            // Store request with resolve/reject functions
            pendingAudits.set(requestId, { resolve, reject });
            
            socket.emit('audit_ids', {
                id: requestId,
                ids: idsXml
            });
        });
        
    } catch (err) {
        Bonsai.auditing = false;
        const message = err instanceof Error ? err.message : String(err);
        error(`Failed to run Bonsai audit: ${message}`);
        return null;
    }
};

/**
 * Handles audit results from Bonsai server
 * @param {Object} data - Audit result data
 */
const handleAuditResult = (data: AuditResultPayload) => {
    if (!data.id || !data.json_report) return;
    
    const pendingAudit = pendingAudits.get(data.id);
    if (!pendingAudit) {
        console.warn('[Bonsai] Received response for unknown audit ID:', data.id);
        return;
    }
    
    pendingAudits.delete(data.id);
    const { resolve } = pendingAudit;
    
    try {
        const reportData = JSON.parse(data.json_report) as AuditReportData;
        
        const auditReport: AuditReport = {
            id: data.id,
            modelId: `bonsai:${data.id}`,
            date: new Date().toISOString(),
            modelName: 'Bonsai IFC Model',
            document: IDS.Module.activeDocument ?? "",
            data: reportData,
            htmlReport: data.html_report
        };
        
        // Store audit report
        IFCModels.audits.unshift(auditReport);
        
        Bonsai.auditing = false;
        success('Audit completed (Bonsai)');
        
        // Resolve promise with audit ID
        resolve(data.id);
        
    } catch (err) {
        Bonsai.auditing = false;
        const message = err instanceof Error ? err.message : String(err);
        error(`Failed to process audit result: ${message}`);
        resolve(null);
    }
};

/**
 * Handles audit errors from Bonsai server
 * @param {Object} data - Error data
 */
const handleAuditError = (data: AuditErrorPayload) => {
    if (!data.id) return;
    
    const pendingAudit = pendingAudits.get(data.id);
    if (!pendingAudit) {
        console.warn('[Bonsai] Received error for unknown audit ID:', data.id);
        return;
    }
    
    pendingAudits.delete(data.id);
    const { resolve } = pendingAudit;
    
    Bonsai.auditing = false;
    error(`Audit failed (Bonsai): ${data.error ?? "Unknown error"}`);
    resolve(null);
};
