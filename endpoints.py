
def hierarchy(*params, join_with="/"):
    """Concatenate array elements with given string"""
    return join_with.join([str(elem) for elem in params])


class Defaults:
    BASE_URL = "https://api.nexmo.com"
    api_key = "802a78e0"
    api_secret = "DGpJNpdaUbKD53Bm"
    DEF_HEADERS = {"Content-Type": "application/json"}
    private_key = """
    -----BEGIN PRIVATE KEY-----
        MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDORF+MhfetfAKM
        BoNiohcEcO6DbwDMipSL7Tv5Mf3KEJucVWDyVsgGHMDpbYc+ikLGlG850I+ih9XY
        O+7n+iFiGAzetP7BmerFH4t3loWz18B25mEAUYxCzomlImsNWFkCFKjiaKONCfYR
        WxI+C4zLtIU64rbMocCPpCdLWrHEN6jrVTPYD7a48kzkKQI6CdCT45ZgkhkoZt86
        aJFl4pdv8xPmkFwRCbzfHfnG8DvnGM1IiDoRLRk8G9CHbtrjlqSt//2F9UwzcG/w
        IlDMq9Ku8u75erUyGkaUbKGdAwyYRDSiDkem+9Ju/gqbmPOgySLHPIsM8UXvU/jB
        Ep8NU9S5AgMBAAECggEARhz9saGUKDdgEkLghDV+x3avzKN9zQlKJyoz2agBkZ8F
        liV7d8TB5zn85Rvi/gI3YpLwH+HiAShVK1RsCBSBJnvwW/+AHUT5hZoMaVEUD6bF
        +GSlElul5suYBDbn1rhyQP/OzG8vMPDy4MFpOQfqCxBIvVR1OKe+8dSlurqQdJau
        rUXLBCdoNjY7SDULp5fLHLAh4fWQvX7qhdxDrkSnxjJOA50YrYEuJQeEA8xA9vK8
        CfR7z3YJE1bFrjLrMRJpZ3NHNYcUbQyIzlbhAMtQTKjlvSa5vbXd0LpBLFB9SyHP
        klg1OmgQ2K3meZAS1bgid+G9Tts8pJQtqBD16rBBtQKBgQDn0AZ2PncNV6eFJT+G
        zKDY9Rw5F9O0plY4JcFrRyVPY2GIAr+oLyYugeWdAk24sJWxmpMtJt0zXUggigTj
        mhIue6zUXWU+Hpt1an2vc3EdPdGrVVnKczLoOGyBL/GG4EYPzv1b081wWqQOiogS
        nYuQmXE7fFbmm/AUBmBkDkZg4wKBgQDjyf+j3ujEEW5u6PqywKCoyCVfB6NkAHFj
        rE+cUTrcqT6/G/ZYletIVNuueGVeOvxhQPDzW8J5qRf1koLxwoGeJ5tVF+V/AjFi
        gvsLMMxIwQSNrnFZMtv5a9LfpBU9GH+lnCB/UEDQF5tHTw6lHtUWKRpq0+dKuSma
        4YfuB3NyswKBgQDJbNbQlAJ6k3m6ld0XUmNJYeI+MdgBFq/AZf4lK1LeIqqytkC2
        8REqRDCyNzg1jSrlgjz0dNqsMRflPkh1RIEb5tcMSIMacRn/8qJ3e8YD9J1lVOqK
        oYLQiYau0mv6GJKIVgGMcwQF5py7DeCi3EZTRSFA4Q/ZnhIENG45QrYgpQKBgQDI
        JKEga+ha9fHxM3Wq/8Np6UmkwMJYSGdYq3rbnye34GEIa9o8paUwTZckKhbu/6bn
        ELdlLBeo6+DoXY3+O+fFfYlm7/MucE/R/cH0aDDmL+n/Tum69QwAkDOdWr9qig8G
        BTMsiegYrtU5h4YXoQqbSQw0FvIfXqfmtQjJJPTULwKBgFgJIC/DUc2+ERdNcZK4
        oB/4NzJMbzBqAlkhNke0uFJrHOz0gqQY/cym1q2J784RIAIjT7qCH8OZSER7BZYG
        OPr1QfEFDKiqSCvxGkhEpElp7qIfiXYS2XlY51rwURbsekgMhFMcTbFiwlkxEYV8
        T2FvPkwzSFBbnZRPSz0wedRc
    -----END PRIVATE KEY-----
    """
    application_name = "mmeta-testing"
    app_id = "ec450cce-1585-44c7-80d8-78b90d0f99cc"
    # Use https://developer.nexmo.com/jwt to generate jwt token
    # Below token is generated for a period of 365 days validity
    jwt_token = """eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE2MjY1MjY5NTQsImV4cCI6MTY1ODA2Mjk1NCwianRpIjoiQ29USmJsWGI4ZGZSIiwiYXBwbGljYXRpb25faWQiOiJlYzQ1MGNjZS0xNTg1LTQ0YzctODBkOC03OGI5MGQwZjk5Y2MifQ.XHCNqa8yKDOJ-dE7QfwoePZDFrNakudqh1V-XNgizuWjWT4GI2eKLrZm4JrwvRjNHvlo9wBXK5ovT1Alj7WaSm-pYonDCm6fbM_vZZ-RFSbP7HZB7YCXKFbyfe3pWbgJSFyI3cpQLZakdVeXO-gitHGnPPdXpd358l_3N_9ZSRKmUwZtvfrWYgaUyRtf1GBkeOlGeLaM1E7k6otolsU19iFWoOE6_jDpclBkpQq33O7m6CtYjejxrLnjRm-Unx2e2hrKiR-4ka7pmCIc-Tc7Fv1br4wAA9N6w2L7_IhVr4ZMvIewhPS8roihtXj-sXpC3OgEOohkcwpf-Ez200CJ6A"""
    # Log onto https://dashboard.nexmo.com/ to view application and its setting in developer dashboard
    log_level = "INFO"
    CHANNELS_LIST = ["app", "phone", "sip", "websocket", "vbc"]


