from io import StringIO
import sys
from unittest.mock import patch, MagicMock
from mhr import mhr
import unittest


class TestMHRMethods(unittest.TestCase):

    def test_main_missing_input(self):
        with patch('sys.exit', new=MagicMock()) as sysmock:
            with patch('sys.stderr', new=StringIO()) as mock_stderr:
                sys.argv = ["cmd"]
                mhr.main()
                self.assertEqual(mock_stderr.getvalue(), "usage: cmd [-h] artifact\ncmd: error: the following arguments are required: artifact\n")
                sysmock.assert_called_once_with(2)

    def test_main_success(self):
        output = {"foo": "bar"}
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            with patch('mhr.mhr.analyze', new=MagicMock(return_value=output)) as mock:
                sys.argv = ["cmd", "input"]
                mhr.main()
                expected = '{"foo": "bar"}\n'
                self.assertEqual(mock_stdout.getvalue(), expected)
                mock.assert_called_once()

    def test_sendReq(self):
        output = "84af04b8e69682782607a0c5796ca56999eda6b3 1563161433 35"
        hash = "abcd1234"
        server = "hash.cymru.com"
        flags = 0
        options = {"whoishost": server}
        with patch('whois.NICClient.whois_lookup', new=MagicMock(return_value=output)) as mock:
            response = mhr.sendReq(hash)
            mock.assert_called_once_with(options, hash, flags)
            self.assertIsNotNone(response)
            self.assertEqual(response, {"hash": "84af04b8e69682782607a0c5796ca56999eda6b3", "last_seen": "2019-15-07 03:30:33", "av_detection_percentage": 35})

    def test_sendReqNoData(self):
        output = "84af04b8e69682782607a0c5796ca5696b3 NO_DATA"
        hash = "abcd1234"
        server = "hash.cymru.com"
        flags = 0
        options = {"whoishost": server}
        with patch('whois.NICClient.whois_lookup', new=MagicMock(return_value=output)) as mock:
            response = mhr.sendReq(hash)
            mock.assert_called_once_with(options, hash, flags)
            self.assertIsNotNone(response)
            self.assertEqual(response, {"hash": "84af04b8e69682782607a0c5796ca5696b3", "last_seen": "NO_DATA", "av_detection_percentage": 0})

    def test_prepareResults_none(self):
        raw = {"hash": "14af04b8e69682782607a0c5796ca56999eda6b3", "last_seen": "NO_DATA", "av_detection_percentage": 0}
        results = mhr.prepareResults(raw)
        self.assertEqual(results["response"], raw)
        self.assertEqual(results["summary"], "No results found.")
        self.assertEqual(results["status"], "ok")

    def test_prepareResults_harmless(self):
        raw = {"hash": "14af04b8e69682782607a0c5796ca56999eda6b3", "last_seen": "123456", "av_detection_percentage": 0}
        results = mhr.prepareResults(raw)
        self.assertEqual(results["response"], raw)
        self.assertEqual(results["summary"], "harmless")
        self.assertEqual(results["status"], "ok")

    def test_prepareResults_sus(self):
        raw = {"hash": "14af04b8e69682782607a0c5796ca56999eda6b3", "last_seen": "123456", "av_detection_percentage": 1}
        results = mhr.prepareResults(raw)
        self.assertEqual(results["response"], raw)
        self.assertEqual(results["summary"], "suspicious")
        self.assertEqual(results["status"], "caution")

    def test_prepareResults_mal(self):
        raw = {"hash": "14af04b8e69682782607a0c5796ca56999eda6b3", "last_seen": "123456", "av_detection_percentage": 51}
        results = mhr.prepareResults(raw)
        self.assertEqual(results["response"], raw)
        self.assertEqual(results["summary"], "malicious")
        self.assertEqual(results["status"], "threat")

    def test_prepareResults_error(self):
        raw = {}
        results = mhr.prepareResults(raw)
        self.assertEqual(results["response"], raw)
        self.assertEqual(results["summary"], "internal_failure")
        self.assertEqual(results["status"], "caution")

    def test_analyze(self):
        output = {"hash": "14af04b8e69682782607a0c5796ca56999eda6b3", "last_seen": "NO_DATA", "av_detection_percentage": 0}
        artifactInput = '{"value": "14af04b8e69682782607a0c5796ca56999eda6b3", "artifactType": "hash"}'
        with patch('mhr.mhr.sendReq', new=MagicMock(return_value=output)) as mock:
            results = mhr.analyze(artifactInput)
            self.assertEqual(results["summary"], "No results found.")
            mock.assert_called_once()
