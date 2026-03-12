import base64
import hashlib
import os
import secrets
import struct
import time
from typing import Optional, List, Tuple

import httpx
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding


class WeComClient:
    def __init__(self, scope: str = "contact"):
        self.scope = scope
        self.corp_id = (os.getenv("WECOM_CORP_ID") or "").strip() or None
        self.agent_id = (os.getenv("WECOM_AGENT_ID") or "").strip() or None
        self.secret = (os.getenv("WECOM_SECRET") or "").strip() or None

        token_key = f"WECOM_{scope.upper()}_TOKEN"
        aes_key = f"WECOM_{scope.upper()}_ENCODING_AES_KEY"
        self.token = (os.getenv(token_key) or os.getenv("WECOM_TOKEN") or "").strip() or None
        self.encoding_aes_key = (os.getenv(aes_key) or os.getenv("WECOM_ENCODING_AES_KEY") or "").strip() or None

        debug_key = f"WECOM_{scope.upper()}_DEBUG_PLAINTEXT"
        self.debug_plaintext = (os.getenv(debug_key) or os.getenv("WECOM_DEBUG_PLAINTEXT") or "true").lower() == "true"
        self.send_mode = os.getenv("WECOM_SEND_MODE", "disabled").lower()
        self.api_base = "https://qyapi.weixin.qq.com/cgi-bin"
        self.last_error: Optional[str] = None

    def is_configured(self) -> bool:
        return bool(self.corp_id and self.agent_id and self.secret)

    def is_callback_configured(self) -> bool:
        return bool(self.corp_id and self.token and self.encoding_aes_key)

    def _get_aes_key(self) -> Optional[bytes]:
        if not self.encoding_aes_key:
            return None
        key = self.encoding_aes_key.strip()
        padding_len = (4 - len(key) % 4) % 4
        key = key + ("=" * padding_len)
        try:
            return base64.b64decode(key, validate=True)
        except Exception:
            return None

    def aes_key_fingerprint(self) -> Optional[str]:
        if not self.encoding_aes_key:
            return None
        digest = hashlib.sha256(self.encoding_aes_key.encode("utf-8")).hexdigest()
        return digest[:16]

    def _sha1(self, token: str, timestamp: str, nonce: str, encrypt: str) -> str:
        params = [token, timestamp, nonce, encrypt]
        params.sort()
        raw = "".join(params).encode("utf-8")
        return hashlib.sha1(raw).hexdigest()

    def verify_signature(self, signature: str, timestamp: str, nonce: str, encrypt: str) -> bool:
        if not (self.token and signature and timestamp and nonce and encrypt):
            return False
        expected = self._sha1(self.token, timestamp, nonce, encrypt)
        return expected == signature

    def decrypt_message(self, encrypt_text: str) -> Optional[str]:
        aes_key = self._get_aes_key()
        if not aes_key:
            self.last_error = "invalid_aes_key"
            return None
        try:
            try:
                encrypted = base64.b64decode(encrypt_text, validate=True)
            except Exception:
                self.last_error = "base64_decode_failed"
                return None
            if len(encrypted) % 16 != 0:
                self.last_error = "invalid_block_length"
                return None
            cipher = Cipher(algorithms.AES(aes_key), modes.CBC(aes_key[:16]))
            decryptor = cipher.decryptor()
            padded = decryptor.update(encrypted) + decryptor.finalize()
            # WeCom uses PKCS7 with a 32-byte block size (not AES block size).
            unpadder = padding.PKCS7(32 * 8).unpadder()
            try:
                plain = unpadder.update(padded) + unpadder.finalize()
            except ValueError:
                self.last_error = "invalid_padding"
                return None
            if len(plain) < 20:
                self.last_error = "invalid_plain_length"
                return None
            msg_len = struct.unpack("!I", plain[16:20])[0]
            msg = plain[20: 20 + msg_len]
            try:
                corp = plain[20 + msg_len:].decode("utf-8")
            except Exception:
                self.last_error = "corp_decode_failed"
                return None
            if self.corp_id and corp != self.corp_id:
                self.last_error = "corp_id_mismatch"
                return None
            return msg.decode("utf-8")
        except Exception as exc:
            self.last_error = f"decrypt_exception:{type(exc).__name__}"
            return None

    def encrypt_message(self, plaintext: str) -> Optional[Tuple[str, str, str, str]]:
        aes_key = self._get_aes_key()
        if not aes_key:
            return None
        random16 = secrets.token_bytes(16)
        msg = plaintext.encode("utf-8")
        msg_len = struct.pack("!I", len(msg))
        corp = (self.corp_id or "").encode("utf-8")
        raw = random16 + msg_len + msg + corp
        # WeCom uses PKCS7 with a 32-byte block size (not AES block size).
        padder = padding.PKCS7(32 * 8).padder()
        padded = padder.update(raw) + padder.finalize()
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(aes_key[:16]))
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded) + encryptor.finalize()
        encrypt_b64 = base64.b64encode(encrypted).decode("utf-8")
        timestamp = str(int(time.time()))
        nonce = secrets.token_hex(8)
        signature = self._sha1(self.token or "", timestamp, nonce, encrypt_b64)
        return encrypt_b64, signature, timestamp, nonce

    def _get_access_token(self) -> Optional[str]:
        if not self.is_configured():
            return None
        url = f"{self.api_base}/gettoken"
        params = {"corpid": self.corp_id, "corpsecret": self.secret}
        with httpx.Client(timeout=10) as client:
            resp = client.get(url, params=params)
            if resp.status_code != 200:
                return None
            data = resp.json()
            if data.get("errcode") != 0:
                return None
            return data.get("access_token")

    def send_group_message(
        self,
        external_group_id: str,
        content: str,
        at_user_ids: Optional[List[str]] = None,
    ) -> dict:
        if self.send_mode != "official":
            return {"ok": False, "error": "WECOM send disabled"}
        if not self.is_configured():
            return {"ok": False, "error": "WECOM not configured"}
        token = self._get_access_token()
        if not token:
            return {"ok": False, "error": "WECOM token failed"}

        # TODO: Replace with the correct customer group send API endpoint and payload
        # once confirmed from official WeCom documentation.
        url = f"{self.api_base}/externalcontact/add_msg_template?access_token={token}"
        payload = {
            "chat_type": "single",
            "external_userid": None,
            "sender": None,
            "text": {"content": content},
        }
        if at_user_ids:
            payload["text"]["mentioned_list"] = at_user_ids
        with httpx.Client(timeout=10) as client:
            resp = client.post(url, json=payload)
            if resp.status_code != 200:
                return {"ok": False, "error": f"HTTP {resp.status_code}"}
            data = resp.json()
            if data.get("errcode") != 0:
                return {"ok": False, "error": data.get("errmsg") or "send_failed"}
            return {"ok": True, "data": data}

    def send_app_message(self, to_user: Optional[str], content: str) -> dict:
        if self.send_mode != "official":
            return {"ok": False, "error": "WECOM send disabled"}
        if not self.is_configured():
            return {"ok": False, "error": "WECOM not configured"}
        if not to_user:
            return {"ok": False, "error": "Missing to_user"}
        token = self._get_access_token()
        if not token:
            return {"ok": False, "error": "WECOM token failed"}
        try:
            agent_id = int(self.agent_id) if self.agent_id else None
        except ValueError:
            agent_id = None
        if not agent_id:
            return {"ok": False, "error": "Invalid agent_id"}
        url = f"{self.api_base}/message/send?access_token={token}"
        payload = {
            "touser": to_user,
            "msgtype": "text",
            "agentid": agent_id,
            "text": {"content": content},
        }
        with httpx.Client(timeout=10) as client:
            resp = client.post(url, json=payload)
            if resp.status_code != 200:
                return {"ok": False, "error": f"HTTP {resp.status_code}"}
            data = resp.json()
            if data.get("errcode") != 0:
                return {"ok": False, "error": data.get("errmsg") or "send_failed"}
            return {"ok": True, "data": data}

    def create_app_chat(self, name: str, owner: str, userlist: List[str], chatid: Optional[str] = None) -> dict:
        if not self.is_configured():
            return {"ok": False, "error": "WECOM not configured"}
        token = self._get_access_token()
        if not token:
            return {"ok": False, "error": "WECOM token failed"}
        url = f"{self.api_base}/appchat/create?access_token={token}"
        payload = {
            "name": name,
            "owner": owner,
            "userlist": userlist,
        }
        if chatid:
            payload["chatid"] = chatid
        with httpx.Client(timeout=10) as client:
            resp = client.post(url, json=payload)
            if resp.status_code != 200:
                return {"ok": False, "error": f"HTTP {resp.status_code}"}
            data = resp.json()
            if data.get("errcode") != 0:
                return {"ok": False, "error": data.get("errmsg") or "create_failed", "data": data}
            return {"ok": True, "data": data}

    def send_app_chat_message(self, chatid: str, content: str) -> dict:
        if not self.is_configured():
            return {"ok": False, "error": "WECOM not configured"}
        token = self._get_access_token()
        if not token:
            return {"ok": False, "error": "WECOM token failed"}
        url = f"{self.api_base}/appchat/send?access_token={token}"
        try:
            agent_id = int(self.agent_id) if self.agent_id else None
        except ValueError:
            agent_id = None
        if not agent_id:
            return {"ok": False, "error": "Invalid agent_id"}
        payload = {
            "chatid": chatid,
            "msgtype": "text",
            "text": {"content": content},
        }
        with httpx.Client(timeout=10) as client:
            resp = client.post(url, json=payload)
            if resp.status_code != 200:
                return {"ok": False, "error": f"HTTP {resp.status_code}"}
            data = resp.json()
            if data.get("errcode") != 0:
                return {"ok": False, "error": data.get("errmsg") or "send_failed", "data": data}
            return {"ok": True, "data": data}
