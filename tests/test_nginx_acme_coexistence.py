from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class NginxAcmeCoexistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.setup = (ROOT / "scripts/setup-trusted-rdp-cert.sh").read_text(
            encoding="utf-8"
        )

    def test_nginx_listener_uses_webroot_without_stopping_nginx(self) -> None:
        for marker in (
            "configure_nginx_webroot",
            "ACME_MODE=\"nginx-webroot\"",
            "/etc/nginx/conf.d/hermes-rdp-acme.conf",
            "/etc/nginx/sites-enabled/hermes-rdp-acme.conf",
            "server_name $HOST;",
            "location ^~ /.well-known/acme-challenge/",
            "root $ACME_WEBROOT;",
            'systemctl reload nginx',
            '-H "Host: $HOST"',
            '"${AUTH_ARGS[@]}"',
            '--webroot-path "$ACME_WEBROOT"',
            "tcp80=NGINX_WEBROOT",
        ):
            self.assertIn(marker, self.setup)

        self.assertNotIn("systemctl stop nginx", self.setup)
        self.assertNotIn("systemctl restart nginx", self.setup)

    def test_free_port_keeps_standalone_and_other_listeners_fail_closed(self) -> None:
        self.assertIn('ACME_MODE="standalone"', self.setup)
        self.assertIn("TCP 80 is already occupied by a non-nginx service", self.setup)
        self.assertIn('printf \'%s\\n\' --standalone', self.setup)

    def test_nginx_config_is_bounded_and_rolled_back_on_failed_setup(self) -> None:
        for marker in (
            "# Managed by Hermes RDP",
            "Refusing to overwrite unmanaged nginx config",
            "NGINX_CONF_CHANGED=1",
            "NGINX_CONF_PREEXISTED=1",
            "nginx-conf.backup",
            "SETUP_COMPLETE=1",
        ):
            self.assertIn(marker, self.setup)


if __name__ == "__main__":
    unittest.main()
