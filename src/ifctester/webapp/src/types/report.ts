export type ResultsPercent = number | "N/A";

export type AuditReportEntity = {
    reason?: string;
    element?: unknown;
    element_type?: unknown;
    class?: string;
    predefined_type?: string;
    name?: string | null;
    description?: string | null;
    id?: number;
    global_id?: string | null;
    tag?: string | null;
    type_name?: string;
    type_tag?: string | null;
    type_global_id?: string | null;
    extra_of_type?: number;
};

export type AuditRequirement = {
    facet_type: string;
    metadata: Record<string, unknown>;
    label: string;
    value: string;
    description: string;
    status: boolean;
    passed_entities: AuditReportEntity[];
    failed_entities: AuditReportEntity[];
    total_applicable: number;
    total_pass: number;
    total_fail: number;
    percent_pass: ResultsPercent;
    instructions?: string;
    total_failed_entities?: number;
    total_omitted_failures?: number;
    has_omitted_failures?: boolean;
    total_passed_entities?: number;
    total_omitted_passes?: number;
    has_omitted_passes?: boolean;
};

export type AuditSpecification = {
    name: string;
    description: string;
    instructions: string;
    status: boolean;
    is_skipped?: boolean;
    is_ifc_version: boolean;
    total_applicable: number;
    total_applicable_pass: number;
    total_applicable_fail: number;
    percent_applicable_pass: ResultsPercent;
    total_checks: number;
    total_checks_pass: number;
    total_checks_fail: number;
    percent_checks_pass: ResultsPercent;
    cardinality: string;
    applicability: string[];
    applicable_entities?: AuditReportEntity[];
    requirements: AuditRequirement[];
    total_requirements?: number;
    total_requirements_pass?: number;
};

export type AuditReportData = {
    title: string;
    date: string;
    filepath: string | null;
    filename: string | null;
    hide_skipped: boolean;
    specifications: AuditSpecification[];
    status: boolean;
    total_specifications: number;
    total_specifications_pass: number;
    total_specifications_fail: number;
    percent_specifications_pass: ResultsPercent;
    total_requirements: number;
    total_requirements_pass: number;
    total_requirements_fail: number;
    percent_requirements_pass: ResultsPercent;
    total_checks: number;
    total_checks_pass: number;
    total_checks_fail: number;
    percent_checks_pass: ResultsPercent;
};

export type AuditReport = {
    id: string;
    modelId: string;
    modelName: string;
    document: string;
    date: string;
    data: AuditReportData;
    htmlReport?: string | null;
};
