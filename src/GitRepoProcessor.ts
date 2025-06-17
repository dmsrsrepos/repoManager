import fs, { PathLike } from "node:fs";
import path from "path";
import * as ini from 'ini'; // 需要先安装ini库，命令：npm install ini
import { Context, Proccessor, Repo } from './types';
import { gitClone } from './gitclone';

export class GitRepoProcessor implements Proccessor {
    readonly name: string = '.git';
    async shouldRestore(ctx: Context, repo: Repo) {
        return repo?.__processorName === this.name;
    }

    async shouldBackup(ctx: Context) {
        return fs.existsSync(path.join(ctx.curDir, '.git'));
    }
    async backupRepo(ctx: Context) {
        // 定义一个GitRepo对象，用于存储git库的信息
        let repo: Repo = {
            name: 'unknown'
        };
        console.log(`Backuping... git配置文件：${ctx.curDir}`)
        let configPath = path.join(ctx.curDir, '.git', 'config')

        repo = readGitConfig(configPath)
        return repo;
    }

    async restoreRepo(ctx, repo) {
        gitClone(repo, ctx.curDir)
        return false;
    }
}

function fixSectionName(str: string) {
    // ini.parse 会把section中的`.`作为对象层级的分割，所以，把原有.替换为$dot$，然后将空格替换为`.`，则自动解析
    return str.replaceAll(/\[.*?\]/g, function (match) {
        // return `[${match.slice(1, match.length - 1).split(` `)
        //     .filter(item => !!item)
        //     .map(item => item.replaceAll(`"`, ``))
        //     .map(item => ini.safe(item)).join('.')}]`
        return (match.replaceAll(`"`, ``).replaceAll('.', '$dot$').replace(/[ \t]+/g, '.'))
    });
}

function readGitConfig(configPath: PathLike) {
    // 读取.git/config文件
    let configContent = ''
    let gitConfig: Repo = null

    // const prefixes = ['remote', 'branch', 'submodule']
    try {
        configContent = fs.readFileSync(configPath, 'utf-8')
        // 解析ini内容为对象
        gitConfig = ini.parse(fixSectionName(configContent)) as any;
        // Object.keys(gitConfig).map((key) => {
        //     let prefix = prefixes.find(prefix => key.startsWith(prefix))
        //     if (prefix) {
        //         let subKey = extractQuotedValue(key);
        //         if (subKey) {
        //             if (!gitConfig[prefix]) {
        //                 gitConfig[prefix] = {}
        //             }
        //             gitConfig[prefix][subKey] = extend({}, gitConfig[prefix][subKey], gitConfig[key])
        //             delete gitConfig[key];
        //         }
        //     }
        // })
        gitConfig.name = (
            gitConfig.remote?.origin?.url ||
            gitConfig.remote?.upstream?.url ||
            (gitConfig.remote ? Object.values(gitConfig.remote).findLast(v => v.url)?.url : '/unknown')
        )?.split('/')?.pop();
        if (gitConfig.name == 'unknown') {
            console.error('git config would be wrong!')
            console.error(' ', 'file path:', configPath)
            console.error(' ', 'config Content', configContent)
            console.error(' ', 'git config:', gitConfig)
        }

        return gitConfig;
    } catch (err) {
        console.error('error on reading:', configPath, 'content:', configContent, 'error:', err.message, ',', err.stack)
        return {
            name: 'unknown',
            desc: `error:${err.message}.${err.stack}. file:${configPath}. content:${configContent}. gitConfig: ${JSON.stringify(gitConfig)}`
        }
    }

}


const gitConfigPath = path.join(`C:/ScriptsApplications/code-front/vite-templates`, `.git`, 'config');
const test = `[core]
	repositoryformatversion = 0
	filemode = false
	bare = false
	logallrefupdates = true
	ignorecase = true
[remote "origin"]
	url = https://github.com/niubilitynetcore/EmitMapper.git
	fetch = +refs/heads/*:refs/remotes/origin/*
	pushurl = https://github.com/niubilitynetcore/EmitMapper.git
[branch "master"]
	remote = origin
	merge = refs/heads/master
[remote "origin2"]
	url = https://gitee.com/code-shelter/EmitMapper.git
	fetch = +refs/heads/*:refs/remotes/origin2/*
[branch "net8.0"]
	remote = origin
	merge = refs/heads/net8.0`
// console.log(fixSectionName(test))