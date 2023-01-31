import time

import pytest
from requests_cache import CachedSession
from requests_mock import Adapter, ANY

MOCK_PROTOCOL = "http+mock://"

MOCK_URL = MOCK_PROTOCOL + "test.de"


def mount_mock_apater(session: CachedSession) -> CachedSession:
    adapter = get_mock_adapter()
    session.mount(MOCK_PROTOCOL, adapter)
    session.mock_adapter = adapter
    return session


def get_mock_adapter() -> Adapter:
    adapter = Adapter()
    adapter.register_uri(ANY, MOCK_URL,
                         [{"text": "200 Response", "status_code": 200},
                          {"text": "404 Response", "status_code": 404}])
    return adapter


@pytest.fixture
def mocked_session():
    cs = CachedSession(stale_if_error=True, expire_after=1, allowable_codes=[200, 404])
    cs = mount_mock_apater(cs)
    yield cs
    cs.cache.clear()


class TestCachedSession:

    def test_200_404(self, mocked_session):
        result = mocked_session.get(MOCK_URL)
        assert result.status_code == 200
        assert result.from_cache is False

        result = mocked_session.get(MOCK_URL)
        assert result.status_code == 200
        assert result.from_cache is True

        time.sleep(2)

        result = mocked_session.get(MOCK_URL)
        assert result.status_code == 404
        assert result.from_cache is False
