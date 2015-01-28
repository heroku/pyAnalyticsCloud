from unittest import TestCase

class TestImport(TestCase):
    def test_db_import(self):
        from analyticscloud.importers import db

        self.assertIn('metadata_dict', db.__dict__)

    def test_uploader(self):
        from analyticscloud import uploader

        self.assertIn('AnalyticsCloudUploader', uploader.__dict__)
