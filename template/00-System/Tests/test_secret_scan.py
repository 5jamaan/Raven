import unittest,sys,json,io,contextlib
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Scripts'))
import brain,secret_scan
class PolicyDigestScanTests(unittest.TestCase):
    def scan(self,data,name='00-System/Config/settings.json'):
        def output(command,**kwargs):
            return name.encode()+b'\0' if command[1]=='diff' else json.dumps(data).encode()
        with patch.object(secret_scan.subprocess,'check_output',side_effect=output),contextlib.redirect_stdout(io.StringIO()):
            return secret_scan.scan()
    def test_current_public_policy_digest_is_allowed(self):
        self.assertEqual(self.scan({'mem0':{'policy_approval':brain.policy_hash()}}),0)
    def test_other_secret_is_still_blocked(self):
        self.assertEqual(self.scan({'mem0':{'policy_approval':brain.policy_hash()},'other':'sk-'+('fakeTEST9'*7)}),1)
    def test_unrecognized_digest_is_blocked(self):
        self.assertEqual(self.scan({'mem0':{'policy_approval':'a'*64}}),1)
    def test_digest_in_unapproved_file_is_blocked(self):
        self.assertEqual(self.scan({'mem0':{'policy_approval':brain.policy_hash()}},'other.json'),1)
if __name__=='__main__':unittest.main()
