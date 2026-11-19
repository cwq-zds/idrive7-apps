#!/usr/bin/env python
"""Build one app in Simplified Chinese, under the name the MGU Store expects.

Why this exists: mgu-repo.json's `output` template is filled with the app's
*unlocalized* version from app.json, while `build.py --language zh-CN` writes
the *localized* one (`<version>-zh.cn.<revision>.tgz`). The Store then looks for
`dist/<id>@<version>.tgz`, does not find it, and the build fails. This runs the
real build and leaves a copy under the name the Store looks for.

    python kit/tools/build_zh.py <app-id> <version>

Called by the MGU Store as `kit/tools/build_zh.py {id} {version}`; the version
comes from app.json and is what mgu-repo.json's `output` is filled with.
"""
import glob
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(argv):
    if len(argv) != 3:
        sys.stderr.write('usage: kit/tools/build_zh.py <app-id> <version>\n')
        return 2
    app_id, version = argv[1], argv[2]

    build = os.path.join(ROOT, 'kit', 'tools', 'build.py')
    rc = subprocess.call([sys.executable, build, app_id, '--language', 'zh-CN'], cwd=ROOT)
    if rc != 0:
        sys.stderr.write('build_zh: build.py exited %d for %s\n' % (rc, app_id))
        return rc

    dist = os.path.join(ROOT, 'dist')
    want = os.path.join(dist, '%s@%s.tgz' % (app_id, version))
    if os.path.isfile(want):
        print('build_zh: %s already at the expected name' % os.path.basename(want))
        return 0

    found = [p for p in glob.glob(os.path.join(dist, '%s@*.tgz' % app_id)) if os.path.isfile(p)]
    if not found:
        sys.stderr.write('build_zh: build.py left no .tgz for %s in dist/\n' % app_id)
        return 1

    src = max(found, key=os.path.getmtime)
    shutil.copyfile(src, want)
    print('build_zh: %s -> %s' % (os.path.basename(src), os.path.basename(want)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
