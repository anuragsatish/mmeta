import unittest

from api_base_class import ApiBaseClass
from endpoints import Defaults, Conversations

log = None


class ConversationsTesting(ApiBaseClass):
    def setUp(self) -> None:
        super().setUp()
        global log
        log = self.log
        log.setLevel(self.args.log_level.upper())
        self.default_login()
        self.conv = Conversations(url=self.args.base_url)

    def test_sample(self):
        log.info("Sample log statement")
        log.info("Another print statement")
        http_resp = self.session.get(self.conv.conversations)
        eval_http, resp = self.validate_without_assert(
            http_resp, self.mismatched_http_resp
        )
        self.assertTrue(eval_http, "Unable to fetch list of conversations")


if __name__ == "__main__":
    unittest.main()
