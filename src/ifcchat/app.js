// app.js
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

// ---- Provider switching ----

const PROVIDER_MODELS = {
    openai: ["gpt-5", "gpt-4.1"],
    anthropic: ["claude-sonnet-4-6", "claude-opus-4-6", "claude-haiku-4-5-20251001"],
};

const PROVIDER_LABELS = {
    openai: "OpenAI API key",
    anthropic: "Anthropic API key",
};

const PROVIDER_PLACEHOLDERS = {
    openai: "sk-...",
    anthropic: "sk-ant-...",
};

function getProvider() {
    return providerEl.value;
}

function updateProviderUI() {
    const provider = getProvider();
    $("apiKeyLabel").innerHTML = `${PROVIDER_LABELS[provider]}<span class="small">stored in browser memory; only sent to provider servers</span>`;
    apiKeyEl.placeholder = PROVIDER_PLACEHOLDERS[provider];

    // Enable/disable model optgroups and select first available model
    for (const [key, models] of Object.entries(PROVIDER_MODELS)) {
        const group = $(`modelGroup${key.charAt(0).toUpperCase() + key.slice(1)}`);
        if (!group) continue;
        const isActive = key === provider;
        group.disabled = !isActive;
        for (const opt of group.querySelectorAll("option")) {
            opt.disabled = !isActive;
        }
    }

    modelEl.value = PROVIDER_MODELS[provider][0];

    // Reset conversation on provider switch
    openaiInputItems = [];
    anthropicMessages = [];
}

providerEl.addEventListener("change", updateProviderUI);

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

    setStatus(isBusy ? (reason || "Working…") : "Ready");
}

