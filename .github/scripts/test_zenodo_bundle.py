"""Offline tests for reproducible Zenodo source bundles."""

import importlib.util
import io
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch


spec = importlib.util.spec_from_file_location(
    "zenodo_release", Path(__file__).with_name("zenodo_release.py")
)
z = importlib.util.module_from_spec(spec)
spec.loader.exec_module(z)


class BundleTests(unittest.TestCase):
    def test_bundle_is_independent_of_order_and_file_metadata(self):
        root = Path(__file__).resolve().parents[2]
        files = [root / "CITATION.cff", root / "README.md"]
        buffers = []
        real_zip = zipfile.ZipFile

        def capture(*args, **kwargs):
            output = io.BytesIO()
            buffers.append(output)
            return real_zip(output, *args[1:], **kwargs)

        with patch.object(z.zipfile, "ZipFile", side_effect=capture):
            z.write_bundle(files, root / "ignored.zip")
            z.write_bundle(list(reversed(files)), root / "ignored.zip")

        self.assertEqual(buffers[0].getvalue(), buffers[1].getvalue())
        with real_zip(io.BytesIO(buffers[0].getvalue())) as archive:
            self.assertEqual(archive.namelist(), ["CITATION.cff", "README.md"])
            for entry in archive.infolist():
                self.assertEqual(entry.date_time, (1980, 1, 1, 0, 0, 0))
                self.assertEqual(entry.external_attr >> 16, 0o100644)
                self.assertEqual(archive.read(entry), (root / entry.filename).read_bytes())


if __name__ == "__main__":
    unittest.main()
