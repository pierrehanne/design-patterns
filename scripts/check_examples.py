#!/usr/bin/env python3
"""Compile/run standalone examples and exercise repaired encoding contracts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
EXTENSIONS = {'python': 'py', 'typescript': 'ts', 'rust': 'rs', 'go': 'go'}


def run(command, *, timeout=120):
    result = subprocess.run([str(part) for part in command], cwd=ROOT, text=True,
                            capture_output=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f"{' '.join(map(str, command))}\n{result.stdout}{result.stderr}")
    return result.stdout


def require(tool):
    path = shutil.which(tool)
    if not path:
        raise RuntimeError(f'Required tool not found: {tool}. Install it before running this check.')
    return path


def encoding_regression(language, tmp, compiler=None):
    """Append a small language-native harness without changing the teaching files."""
    ext = EXTENSIONS[language]
    original = ROOT / f'structural-design-pattern/decorator-pattern/decorator.{ext}'
    values = json.loads((ROOT / 'tests/decorator_cases.json').read_text())
    literals = ',\n'.join(json.dumps(value, ensure_ascii=False) for value in values)
    if language == 'typescript':
        harness = '''
for (const value of [VALUES]) {
  const pipelines: DataSource[] = [
    new CompressionDecorator(new StringDataSource()),
    new EncryptionDecorator(new CompressionDecorator(new StringDataSource()), 5),
    new CompressionDecorator(new EncryptionDecorator(new StringDataSource(), 5)),
  ];
  for (const pipeline of pipelines) {
    if (pipeline.read(pipeline.write(value)) !== value) throw new Error(`Round trip failed: ${value}`);
  }
}
'''.replace('VALUES', literals)
        source = tmp / 'decorator_regression.ts'
        source.write_text(original.read_text() + harness)
        # This temporary harness is compiled independently of the repository project.
        run([compiler, '--ignoreConfig', '--strict', '--target', 'ES2022', '--module', 'commonjs', '--outDir', tmp, source])
        run(['node', tmp / 'decorator_regression.js'])
    elif language == 'rust':
        harness = '''
#[test]
fn encoding_round_trips() {
    for value in [VALUES] {
        let pipelines: Vec<Box<dyn DataSource>> = vec![
            Box::new(CompressionDecorator::new(Box::new(StringDataSource))),
            Box::new(EncryptionDecorator::new(Box::new(CompressionDecorator::new(Box::new(StringDataSource))), 5)),
            Box::new(CompressionDecorator::new(Box::new(EncryptionDecorator::new(Box::new(StringDataSource), 5)))),
        ];
        for pipeline in pipelines { assert_eq!(pipeline.read(&pipeline.write(value)), value); }
    }
}
'''.replace('VALUES', literals)
        source = tmp / 'decorator_regression.rs'
        source.write_text(original.read_text() + harness)
        run(['rustc', '--edition=2021', '--test', source, '-o', tmp / 'regression'])
        run([tmp / 'regression'])
    elif language == 'go':
        harness = '''
func init() {
    for _, value := range []string{VALUES,} {
        pipelines := []DataSource{
            NewCompressionDecorator(&StringDataSource{}),
            NewEncryptionDecorator(NewCompressionDecorator(&StringDataSource{}), 5),
            NewCompressionDecorator(NewEncryptionDecorator(&StringDataSource{}, 5)),
        }
        for _, pipeline := range pipelines {
            if pipeline.Read(pipeline.Write(value)) != value { panic("encoding round trip failed") }
        }
    }
}
'''.replace('VALUES', literals)
        source = tmp / 'decorator_regression.go'
        source.write_text(original.read_text() + harness)
        run(['go', 'run', source])


def check(language):
    ext = EXTENSIONS[language]
    files = sorted(ROOT.glob(f'*-design-pattern/*/*.{ext}'))
    if len(files) != 23:
        raise RuntimeError(f'Expected 23 {language} examples; found {len(files)}')
    compiler = None
    if language == 'typescript':
        require('node')
        local = ROOT / 'node_modules/.bin/tsc'
        compiler = str(local) if local.exists() else require('tsc')
    elif language != 'python':
        require({'go': 'go', 'rust': 'rustc'}[language])
    with tempfile.TemporaryDirectory(prefix='design-patterns-') as directory:
        tmp = Path(directory)
        if language == 'typescript':
            run([compiler, '--project', ROOT / 'tsconfig.json', '--outDir', tmp])
        for source in files:
            relative = source.relative_to(ROOT)
            if language == 'python':
                output = run([sys.executable, source])
            elif language == 'typescript':
                output = run(['node', tmp / relative.with_suffix('.js')])
            elif language == 'rust':
                run(['rustc', '--edition=2021', source, '-o', tmp / 'example'])
                output = run([tmp / 'example'])
            else:
                output = run(['go', 'run', source])
            if not output.strip():
                raise RuntimeError(f'Example produced no demonstration output: {relative}')
            print(f'PASS {relative}', flush=True)
        if language == 'python':
            print(run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v']), end='')
        else:
            encoding_regression(language, tmp, compiler)
            if language == 'go':
                run(['go', 'run', '-race', ROOT / 'creational-design-pattern/singleton-pattern/singleton.go'])
    print(f'PASS {language}: 23 runnable examples and regression checks')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language', choices=[*EXTENSIONS, 'all'], default='all')
    args = parser.parse_args()
    try:
        for language in EXTENSIONS if args.language == 'all' else [args.language]:
            check(language)
    except (RuntimeError, subprocess.TimeoutExpired) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
