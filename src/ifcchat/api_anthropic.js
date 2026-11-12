// This file was generated with the assistance of an AI coding tool.

function parseArguments(argumentsText) {
    if (!argumentsText) return {};
    try {
        return JSON.parse(argumentsText);
    } catch {
        return {};
    }
}

function toAnthropicTools(tools = []) {
    return tools.map((tool) => ({
        name: tool.function.name,
        description: tool.function.description,
        input_schema: tool.function.parameters,
    }));
}

function toAnthropicAssistantContent(message) {
    const content = [];

    if (message.content) {
        content.push({ type: "text", text: message.content });
    }

    for (const toolCall of message.tool_calls ?? []) {
        content.push({
            type: "tool_use",
            id: toolCall.id,
            name: toolCall.function.name,
            input: parseArguments(toolCall.function.arguments),
        });
    }

    if (content.length === 0) {
        return "";
    }

    return content.length === 1 && content[0].type === "text" ? content[0].text : content;
}

function toAnthropicUserContent(message) {
    return typeof message.content === "string" ? message.content : JSON.stringify(message.content ?? "");
}

function toAnthropicToolResult(message) {
    return {
        type: "tool_result",
        tool_use_id: message.tool_call_id,
        content: typeof message.content === "string" ? message.content : JSON.stringify(message.content ?? ""),
    };
}

function splitSystemAndMessages(messages = []) {
    const system = [];
    const anthropicMessages = [];
    let pendingToolResults = [];

    const flushToolResults = () => {
        if (pendingToolResults.length === 0) return;
        anthropicMessages.push({ role: "user", content: pendingToolResults });
        pendingToolResults = [];
    };

    for (const message of messages) {
        if (message.role === "system") {
            if (message.content) {
                system.push(message.content);
            }
            continue;
        }

        if (message.role === "tool") {
            pendingToolResults.push(toAnthropicToolResult(message));
            continue;
        }

        flushToolResults();

        if (message.role === "user") {
            anthropicMessages.push({
                role: "user",
                content: toAnthropicUserContent(message),
            });
            continue;
        }

        if (message.role === "assistant") {
            anthropicMessages.push({
                role: "assistant",
                content: toAnthropicAssistantContent(message),
            });
        }
    }

    flushToolResults();

    return {
        system: system.join("\n\n"),
        messages: anthropicMessages,
    };
}

function toChatCompletionResponse(response) {
    const text = [];
    const toolCalls = [];

    for (const block of response.content ?? []) {
        if (block.type === "text") {
            text.push(block.text);
            continue;
        }

        if (block.type === "tool_use") {
            toolCalls.push({
                id: block.id,
                type: "function",
                function: {
                    name: block.name,
                    arguments: JSON.stringify(block.input ?? {}),
                },
            });
        }
    }

    const message = { role: "assistant" };
    const content = text.join("\n").trim();

    if (content) {
        message.content = content;
    }

    if (toolCalls.length) {
        message.tool_calls = toolCalls;
    }

    return {
        choices: [
            {
                message,
            },
        ],
    };
}

export async function chat({ apiKey, model, messages, tools }) {
    const request = splitSystemAndMessages(messages);
    const anthropicTools = toAnthropicTools(tools);

    // Mark the last tool with cache_control so the entire tool list is cached
    if (anthropicTools.length > 0) {
        anthropicTools[anthropicTools.length - 1].cache_control = { type: "ephemeral" };
    }

    const body = {
        model,
        max_tokens: 4096,
        messages: request.messages,
        tools: anthropicTools,
    };

    if (request.system) {
        body.system = [{ type: "text", text: request.system, cache_control: { type: "ephemeral" } }];
    }

    const res = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "x-api-key": apiKey,
            "anthropic-version": "2023-06-01",
            "anthropic-dangerous-direct-browser-access": "true",
        },
        body: JSON.stringify(body),
    });

    if (!res.ok) {
        const text = await res.text();
        throw new Error(`Anthropic error ${res.status}: ${text}`);
    }

    return toChatCompletionResponse(await res.json());
}
