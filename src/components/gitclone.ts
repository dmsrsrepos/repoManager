import { exec, execSync } from 'child_process';
import { Repo } from '../types';
import fs from 'node:fs';

// 创建一个异步函数来执行git clone命令
export function gitClone(repo: Repo, targetDir: string) {
    if (repo.remote)
        Object.entries(repo.remote)
            .map(([name, remoteConfig]) => {
                console.log(`=====`)
                console.log(`Restore... ${name} = ${remoteConfig.url} to ${targetDir}`);
                return cloneOrAddRemote(targetDir, name, remoteConfig.url)
            })
}

function executeCommand(command: string) {
    console.log("🚀 ~ executeCommand:", command)
    return execSync(command, { encoding: 'utf-8' }).trim();
}

function repositoryExistsAtPath(repoPath: string): boolean {
    try {
        if (fs.existsSync(repoPath)) {
            executeCommand(`cd ${repoPath} && git rev-parse --git-dir`);
            return true;
        }
        return false;
    } catch (error) {
        return false;
    }
}

function addRemoteIfNotExists(repoPath: string, remoteName: string, remoteUrl: string) {
    const existingRemotes = executeCommand(`cd ${repoPath} && git remote -v`).split('\n');
    if (!existingRemotes.some(remote => remote.includes(`${remoteUrl}`))) {
        console.log(`Adding remote...`);
        while (true) {
            try {
                let result = executeCommand(`cd ${repoPath} && git remote add ${remoteName} ${remoteUrl}`);
                return result;
            } catch (errr) {
                remoteName = remoteName + '1';
            }
        }
    } else {
        let msg = `Ignored. Remote ${remoteName} already exists with URL  = ${remoteUrl}.`
        // console.log(msg);
        return msg;
    }
}

function cloneOrAddRemote(repoPath: string, remoteName: string, remoteUrl: string) {
    if (!repositoryExistsAtPath(repoPath)) {

        try {
            console.log(`Cloning...`);
            return executeCommand(`git clone ${remoteUrl} ${repoPath} -o ${remoteName}`);

        } catch (error) {
            return JSON.stringify(error);
        }
    } else {
        return addRemoteIfNotExists(repoPath, remoteName, remoteUrl);
    }
}

const targetDirectory = './../../my-repo';
const repositoryUrl = {
    "name": "vue3_vite_ts.git",
    "core": {
        "repositoryformatversion": "0",
        "filemode": false,
        "bare": false,
        "logallrefupdates": true,
        "symlinks": false,
        "ignorecase": true
    },
    "remote": {
        "origin": {
            "url": "https://gitee.com/cnjimbo/vite-templates.git",
            "fetch": "+refs/heads/*:refs/remotes/origin/*"
        }
    },
    "branch": {
        "master": {
            "remote": "origin",
            "merge": "refs/heads/master"
        }
    },
    "submodule": {
        "js_geeker-admin": {
            "active": true,
            "url": "https://gitee.com/HalseySpicy/Geeker-Admin.git"
        },
        "vue-admin-template": {
            "url": "https://gitee.com/panjiachen/vue-admin-template.git",
            "active": true
        },
        "js_react-admin-template": {
            "active": true,
            "url": "https://gitee.com/asdadsaf/react-admin-template.git"
        },
        "jpure-admin-thin": {
            "active": true,
            "url": "https://gitee.com/yiming_chang/pure-admin-thin.git"
        },
        "vite-plugin-cdn-import-async": {
            "active": true,
            "url": "https://github.com/VaJoy/vite-plugin-cdn-import-async.git"
        },
        "vite_Vue3-TDesign-admin": {
            "active": true,
            "url": "https://github.com/WaliAblikim/Vue3-TDesign-admin.git"
        },
        "vite_admin-boilerplate": {
            "active": true,
            "url": "https://github.com/hiliyongke/vue3-admin-boilerplate.git"
        },
        "vue-pure-admin": {
            "active": true,
            "url": "https://gitee.com/yiming_chang/vue-pure-admin.git"
        },
        "vue3-vite-ts": {
            "active": true,
            "url": "https://gitee.com/spiketyke/vue3_vite_ts.git"
        }
    }
};
const REMOTE_REPO_URL = "https://gitee.com/spiketyke/vue3_vite_ts.git";

// 调用函数执行git clone
function test_clone() {
    gitClone(repositoryUrl, targetDirectory)
    // .then(() => console.log('Clone completed successfully.'))
    // .catch(err => console.error('Error during cloning:', err));
}

// test_clone()