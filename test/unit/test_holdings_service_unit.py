import builtins
import importlib
import sys
import unittest
from unittest.mock import patch


class TestHoldingsServiceUnit(unittest.TestCase):
    def test_service_import_does_not_require_broker_sdks(self):
        original_import = builtins.__import__

        def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
            blocked = {"taishin_sdk", "fubon_neo"}
            if name in blocked:
                raise ModuleNotFoundError(f"No module named '{name}'")
            return original_import(name, globals, locals, fromlist, level)

        for module_name in [
            "service.holdings_service",
            "broker.tssco.client",
            "broker.fubon.client",
        ]:
            sys.modules.pop(module_name, None)

        with patch("builtins.__import__", side_effect=guarded_import):
            module = importlib.import_module("service.holdings_service")

        service = module.HoldingsService()
        self.assertIsNotNone(service)


if __name__ == "__main__":
    unittest.main()
