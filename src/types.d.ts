
import { Low } from 'lowdb';
import * as semver from 'semver';

export type Repos = Record<string, Repo | undefined>

export type Proccessor = {
    name: string;
    shouldBackup(ctx: Context): Promise<boolean>;
    backupRepo(ctx: Context): Promise<Repo>;

    shouldRestore(ctx: Context, repo: Repo): Promise<boolean>;
    restoreRepo(ctx: Context, repo: Repo): Promise<boolean>;
}
export type Factory = Set<Proccessor>;
export type Warnnig = {}
export type Db = {
    __version?: string;
    repos?: Repos;
}
export type Context = {
    curDirFullPath: string;
    db: Low<Db>;
    rootDirFullPath: string;
}
export interface MergeOptions {
    // 如果为 true，则进行深度合并，否则仅浅层合并
    deep?: boolean;
}
export type Remote = {
    url: string;
    pushurl?: string;
    // fetch?: string;
}
export type ModulePath = {
    active?: boolean;
    url: string;
}
export type Submodule = {
    [path: string]: ModulePath
};


export type Remotes = Record<string, Remote>;

export type Repo = {
    name: string;
    __processorName?: string;
    desc?: string; // optional description of the repository
    remote?: Remotes;
    submodule?: Submodule;
    isPull?: boolean;
    fromPaths?: Record<string, string[]>;
} // optional list of remote repositories

export type Pattern = {
    pattern?: RegExp,
    keys: string[]
}