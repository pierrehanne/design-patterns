"""Regression contracts for fixed behavior, independent of demonstration output."""
import contextlib
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import io
import json
from pathlib import Path
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EncodingTests(unittest.TestCase):
    def test_round_trips_in_both_wrapper_orders(self):
        module = load('decorator', 'structural-design-pattern/decorator-pattern/decorator.py')
        values = json.loads((ROOT / 'tests/decorator_cases.json').read_text())
        pipelines = [
            module.CompressionDecorator(module.StringDataSource()),
            module.EncryptionDecorator(module.CompressionDecorator(module.StringDataSource()), 5),
            module.CompressionDecorator(module.EncryptionDecorator(module.StringDataSource(), 5)),
        ]
        for pipeline in pipelines:
            for value in values:
                with self.subTest(pipeline=type(pipeline).__name__, value=value):
                    self.assertEqual(pipeline.read(pipeline.write(value)), value)

    def test_malformed_records_fail_explicitly(self):
        module = load('decorator', 'structural-design-pattern/decorator-pattern/decorator.py')
        for value in ['1', '0:a', ':a', '-2:a', '2:', '٢:a']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                module.CompressionDecorator._rle_decode(value)


class SingletonTests(unittest.TestCase):
    def test_instance_is_initialized_before_publication(self):
        module = load('singleton', 'creational-design-pattern/singleton-pattern/singleton.py')
        cls = module.ConfigurationManager
        with contextlib.redirect_stdout(io.StringIO()):
            # __new__ publishes the instance; no reader may see missing fields.
            instance = cls.__new__(cls)
            instance.set('before_init', 'preserved')
            instance.__init__()
            self.assertIs(instance, cls())
            self.assertEqual(cls().get('before_init'), 'preserved')

    def test_concurrent_first_use_and_independent_snapshot(self):
        module = load('singleton', 'creational-design-pattern/singleton-pattern/singleton.py')
        barrier = threading.Barrier(24)
        def worker(index):
            barrier.wait(timeout=10)
            config = module.ConfigurationManager()
            config.set(str(index), str(index))
            self.assertEqual(config.get(str(index)), str(index))
            return config
        with contextlib.redirect_stdout(io.StringIO()), ThreadPoolExecutor(max_workers=24) as pool:
            configs = list(pool.map(worker, range(24)))
        self.assertTrue(all(item is configs[0] for item in configs))
        self.assertEqual(len(configs[0].all()), 24)
        snapshot = configs[0].all()
        snapshot.clear()
        self.assertEqual(len(configs[0].all()), 24)


if __name__ == '__main__':
    unittest.main()
