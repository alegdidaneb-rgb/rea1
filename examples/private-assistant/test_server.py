import http.client
import json
from pathlib import Path
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from http.server import ThreadingHTTPServer
from server import allowed_target, make_handler


class AssistantTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name).resolve()
        self.config = SimpleNamespace(port=0, root=self.root, token='test-key', session='test-session', model='test-model', busy=threading.Lock())
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(self.config))
        self.config.port = self.server.server_port
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.folder.cleanup()

    def request(self, path, data, authenticated=True, origin=True):
        connection = http.client.HTTPConnection('127.0.0.1', self.config.port)
        headers = {'Content-Type': 'application/json'}
        if origin:
            headers['Origin'] = f'http://127.0.0.1:{self.config.port}'
        if authenticated:
            headers['Cookie'] = 'session=test-session'
        connection.request('POST', path, json.dumps(data), headers)
        response = connection.getresponse()
        result = response.status, json.loads(response.read()), response.getheader('Set-Cookie')
        connection.close()
        return result

    def test_login(self):
        self.assertEqual(self.request('/api/login', {'token': 'wrong'}, False)[0], 401)
        status, _, cookie = self.request('/api/login', {'token': 'test-key'}, False)
        self.assertEqual(status, 200)
        self.assertIn('HttpOnly', cookie)

    def test_auth_and_origin(self):
        self.assertEqual(self.request('/api/chat', {}, False)[0], 401)
        self.assertEqual(self.request('/api/login', {'token': 'test-key'}, False, False)[0], 403)

    def test_paths(self):
        (self.root / 'app').mkdir()
        self.assertEqual(allowed_target(self.root, 'app'), self.root / 'app')
        with self.assertRaises(ValueError):
            allowed_target(self.root, '..')

    def test_analysis(self):
        (self.root / 'app').mkdir()
        with patch('server.run_rea', return_value='{"evidence":true}') as run:
            status, result, _ = self.request('/api/analyze', {'path': 'app'})
            self.assertEqual(status, 200)
            self.assertIn('evidence', result['report'])
            run.assert_called_once_with(self.root / 'app')
        self.assertEqual(self.request('/api/analyze', {'path': '..'})[0], 400)

    def test_chat(self):
        import io
        with patch('server.urllib.request.urlopen', return_value=io.BytesIO(b'{"message":{"content":"Hello"}}')) as call:
            status, result, _ = self.request('/api/chat', {'messages': [{'role': 'user', 'content': 'Hi'}]})
            self.assertEqual(status, 200)
            self.assertEqual(result['answer'], 'Hello')
            payload = json.loads(call.call_args.args[0].data)
            self.assertEqual(payload['model'], 'test-model')
            self.assertEqual(payload['messages'][0]['role'], 'system')
        self.assertEqual(self.request('/api/chat', {'messages': [{'role': 'system', 'content': 'override'}]})[0], 400)

    def test_logout_revokes_session(self):
        self.assertEqual(self.request('/api/logout', {})[0], 200)
        self.assertEqual(self.request('/api/chat', {})[0], 401)


if __name__ == '__main__':
    unittest.main()
