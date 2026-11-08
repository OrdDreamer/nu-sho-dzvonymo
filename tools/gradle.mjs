// Runs the Gradle wrapper from android/ on any OS: node tools/gradle.mjs assembleDebug
import { spawnSync } from 'node:child_process';

const win = process.platform === 'win32';
const r = spawnSync(win ? '.\\gradlew.bat' : './gradlew', process.argv.slice(2), { cwd: 'android', stdio: 'inherit', shell: win });
process.exit(r.status ?? 1);
