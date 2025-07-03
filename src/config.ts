import { Pattern, Db } from "./types";

import * as semver from 'semver';
export const CATEGORYPATTERNS: Record<string, Pattern> = {
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

export const RestoringCategories: string[] = Object.keys(CATEGORYPATTERNS)

export const defaultData: Db = {
    __version: '0.0.1',
    repos: {}
};

export const storeType: 'single' | 'multi' = 'single'