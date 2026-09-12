import unittest,tempfile,json,sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Scripts'))
import brain
class LifecycleEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='RavenOS-proof-test-')
        self.addCleanup(self.tmp.cleanup)
        p=patch.object(brain,'STATE',Path(self.tmp.name));p.start();self.addCleanup(p.stop)
        p=patch.object(brain,'lifecycle_signature',return_value={'test':'current'});p.start();self.addCleanup(p.stop)
        self.path=Path(self.tmp.name)/'lifecycle-verification.json'
        self.good={'status':'verified','fingerprints':{'test':'current'},'observed_events':['SessionStart','UserPromptSubmit','Stop']}
    def write(self,data):self.path.write_text(json.dumps(data),encoding='utf-8')
    def test_missing_proof_is_not_success(self):self.assertFalse(brain.lifecycle_verified())
    def test_matching_complete_proof(self):
        self.write(self.good);self.assertTrue(brain.lifecycle_verified())
    def test_old_code_invalidates_proof(self):
        self.write(dict(self.good,fingerprints={'test':'old'}));self.assertFalse(brain.lifecycle_verified())
    def test_incomplete_events_are_not_success(self):
        self.write(dict(self.good,observed_events=['SessionStart']));self.assertFalse(brain.lifecycle_verified())
if __name__=='__main__':unittest.main()
