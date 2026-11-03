import json,tempfile,pathlib,unittest,sqlite3
from training import load,import_data,predict
class ImportTests(unittest.TestCase):
 def test_repeat_and_raw_preservation(self):
  with tempfile.TemporaryDirectory() as t:
   p=pathlib.Path(t)/'data.json';raw=b'[{"id":1,"weeks":[],"unknown":{"keep":true}}]';p.write_bytes(raw);db=pathlib.Path(t)/'db'
   import_data(p,db);import_data(p,db)
   with sqlite3.connect(db) as c:
    self.assertEqual(c.execute('select count(*) from mesos').fetchone()[0],1)
    self.assertEqual(c.execute('select raw from imports').fetchone()[0],raw)
 def test_duplicate_rejected(self):
  with tempfile.TemporaryDirectory() as t:
   p=pathlib.Path(t)/'x';p.write_text('[{"id":1,"weeks":[]},{"id":1,"weeks":[]}]')
   with self.assertRaises(ValueError):load(p)
 def test_rounding(self):self.assertEqual(predict(100,.025,2.5),102.5)
if __name__=='__main__':unittest.main()
