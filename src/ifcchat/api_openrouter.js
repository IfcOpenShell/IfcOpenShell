
export async function chat({ apiKey, model, messages, tools }) {
    const res = await fetch("https://openrouter.ai/api/v1/chat/completions", {
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
