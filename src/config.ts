import { Alias, Db } from "./types";

import * as semver from 'semver';
export const MAPPER: Record<string, Alias> = {
    ai: {

        keys: ["ai"]
    },
    vPress: {
        keys: ["vPress",],
    },
    frontend: {
        keys: ["frontend", 'vue', 'Vue'],
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
    },

    net: {
        keys: ['net'],
    },

    wechat: {
        keys: ['wechat', 'wx', '微信'],
    }
}

export type AliasType = keyof typeof MAPPER

export const RestoreAlias: AliasType[] = Object.keys(MAPPER)

export const defaultData: Db = {
    __version: semver.parse('1.0.0'),
    repos: {}
};

export const storeType: 'single' | 'multi' = 'single'