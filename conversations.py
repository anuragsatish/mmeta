import json
from typing import Optional
import unittest

from api_base_class import ApiBaseClass
from endpoints import Defaults, Conversations, hierarchy

log = None


class ConversationsTesting(ApiBaseClass):
    def setUp(self) -> None:
        super().setUp()
        global log
        log = self.log
        log.setLevel(self.args.log_level.upper())
        self.default_login()
        self.conv = Conversations(url=self.args.base_url)
        self.report.column_headers = ["TestCase", "Expected", "Actual", "Reason"]

    def test_conversation_api(self):
        self.fail_count = 0

        self.create_conversation()
        if hasattr(self, "new_conv"):
            self.list_conversations()
            breakpoint()
            self.get_delete_user_specified_conversation("get", self.new_conv["id"])
            self.get_delete_user_specified_conversation("delete", self.new_conv["id"])

        log.info(f"{self.pretty_formatter}Consolidated test report\n")
        log.info(f"\n{self.report}\n")
        self.assertEqual(
            self.fail_count,
            0,
            "Few of the tests had failed please check the consolidated report for failures",
        )

    def create_update_conv_payload(self, **kwargs):
        name = kwargs.get("name", f"name_{self.random_uuid_string()}")
        dp_name = kwargs.get("display_name", f"dp_name_{self.random_uuid_string()}")
        image_url = kwargs.get("image_url", "https://example.com/image.png")
        ttl = kwargs.get("ttl", 60)
        payload = {
            "name": name,
            "display_name": dp_name,
            "image_url": image_url,
            "properties": {"ttl": ttl},
        }
        return payload

    def create_conversation(self):
        tc_msg = "Create a new conversation"
        log.info(self.pretty_formatter)
        log.info(self.start_tc % tc_msg)
        test_matrix = ["create_conversation", "Pass"]

        try:
            payload = self.create_update_conv_payload()
            http_resp = self.session.post(
                self.conv.conversations, data=json.dumps(payload)
            )
            eval_http, resp = self.validate_without_assert(
                http_resp, self.mismatched_http_resp
            )
            if not eval_http:
                fail_msg = "Unable to create a conversation"
                log.error(fail_msg)
                test_matrix.extend(["Fail", fail_msg])
            else:
                log.info("User able to create a conversation successfully")
                self.new_conv = resp
                test_matrix.extend(["Pass", None])
        except Exception:
            log.exception(self.exception_msg)
            test_matrix.extend(["Fail", self.exception_msg])

        self.report.append_row(test_matrix)
        log.info(self.end_tc % tc_msg)

    def list_conversations(self):
        tc_msg = "List all available conversations"
        log.info(self.pretty_formatter)
        log.info(self.start_tc % tc_msg)
        test_matrix = ["list_conversations", "Pass"]

        try:
            http_resp = self.session.get(self.conv.conversations)
            eval_http, resp = self.validate_without_assert(
                http_resp, self.mismatched_http_resp
            )
            if not eval_http:
                fail_msg = f"Unable to {tc_msg.lower()}"
                log.error(fail_msg)
                test_matrix.extend(["Fail", fail_msg])
            else:
                log.info(f"User able to {tc_msg.lower()} successfully")
                test_matrix.extend(["Pass", None])
        except Exception:
            log.exception(self.exception_msg)
            test_matrix.extend(["Fail", self.exception_msg])

        self.report.append_row(test_matrix)
        log.info(self.end_tc % tc_msg)

    def get_delete_user_specified_conversation(self, crud: str, conv_id: str) -> None:
        parent_msg = "Fetch" if crud == "get" else "Delete"
        tc_msg = f"{parent_msg} user specified conversation using id"
        log.info(self.pretty_formatter)
        log.info(self.start_tc % tc_msg)
        test_matrix = [f"{parent_msg.lower()}_user_specified_conversation", "Pass"]

        try:
            url = hierarchy(self.conv.conversations, conv_id)
            http_method_request = getattr(self.session, crud)
            http_resp = http_method_request(url)
            eval_http, resp = self.validate_without_assert(
                http_resp, self.mismatched_http_resp
            )
            if not eval_http:
                fail_msg = f"Unable to {tc_msg.lower()}"
                log.error(fail_msg)
                test_matrix.extend(["Fail", fail_msg])
            else:
                log.info(f"User able to {tc_msg.lower()} successfully")
                test_matrix.extend(["Pass", None])
        except Exception:
            log.exception(self.exception_msg)
            test_matrix.extend(["Fail", self.exception_msg])

        self.report.append_row(test_matrix)
        log.info(self.end_tc % tc_msg)


if __name__ == "__main__":
    unittest.main()
