// gitBackup.ts
import fs from 'node:fs';
import path from 'path';
import { Context, Db, Repos } from './types'
import { JSONFilePreset } from 'lowdb/node';
import { extend, getClassifiedPath, upgradeConfig } from './utils'
import { factory } from './components/factory';
import { RestoreAlias } from './alias_config'

async function restoreRepo(_ctx: Context) {
    console.log("🚀 ~ Restore categories:", RestoreAlias)

    if (_ctx.db.data.repos)
        return Object.entries(_ctx.db.data.repos).map(async ([relativePath, repo], idx, data) => {
            relativePath = getClassifiedPath(relativePath)
            let ctx = extend({}, _ctx, { rootDirFullPath: _ctx.rootDirFullPath, curDirFullPath: path.join(_ctx.rootDirFullPath, relativePath) });
            let p = factory.find(async (p, _idx, _all) => await p.shouldRestore(ctx, repo));
            if (p) {
                const alias = relativePath.split(path.sep)[0]
                if (RestoreAlias.includes(alias)) {
                    console.log("🚀 ~ =====")
                    console.log(`🚀 ~ Start restoring  ${idx + 1}/${data.length} `)
                    // 定义一个GitRepo对象，用于存储git库的信息
                    return await p.restoreRepo(ctx, repo)
                }
            }
        })
}
export async function findAndBackupRepos(rootDirFullPath: string, maxDepth: number): Promise<void> {
    let defaultData = {} as Db;
    await JSONFilePreset('db.json', defaultData)
        .then(async db => {
            const ctx: Context = {
                curDirFullPath: rootDirFullPath,
                db,
                rootDirFullPath: rootDirFullPath,
            };
            await upgradeConfig(db)
            return ctx;
        })
        .then(async ctx => {

            await restoreRepo(ctx)
            return ctx;
        })
        .then(ctx => console.log('\r\n\r\n', 'Done! Check the ' + ctx.rootDirFullPath + ' file for the results.'))
        .catch(err => console.error('\r\n\r\n', 'Error：', err))
}

const ROOT_DIR = ['C:\\AppData\\code', 'G:\\code'].filter(val => fs.existsSync(val))[0];
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