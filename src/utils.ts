import { Low } from "lowdb";
import { deepmergeCustom, getObjectType, ObjectType } from 'deepmerge-ts';
import { Context, Db } from "./types";
import path from 'path';
import { defaultData, MAPPER, storeType } from "./config";
import { glob } from 'glob'
import os from 'node:os';
import { JSONFilePreset } from "lowdb/node";

export function getMachineKey() {
    return os.hostname();// + '_' + os.userInfo().username;
}

const mappers = Object.entries(MAPPER)

// 自定义深层合并配置
const customDeepMerge = deepmergeCustom({
    // 合并数组时去重（支持嵌套对象）
    mergeArrays: (arrays, utils, meta) => {
        console.log("🚀 ~ meta:", meta)
        // console.log("🚀 ~ utils:", JSON.stringify(utils))
        // console.log("🚀 ~ arrays:", arrays)

        let result = utils.defaultMergeFunctions.mergeArrays(arrays);
        // console.log("🚀 ~ result:", result)

        return removeDuplicates(result) as any;
        // // 合并基础元素（去重）
        // const merged = deduplicate(dest, src);
        // // 递归处理嵌套对象
        // return merged.map(item =>
        //     getObjectType(item) === ObjectType.RECORD ? customDeepMerge(item, item) : item
        // );
    }
});

export function extend<T extends object, U, U2, U3, U4 extends object>(target: T, s1: U, s2?: U2, s3?: U3, s4?: U4, ...others: any): T & U & U2 & U3 & U4 {
    return customDeepMerge(target, s1, s2, s3, s4, ...others) as T & U & U2 & U3 & U4
    // const isDeep = true;
    // target = Object.assign({}, target);
    // const sources = [s1, s2, s3, s4, ...others];
    // for (const source of sources) {
    //     for (const key in source as any) {
    //         if (Object.hasOwn(source as any, key)) {
    //             const srcVal = source[key];
    //             const tarVal = target[key];

    //             if (isDeep && typeof srcVal === 'object' && srcVal !== null && !Array.isArray(srcVal)
    //                 && typeof tarVal === 'object' && tarVal !== null) {
    //                 target[key] = extend(tarVal as any, srcVal as any);
    //             } else {
    //                 target[key] = srcVal;
    //             }
    //         }
    //     }
    // }

    // return target;
}


export function removeDuplicates<T>(array: T[]): T[] {
    return [...new Set(array)];
}




export function getNextCharacter(source: string): string {
    if (!source)
        return source;
    let nextChar: string[] = [], n = source.length;
    // 获取字符的Unicode码点
    for (let i = 0; i < n; i++) {
        let charCode = source.charCodeAt(i);
        if (charCode === 0x10FFFF) {
            // Unicode的最大码点是0x10FFFF，超过此值无意义
            nextChar[i] = source[i]
        } else {
            const nextCharCode = charCode + 1;
            nextChar[i] = String.fromCharCode(nextCharCode);
        }
    }
    return nextChar.join('');
}

// const test = "[branch \"net8.0\"]"
// // todo: test need delete
// console.log(extractQuotedValue(test))

export function extractQuotedValue(str: string): string | undefined {
    // 匹配单引号或双引号包裹的内容，包括引号本身
    const regexSingleQuote = /"((?:\\.|[^"])*)"/;
    const regexDoubleQuote = /"((?:\\.|[^"])*)"/;

    // 先尝试匹配双引号
    const doubleQuoteMatch = str.match(regexDoubleQuote);
    if (doubleQuoteMatch && doubleQuoteMatch.length > 1) {
        return doubleQuoteMatch[1];
    }

    // 如果没找到双引号，则尝试匹配单引号
    const singleQuoteMatch = str.match(regexSingleQuote);
    if (singleQuoteMatch && singleQuoteMatch.length > 1) {
        return singleQuoteMatch[1];
    }

    // 如果都没有找到匹配项，返回undefined
    return undefined;
}
export async function upgradeConfig(db: Low<Db>) {
    if (!db.data.__version) {
        db.data.__version = '1.0.0'
    }
    else {

        var version = db.data.__version;
        if (typeof version !== 'string') {
            db.data.__version = '1.0.0'

        }
        console.log('config db file version:', db.data.__version);

        if (!db.data.repos) {
            db.data.repos = {}
        }
        const repos = db.data.repos;
        Object.entries(repos)
            .filter(([key, value]) => key.startsWith('test\\'))
            .forEach(([key, value]) => {
                delete repos[key];
            })
        await db.write()
        Object.entries(repos)
            .filter(([key, value]) => key.startsWith('test\\'))
            .forEach(([key, value]) => {
                repos[key.replace('test\\', '')] = extend({}, value, repos[key.replace('test\\', '')])
                delete repos[key];
            })
        await db.write()
    }
}

