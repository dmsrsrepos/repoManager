import { Proccessor } from './types';

import { GitRepoProcessor } from "./GitRepoProcessor";

export let factory: Proccessor[] = [new GitRepoProcessor()];
