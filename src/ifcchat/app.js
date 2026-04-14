// app.js
import * as openaiApi from "./api_openai.js";
import * as anthropicApi from "./api_anthropic.js";
import * as openrouterApi from "./api_openrouter.js";

const PROVIDERS = {
    openai: {
        api: openaiApi,
        apiKeyLabel: "OpenAI API key",
        apiKeyPlaceholder: "sk-...",
        baseUrlLabel: "Base URL",
        baseUrlPlaceholder: "https://api.openai.com/v1",
        baseUrlDefault: "https://api.openai.com/v1",
        models: [
            {
                value: "gpt-5.2",
                label: "gpt-5.2"
            },
            {
                value: "gpt-5.2-chat-latest",
                label: "gpt-5.2-chat-latest"
            },
            {
                value: "gpt-5",
                label: "gpt-5"
            },
            {
                value: "gpt-5-chat-latest",
                label: "gpt-5-chat-latest"
            },
            {
                value: "gpt-5-mini",
                label: "gpt-5-mini"
            },
            {
                value: "gpt-5-nano",
                label: "gpt-5-nano"
            },
            {
                value: "gpt-4.1",
                label: "gpt-4.1"
            },
            {
                value: "gpt-4.1-mini",
                label: "gpt-4.1-mini"
            },
            {
                value: "gpt-4.1-nano",
                label: "gpt-4.1-nano"
            },
        ],
    },
    anthropic: {
        api: anthropicApi,
        apiKeyLabel: "Anthropic API key",
        apiKeyPlaceholder: "sk-ant-...",
        models: [
            {
                value: "claude-sonnet-4-6",
                label: "claude-sonnet-4-6"
            },
            {
                value: "claude-opus-4-6",
                label: "claude-opus-4-6"
            },
            {
                value: "claude-haiku-4-5-20251001",
                label: "claude-haiku-4-5"
            },
        ],
    },
    gemini: {
        api: openaiApi,
        apiKeyLabel: "Gemini API key",
        apiKeyPlaceholder: "AIza...",
        baseUrlLabel: "Base URL",
        baseUrlPlaceholder: "https://generativelanguage.googleapis.com/v1beta/openai/",
        baseUrlDefault: "https://generativelanguage.googleapis.com/v1beta/openai/",
        models: [
            {
                value: "gemini-3-flash-preview",
                label: "gemini-3-flash-preview"
            },
            {
                value: "gemini-2.5-flash",
                label: "gemini-2.5-flash"
            },
            {
                value: "gemini-2.5-pro",
                label: "gemini-2.5-pro"
            },
        ],
    },
    openrouter: {
        api: openrouterApi,
        apiKeyLabel: "OpenRouter API key",
        apiKeyPlaceholder: "sk-or-v1-...",
        baseUrlLabel: "Base URL",
        baseUrlPlaceholder: "https://openrouter.ai/api/v1",
        baseUrlDefault: "https://openrouter.ai/api/v1",
        models: [
            { 
                value: "openai/gpt-oss-20b",
                label: "gpt-oss-20b" 
            },
            { 
                value: "openai/gpt-oss-120b",
                label: "gpt-oss-120b" 
            },
            { 
                value: "mistralai/mistral-small-3.2-24b-instruct",
                label: "mistral-small-3.2" 
            },
            { 
                value: "openai/gpt-4.1",                    
                label: "gpt-4.1" 
            },
            { 
                value: "anthropic/claude-sonnet-4-5",       
                label: "claude-sonnet-4-5" 
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
const apiKeyLabelEl = $("apiKeyLabel");
const baseUrlRowEl = $("baseUrlRow");
const baseUrlLabelEl = $("baseUrlLabel");
const baseUrlEl = $("baseUrl");
const thinkingIndicatorEl = $("thinkingIndicator");
const compactingIndicatorEl = $("compactingIndicator");
const modelEl = $("model");
const providerEls = document.querySelectorAll('input[name="provider"]');
const ifcFileEl = $("ifcFile");
const newBtn = $("newModel");
const downloadBtn = $("downloadIfc");

function getProviderValue() {
    return document.querySelector('input[name="provider"]:checked')?.value || "openai";
}

function onProviderChange() {
    const provider = PROVIDERS[getProviderValue()];
    apiKeyLabelEl.innerHTML = `${provider.apiKeyLabel}<span class="small">stored in browser memory; only sent to provider servers</span>`;
    apiKeyEl.placeholder = provider.apiKeyPlaceholder;
    baseUrlRowEl.hidden = !provider.baseUrlDefault;
    if (provider.baseUrlDefault) {
        baseUrlLabelEl.innerHTML = `${provider.baseUrlLabel}<span class="small">override the API endpoint for OpenAI-compatible providers</span>`;
        baseUrlEl.placeholder = provider.baseUrlPlaceholder;
        baseUrlEl.value = provider.baseUrlDefault;
    } else {
        baseUrlEl.value = "";
        baseUrlEl.placeholder = "";
    }
    modelEl.innerHTML = provider.models.map(m => `<option value="${m.value}">${m.label}</option>`).join("");
}

for (const providerEl of providerEls) {
    providerEl.addEventListener("change", onProviderChange);
}
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

function escapeHtml(text) {
    return text
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function sanitizeUrl(url) {
    try {
        const parsed = new URL(url, window.location.href);
        if (["http:", "https:", "mailto:"].includes(parsed.protocol)) {
            return parsed.href;
        }
    } catch {
    }
    return null;
}

function renderInlineMarkdown(text) {
    const placeholders = [];
    const addPlaceholder = (html) => {
        const token = `@@MD${placeholders.length}@@`;
        placeholders.push({ token, html });
        return token;
    };

    let rendered = text;

    rendered = rendered.replace(/`([^`]+)`/g, (_, code) => addPlaceholder(`<code>${escapeHtml(code)}</code>`));
    rendered = rendered.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_, label, url) => {
        const href = sanitizeUrl(url);
        if (!href) {
            return `${label} (${url})`;
        }
        return addPlaceholder(
            `<a href="${escapeHtml(href)}" target="_blank" rel="noreferrer noopener">${escapeHtml(label)}</a>`
        );
    });

    rendered = escapeHtml(rendered);
    rendered = rendered.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    rendered = rendered.replace(/\*([^*]+)\*/g, "<em>$1</em>");
    rendered = rendered.replace(/_([^_]+)_/g, "<em>$1</em>");

    for (const placeholder of placeholders) {
        rendered = rendered.replaceAll(placeholder.token, placeholder.html);
    }

    return rendered;
}

function renderMarkdown(text) {
    const lines = String(text).replace(/\r\n?/g, "\n").split("\n");
    const html = [];
    let paragraphLines = [];
    let quoteLines = [];
    let listType = null;
    let listItems = [];

    const flushParagraph = () => {
        if (!paragraphLines.length) return;
        html.push(`<p>${renderInlineMarkdown(paragraphLines.join(" "))}</p>`);
        paragraphLines = [];
    };

    const flushQuote = () => {
        if (!quoteLines.length) return;
        const quoteBody = quoteLines.map((line) => renderInlineMarkdown(line)).join("<br />");
        html.push(`<blockquote><p>${quoteBody}</p></blockquote>`);
        quoteLines = [];
    };

    const flushList = () => {
        if (!listItems.length || !listType) return;
        const items = listItems.map((item) => `<li>${renderInlineMarkdown(item)}</li>`).join("");
        html.push(`<${listType}>${items}</${listType}>`);
        listType = null;
        listItems = [];
    };

    const flushAll = () => {
        flushParagraph();
        flushQuote();
        flushList();
    };

    for (let index = 0; index < lines.length; index++) {
        const line = lines[index];
        const trimmed = line.trim();

        if (trimmed.startsWith("```")) {
            flushAll();
            const language = trimmed.slice(3).trim();
            const codeLines = [];
            index += 1;
            while (index < lines.length && !lines[index].trim().startsWith("```")) {
                codeLines.push(lines[index]);
                index += 1;
            }
            const languageClass = language ? ` class="language-${escapeHtml(language)}"` : "";
            html.push(`<pre><code${languageClass}>${escapeHtml(codeLines.join("\n"))}</code></pre>`);
            continue;
        }

        if (!trimmed) {
            flushAll();
            continue;
        }

        const headingMatch = trimmed.match(/^(#{1,6})\s+(.+)$/);
        if (headingMatch) {
            flushAll();
            const level = headingMatch[1].length;
            html.push(`<h${level}>${renderInlineMarkdown(headingMatch[2])}</h${level}>`);
            continue;
        }

        const quoteMatch = trimmed.match(/^>\s?(.*)$/);
        if (quoteMatch) {
            flushParagraph();
            flushList();
            quoteLines.push(quoteMatch[1]);
            continue;
        }

        if (quoteLines.length) {
            flushQuote();
        }

        const unorderedListMatch = trimmed.match(/^[-*]\s+(.+)$/);
        if (unorderedListMatch) {
            flushParagraph();
            if (listType && listType !== "ul") {
                flushList();
            }
            listType = "ul";
            listItems.push(unorderedListMatch[1]);
            continue;
        }

        const orderedListMatch = trimmed.match(/^\d+\.\s+(.+)$/);
        if (orderedListMatch) {
            flushParagraph();
            if (listType && listType !== "ol") {
                flushList();
            }
            listType = "ol";
            listItems.push(orderedListMatch[1]);
            continue;
        }

        if (listItems.length) {
            flushList();
        }

        paragraphLines.push(trimmed);
    }

    flushAll();

    return html.join("");
}

function addMessage(role, text) {
    if (text.ok) {
        text = text.data;
    }
    if (typeof text !== "string") {
        text = JSON.stringify(text, null, 2);
    }
    const wrap = document.createElement("div");
    wrap.className = `msg ${role}`;
    wrap.innerHTML = `
    <div class="role ${role}">${role}${role === "tool" ? '<span class="chevron">▶</span>' : ''}</div>
    <div class="bubble"></div>`;
    const bubble = wrap.querySelector(".bubble");
    if (role === "assistant") {
        bubble.classList.add("markdown-content");
        bubble.innerHTML = renderMarkdown(text);
    } else {
        bubble.textContent = text;
    }
    bubble.onclick = function () {
        if (bubble.scrollHeight > 100 && role === "tool") {
            const expanded = bubble.style.maxHeight === 'none';
            bubble.style.maxHeight = expanded ? '' : 'none';
            bubble.style.borderBottom = expanded ? '' : 'dotted 2px gray';
            wrap.querySelector(".chevron").style.transform = expanded ? '' : 'rotate(90deg)';
        }
    }
    msgsEl.insertBefore(wrap, thinkingIndicatorEl);
    msgsEl.scrollTop = msgsEl.scrollHeight;
}

function setStatus(text) {
    statusEl.textContent = text;
    thinkingIndicatorEl.hidden = text !== "Thinking…";
    compactingIndicatorEl.hidden = text !== "Compacting…";
    msgsEl.scrollTop = msgsEl.scrollHeight;
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
        type: "function", function: { name: "ifc_new", description: "Create a new empty IFC model in memory. Valid schemas: IFC4, IFC2X3, IFC4X3 (for IFC 4.3).",
        parameters: { type: "object", properties: { schema: { type: "string", enum: ["IFC4", "IFC2X3", "IFC4X3"] } }, required: [], additionalProperties: false } }
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
- In case of type errors on api functions, retry providing values as strings (for example in the case of the matrix in geometry.edit_object_placement).
- After edits, explain what changed and suggest downloading the IFC.
Be concise. Avoid dumping huge trees unless asked.
`;

let messages = []; // running conversation state (Chat Completions style)

const MAX_TOOL_RESULT_CHARS = 0;
const MAX_HISTORY_MESSAGES = 40;
const ESTIMATED_CHARS_PER_TOKEN = 4;
const MAX_ESTIMATED_TOKENS_PER_MINUTE = 24000;
const COMPACT_WHEN_ESTIMATED_TOKENS = 18000;
const KEEP_RAW_TURN_GROUPS = 1;
const minuteTokenMap = new Map();

function truncateToolResult(text) {
    if (MAX_TOOL_RESULT_CHARS == 0 || text.length <= MAX_TOOL_RESULT_CHARS) return text;
    return text.slice(0, MAX_TOOL_RESULT_CHARS) + "\n... (truncated)";
}

function trimHistory() {
    if (messages.length <= MAX_HISTORY_MESSAGES) return;
    // Find a safe cut point — don't break mid-tool-call sequence.
    // Walk forward from the trim target to find a user message boundary.
    let cut = messages.length - MAX_HISTORY_MESSAGES;
    while (cut < messages.length && messages[cut].role !== "user") {
        cut++;
    }
    if (cut > 0 && cut < messages.length) {
        messages.splice(0, cut);
    }
}

function getEstimatedTokenMinuteLog(firstIterationMinuteBucket) {
    return Array.from(minuteTokenMap.entries())
        .filter(([minuteBucket]) => minuteBucket >= firstIterationMinuteBucket)
        .sort(([leftMinuteBucket], [rightMinuteBucket]) => leftMinuteBucket - rightMinuteBucket)
        .map(([minuteBucket, estimatedTokens]) => ({
            timestamp: new Date(minuteBucket * 60000).toISOString(),
            estimated_tokens: estimatedTokens,
        }));
}

async function chatWithMinuteDelay({ chat, apiKey, baseURL, model, messages, tools }) {
    const estimatedTokens = Math.max(
        1,
        Math.ceil(JSON.stringify({ model, messages, ...(tools ? { tools } : {}) }).length / ESTIMATED_CHARS_PER_TOKEN)
    );
    let currentMinuteBucket = Math.floor(Date.now() / 60000);
    const estimateTokenUsage = (minuteTokenMap.get(currentMinuteBucket) ?? 0) + estimatedTokens;

    if (estimateTokenUsage > MAX_ESTIMATED_TOKENS_PER_MINUTE) {
        currentMinuteBucket += 1;
        await new Promise((resolve) => setTimeout(() => resolve(), 60000));
    }

    minuteTokenMap.set(currentMinuteBucket, (minuteTokenMap.get(currentMinuteBucket) ?? 0) + estimatedTokens);

    return {
        minuteBucket: currentMinuteBucket,
        response: await chat({ apiKey, baseURL, model, messages, tools }),
    };
}

async function compactHistoryWithLLM(chat, apiKey, baseURL, model) {
    const estimatedTokens = Math.max(
        1,
        Math.ceil(JSON.stringify([{ role: "system", content: SYSTEM_INSTRUCTIONS }, ...messages]).length / ESTIMATED_CHARS_PER_TOKEN)
    );
    if (messages.length <= MAX_HISTORY_MESSAGES && estimatedTokens <= COMPACT_WHEN_ESTIMATED_TOKENS) return null;

    const { prefix, groups } = messages.reduce((acc, message) => {
        if (message.role === "user") {
            acc.groups.push([message]);
        } else if (acc.groups.length) {
            acc.groups[acc.groups.length - 1].push(message);
        } else {
            acc.prefix.push(message);
        }
        return acc;
    }, { prefix: [], groups: [] });

    if (groups.length <= KEEP_RAW_TURN_GROUPS) return null;

    const compacted = [...prefix, ...groups.slice(0, -KEEP_RAW_TURN_GROUPS).flat()];
    if (!compacted.length) return null;

    setStatus("Compacting…");
    try {
        const before = {
            message_count: messages.length,
            turn_group_count: groups.length,
            estimated_tokens: estimatedTokens,
        };
        const { minuteBucket, response } = await chatWithMinuteDelay({
            chat,
            apiKey,
            baseURL,
            model,
            messages: [
                {
                    role: "system",
                    content: "Summarize older IFC chat context for continuation. Preserve user goals, model state and schema, edits already applied, important ids, names, selectors, and unresolved questions. Be concise, factual, and use short markdown bullets. Do not mention that this is a summary."
                },
                { role: "user", content: JSON.stringify(compacted) },
            ],
        });
        const summary = response.choices?.[0]?.message?.content?.trim();

        if (!summary) return minuteBucket;

        messages = [
            { role: "assistant", content: `[Context summary]\n${summary}` },
            ...groups.slice(-KEEP_RAW_TURN_GROUPS).flat(),
        ];
        console.log("History compaction before", before);
        console.log("History compaction after", {
            message_count: messages.length,
            turn_group_count: messages.filter((message) => message.role === "user").length,
            estimated_tokens: Math.max(
                1,
                Math.ceil(JSON.stringify([{ role: "system", content: SYSTEM_INSTRUCTIONS }, ...messages]).length / ESTIMATED_CHARS_PER_TOKEN)
            ),
        });
        return minuteBucket;
    } finally {
        setStatus("Thinking…");
    }
}

async function runAgentTurn(userText) {
    const apiKey = apiKeyEl.value.trim();
    if (!apiKey) throw new Error("Missing API key");

    const provider = PROVIDERS[getProviderValue()];
    const { chat } = provider.api;
    const baseURL = provider.baseUrlDefault ? baseUrlEl.value.trim() : undefined;
    let firstIterationMinuteBucket = null;

    messages.push({ role: "user", content: userText });

    for (let i = 0; i < 64; i++) {
        const compactedMinuteBucket = await compactHistoryWithLLM(chat, apiKey, baseURL, modelEl.value);
        if (firstIterationMinuteBucket === null && compactedMinuteBucket !== null) {
            firstIterationMinuteBucket = compactedMinuteBucket;
        }
        if (messages.length > MAX_HISTORY_MESSAGES * 2) trimHistory();

        const messages_with_system = [{ role: "system", content: SYSTEM_INSTRUCTIONS }, ...messages];
        const { minuteBucket, response } = await chatWithMinuteDelay({
            chat,
            apiKey,
            baseURL,
            model: modelEl.value,
            messages: messages_with_system,
            tools,
        });
        if (firstIterationMinuteBucket === null) {
            firstIterationMinuteBucket = minuteBucket;
        }

        const message = response.choices?.[0]?.message;
        if (!message) throw new Error("No message in response");

        messages.push(message);

        if (message.content) addMessage("assistant", message.content);

        const calls = message.tool_calls ?? [];
        if (calls.length === 0) {
            console.log("Estimated token usage by minute", getEstimatedTokenMinuteLog(firstIterationMinuteBucket));
            return;
        }

        for (const call of calls) {
            let args = {};
            try { args = call.function.arguments ? JSON.parse(call.function.arguments) : {}; }
            catch { args = {}; }

            addMessage("tool", `→ ${call.function.name}(${JSON.stringify(args)})`);

            const toolRes = await callWorker("toolCall", { name: call.function.name, args });

            const fullResult = JSON.stringify(toolRes.result);

            messages.push({
                role: "tool",
                tool_call_id: call.id,
                content: truncateToolResult(fullResult),
            });

            // Show full result in UI, but only truncated version goes to the LLM
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
        const r = await callWorker("toolCall", { name: "ifc_new", args: { schema: "IFC4X3" } });
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
