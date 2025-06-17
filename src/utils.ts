import { Low } from "lowdb";
import semver from "semver";
import { Repos } from "./types";

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
            // db.data['__version'] = '2.0.0'
            // for (let key in db.data) {
            //     let repo = db.data[key];
            //     repo['remotes'] = repo['remotes'] || []
            // }
        }
    }
}


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