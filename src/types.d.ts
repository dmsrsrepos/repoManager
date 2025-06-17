
import { Low } from 'lowdb';
import semver from 'semver';


export type Repos = {
    [dir: string]: Repo;
} & { "__version"?: semver; };

export type Proccessor = {
    name: string;
    shouldBackup(ctx: Context): Promise<boolean>;
    backupRepo(ctx: Context): Promise<Repo>;

    shouldRestore(ctx: Context, repo: Repo): Promise<boolean>;
    restoreRepo(ctx: Context, repo: Repo): Promise<boolean>;
}
export type Factory = Set<Proccessor>;
export type Context = {
    curDir: string;
    db: Low<Repos>;
    rootDir: string;
}
export interface MergeOptions {
    // 如果为 true，则进行深度合并，否则仅浅层合并
    deep?: boolean;
}
export type Remote = {
    url: string;
    pushurl?: string;
    fetch?: string;
} & {}
export type Submodule = {
    [path: string]: {
        active?: boolean;
        url: string;
    }
};
export type Repo = {
    name: string;
    __processorName?: string;
    desc?: string; // optional description of the repository
    remote?: {
        origin?: Remote;
    } & {
        [name: string]: Remote
    };
    submodule?: Submodule
} & {}; // optional list of remote repositories
