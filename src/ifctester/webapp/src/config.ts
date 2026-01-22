import configJson from "./config.json";

export type IfcTesterInstallSource = "wheel" | "pypi";

export const CONFIG = configJson as {
    wasm: {
        wheel_url: string;
        odfpy_url: string;
        api_py_url: string;
    };
};

export const IFCTESTER_INSTALL_SOURCE: IfcTesterInstallSource =
    (import.meta.env.VITE_IFCTESTER_INSTALL_SOURCE as IfcTesterInstallSource | undefined) ?? "pypi";

export const IFCTESTER_WHEEL_URL: string =
    import.meta.env.VITE_IFCTESTER_WHEEL_URL ?? "";
