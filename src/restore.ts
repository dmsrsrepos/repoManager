// gitBackup.ts
import fs from 'node:fs';
import path from 'path';
import { Context, Db, Repos } from './types'

import { extend, findAllStoreFileContexts, getClassifiedPath } from './utils'
import { factory } from './components/factory';
import { RestoringCategories } from './config'

async function restoreRepo(context: Context) {
    console.log("🚀 ~ Restore categories:", RestoringCategories)

    if (context.db.data.repos)
        return Object.entries(context.db.data.repos).map(async ([relativePath, repo], idx, data) => {
            relativePath = getClassifiedPath(relativePath)
            let ctx = extend({}, context, { rootDirFullPath: context.rootDirFullPath, curDirFullPath: path.join(context.rootDirFullPath, relativePath) });
            let p = factory.find(async (p, _idx, _all) => await p.shouldRestore(ctx, repo));
            if (p) {
                const alias = relativePath.split(path.sep)[0]
                if (RestoringCategories.includes(alias)) {
                    console.log("🚀 ~ =====")
                    console.log(`🚀 ~ Start restoring  ${idx + 1}/${data.length} `)
                    // 定义一个GitRepo对象，用于存储git库的信息
                    return await p.restoreRepo(ctx, repo)
                }
            }
        })
}
export async function findAndBackupRepos(rootDirFullPath: string, maxDepth: number): Promise<void> {

    await findAllStoreFileContexts(rootDirFullPath)
        .then(async contexts => {
            return await contexts.reduce((prev, ctx) => {
                return prev.then(async () => {
                    const context = await ctx
                    await restoreRepo(context)
                        .catch(err => console.error('\r\n\r\n', 'Error：', err))
                })
            }, Promise.resolve())

        })
        .then(r => console.log('\r\n\r\n', 'Done! Check the ' + rootDirFullPath + ' file for the results.'))
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