export type IdsCardinality = "required" | "optional" | "prohibited";

export type RestrictionValue = {
    "@value": string;
};

export type Restriction = {
    "@base"?: string;
    enumeration?: RestrictionValue[];
    pattern?: RestrictionValue[];
    length?: RestrictionValue[];
    minLength?: RestrictionValue[];
    maxLength?: RestrictionValue[];
    minInclusive?: RestrictionValue[];
    maxInclusive?: RestrictionValue[];
    minExclusive?: RestrictionValue[];
    maxExclusive?: RestrictionValue[];
};

export type SimpleValue = {
    simpleValue: string;
};

export type FacetValue = {
    simpleValue?: string;
    restriction?: Restriction;
};

export type Facet = Record<string, FacetValue | string | number | boolean | null | undefined>;

export type FacetClause = Record<string, Facet[] | number | "unbounded" | undefined>;

export type Specification = {
    "@name"?: string;
    "@identifier"?: string;
    "@description"?: string;
    "@instructions"?: string;
    "@ifcVersion"?: string[];
    applicability?: FacetClause;
    requirements?: FacetClause;
};

export type IdsInfo = {
    title?: string;
    copyright?: string;
    version?: string;
    description?: string;
    author?: string;
    date?: string;
    purpose?: string;
    milestone?: string;
};

export type IdsDocument = {
    "@xmlns"?: string;
    "@xmlns:xs"?: string;
    "@xmlns:xsi"?: string;
    "@xsi:schemaLocation"?: string;
    info: IdsInfo;
    specifications: {
        specification: Specification[];
    };
};

export type DocumentState = {
    activeTab: "info" | "applicability" | "requirements";
    viewMode: "editor" | "viewer";
    activeSpecification: number | null;
    auditReport?: string | null;
};
