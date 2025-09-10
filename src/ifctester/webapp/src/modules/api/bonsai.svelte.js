import { io } from 'socket.io-client';
import { IFCModels } from './api.svelte.js';
import * as IDS from './ids.svelte.js';
import { error, success } from '../utils/toast.svelte.js';
import hyperid from 'hyperid';
import { onMount } from 'svelte';

// Bonsai connection state
export let Bonsai = $state({
    enabled: false,
    port: null,
    socket: null,
    connected: false,
    auditing: false
});

const id = hyperid();
const pendingAudits = new Map();

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
export const connect = () => new Promise((resolve, reject) => {
    if (!Bonsai.port) return;
    
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
        
        Bonsai.socket.on('connect_error', (err) => {
            Bonsai.connected = false;
            error(`Failed to connect to Bonsai: ${err.message}`);
            reject(err);
        });
        
        Bonsai.socket.on('audit_result', handleAuditResult);
        Bonsai.socket.on('error', handleAuditError);
        
    } catch (err) {
        error(`Failed to connect to Bonsai: ${err.message}`);
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
        
        const requestId = id();
        
        return new Promise((resolve, reject) => {
            // Store request with resolve/reject functions
            pendingAudits.set(requestId, { resolve, reject });
            
            Bonsai.socket.emit('audit_ids', {
                id: requestId,
                ids: idsXml
            });
        });
        
    } catch (err) {
        Bonsai.auditing = false;
        error(`Failed to run Bonsai audit: ${err.message}`);
        return null;
    }
};

/**
 * Handles audit results from Bonsai server
 * @param {Object} data - Audit result data
 */
const handleAuditResult = (data) => {
    if (!data.id || !data.json_report) return;
    
    const pendingAudit = pendingAudits.get(data.id);
    if (!pendingAudit) {
        console.warn('[Bonsai] Received response for unknown audit ID:', data.id);
        return;
    }
    
    pendingAudits.delete(data.id);
    const { resolve } = pendingAudit;
    
    try {
        const reportData = JSON.parse(data.json_report);
        
        const auditReport = {
            id: data.id,
            date: new Date().toISOString(),
            modelName: 'Bonsai IFC Model',
            document: IDS.Module.activeDocument,
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
        error(`Failed to process audit result: ${err.message}`);
        resolve(null);
    }
};

/**
 * Handles audit errors from Bonsai server
 * @param {Object} data - Error data
 */
const handleAuditError = (data) => {
    if (!data.id) return;
    
    const pendingAudit = pendingAudits.get(data.id);
    if (!pendingAudit) {
        console.warn('[Bonsai] Received error for unknown audit ID:', data.id);
        return;
    }
    
    pendingAudits.delete(data.id);
    const { resolve } = pendingAudit;
    
    Bonsai.auditing = false;
    error(`Audit failed (Bonsai): ${data.error}`);
    resolve(null);
};

