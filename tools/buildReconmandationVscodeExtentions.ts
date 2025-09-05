// 使用code code runner 运行此脚本，生成推荐插件id列表。
// code runner需要 pnpm add -D ts-node -w
// 并且  需要设置code runner执行环境为
/*
    "code-runner.executorMap": {
      "typescript": "cd $dir && node --es-module-specifier-resolution=node --loader ts-node/esm $fullFileName",
      "javascript": "cd $dir && node  --es-module-specifier-resolution=node  $fullFileName"
    },
    //或者使用如下 tsx包 来运行，需安装 pnpm add -D tsx -w
    "code-runner.executorMap": {
      "typescript": "cd $dir && npx tsx $fullFileName",
    },

    "code-runner.executorMap": {
    "typescript": "cd $dir && npx tsx $fullFileName"
    }

    "code-runner.executorMapByFileExtension": {
    ".ts": "cd $dir && npx tsx $fullFileName"
    }
  */
// 最后将输出内容复制到code-workspace的对应位置
import * as fs from 'node:fs'
import { execSync } from 'child_process'
import JSON5 from 'json5'
import { glob } from 'glob'
function _getGitRoot(): string {
  try {
    const gitRoot = execSync('git rev-parse --show-toplevel').toString().trim()
    return gitRoot
  }
  catch (error) {
    console.error('Failed to get Git root directory. This might not be a Git repository.', error)
    throw error
  }
}

function parseJsonWithComments(jsonString: string) {
  return JSON5.parse(jsonString)
}

async function readFileToJson(filePath: string): Promise<Record<string, any>> {
  if (!fs.existsSync(filePath))
    return {}
  const fileContent = await fs.promises.readFile(filePath, 'utf8')
  const jsonObject = parseJsonWithComments(fileContent)
  return jsonObject
}

async function writeJsonToFile(filePath: string, target: object): Promise<void> {
  const content = JSON.stringify(target, null, '  ')
  if (content != await fs.promises.readFile(filePath, 'utf8')) {
    await fs.promises.writeFile(filePath, content, 'utf8')
  }
  console.log(`JSON data has been successfully written to ${filePath}`)
}
async function findInstalledExtensions(data): Promise<string[]> {
  const extensions = parseJsonWithComments(data.extensions) as Array<any>
  const ids = []
  for (let i = 0, n = extensions.length; i < n; i++) {
    const m = extensions[i]
    if (!m.disabled) {
      ids.push(m.identifier.id)
    }
  }
  return ids
}

console.log('-----------------------------', 'start', '-----------------------------')
const codeProfile = './tswindows.code-profile'

const vscodeExtensionsPattern = './**/.vscode/extensions.json'
const vscodeExtensions = await glob(vscodeExtensionsPattern, { cwd: process.cwd(), absolute: true })

const codeWorkspacePathPattern = '../**/*.code-workspace'
const codeWorkspacePaths = await glob(codeWorkspacePathPattern, { cwd: process.cwd(), absolute: true })

readFileToJson(codeProfile)
  .then(async (data) => {
    return await findInstalledExtensions(data)
  })
  .then(async (ids) => {

    codeWorkspacePaths.forEach(async (codeWorkspace) => {
      if (fs.existsSync(codeWorkspace)) {
        const target = await readFileToJson(codeWorkspace)
        target.extensions.recommendations = ids
        await writeJsonToFile(codeWorkspace, target)
      }
    })
    return ids
  })
  .then(async (ids) => {
    vscodeExtensions.forEach(async (extensionWorkspace) => {
      if (!fs.existsSync(extensionWorkspace))
        fs.writeFileSync(extensionWorkspace, '{}')
      const target = await readFileToJson(extensionWorkspace)
      target.recommendations = ids
      await writeJsonToFile(extensionWorkspace, target)
    })

    return { ids }
  })
  // .catch(err => console.error(err))
  .then(_ => console.log('-----------------------------', 'end', '-----------------------------'))
