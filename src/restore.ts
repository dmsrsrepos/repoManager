// gitBackup.ts
import fs from 'node:fs';
import path from 'path';
import { Context, Repos } from './types'
import { JSONFilePreset } from 'lowdb/node';
import { extend, upgradeConfig } from './utils'
import { factory } from './factory';

async function restoreRepo(_ctx: Context) {
    return Object.entries(_ctx.db.data).map(async ([relativePath, repo]) => {

        if (relativePath == '__version') return;

        let ctx = extend({}, _ctx, { rootDir: _ctx.rootDir, curDir: path.join(_ctx.rootDir, relativePath) });
        let p = factory.find(async p => await p.shouldRestore(ctx, repo));
        if (p) {
            // 定义一个GitRepo对象，用于存储git库的信息
            return await p.restoreRepo(ctx, repo)
        }
    })
}
export async function findAndBackupRepos(rootDir: string, maxDepth: number): Promise<void> {
    let defaultData: Repos = {};
    await JSONFilePreset('db.json', defaultData)
        .then(async db => {
            const ctx: Context = {
                curDir: rootDir,
                db,
                rootDir
            };
            await upgradeConfig(db)
            return ctx;
        })
        .then(async ctx => {

            await restoreRepo(ctx)
            return ctx;
        })
        .then(ctx => console.log('\r\n\r\n', 'Done! Check the ' + ctx.rootDir + ' file for the results.'))
        .catch(err => console.error('\r\n\r\n', 'Error：', err))
}

const ROOT_DIR = ['C:\\ScriptsApplications\\test', 'G:\\test'].filter(val => fs.existsSync(val))[0];
const MAX_DEPTH = 5;

(async () => {
    console.log(``)
    console.log(``)
    console.log(' ', '', '', '',)
    console.log(`Starting: target:${ROOT_DIR}`)

    if (!ROOT_DIR) {
        console.error('not find target folder, please set it and retry again')
    }
    await findAndBackupRepos(ROOT_DIR, MAX_DEPTH);
})();