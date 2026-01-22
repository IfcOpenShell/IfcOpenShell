import configJson from "./config.json";

export const CONFIG = configJson as {
    wasm: {
        wheel_url: string;
        odfpy_url: string;
        api_py_url: string;
    };
};

const DEFAULT_IFCTESTER_WHEEL_URL =
    "/worker/bin/ifctester-0.8.5a260122-py3-none-any.whl";

export const IFCTESTER_WHEEL_URL: string =
    import.meta.env.VITE_IFCTESTER_WHEEL_URL ?? DEFAULT_IFCTESTER_WHEEL_URL;
