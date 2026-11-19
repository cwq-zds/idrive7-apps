#!/usr/bin/env python
"""Build one app in Simplified Chinese, with a version the Store and the
deploy tool accept.

Why this exists: `build.py --language zh-CN` writes the localized version
(`<version>-zh.cn.<revision>`) into the package's package.json and its
rhmiData/application.json. Both the MGU Store and mgu-deploy require a strict
x.y.z version and refuse anything else:

    package.json needs a lower-case name and an x.y.z version   (the Store)
    version is not x.y.z: 2.0.45-zh.cn.2                        (mgu-deploy)

So this runs the real build with package_version overridden to keep the plain
version. The localized texts, the string tables and the translation credit are
untouched: only the version string is kept. dist/<id>@<version>.tgz is then
exactly the file mgu-repo.json's `output` names, so no renaming is needed.

    python kit/tools/build_zh.py <app-id> <version>

Called by the MGU Store as `kit/tools/build_zh.py {id} {version}`.
"""
import json
import os
import sys
import tarfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'kit', 'tools'))

import localize  # noqa: E402  (after sys.path)


def built_version(package):
    """The version the Store and mgu-deploy read: package/package.json."""
    with tarfile.open(package, 'r:gz') as tf:
        member = tf.extractfile('package/package.json')
        if member is None:
            raise SystemExit('build_zh: %s has no package/package.json' % package)
        return json.loads(member.read().decode('utf-8')).get('version')


def main(argv):
    if len(argv) != 3:
        sys.stderr.write('usage: kit/tools/build_zh.py <app-id> <version>\n')
        return 2
    app_id, version = argv[1], argv[2]

    # Keep x.y.z: both the Store and mgu-deploy refuse a localized suffix.
    localize.package_version = lambda v, language: v

    import build  # noqa: E402  (its localize_spec reads the patched function)

    try:
        build.build(app_id, 'zh-CN')
    except SystemExit as e:
        sys.stderr.write('build_zh: %s\n' % e)
        return 1

    package = os.path.join(ROOT, 'dist', '%s@%s.tgz' % (app_id, version))
    if not os.path.isfile(package):
        sys.stderr.write('build_zh: build.py left no %s\n' % os.path.relpath(package, ROOT))
        return 1

    got = built_version(package)
    if got != version:
        sys.stderr.write('build_zh: %s carries version %s, the Store expects %s\n'
                         % (os.path.relpath(package, ROOT), got, version))
        return 1

    print('build_zh: %s %s (zh-CN)' % (app_id, version))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
