import fs, { PathLike } from "node:fs";
import path from "path";
import * as ini from 'ini'; // 需要先安装ini库，命令：npm install ini
import { Context, Proccessor, Remotes, Repo } from '../types';
import { gitClone } from './gitclone';
import { extend, getMachineKey } from "../utils";

export class GitRepoProcessor implements Proccessor {
    readonly name: string = '.git';
    async shouldRestore(ctx: Context, repo: Repo) {
        return repo?.__processorName === this.name;
    }

    async shouldBackup(ctx: Context) {
        return fs.existsSync(path.join(ctx.curDirFullPath, '.git'));
    }
    async backupRepo(ctx: Context) {
        // 定义一个GitRepo对象，用于存储git库的信息

        console.log(`Backuping... git配置文件：${ctx.curDirFullPath}`)
        let gitConfigPath = path.join(ctx.curDirFullPath, '.git', 'config')

        let repo: Repo = readGitConfig(gitConfigPath, ctx.curDirFullPath.toString().split(path.sep).pop() || 'unknown')
        repo = extend({ __processorName: this.name }, repo)
        repo.fromPaths = { [getMachineKey()]: [ctx.curDirFullPath] }
        return repo;
    }

    async restoreRepo(ctx, repo) {
        gitClone(repo, ctx.curDirFullPath)
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

function readGitConfig(configPath: PathLike, folderName) {
    // 读取.git/config文件
    let configContent = ''
    let gitConfig: Repo = {} as any;
    // const prefixes = ['remote', 'branch', 'submodule']
    try {
        configContent = fs.readFileSync(configPath, 'utf-8')
        // 解析ini内容为对象
        gitConfig = ini.parse(fixSectionName(configContent)) as any;

        gitConfig.name = folderName;
        // if (gitConfig.name == unknownName) {
        //     console.error('git config would be wrong!')
        //     console.error(' ', 'file path:')
        //     console.error('--', ' ', configPath)
        //     console.error('--', 'config Content')
        //     console.error('--', ' ', configContent)
        //     console.error('-', 'git config:')
        //     console.error('--', ' ', gitConfig)
        // }
        const ret = {} as Repo
        ret.name = gitConfig.name
        // ret.__processorName = gitConfig.__processorName
        ret.desc = gitConfig.desc
        ret.remote = gitConfig.remote
        ret.submodule = gitConfig.submodule
        if (ret.remote) {
            Object.entries(ret.remote).forEach(([key, value]) => {
                if (ret.remote)
                    ret.remote[key] = { url: value.url ?? value.pushurl }
            })
        }
        return ret;
    } catch (err) {
        console.error('error on reading:', configPath, 'content:', configContent, 'error:', err.message, ',', err.stack)

        return {
            name: folderName,
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