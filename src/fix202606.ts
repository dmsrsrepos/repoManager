// gitBackup.ts
// 脚本修复存储的内容，移除非必要的git库配置内容，比如 core，branch，gitflow， 等等
import fs from 'node:fs';
import path from 'path';
import { Context, Repos, Db, Repo } from './types'
import { JSONFilePreset } from 'lowdb/node';
import { extend, getClassifiedPath, upgradeConfig } from './utils'
import { factory } from './components/factory';
import { RestoreAlias } from './alias_config'
async function restoreRepo(_ctx: Context) {
    const repos = _ctx.db.data.repos
    if (repos) {
        Object.entries(repos).map(async ([relativePath, gitConfig], idx, data) => {
            const ret = {} as Repo
            ret.name = gitConfig.name
            // ret.__processorName = gitConfig.__processorName
            ret.desc = gitConfig.desc
            ret.remote = gitConfig.remote
            ret.submodule = gitConfig.submodule
            if (ret.remote) {
                Object.entries(ret.remote).forEach(([key, value]) => {
                    if (ret.remote)
                        ret.remote[key] = { url: value.url }
                })
            }
            repos[relativePath] = ret;
            return [relativePath, ret];
        })
        _ctx.db.write();
    }
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

const ROOT_DIR = ['C:\\AppData\\test', 'G:\\code'].filter(val => fs.existsSync(val))[0];
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