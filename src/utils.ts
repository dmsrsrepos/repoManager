import { Low } from "lowdb";
import semver from "semver";
import { Repos } from "./types";
import path from 'path';
import { globSync } from 'glob';

// utils.ts
export function extend<T extends object, U, U2, U3, U4 extends object>(target, s1: U, s2?: U2, s3?: U3, s4?: U4, ...others: any): T & U & U2 & U3 & U4 {
    const isDeep = true;
    target = Object.assign({}, target);
    const sources = [s1, s2, s3, s4, ...others];
    for (const source of sources) {
        for (const key in source as any) {
            if (Object.hasOwn(source as any, key)) {
                const srcVal = source[key];
                const tarVal = target[key];

                if (isDeep && typeof srcVal === 'object' && srcVal !== null && !Array.isArray(srcVal)
                    && typeof tarVal === 'object' && tarVal !== null) {
                    target[key] = extend(tarVal as any, srcVal as any);
                } else {
                    target[key] = srcVal;
                }
            }
        }
    }

    return target;
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
export async function upgradeConfig(db: Low<Repos>) {
    if (!Object.hasOwn(db.data, '__version')) {
        db.data['__version'] = semver.parse('1.0.0');
        for (let key in db.data) {
            delete db.data[key]['remotes'];
        }
    }
    else {
        var version = db.data['__version'];
        console.log('config db file version:', version.raw);
        if (version === '1.0.0') {



        }
        let data = db.data;
        Object.entries(db.data)
            .filter(([key, value]) => key.startsWith('test\\'))
            .forEach(([key, value]) => {
                delete db.data[key];
            })
        db.write()
        Object.entries(db.data)
            .filter(([key, value]) => key.startsWith('test\\'))
            .forEach(([key, value]) => {
                db.data[key.replace('test\\', '')] = extend({}, value, data[key.replace('test\\', '')])
                delete db.data[key];
            })
        db.write()
    }
}



function isPathMatch(path: string, pattern: string): boolean {
    // 注意：glob 默认会忽略隐藏文件（以 . 开头），除非模式显式包含 .*
    const matches = globSync(pattern, {
        dot: true, // 包含隐藏文件（如 .gitignore）
        nocase: false, // 是否大小写不敏感（默认 false）
    });
    return matches.includes(path);
}
const MAPPER = {
    ai: {
        pattern: "",
        keys: ["ai"]
    },
    vPress: {
        pattern: "",
        keys: ["vPress"],
    },
    frontend: {
        pattern: "",
        keys: ["frontend"],
    },
    learn: {
        pattern: "",
        keys: ['learn'],
    },
    vsextension: {
        pattern: "",
        keys: ['vsextension'],
    },
    code: {
        pattern: "",
        keys: ['code'],
    }
}
function getTopLevelDir(inputPath: string): string {
    const processedPath = path.normalize(inputPath);
    const isAbsolute = path.isAbsolute(processedPath);
    const sep = path.sep;

    // 分割路径为部分，处理Windows的驱动器情况
    let parts: string[];
    if (isAbsolute) {
        // 绝对路径，例如 '/a/b/c' 或 'C:\a\b\c'
        parts = processedPath.split(sep);
        // 过滤掉空字符串（可能出现在Unix根路径或Windows驱动器后的分隔符）
        // 例如，Unix的 '/' → split('/') → ['', ''] → 过滤后 []
        // Windows的 'C:\\' → split('\\') → ['C:', '', ''] → 过滤后 ['C:']
        parts = parts.filter(p => p !== '');
    } else {
        // 相对路径，例如 'a/b/c' 或 'a\b\c'
        parts = processedPath.split(sep).filter(p => p !== '');
    }

    if (parts.length === 0) {
        // 空路径或根路径（如 '/' 或 'C:\'）
        return isAbsolute ? processedPath : '';
    }

    // 对于Unix绝对路径，顶层目录是 '/' + parts[0]
    if (isAbsolute && sep === '/') {
        return `/${parts[0]}`;
    }

    // 对于Windows绝对路径，顶层目录是 parts[0] + '\'（如果parts[0]是驱动器）
    if (isAbsolute && sep === '\\') {
        // 检查是否是驱动器路径（如 'C:'）
        if (parts[0].length === 2 && parts[0][1] === ':') {
            return `${parts[0]}\\${parts[1]}`;
        } else {
            // 其他绝对路径（如 '\\server\share\path'）
            return parts[0];
        }
    }
    Object.entries(MAPPER).forEach(([key, value]) => {
        if (value.keys.findIndex(p => p.startsWith(parts[0]) || p.includes(parts[0]) || p.endsWith(parts[0]))) {
            parts[0] = key;
        } else if (new RegExp(value.pattern).test(parts[0])) {
            parts[0] = key;
        } else {
            parts[0] = 'code';
        }
    })
    // 相对路径，顶层目录是第一个部分
    return parts.join(sep);
}

function testGroupPathsByTopLevelDir(paths: string[]): Record<string, string[]> {
    const groups: Record<string, string[]> = {};

    for (const filePath of paths) {
        const topLevelDir = getTopLevelDir(filePath);
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
    const grouped = testGroupPathsByTopLevelDir(paths);
    console.log(grouped);
}

test_key();
export default {
    extend,
    removeDuplicates,
    getNextCharacter,
    extractQuotedValue,
    upgradeConfig
}

function test_extend() {
    const a = undefined;
    const b = null;
    const c = { __processor: undefined }
    const d = { __processor1: null }
    const e = { e: 5, f: 6 };
    const f = { e: 10, f: 6, g: 7 };

    console.log(extend({}, a, b, c, d, e, f));
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