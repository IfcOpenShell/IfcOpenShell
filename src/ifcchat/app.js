// app.js
import * as openaiApi from "./api_openai.js";
import * as openrouterApi from "./api_openrouter.js";

const PROVIDERS = {
    openai: {
        api: openaiApi,
        models: [
            { 
                value: "gpt-5",      
                label: "gpt-5" 
            },
            { 
                value: "gpt-4.1",      
                label: "gpt-4.1" 
            },
        ],
    },
    openrouter: {
        api: openrouterApi,
        models: [
            { 
                value: "openai/gpt-oss-20b",                
                label: "gpt-oss-20b" 
            },
            { 
                value: "anthropic/claude-sonnet-4-5",       
                label: "claude-sonnet-4-5" 
            },
            { 
                value: "openai/gpt-4.1",                    
                label: "gpt-4.1" 
            },
            { 
                value: "google/gemini-2.5-pro-preview",     
                label: "gemini-2.5-pro" 
            },
        ],
    },
};

const $ = (id) => document.getElementById(id);

const statusEl = $("status");
const msgsEl = $("msgs");
const sendBtn = $("send");
const inputEl = $("input");
const apiKeyEl = $("apiKey");
const modelEl = $("model");
const providerEl = $("provider");
const ifcFileEl = $("ifcFile");
const newBtn = $("newModel");
const downloadBtn = $("downloadIfc");

function onProviderChange() {
    const p = PROVIDERS[providerEl.value];
    modelEl.innerHTML = p.models.map(m => `<option value="${m.value}">${m.label}</option>`).join("");
}

providerEl.addEventListener("change", onProviderChange);
onProviderChange();

function setBusy(isBusy, reason = "") {
    const controls = [
        $("send"),
        $("newModel"),
        $("downloadIfc"),
        $("ifcFile"),
    ];

    for (const el of controls) el.disabled = isBusy;

    $("input").disabled = isBusy;

    const browseBtn = $("browseBtn");
    if (browseBtn) {
        browseBtn.classList.toggle("disabled", isBusy);
        browseBtn.setAttribute("aria-disabled", isBusy ? "true" : "false");
        browseBtn.tabIndex = isBusy ? -1 : 0;
    }

    sendBtn.innerHTML = isBusy
        ? `<span class="spinner"></span>`
        : `Send <span class="material-icons">send</span>`;

    setStatus(isBusy ? (reason || "Working…") : "Ready");
}

function addMessage(role, text) {
    if (text.ok) {
        text = text.data;
    }
    const wrap = document.createElement("div");
    wrap.className = `msg ${role}`;
    wrap.innerHTML = `
    <div class="role ${role}">${role}${role === "tool" ? '<span class="chevron">▶</span>' : ''}</div>
    <div class="bubble"></div>`;
    const bubble = wrap.querySelector(".bubble");
    bubble.textContent = text;
    bubble.onclick = function () {
        if (bubble.scrollHeight > 100 && role === "tool") {
            const expanded = bubble.style.maxHeight === 'none';
            bubble.style.maxHeight = expanded ? '' : 'none';
            bubble.style.borderBottom = expanded ? '' : 'dotted 2px gray';
            wrap.querySelector(".chevron").style.transform = expanded ? '' : 'rotate(90deg)';
        }
    }
    msgsEl.appendChild(wrap);
    msgsEl.scrollTop = msgsEl.scrollHeight;
}

function setStatus(text) {
    statusEl.textContent = text;
}

const worker = new Worker("./ifc_worker.js", { type: "module" });

function callWorker(type, payload = {}) {
    return new Promise((resolve, reject) => {
        const id = crypto.randomUUID();
        const onMsg = (ev) => {
            const msg = ev.data;
            if (!msg || msg.id !== id) return;
            worker.removeEventListener("message", onMsg);
            if (msg.ok) resolve(msg);
            else reject(new Error(msg.error || "Worker error"));
        };
        worker.addEventListener("message", onMsg);
        worker.postMessage({ id, type, payload });
    });
}