function addMessage(role, text) {
    if (text.ok) {
        text = text.data;
    }
    const wrap = document.createElement("div");
    wrap.className = `msg ${role}`;
    wrap.innerHTML = `
    <div class="role ${role}">${role}</div>
    <div class="bubble"></div>`;
    const bubble = wrap.querySelector(".bubble");
    bubble.textContent = text;
    bubble.onclick = function () {
        if (bubble.scrollHeight > 100 && role === "tool") {
            bubble.style.maxHeight = bubble.style.maxHeight == 'none' ? '' : 'none';
            bubble.style.borderBottom = bubble.style.borderBottom == '' ? 'dotted 2px gray' : '';
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

// ---- Tool schemas (OpenAI Responses API format) ----
const tools = [
    {
        type: "function", name: "ifc_new", description: "Create a new empty IFC model in memory.",
        parameters: { type: "object", properties: { schema: { type: "string" } }, required: [], additionalProperties: false }
    },
    {
        type: "function", name: "ifc_summary", description: "Get a concise overview of the loaded IFC model.",
        parameters: { type: "object", properties: {}, required: [], additionalProperties: false }
    },
    {
        type: "function", name: "ifc_tree", description: "Get the full spatial hierarchy tree.",
        parameters: { type: "object", properties: {}, required: [], additionalProperties: false }
    },
    {
        type: "function", name: "ifc_select", description: "Select elements using ifcopenshell selector syntax (e.g. 'IfcWall').",
        parameters: { type: "object", properties: { query: { type: "string" } }, required: ["query"], additionalProperties: false }
    },
    {
        type: "function", name: "ifc_info", description: "Inspect an entity by STEP id.",
        parameters: { type: "object", properties: { element_id: { type: "integer" } }, required: ["element_id"], additionalProperties: false }
    },
    {
        type: "function", name: "ifc_relations", description: "Get relationships for an element. traverse='up' walks to IfcProject.",
        parameters: {
            type: "object", properties: { element_id: { type: "integer" }, traverse: { type: "string" } },
            required: ["element_id"], additionalProperties: false
        }
    },
    {
        type: "function", name: "ifc_clash", description: "Run clash/clearance checks for an element.",
        parameters: {
            type: "object", properties: { element_id: { type: "integer" }, clearance: { type: "number" }, tolerance: { type: "number" }, scope: { type: "string" } },
            required: ["element_id"], additionalProperties: false
        }
    },
    {
        type: "function", name: "ifc_list", description: "List ifcopenshell.api modules or functions within a module.",
        parameters: { type: "object", properties: { module: { type: "string" } }, required: [], additionalProperties: false }
    },
    {
        type: "function", name: "ifc_docs", description: "Get documentation for an ifcopenshell.api function, 'module.function'.",
        parameters: { type: "object", properties: { function_path: { type: "string" } }, required: ["function_path"], additionalProperties: false }
    },
    {
        type: "function", name: "ifc_edit", description: "Execute an ifcopenshell.api mutation; params is a JSON string of stringly-typed kwargs.",
        parameters: { type: "object", properties: { function_path: { type: "string" }, params: { type: "string" } }, required: ["function_path"], additionalProperties: false }
    },
    {
        type: "function", name: "ifc_validate", description: "Validate the loaded model. Returns valid bool and list of issues.",
        parameters: { type: "object", properties: { express_rules: { type: "boolean" } }, required: [], additionalProperties: false }
    },
    {
        type: "function", name: "ifc_schedule", description: "List work schedules and nested tasks. Use max_depth=1 for top-level phases only on large projects.",
        parameters: { type: "object", properties: { max_depth: { type: "integer" } }, required: [], additionalProperties: false }
    },
    {
        type: "function", name: "ifc_cost", description: "List cost schedules and nested cost items. Use max_depth=1 for top-level sections only on large BoQs.",
        parameters: { type: "object", properties: { max_depth: { type: "integer" } }, required: [], additionalProperties: false }
    },
    {
        type: "function", name: "ifc_schema", description: "Return IFC class documentation for an entity type.",
        parameters: { type: "object", properties: { entity_type: { type: "string" } }, required: ["entity_type"], additionalProperties: false }
    },
    {
        type: "function", name: "ifc_quantify", description: "Run quantity take-off (QTO) on the model. Modifies model in-place; call ifc_save() after.",
        parameters: { type: "object", properties: { rule: { type: "string" }, selector: { type: "string" } }, required: ["rule"], additionalProperties: false }
    },
];

// Convert OpenAI tool format to Anthropic tool format
function toolsForAnthropic() {
    return tools.map((t) => ({
        name: t.name,
        description: t.description,
        input_schema: t.parameters,
    }));
}

const SYSTEM_INSTRUCTIONS = `
You are an IFC copilot running in a browser. You can call tools to inspect or modify the currently loaded IFC model.
Rules:
- If the user asks about model contents (counts, lists, properties, hierarchy), use tools like ifc_summary/ifc_select/ifc_info/ifc_tree.
- If the user asks to change the model, prefer: (1) ifc_list to find candidate API modules, (2) ifc_docs for the exact function signature, then (3) ifc_edit.
- If there is no model and the user wants to create one, call ifc_new.
- After edits, explain what changed and suggest downloading the IFC.
Be concise. Avoid dumping huge trees unless asked.
`;

// ---- OpenAI state ----
let openaiInputItems = [];

// ---- Anthropic state ----
let anthropicMessages = [];

// ============================================================
// OpenAI Responses API
// ============================================================

async function openAIResponsesCreate({ apiKey, model, input, tools }) {
    const res = await fetch("https://api.openai.com/v1/responses", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
            model,
            instructions: SYSTEM_INSTRUCTIONS,
            tools,
            input,
        }),
    });

    if (!res.ok) {
        const text = await res.text();
        throw new Error(`OpenAI error ${res.status}: ${text}`);
    }
    return await res.json();
}

function extractAssistantTextOpenAI(response) {
    const out = [];
    for (const item of response.output ?? []) {
        if (item.type === "message" && item.role === "assistant") {
            for (const c of item.content ?? []) {
                if (c.type === "output_text") out.push(c.text);
            }
        }
    }
    return out.join("\n").trim();
}

