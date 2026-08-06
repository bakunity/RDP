import tempfile
import unittest
from pathlib import Path

from hermes_rdp.db import Registry


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.registry = Registry(Path(self.temp.name) / "state.sqlite3", 53389, 53391)

    def tearDown(self):
        self.temp.cleanup()

    def test_pair_register_and_authenticate(self):
        code = self.registry.create_pair_code(display_name="Windows-PC-01", preferred_port=53389)
        pair = self.registry.consume_pair_code(code)
        device, token = self.registry.register_device(
            pair=pair,
            display_name="Ignored",
            machine_name="WINDOWS-PC-01",
            fingerprint="abc",
        )
        self.assertEqual(device["display_name"], "Windows-PC-01")
        self.assertEqual(device["rdp_port"], 53389)
        self.assertIsNotNone(self.registry.authenticate(device["id"], token))
        self.assertIsNone(self.registry.authenticate(device["id"], "wrong"))

    def test_auto_port_allocation(self):
        for expected in (53389, 53390, 53391):
            code = self.registry.create_pair_code()
            pair = self.registry.consume_pair_code(code)
            device, _ = self.registry.register_device(
                pair=pair,
                display_name=f"PC {expected}",
                machine_name=f"PC-{expected}",
                fingerprint="x",
            )
            self.assertEqual(device["rdp_port"], expected)
        with self.assertRaises(RuntimeError):
            self.registry.allocate_port()

    def test_command_lifecycle(self):
        code = self.registry.create_pair_code()
        device, token = self.registry.register_device(
            pair=self.registry.consume_pair_code(code),
            display_name="PC",
            machine_name="PC",
            fingerprint="x",
        )
        seq = self.registry.queue_command(device["id"], "restart")
        command = self.registry.update_telemetry(device["id"], {"cpu_percent": 1})
        self.assertEqual(command["seq"], seq)
        self.assertEqual(command["action"], "restart")
        self.registry.complete_command(device["id"], seq, True, "ok")
        self.assertIsNone(self.registry.pending_command(device["id"]))


if __name__ == "__main__":
    unittest.main()