// ---- Tool schemas (should match ifcmcp.core openai_tools()) ----
const tools = [
    {
        type: "function", function: { name: "ifc_new", description: "Create a new empty IFC model in memory.",
        parameters: { type: "object", properties: { schema: { type: "string" } }, required: [], additionalProperties: false } }
    },
    {
        type: "function", function: { name: "ifc_summary", description: "Get a concise overview of the loaded IFC model.",
        parameters: { type: "object", properties: {}, required: [], additionalProperties: false } }
    },
    {
        type: "function", function: { name: "ifc_tree", description: "Get the full spatial hierarchy tree.",
        parameters: { type: "object", properties: {}, required: [], additionalProperties: false } }
    },
    {
        type: "function", function: { name: "ifc_select", description: "Select elements using ifcopenshell selector syntax (e.g. 'IfcWall').",
        parameters: { type: "object", properties: { query: { type: "string" } }, required: ["query"], additionalProperties: false } }
    },
    {
        type: "function", function: { name: "ifc_info", description: "Inspect an entity by STEP id.",
        parameters: { type: "object", properties: { element_id: { type: "integer" } }, required: ["element_id"], additionalProperties: false } }
    },
    {
        type: "function", function: { name: "ifc_relations", description: "Get relationships for an element. traverse='up' walks to IfcProject.",
        parameters: {
            type: "object", properties: { element_id: { type: "integer" }, traverse: { type: "string" } },
            required: ["element_id"], additionalProperties: false
        } }
    },
    {
        type: "function", function: { name: "ifc_clash", description: "Run clash/clearance checks for an element.",
        parameters: {
            type: "object", properties: { element_id: { type: "integer" }, clearance: { type: "number" }, tolerance: { type: "number" }, scope: { type: "string" } },
            required: ["element_id"], additionalProperties: false
        } }
    },
    {
        type: "function", function: { name: "ifc_list", description: "List ifcopenshell.api modules or functions within a module.",
        parameters: { type: "object", properties: { module: { type: "string" } }, required: [], additionalProperties: false } }
    },
    {
        type: "function", function: { name: "ifc_docs", description: "Get documentation for an ifcopenshell.api function, 'module.function'.",
        parameters: { type: "object", properties: { function_path: { type: "string" } }, required: ["function_path"], additionalProperties: false } }
    },
    {
        type: "function", function: { name: "ifc_edit", description: "Execute an ifcopenshell.api mutation; params is a JSON string of stringly-typed kwargs.",
        parameters: { type: "object", properties: { function_path: { type: "string" }, params: { type: "string" } }, required: ["function_path"], additionalProperties: false } }
    },
    {
        type: "function", function: { name: "ifc_validate", description: "Validate the loaded model. Returns valid bool and list of issues.",
        parameters: { type: "object", properties: { express_rules: { type: "boolean" } }, required: [], additionalProperties: false } }
    },
    {
        type: "function", function: { name: "ifc_schedule", description: "List work schedules and nested tasks. Use max_depth=1 for top-level phases only on large projects.",
        parameters: { type: "object", properties: { max_depth: { type: "integer" } }, required: [], additionalProperties: false } }
    },
    {
        type: "function", function: { name: "ifc_cost", description: "List cost schedules and nested cost items. Use max_depth=1 for top-level sections only on large BoQs.",
        parameters: { type: "object", properties: { max_depth: { type: "integer" } }, required: [], additionalProperties: false } }
    },
    {
        type: "function", function: { name: "ifc_schema", description: "Return IFC class documentation for an entity type.",
        parameters: { type: "object", properties: { entity_type: { type: "string" } }, required: ["entity_type"], additionalProperties: false } }
    },
    {
        type: "function", function: { name: "ifc_quantify", description: "Run quantity take-off (QTO) on the model. Modifies model in-place; call ifc_save() after.",
        parameters: { type: "object", properties: { rule: { type: "string" }, selector: { type: "string" } }, required: ["rule"], additionalProperties: false } }
    },
];

