import configJson from "./config.json";

export const CONFIG = configJson as {
    wasm: {
        wheel_url: string;
        odfpy_url: string;
        api_py_url: string;
        ifctester_wheel_url: string;
    };
};

export const IFCTESTER_WHEEL_URL: string =
    import.meta.env.VITE_IFCTESTER_WHEEL_URL ?? CONFIG.wasm.ifctester_wheel_url;
