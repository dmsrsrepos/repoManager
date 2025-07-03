// gitBackup.ts
// 脚本修复存储的内容，移除非必要的git库配置内容，比如 core，branch，gitflow， 等等
import fs from 'node:fs';
import { Context, Db, Repo } from './types'
import { extend, getClassifiedPath } from './utils'
import { findAllStoreFileContexts } from './utils';
import { Low } from 'lowdb';
async function restoreRepo(_ctx: Context) {
    const repos = _ctx.db.data.repos
    if (repos) {
        Object.entries(repos)
            .map<[string, Repo]>(([relativePath, gitConfig], idx, data) => {
                const ret = {} as Repo
                ret.__processorName = gitConfig.__processorName
                ret.name = gitConfig.name
                ret.remote = gitConfig.remote
                ret.submodule = gitConfig.submodule
                if (ret.remote) {
                    Object.entries(ret.remote).forEach(([key, value]) => {
                        if (ret.remote)
                            ret.remote[key] = { url: value.url }
                    })
                }
                ret.desc = gitConfig.desc
                ret.fromPaths = gitConfig.fromPaths
                ret['originalPaths'] = undefined
                delete repos[relativePath]
                relativePath = getClassifiedPath(relativePath)
                if (_ctx.db.data.repos)
                    _ctx.db.data.repos[relativePath] = ret;
                return [relativePath, ret];
            })
        await _ctx.db.write()
    }
}
export async function findAndBackupRepos(rootDirFullPath: string, maxDepth: number): Promise<void> {

    await findAllStoreFileContexts(rootDirFullPath)
        .then(async contexts => {
            return await contexts.reduce((prev, ctx) => {
                return prev.then(async () => {
                    const context = await ctx
                    await upgradeConfig(context.db)
                    await restoreRepo(context)
                        .catch(err => console.error('\r\n\r\n', 'Error：', err))
                })
            }, Promise.resolve())

        })
        .then(r => console.log('\r\n\r\n', 'Done! Check the ' + rootDirFullPath + ' file for the results.'))
        .catch(err => console.error('\r\n\r\n', 'Error：', err))
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