const SYSTEM_INSTRUCTIONS = `
You are an IFC copilot running in a browser. You can call tools to inspect or modify the currently loaded IFC model.
Rules:
- If the user asks about model contents (counts, lists, properties, hierarchy), use tools like ifc_summary/ifc_select/ifc_info/ifc_tree.
- If the user asks to change the model, prefer: (1) ifc_list to find candidate API modules, (2) ifc_docs for the exact function signature, then (3) ifc_edit.
- If there is no model and the user wants to create one, call ifc_new.
- After edits, explain what changed and suggest downloading the IFC.
Be concise. Avoid dumping huge trees unless asked.
`;

let messages = []; // running conversation state (Chat Completions style)

async function runAgentTurn(userText) {
    const apiKey = apiKeyEl.value.trim();
    if (!apiKey) throw new Error("Missing API key");

    const { chat } = PROVIDERS[providerEl.value].api;

    messages.push({ role: "user", content: userText });

    for (let i = 0; i < 64; i++) {
        const response = await chat({
            apiKey,
            model: modelEl.value,
            messages: [{ role: "system", content: SYSTEM_INSTRUCTIONS }, ...messages],
            tools,
        });

        const message = response.choices?.[0]?.message;
        if (!message) throw new Error("No message in response");

        messages.push(message);

        if (message.content) addMessage("assistant", message.content);

        const calls = message.tool_calls ?? [];
        if (calls.length === 0) return;

        for (const call of calls) {
            let args = {};
            try { args = call.function.arguments ? JSON.parse(call.function.arguments) : {}; }
            catch { args = {}; }

            addMessage("tool", `→ ${call.function.name}(${JSON.stringify(args)})`);

            const toolRes = await callWorker("toolCall", { name: call.function.name, args });

            messages.push({
                role: "tool",
                tool_call_id: call.id,
                content: JSON.stringify(toolRes.result),
            });

            addMessage("tool", `← ${call.function.name}: ${JSON.stringify(toolRes.result, null, 2)}`);
        }
    }

    addMessage("assistant", "I hit the tool-call loop limit. Try narrowing your request.");
}

sendBtn.onclick = async () => {
    const text = inputEl.value.trim();
    if (!text) return;
    inputEl.value = "";
    addMessage("user", text);
    try {
        setBusy(true, "Thinking…");
        await runAgentTurn(text);
        setBusy(false, "Ready");
    } catch (e) {
        setBusy(false, "Error");
        addMessage("assistant", `Error: ${e.message}`);
    }
};

inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendBtn.click();
    }
});

ifcFileEl.onchange = async () => {
    const f = ifcFileEl.files?.[0];
    if (!f) return;
    setBusy(true, "Loading IFC into Pyodide…");
    const buf = await f.arrayBuffer();
    try {
        const r = await callWorker("loadIfc", { filename: f.name, bytes: buf }, [buf]);
        addMessage("assistant", r.result);
        setBusy(false, "Ready");
    } catch (e) {
        setStatus(true, "Error");
        addMessage("assistant", `Load error: ${e.message}`);
    }
};

newBtn.onclick = async () => {
    try {
        setBusy(true, "Creating new model…");
        const r = await callWorker("toolCall", { name: "ifc_new", args: { schema: "IFC4" } });
        addMessage("assistant", `New model: ${JSON.stringify(r.result)}`);
        setBusy(false, "Ready");
    } catch (e) {
        setBusy(true, "Error");
        addMessage("assistant", `Error: ${e.message}`);
    }
};

downloadBtn.onclick = async () => {
    try {
        setBusy(true, "Exporting IFC…");
        const r = await callWorker("exportIfc", {});
        const blob = new Blob([r.bytes], { type: "application/octet-stream" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = r.filename || "model.ifc";
        a.click();
        URL.revokeObjectURL(url);
        setBusy(false, "Ready");
    } catch (e) {
        setBusy(true, "Error");
        addMessage("assistant", `Export error: ${e.message}`);
    }
};

(async () => {
    try {
        setBusy(true, "Initializing Pyodide and IfcOpenShell for in-memory IFC access…");
        await callWorker("init", {});
        setBusy(false, "Ready");
    } catch (e) {
        setBusy(true, "Error");
        addMessage("assistant", `Worker init failed: ${e.message}`);
    }
})();