class HTTP_CODES:
    SUCCESS = tuple(range(200, 300))
    REDIRECTS = tuple(range(300, 400))
    CLIENT_ERRORS = tuple(range(400, 500))
    SERVER_ERRORS = tuple(range(500, 600))
    INFO_RESP = tuple(range(100, 200))


class Parent:
    def __init__(self, endpoints, **kwargs):
        self.base_url = kwargs.get("url", Defaults.BASE_URL)
        for k, v in endpoints.items():
            setattr(self, k, f"{hierarchy(self.base_url, v)}")


class Conversations(Parent):
    parent = "v0.1"
    endpoints = {
        "conversations": hierarchy(parent, "conversations"),
        "record": hierarchy("v1", "conversations", "%s", "record"),
    }

    def __init__(self, **kwargs):
        super().__init__(endpoints=self.endpoints, **kwargs)


class User(Parent):
    parent = "v0.1"
    endpoints = {
        "users": hierarchy(parent, "users"),
        "list_conversations": hierarchy(parent, "users", "%s", "conversations"),
    }

    def __init__(self, **kwargs):
        super().__init__(endpoints=self.endpoints, **kwargs)


class Member(Parent):
    parent = "v0.1"
    endpoints = {
        "members": hierarchy(parent, "conversations", "%s", "members"),
    }

    def __init__(self, **kwargs):
        super().__init__(endpoints=self.endpoints, **kwargs)


class Event(Parent):
    parent = "v0.1"
    endpoints = {
        "events": hierarchy(parent, "conversations", "%s", "events"),
    }

    def __init__(self, **kwargs):
        super().__init__(endpoints=self.endpoints, **kwargs)


class Leg(Parent):
    parent = "v0.1"
    endpoints = {
        "legs": hierarchy(parent, "legs"),
    }

    def __init__(self, **kwargs):
        super().__init__(endpoints=self.endpoints, **kwargs)
