import time

import pytest
from requests import Session
from requests_cache import CachedSession
from requests_mock import Adapter, ANY

MOCK_PROTOCOL = "http+mock://"

MOCK_URL = MOCK_PROTOCOL + "test.de"


def mount_mock_adapter(session):
    adapter = Adapter()
    # A call on MOCK_URL should return 200 on the first call and 404 on all following calls.
    adapter.register_uri(ANY, MOCK_URL,
                         [{"text": "200 Response", "status_code": 200},
                          {"text": "404 Response", "status_code": 404}])
    session.mount(MOCK_PROTOCOL, adapter)
    return session


@pytest.fixture
def mocked_cached_session():
    cs = CachedSession(stale_if_error=True, expire_after=5, allowable_codes=[200, 404])
    cs = mount_mock_adapter(cs)
    yield cs
    cs.cache.clear()


@pytest.fixture
def mocked_session():
    s = Session()
    s = mount_mock_adapter(s)
    yield s


class TestCachedSession:

    def test_mock_adapter(self, mocked_session):
        """
        Check if the mock adapter works as expected.
        For this we use a normal session.
        """
        result = mocked_session.get(MOCK_URL)
        assert result.status_code == 200
        result = mocked_session.get(MOCK_URL)
        assert result.status_code == 404
        result = mocked_session.get(MOCK_URL)
        assert result.status_code == 404

    def test_200_404(self, mocked_cached_session):
        result = mocked_cached_session.get(MOCK_URL)  # as the cache is new, a call to MOCK_URL is made, which returns 200
        assert result.status_code == 200
        assert result.from_cache is False  # the result is "fresh"
        assert result.is_expired is False  # the result is "fresh"

        result = mocked_cached_session.get(MOCK_URL)  # as the cache for this request is not expired yet, no new call is made and the cache is returned
        assert result.status_code == 200
        assert result.from_cache is True
        assert result.is_expired is False

        time.sleep(6)  # wait for the cache to expire

        result = mocked_cached_session.get(MOCK_URL)  # as the cache is expired, a new call is made, which returns 404
        assert result.status_code == 404  # 404 should be passed through, as it's in allowable_codes
        assert result.is_expired is False  # The result should not be expired, as the 404 is "fresh"
