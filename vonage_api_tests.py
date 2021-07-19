import json
import random
import unittest

from api_base_class import ApiBaseClass
from endpoints import Defaults, Conversations, hierarchy, User, Member, Event, Leg
from pprint import pformat
from typing import Optional

log = None


class ConversationsTesting(ApiBaseClass):
    """
    Verify Conversations APIs funcionality
    """

    def setUp(self) -> None:
        """
        Initialize the test variables
        """
        super().setUp()
        global log
        log = self.log
        log.setLevel(self.args.log_level.upper())
        self.default_login()
        self.conv_edpt = Conversations(url=self.args.base_url)
        self.user_edpt = User(url=self.args.base_url)
        self.member_edpt = Member(url=self.args.base_url)
        self.event_edpt = Event(url=self.args.base_url)
        self.leg_edpt = Leg(url=self.args.base_url)
        self.report.column_headers = ["TestCase", "Expected", "Actual", "Reason"]

    def test_conversation_api(self) -> None:
        """
        Test all CRUD operations available in conversations api's
        """
        self.fail_count = 0

        self.create_update_conversation("post")
        if hasattr(self, "new_conv"):
            self.create_update_conversation(
                "put", self.new_conv["id"], name=f"name_{self.random_uuid_string()}_v2"
            )
            self.list_conversations()
            # self.record_user_specified_conversation(self.new_conv["id"])
            # self.record_user_specified_conversation(self.new_conv["id"], "stop")
            self.get_delete_user_specified_conversation("get", self.new_conv["id"])
            self.create_update_and_verify_user_details()
            if hasattr(self, "new_user"):
                self.create_update_and_verify_user_details(
                    "put", user_id=self.new_user["id"], channles=self.channel_def()
                )
                self.list_get_delete_user(user_id=self.new_user["id"])
                self.list_get_delete_user("get", user_id=self.new_user["id"])
                self.create_update_and_verify_member(
                    "post",
                    self.new_conv["id"],
                    channel=self.channel_def(from_user=self.new_conv["id"]),
                )
                self.get_delete_leg()
                if hasattr(self, "new_member"):
                    self.create_update_and_verify_member(
                        "put",
                        self.new_conv["id"],
                        self.new_member["id"],
                        action="join",
                        channel=self.channel_def(from_user=self.new_conv["id"]),
                    )
                    self.get_delete_member(
                        "get", self.new_conv["id"], self.new_member["id"]
                    )
                    self.create_event(self.new_conv["id"], self.new_member["id"])
                    if hasattr(self, "new_event"):
                        self.get_delete_event(
                            "get", self.new_conv["id"], self.new_event["id"]
                        )
                        self.get_delete_event(
                            "delete", self.new_conv["id"], self.new_event["id"]
                        )
                    self.get_delete_member(
                        "delete", self.new_conv["id"], self.new_member["id"]
                    )
                self.list_get_delete_user("delete", user_id=self.new_user["id"])

            self.get_delete_user_specified_conversation("delete", self.new_conv["id"])

        log.info(f"{self.pretty_formatter}Consolidated test report\n")
        log.info(f"\n{self.report}\n")
        self.assertEqual(
            self.fail_count,
            0,
            "Few of the tests had failed please check the consolidated report for failures",
        )

    def create_update_conv_payload(self, **kwargs) -> dict:
        """
        Generate payload for create/update conversation
        """
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
        log.info(f"Payload:\n{pformat(payload)}")
        return payload

    def channel_def(
        self,
        leg_id: Optional[str] = None,
        from_user: Optional[dict] = None,
        to_user: Optional[dict] = None,
        do_not_set_leg_id: bool = False,
    ) -> dict:
        """
        Create channels definition for payload
        """
        if leg_id is None:
            leg_id = "a595959595959595995"
        channels = {
            "type": random.choice(Defaults.CHANNELS_LIST),
        }
        if leg_id is not None and not do_not_set_leg_id:
            # if leg_id is not None:
            channels.update(
                {
                    "leg_id": leg_id,
                    "leg_ids": [{"leg_id": leg_id}],
                }
            )
        if from_user:
            channels["from"] = from_user
        if to_user:
            channels["to"] = to_user
        return channels

    def create_update_user_payload(self, **kwargs: dict) -> dict:
        """
        Generate payload for create/update user
        """
        name = kwargs.get("name", f"user_{self.random_uuid_string()}")
        dp_name = kwargs.get(
            "display_name", f"dp_user_name_{self.random_uuid_string()}"
        )
        image_url = kwargs.get("image_url", "https://example.com/image.png")
        payload = {
            "name": name,
            "display_name": dp_name,
            "image_url": image_url,
        }
        channels = kwargs.get("channels", None)
        if channels:
            if channels["type"] not in Defaults.CHANNELS_LIST:
                raise Exception(
                    f"Invalid channel type:{channels['type']} should be one of {Defaults.CHANNELS_LIST}"
                )
            payload["channels"] = channels
        log.info(f"Payload:\n{pformat(payload)}")
        return payload

    def create_update_member_payload(self, **kwargs: dict) -> dict:
        """
        Generate payload for create/update member
        """
        user_id = kwargs.get("user_id", None)
        action = kwargs.get("action", "invite")

        payload = {
            "action": action,
        }

        if user_id:
            payload["user_id"] = user_id

        channel = kwargs.get("channel", None)
        if channel:
            if channel["type"] not in Defaults.CHANNELS_LIST:
                raise Exception(
                    f"Invalid channel type:{channel['type']} should be one of {Defaults.CHANNELS_LIST}"
                )
            payload["channel"] = channel
        log.info(f"Payload:\n{pformat(payload)}")
        return payload

    def create_event_payload(self, **kwargs: dict) -> dict:
        """
        Generate payload for create event
        """
        member_id = kwargs.get("member_id", None)

        payload = {
            "type": "text",
        }

        if member_id is None:
            raise Exception(f"Define valid member-id for creating an event")
        payload["from"] = member_id
        log.info(f"Payload:\n{pformat(payload)}")
        return payload

    def create_update_conversation(
        self, crud: str, conv_id: Optional[str] = None, **kwargs: dict
    ) -> None:
        parent_msg = "Create" if crud == "post" else "Update"
        tc_msg = f"{parent_msg} a conversation"
        log.info(self.pretty_formatter)
        log.info(self.start_tc % tc_msg)
        test_matrix = [f"{parent_msg.lower()}_conversation", "Pass"]

        try:
            payload = self.create_update_conv_payload(**kwargs)
            url = (
                self.conv_edpt.conversations
                if crud == "post"
                else hierarchy(self.conv_edpt.conversations, conv_id)
            )
            http_method_request = getattr(self.session, crud)
            http_resp = http_method_request(url, data=json.dumps(payload))
            eval_http, resp = self.validate_without_assert(
                http_resp, self.mismatched_http_resp
            )
            if not eval_http:
                self.fail_count += 1
                fail_msg = f"Unable to {tc_msg.lower()}"
                log.error(fail_msg)
                test_matrix.extend(["Fail", fail_msg])
            else:
                log.info(f"User able to {tc_msg.lower()} successfully")
                self.new_conv = resp
                test_matrix.extend(["Pass", None])
        except Exception:
            self.fail_count += 1
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
            http_resp = self.session.get(self.conv_edpt.conversations)
            eval_http, resp = self.validate_without_assert(
                http_resp, self.mismatched_http_resp
            )
            if not eval_http:
                self.fail_count += 1
                fail_msg = f"Unable to {tc_msg.lower()}"
                log.error(fail_msg)
                test_matrix.extend(["Fail", fail_msg])
            else:
                log.info(f"User able to {tc_msg.lower()} successfully")
                test_matrix.extend(["Pass", None])
        except Exception:
            self.fail_count += 1
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
            url = hierarchy(self.conv_edpt.conversations, conv_id)
            http_method_request = getattr(self.session, crud)
            http_resp = http_method_request(url)
            eval_http, resp = self.validate_without_assert(
                http_resp, self.mismatched_http_resp
            )
            if not eval_http:
                self.fail_count += 1
                fail_msg = f"Unable to {tc_msg.lower()}"
                log.error(fail_msg)
                test_matrix.extend(["Fail", fail_msg])
            else:
                log.info(f"User able to {tc_msg.lower()} successfully")
                test_matrix.extend(["Pass", None])
        except Exception:
            self.fail_count += 1
            log.exception(self.exception_msg)
            test_matrix.extend(["Fail", self.exception_msg])

        self.report.append_row(test_matrix)
        log.info(self.end_tc % tc_msg)

    def record_user_specified_conversation(
        self, conv_id: str, action: str = "start"
    ) -> None:
        tc_msg = f"Record user specified conversation using id with action:{action}"
        log.info(self.pretty_formatter)
        log.info(self.start_tc % tc_msg)
        test_matrix = [f"record_user_specified_conversation", "Pass"]

        try:
            url = hierarchy(self.conv_edpt.record % conv_id)
            payload = {"action": action}
            http_resp = self.session.put(url, data=json.dumps(payload))
            eval_http, resp = self.validate_without_assert(
                http_resp, self.mismatched_http_resp
            )
            if not eval_http:
                self.fail_count += 1
                fail_msg = f"Unable to {tc_msg.lower()}"
                log.error(fail_msg)
                test_matrix.extend(["Fail", fail_msg])
            else:
                log.info(f"User able to {tc_msg.lower()} successfully")
                test_matrix.extend(["Pass", None])
        except Exception:
            self.fail_count += 1
            log.exception(self.exception_msg)
            test_matrix.extend(["Fail", self.exception_msg])

        self.report.append_row(test_matrix)
        log.info(self.end_tc % tc_msg)

    def create_update_and_verify_user_details(
        self,
        crud: Optional[str] = "post",
        user_id: Optional[str] = None,
        **kwargs: dict,
    ):
        """
        Create and verify user
        """
        parent_msg = "Create" if crud == "post" else "Update"
        tc_msg = f"{parent_msg} and verify user details"
        log.info(self.pretty_formatter)
        log.info(self.start_tc % tc_msg)
        test_matrix = [f"{parent_msg.lower()}_and_verify_user_details", "Pass"]

        try:
            payload = self.create_update_user_payload(**kwargs)
            url = (
                self.user_edpt.users
                if crud == "post"
                else hierarchy(self.user_edpt.users, user_id)
            )
            http_method_request = getattr(self.session, crud)
            http_resp = http_method_request(url, data=json.dumps(payload))
            eval_http, resp = self.validate_without_assert(
                http_resp, self.mismatched_http_resp
            )
            if not eval_http:
                self.fail_count += 1
                fail_msg = f"Unable to {tc_msg.lower()}"
                log.error(fail_msg)
                test_matrix.extend(["Fail", fail_msg])
            else:
                log.info(f"User able to {tc_msg.lower()} successfully")
                self.new_user = resp
                log.info("Fetch user details using id")
                url = hierarchy(self.user_edpt.users, resp["id"])
                http_resp = self.session.get(url)
                eval_http, resp = self.validate_without_assert(
                    http_resp, self.mismatched_http_resp
                )
                if not eval_http:
                    self.fail_count += 1
                    fail_msg = "Unable get user-id details"
                    log.error(fail_msg)
                    test_matrix.extend(["Fail", fail_msg])
                else:
                    log.info("Able to fetch user details")
                    test_matrix.extend(["Pass", None])
        except Exception:
            self.fail_count += 1
            log.exception(self.exception_msg)
            test_matrix.extend(["Fail", self.exception_msg])

        self.report.append_row(test_matrix)
        log.info(self.end_tc % tc_msg)

    def list_get_delete_user(self, op: str = "list", user_id: Optional[str] = None):
        if op == "list":
            tc = "list_user_conversations"
            tc_msg = "List all conversations of a given user"
            pass_msg = (
                f"Able to get entire list of conversations for given user:{user_id}"
            )
            fail_msg = f"Un{pass_msg.lower()}"
            url = hierarchy(self.user_edpt.list_conversations % user_id)
            crud = "get"
        elif op == "get":
            tc = "get_specified_user_details"
            tc_msg = "Get specified user details"
            pass_msg = f"Able to {op} specified user:{user_id} details"
            fail_msg = f"Un{pass_msg.lower()}"
            url = hierarchy(self.user_edpt.users, user_id)
            crud = op
        elif op == "delete":
            tc = "delete_specified_user"
            tc_msg = "Delete specified user"
            pass_msg = f"Able to {op} specified user:{user_id}"
            fail_msg = f"Un{pass_msg.lower()}"
            url = hierarchy(self.user_edpt.users, user_id)
            crud = op

        log.info(self.pretty_formatter)
        log.info(self.start_tc % tc_msg)
        test_matrix = [tc, "Pass"]

        try:
            http_method_request = getattr(self.session, crud)
            http_resp = http_method_request(url)
            eval_http, resp = self.validate_without_assert(
                http_resp, self.mismatched_http_resp
            )
            if not eval_http:
                self.fail_count += 1
                log.error(fail_msg)
                test_matrix.extend(["Fail", fail_msg])
            else:
                log.info(pass_msg)
                test_matrix.extend(["Pass", None])
        except Exception:
            self.fail_count += 1
            log.exception(self.exception_msg)
            test_matrix.extend(["Fail", self.exception_msg])
        self.report.append_row(test_matrix)
        log.info(self.end_tc % tc_msg)

    def create_update_and_verify_member(
        self,
        crud: Optional[str] = "post",
        conv_id: Optional[str] = None,
        member_id: Optional[str] = None,
        **kwargs: dict,
    ):
        """
        Create and verify user
        """
        parent_msg = "Create" if crud == "post" else "Update"
        tc_msg = f"{parent_msg} member details"
        log.info(self.pretty_formatter)
        log.info(self.start_tc % tc_msg)
        test_matrix = [f"{parent_msg.lower()}_and_verify_member_details", "Pass"]

        try:
            if crud == "post":
                payload = self.create_update_member_payload(
                    user_id=self.new_user["id"],
                    action="join",
                    channel=self.channel_def(),
                    from_user={},
                    to_user={},
                )
                url = self.member_edpt.members % conv_id
            elif crud == "put":
                url = hierarchy(self.member_edpt.members % conv_id, member_id)
                payload = self.create_update_member_payload(
                    channel=self.channel_def(), **kwargs
                )
            http_method_request = getattr(self.session, crud)
            http_resp = http_method_request(url, data=json.dumps(payload))
            eval_http, resp = self.validate_without_assert(
                http_resp, self.mismatched_http_resp
            )
            if not eval_http:
                self.fail_count += 1
                fail_msg = f"Unable to {tc_msg.lower()}"
                log.error(fail_msg)
                test_matrix.extend(["Fail", fail_msg])
            else:
                log.info(f"Able to {tc_msg.lower()} successfully")
                self.new_member = resp
                test_matrix.extend(["Pass", None])
        except Exception:
            self.fail_count += 1
            log.exception(self.exception_msg)
            test_matrix.extend(["Fail", self.exception_msg])

        self.report.append_row(test_matrix)
        log.info(self.end_tc % tc_msg)

    def get_delete_member(
        self,
        crud: str = "get",
        conv_id: Optional[str] = None,
        member_id: Optional[str] = None,
    ):
        if crud == "get":
            tc = "get_specified_member_details"
            tc_msg = "Get specified member details"
        elif crud == "delete":
            tc = "delete_specified_member"
            tc_msg = "Delete specified member"

        pass_msg = f"Able to {crud} specified member:{member_id} details"
        fail_msg = f"Un{pass_msg.lower()}"

        log.info(self.pretty_formatter)
        log.info(self.start_tc % tc_msg)
        test_matrix = [tc, "Pass"]

        try:
            url = hierarchy(self.member_edpt.members % conv_id, member_id)
            http_method_request = getattr(self.session, crud)
            http_resp = http_method_request(url)
            eval_http, resp = self.validate_without_assert(
                http_resp, self.mismatched_http_resp
            )
            if not eval_http:
                self.fail_count += 1
                log.error(fail_msg)
                test_matrix.extend(["Fail", fail_msg])
            else:
                log.info(pass_msg)
                test_matrix.extend(["Pass", None])
        except Exception:
            self.fail_count += 1
            log.exception(self.exception_msg)
            test_matrix.extend(["Fail", self.exception_msg])
        self.report.append_row(test_matrix)
        log.info(self.end_tc % tc_msg)

    def create_event(
        self,
        conv_id: Optional[str] = None,
        member_id: Optional[str] = None,
        **kwargs: dict,
    ):
        """
        Create and verify user
        """
        tc_msg = f"Create an event and its details"
        log.info(self.pretty_formatter)
        log.info(self.start_tc % tc_msg)
        test_matrix = [f"create_event", "Pass"]

        try:
            payload = self.create_event_payload(member_id=member_id, **kwargs)
            url = self.event_edpt.events % conv_id
            http_resp = self.session.post(url, data=json.dumps(payload))
            eval_http, resp = self.validate_without_assert(
                http_resp, self.mismatched_http_resp
            )
            if not eval_http:
                self.fail_count += 1
                fail_msg = f"Unable to {tc_msg.lower()}"
                log.error(fail_msg)
                test_matrix.extend(["Fail", fail_msg])
            else:
                log.info(f"Able to {tc_msg.lower()} successfully")
                self.new_event = resp
                test_matrix.extend(["Pass", None])
        except Exception:
            self.fail_count += 1
            log.exception(self.exception_msg)
            test_matrix.extend(["Fail", self.exception_msg])

        self.report.append_row(test_matrix)
        log.info(self.end_tc % tc_msg)

    def get_delete_event(
        self,
        crud: str = "get",
        conv_id: Optional[str] = None,
        event_id: Optional[str] = None,
    ):
        if crud == "get":
            tc = "get_specified_event_details"
            tc_msg = "Get specified event details"
        elif crud == "delete":
            tc = "delete_specified_event"
            tc_msg = "Delete specified event"

        pass_msg = f"Able to {crud} specified event:{event_id} details"
        fail_msg = f"Un{pass_msg.lower()}"

        log.info(self.pretty_formatter)
        log.info(self.start_tc % tc_msg)
        test_matrix = [tc, "Pass"]

        try:
            url = hierarchy(self.event_edpt.events % conv_id, event_id)
            http_method_request = getattr(self.session, crud)
            http_resp = http_method_request(url)
            eval_http, resp = self.validate_without_assert(
                http_resp, self.mismatched_http_resp
            )
            if not eval_http:
                self.fail_count += 1
                log.error(fail_msg)
                test_matrix.extend(["Fail", fail_msg])
            else:
                log.info(pass_msg)
                test_matrix.extend(["Pass", None])
        except Exception:
            self.fail_count += 1
            log.exception(self.exception_msg)
            test_matrix.extend(["Fail", self.exception_msg])
        self.report.append_row(test_matrix)
        log.info(self.end_tc % tc_msg)

    def get_delete_leg(self, crud: str = "get", leg_id: Optional[str] = None):
        if crud == "get":
            tc = "get_all_leg_id_details"
            tc_msg = "Get all leg-id details"
            pass_msg = f"Able to {crud} all leg-id details"
        elif crud == "delete":
            tc = "delete_specified_leg_id"
            tc_msg = "Delete specified event"
            pass_msg = f"Able to {crud} specified leg-id:{leg_id} details"
        fail_msg = f"Un{pass_msg.lower()}"

        log.info(self.pretty_formatter)
        log.info(self.start_tc % tc_msg)
        test_matrix = [tc, "Pass"]

        try:
            url = (
                hierarchy(self.leg_edpt.legs % leg_id)
                if crud == "delete"
                else self.leg_edpt.legs
            )
            http_method_request = getattr(self.session, crud)
            http_resp = http_method_request(url)
            eval_http, resp = self.validate_without_assert(
                http_resp, self.mismatched_http_resp
            )
            if not eval_http:
                self.fail_count += 1
                log.error(fail_msg)
                test_matrix.extend(["Fail", fail_msg])
            else:
                log.info(pass_msg)
                test_matrix.extend(["Pass", None])
        except Exception:
            self.fail_count += 1
            log.exception(self.exception_msg)
            test_matrix.extend(["Fail", self.exception_msg])
        self.report.append_row(test_matrix)
        log.info(self.end_tc % tc_msg)


if __name__ == "__main__":
    unittest.main()
