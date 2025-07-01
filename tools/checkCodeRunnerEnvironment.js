import path from 'path'
import process from 'process'
import JSON5 from 'json5'
import { glob } from 'glob'
import fs from 'fs-extra'
import { deepmerge } from "deepmerge-ts";
import crypto from 'crypto'

function calculatesha256(str) {
  // 创建 MD5 哈希对象
  const hash = crypto.createHash('sha256');

  // 更新哈希内容为输入字符串
  hash.update(str);

  // 计算哈希值并转换为十六进制字符串
  return hash.digest('hex');
}
// import _ from 'lodash'
function parseJsonWithComments(jsonString) {
  return JSON5.parse(jsonString)
}

async function readFileToJson(filePath) {
  if (!fs.existsSync(filePath))
    return null
  console.log("🚀 ~ readFileToJson:", path.resolve(process.cwd(), filePath))
  const fileContent = fs.readFileSync(path.resolve(filePath), 'utf8')
  // console.log('配置内容：', fileContent)
  const jsonObject = parseJsonWithComments(fileContent)
  return jsonObject
}

async function writeJsonToFile(filePath, jsonObject, isJson5 = false) {
  let content
  if (isJson5) {
    // content = JSON5.stringify(jsonObject, {
    //   space: 2,
    //   quote: '"',
    //   // enableSingleQuote: false
    // })
    content = JSON.stringify(jsonObject, null, 2)
  }
  else {
    content = JSON.stringify(jsonObject, null, 2)
  }
  if (content != await fs.promises.readFile(filePath, 'utf8')) {
    await fs.promises.writeFile(filePath, content, 'utf8')
  }

  return jsonObject
}
async function _findInstalledExtensions(data) {
  const extensions = parseJsonWithComments(data.extensions)
  const ids = []
  for (let i = 0, n = extensions.length; i < n; i++) {
    const m = extensions[i]
    if (!m.disabled) {
      ids.push(m.identifier.id)
    }
  }
  return ids
}

function createNewSettings(settingsFilePath, newSettings) {
  return fs.ensureFile(settingsFilePath)
    .then(async (_) => {
      await writeJsonToFile(settingsFilePath, newSettings, false)
      return newSettings
    })
}

function tryMerge(currSettings, newSettings) {
  const merged = deepmerge(currSettings, newSettings)
  return merged
}

console.log('-----------------------------', 'start', '-----------------------------')
const codeWorkspacePath = '../**/*.code-workspace'
const vscodeSettingsPath = path.resolve(process.cwd(), '../.vscode/settings.json')
const vscodeExtensionsPath = path.resolve(process.cwd(), '../.vscode/extensions.json')
function main() {
  const defaultSettings = {
    'code-runner.executorMap': {
      typescript: 'cd $dir && npx tsx $fullFileName'
    },
    'code-runner.executorMapByFileExtension': {
      '.ts': 'cd $dir && npx tsx $fullFileName'
    }
  }
  let handle
  if (fs.existsSync(vscodeSettingsPath)) {
    handle = readFileToJson(vscodeSettingsPath)
      .then((vscodeSettings) => {
        return tryMerge(vscodeSettings, defaultSettings)
      })
      .then(async (vscodeSettings) => {
        // console.log("🚀 ~ .then ~ vscodeSettings:", vscodeSettings)
        await writeJsonToFile(vscodeSettingsPath, vscodeSettings, false)
        return vscodeSettings
      })
  }
  else {
    console.log("🚀 ~ main ~ ", vscodeSettingsPath, " not found, created with default")
    handle = Promise.resolve(createNewSettings(vscodeSettingsPath, defaultSettings))
  }

  handle
    .then(async (vscodeSettings) => {
      return {
        workspaceFiles: await glob(codeWorkspacePath, { cwd: process.cwd(), absolute: true }),
        vscodeSettings,
        vscodeExtensions: await readFileToJson(vscodeExtensionsPath)
      }
    })
    .then(async ({ workspaceFiles, vscodeSettings, vscodeExtensions }) => {
      console.log("🚀 ~ .all workspace ~ files:", workspaceFiles)
      if (workspaceFiles && workspaceFiles.length > 0) {
        for (const workspaceFilePath of workspaceFiles) {
          if (fs.existsSync(workspaceFilePath)) {
            const workspaceObject = await readFileToJson(workspaceFilePath)
            const workspaceSettings = workspaceObject?.settings
            const workspaceExtensions = workspaceObject?.extensions
            if (workspaceSettings) {
              let mergedSettings = tryMerge(vscodeSettings, workspaceSettings)
              workspaceObject.settings = mergedSettings
              let mergedExtensions = tryMerge(vscodeExtensions, workspaceExtensions)
              workspaceObject.extensions = mergedExtensions
              await writeJsonToFile(workspaceFilePath, workspaceObject, true)
              console.log('--------------------------  overrided file:', workspaceFilePath, '-----------------------------  ')

              await writeJsonToFile(vscodeSettingsPath, mergedSettings, true)
              console.log('--------------------------  overrided file:', vscodeSettingsPath, '-----------------------------  ')
              await writeJsonToFile(vscodeExtensionsPath, mergedExtensions, true)
              console.log('--------------------------  overrided file:', vscodeExtensionsPath, '-----------------------------  ')

            }
          }
          else {
            console.log('--------------------------  no file:', workspaceFilePath, '-----------------------------  ')
          }
        }
      }
      else {

        console.log('----  no code-workspace file found', 'root:', process.cwd(), 'pattern:', codeWorkspacePath, '-----------------------------  ')
      }
    })
    .then(() => console.log('-----------------------------  over  -----------------------------'))
    .catch(err => console.error(err))
}

main()