async function runOpenAITurn(userText) {
    const apiKey = apiKeyEl.value.trim();
    if (!apiKey) throw new Error("Missing API key");

    openaiInputItems.push({ role: "user", content: userText });

    for (let i = 0; i < 64; i++) {
        const response = await openAIResponsesCreate({
            apiKey,
            model: modelEl.value,
            input: openaiInputItems,
            tools,
        });

        openaiInputItems.push(...(response.output ?? []));

        const text = extractAssistantTextOpenAI(response);
        if (text) addMessage("assistant", text);

        const calls = (response.output ?? []).filter((x) => x.type === "function_call");
        if (calls.length === 0) return;

        for (const call of calls) {
            let args = {};
            try { args = call.arguments ? JSON.parse(call.arguments) : {}; }
            catch { args = {}; }

            addMessage("tool", `→ ${call.name}(${JSON.stringify(args)})`);

            const toolRes = await callWorker("toolCall", { name: call.name, args });

            openaiInputItems.push({
                type: "function_call_output",
                call_id: call.call_id,
                output: JSON.stringify(toolRes.result),
            });

            addMessage("tool", `← ${call.name}: ${JSON.stringify(toolRes.result, null, 2)}`);
        }
    }

    addMessage("assistant", "I hit the tool-call loop limit. Try narrowing your request.");
}

// ============================================================
// Anthropic Messages API
// ============================================================

async function anthropicMessagesCreate({ apiKey, model, system, messages, tools }) {
    const res = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "x-api-key": apiKey,
            "anthropic-version": "2023-06-01",
            "anthropic-dangerous-direct-browser-access": "true",
        },
        body: JSON.stringify({
            model,
            max_tokens: 4096,
            system,
            tools,
            messages,
        }),
    });

    if (!res.ok) {
        const text = await res.text();
        throw new Error(`Anthropic error ${res.status}: ${text}`);
    }
    return await res.json();
}

function extractAssistantTextAnthropic(response) {
    const out = [];
    for (const block of response.content ?? []) {
        if (block.type === "text") out.push(block.text);
    }
    return out.join("\n").trim();
}

async function runAnthropicTurn(userText) {
    const apiKey = apiKeyEl.value.trim();
    if (!apiKey) throw new Error("Missing API key");

    anthropicMessages.push({ role: "user", content: userText });

    const claudeTools = toolsForAnthropic();

    for (let i = 0; i < 64; i++) {
        const response = await anthropicMessagesCreate({
            apiKey,
            model: modelEl.value,
            system: SYSTEM_INSTRUCTIONS,
            messages: anthropicMessages,
            tools: claudeTools,
        });

        // Show any assistant text
        const text = extractAssistantTextAnthropic(response);
        if (text) addMessage("assistant", text);

        // Append the full assistant response to conversation history
        anthropicMessages.push({ role: "assistant", content: response.content });

        // Check for tool use
        const toolUseBlocks = (response.content ?? []).filter((b) => b.type === "tool_use");
        if (response.stop_reason !== "tool_use" || toolUseBlocks.length === 0) return;

        // Execute each tool call and collect results
        const toolResultBlocks = [];
        for (const toolUse of toolUseBlocks) {
            const args = toolUse.input ?? {};

            addMessage("tool", `→ ${toolUse.name}(${JSON.stringify(args)})`);

            let resultContent;
            try {
                const toolRes = await callWorker("toolCall", { name: toolUse.name, args });
                resultContent = JSON.stringify(toolRes.result);
            } catch (e) {
                resultContent = JSON.stringify({ error: e.message });
            }

            toolResultBlocks.push({
                type: "tool_result",
                tool_use_id: toolUse.id,
                content: resultContent,
            });

            addMessage("tool", `← ${toolUse.name}: ${resultContent}`);
        }

        // Feed all tool results back as a single user message
        anthropicMessages.push({ role: "user", content: toolResultBlocks });
    }

    addMessage("assistant", "I hit the tool-call loop limit. Try narrowing your request.");
}

// ============================================================
// Unified agent turn
// ============================================================

async function runAgentTurn(userText) {
    if (getProvider() === "anthropic") {
        return runAnthropicTurn(userText);
    }
    return runOpenAITurn(userText);
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
        setBusy(true, "Error");
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
        updateProviderUI();
        setBusy(false, "Ready");
    } catch (e) {
        setBusy(true, "Error");
        addMessage("assistant", `Worker init failed: ${e.message}`);
    }
})();
