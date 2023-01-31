from requests_cache import CachedSession, CachedResponse


class CachedRequester:

    def __init__(self):
        self.cached_session = CachedSession(stale_if_error=True, expire_after=10, allowable_codes=[200, 404])

    def request(self, url) -> CachedResponse:
        return self.cached_session.get(url)


URL = "https://c7320187-66b2-4aff-8620-e50f906147c1.mock.pstmn.io/test?id="

requester = CachedRequester()

while True:
    response = requester.request(URL + "123")
    print(f"{response.status_code} | "
          f"from cache: {response.from_cache} |  "
          f"expired: {response.is_expired} | "
          f"expires at: {response.expires}")
    input()