export function getClassifiedPath(relateviePath: string): string {
    const processedPath = path.normalize(relateviePath);
    const sep = path.sep;
    const otherName = 'unclassified'
    // 分割路径为部分，处理Windows的驱动器情况
    let parts: string[];
    // 相对路径，例如 'a/b/c' 或 'a\b\c'
    parts = processedPath.split(sep).filter(p => p !== '');
    let alias = mappers.find(([key, value]) => value.keys.findIndex(p => p.startsWith(parts[0]) || p.includes(parts[0]) || p.endsWith(parts[0])) > -1)
        || mappers.find(([key, value]) => value.pattern && new RegExp(value.pattern).test(parts[0]))
        || mappers.find(([key, value]) => value.keys.findIndex(p => p.startsWith(relateviePath) || p.includes(relateviePath) || p.endsWith(relateviePath)) > -1)
    if (alias) {
        parts[0] = alias[0];
    }
    else {
        parts[0] = otherName;
    }
    // console.log("🚀 ~ getClassifiedPath ~ parts:", parts.join(sep))
    return parts.join(sep);
}
export function getStoreNameByPath(filePath: string): string {
    if (storeType == 'single') {
        return 'repo.db.all.json';
    } else {
        const id = path.normalize(filePath).replaceAll(path.sep, '.').replaceAll(':', '.').replaceAll('..', '.');
        console.log("🚀 ~ findAndBackupRepos ~ id:", id)
        let dbName = `repo.db.${id}.json`
        // dbName = 'all.repo.db.json'
        return dbName;
    }

}

export async function getAllStoreFiles(filePath: string) {
    return glob(`**/repo.db.*.json`, { cwd: process.cwd(), absolute: true })
        .then(async files => {
            console.log("🚀 ~ findAndBackupRepos ~ files:", files)
            return files
        })
}
// test_key();
export default {
    extend,
    removeDuplicates,
    getNextCharacter,
    extractQuotedValue,
    upgradeConfig,
    getClassifiedPath
}

function testGroupPathsBygetClassifiedPath(paths: string[]): Record<string, string[]> {
    const groups: Record<string, string[]> = {};

    for (const filePath of paths) {
        const topLevelDir = getClassifiedPath(filePath);
        if (!groups[topLevelDir]) {
            groups[topLevelDir] = [];
        }
        groups[topLevelDir].push(filePath);
    }

    return groups;
}
const paths = [
    '/home/user/project/src/utils/index.ts',
    '/home/user/project/src/components/Button.ts',
    '/home/user/project/docs/README.md',
    'src/utils/helper.ts',
    'C:\\projects\\app\\src\\main.ts',
    'C:\\projects\\app\\tests\\unit.test.ts',
    'D:\\data\\files\\config.json',
    './relative/path/to/file.txt', // 相对路径，标准化后是 'relative/path/to/file.txt'
];

function test_key() {
    const grouped = testGroupPathsBygetClassifiedPath(paths);
    console.log(grouped);
}

function test_getNextCharacter() {
    const currentChar = 'Visual Studio Code';
    let nextChar = getNextCharacter(currentChar);

    console.log(nextChar);
    let m;
    nextChar = getNextCharacter(m);

    console.log(nextChar);
    m = null;
    nextChar = getNextCharacter(m);

    console.log(nextChar);
}

//  test_extend()
// 使用示例
// test();

function test_extend() {
    const x = {
        record: {
            prop1: "value1",
            prop2: "value2",
        },
        array: [1, 2, 3],
        set: new Set([1, 2, 3]),
        map: new Map([
            ["key1", "value1"],
            ["key2", "value2"],
        ]),
    };

    const y = {
        record: {
            prop1: "changed",
            prop3: "value3",
        },
        array: [2, 3, 4],
        set: new Set([2, 3, 4]),
        map: new Map([
            ["key2", "changed"],
            ["key3", "value3"],
        ]),
    };

    const z = {
        record: {
            prop1: undefined,
            prop3: undefined,
            prop2: undefined,
            prop4: undefined,
        },
        array: [4, 5],
        set: undefined,
        map: undefined,
    };

    const merged = extend(x, y, z);

    console.log(merged);

    const a = undefined;
    const b = null;
    const c = { __processor: undefined }
    const d = { __processor1: null }
    const e = { e: 5, f: 6 };
    const f = { e: 10, f: 6, g: 7 };

    console.log(extend({}, a, b, c, d, e, f));
}
export async function findAllStoreFileContexts(rootDirFullPath: string) {
    let m = await getAllStoreFiles(rootDirFullPath)
        .then(files => {
            return files.map(async (file) => await JSONFilePreset(file, defaultData));
        })
        .then(d => {
            return d.flatMap(async (db) => {
                const ctx: Context = {
                    curDirFullPath: rootDirFullPath,
                    db: await db,
                    rootDirFullPath: rootDirFullPath,
                };
                return ctx;
            });
        });

    return m;

}

// test_extend()