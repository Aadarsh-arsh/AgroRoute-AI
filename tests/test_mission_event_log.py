import unittest
from agroroute.mission_event_log import MissionEventLog

class MissionEventLogTests(unittest.TestCase):
    def test_record_and_export(self):
        log = MissionEventLog()
        item = log.record("inspection", target="2,3")
        self.assertEqual(item.details, {"target": "2,3"})
        self.assertEqual(log.to_list()[0]["event"], "inspection")

    def test_count_and_clear(self):
        log = MissionEventLog()
        log.record("move")
        log.record("move")
        self.assertEqual(log.count("move"), 2)
        log.clear()
        self.assertEqual(log.events, ())

    def test_empty_event_rejected(self):
        with self.assertRaises(ValueError):
            MissionEventLog().record(" ")

if __name__ == "__main__":
    unittest.main()
