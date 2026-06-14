import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from broker.tssco.client import TsscoClient


class TestTsscoSettingsUnit(unittest.TestCase):
    def test_tssco_client_ignores_masterlink_env_settings(self):
        env_content = "\n".join([
            "MASTERLINK_LOGIN_ID=A123456789",
            "MASTERLINK_LOGIN_PWD=secret",
            "MASTERLINK_CERT_FILE=legacy.p12",
            "MASTERLINK_CERT_PWD=legacy-pass",
        ])

        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env.test"
            env_path.write_text(env_content, encoding="utf-8")

            with patch.dict(os.environ, {}, clear=True):
                with patch("broker.tssco.client.TsscoSettings.get_env_file", return_value=str(env_path)):
                    client = TsscoClient()

        self.assertEqual(client.settings.login_id, "")
        self.assertEqual(client.settings.login_pwd, "")
        self.assertEqual(client.settings.cert_file, "")
        self.assertEqual(client.settings.cert_pwd, "")


if __name__ == "__main__":
    unittest.main()
