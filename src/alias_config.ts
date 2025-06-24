import { Alias } from "./types";

export const MAPPER: Record<string, Alias> = {
    ai: {

        keys: ["ai"]
    },
    vPress: {
        keys: ["vPress"],
    },
    frontend: {
        keys: ["frontend"],
    },
    learn: {
        pattern: /[learn]+/,
        keys: ['learn'],
    },
    vsextension: {
        keys: ['vsextension'],
    },

    comm: {
        keys: ['comm'],
    }
}

export type AliasType = keyof typeof MAPPER

export const RestoreAlias: AliasType[] = ['comm']