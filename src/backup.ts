// gitBackup.ts
import fs from 'node:fs';
import path from 'path';
import { Context, Repos } from './types'
import { JSONFilePreset } from 'lowdb/node';
import { factory } from './factory';
import { upgradeConfig, extend, getClassifiedPath } from './utils';
async function findRepos(dirFullPath: string, depth: number, ctx: Context): Promise<void> {
    if (depth === 0) {
        return;
    }

    const files = await fs.promises.readdir(dirFullPath);

    // 遍历所有文件和子目录
    for (let file of files) {
        // 拼接完整的路径
        let curDirFullPath = path.join(dirFullPath, file);
        let key = getClassifiedPath(curDirFullPath.replace(ctx.rootDirFullPath, ''))
        ctx.curDirFullPath = curDirFullPath;
        // 一次性获取目录信息，避免多次调用 fs.statSync
        const isDir = fs.existsSync(curDirFullPath) && fs.statSync(curDirFullPath)?.isDirectory();
        // 如果是目录，判断是否是git库
        if (isDir) {
            let isGitRepo = false;
            for (let p of factory) {
                // 判断是否存在.git目录
                isGitRepo = await p.shouldBackup(ctx);
                // 如果是git库，获取其信息，并添加到数组中
                if (isGitRepo) {                    
                    // 定义一个GitRepo对象，用于存储git库的信息
                    const repo = await p.backupRepo(ctx);
                    ctx.db.data[key] = extend({ "__processorName": p.name }, ctx.db.data[key], repo);
                    // { ...ctx.db.data[key], "__processorName": p.name, ...repo }; //对象扩展仅仅支持浅表复制，无法深层拷贝
                    break; // 只允许一个处理器处理当前库
                }
            }
            if (!isGitRepo) {
                await findRepos(curDirFullPath, depth - 1, ctx);
            }
        }
    }
}

export async function findAndBackupRepos(rootDirFullPath: string, maxDepth: number): Promise<void> {
    let defaultData: Repos = {};
    await JSONFilePreset('db.json', defaultData)
        .then(async db => {
            await upgradeConfig(db);
            const ctx: Context = {
                curDirFullPath: rootDirFullPath,
                db,
                rootDirFullPath: rootDirFullPath
            };
            await findRepos(rootDirFullPath, maxDepth, ctx);
            return ctx;
        })
        .then(async ctx => {
            await ctx.db.write()
            return ctx;
        })
        .then(ctx => console.log('\r\n\r\n', 'Done! Check the ' + ctx.rootDirFullPath + ' file for the results.'))
        .catch(err => console.error('\r\n\r\n', 'Error：', err))
}

const ROOT_DIR = ['C:\\AppData\\code', 'G:\\'].filter(val => fs.existsSync(val))[0];
const MAX_DEPTH = 5;

(async () => {
    console.log(``)
    console.log(``)
    console.log(' ', '', '', '',)
    console.log(`Starting: target:${ROOT_DIR}`)
    if (!ROOT_DIR) {
        console.error('not find target folder, please set it and retry again')
    } else {
        await findAndBackupRepos(ROOT_DIR, MAX_DEPTH);
    }
})();