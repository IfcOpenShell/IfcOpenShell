function getChatCompletionsUrl(baseURL) {
    const root = (baseURL || "https://openrouter.ai/api/v1").replace(/\/+$/, "");
    return `${root}/chat/completions`;
}

export async function chat({ apiKey, baseURL, model, messages, tools }) {
    const res = await fetch(getChatCompletionsUrl(baseURL), {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${apiKey}`,
        },
        body: JSON.stringify({ model, messages, tools }),
    });
    if (!res.ok) {
        const text = await res.text();
        throw new Error(`OpenRouter error ${res.status}: ${text}`);
    }
    return await res.json();
}
