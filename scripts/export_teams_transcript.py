#!/usr/bin/env python3
"""Export Microsoft Teams meeting transcripts through Microsoft Graph.

The primary flow uses the onlineMeetings/getAllTranscripts API to enumerate
transcript metadata, follows @odata.nextLink exactly as returned, and then
downloads transcript content from the transcriptContentUrl returned by Graph.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote

import msal
import requests


GRAPH_ROOT = "https://graph.microsoft.com/v1.0"
GRAPH_SCOPE = "https://graph.microsoft.com/.default"
DELEGATED_SCOPES = ["OnlineMeetingTranscript.Read.All", "User.Read"]
DEFAULT_TOKEN_ENV = "GRAPH_ACCESS_TOKEN"
VTT_ACCEPT = "text/vtt"
TEXT_ACCEPT = "application/vnd.microsoft.graph.transcript+text"


class GraphError(RuntimeError):
    """Raised for Microsoft Graph API errors."""

    def __init__(self, status_code: int, message: str, inner_code: str | None = None):
        self.status_code = status_code
        self.inner_code = inner_code
        super().__init__(message)


@dataclass(frozen=True)
class AuthConfig:
    tenant_id: str | None
    client_id: str | None
    client_secret: str | None
    token_env: str
    auth_mode: str


class GraphClient:
    def __init__(self, access_token: str) -> None:
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {access_token}",
                "User-Agent": "teams-transcript-export/1.0",
            }
        )

    def get_json(self, url: str) -> dict[str, Any]:
        response = self._session.get(url, headers={"Accept": "application/json"}, timeout=60)
        if response.status_code >= 400:
            raise_graph_error(response)
        try:
            payload = response.json()
        except ValueError as exc:
            raise GraphError(response.status_code, "Graph returned a non-JSON response.") from exc
        if not isinstance(payload, dict):
            raise GraphError(response.status_code, "Graph returned an unexpected JSON payload.")
        return payload

    def get_bytes(self, url: str, accept: str) -> bytes:
        response = self._session.get(url, headers={"Accept": accept}, timeout=120)
        if response.status_code >= 400:
            raise_graph_error(response)
        return response.content

    def paged_get(self, url: str) -> Iterable[dict[str, Any]]:
        next_url: str | None = url
        while next_url:
            payload = self.get_json(next_url)
            for item in payload.get("value", []):
                if isinstance(item, dict):
                    yield item
            next_url = payload.get("@odata.nextLink")


def raise_graph_error(response: requests.Response) -> None:
    message = f"Graph request failed with HTTP {response.status_code}."
    inner_code: str | None = None
    try:
        payload = response.json()
    except ValueError:
        body = response.text[:500].strip()
        if body:
            message = f"{message} Response body: {body}"
        raise GraphError(response.status_code, message) from None

    error = payload.get("error") if isinstance(payload, dict) else None
    if isinstance(error, dict):
        graph_message = error.get("message")
        if isinstance(graph_message, str) and graph_message:
            message = graph_message
        inner_code = extract_inner_code(error)
    raise GraphError(response.status_code, message, inner_code)


def extract_inner_code(error: dict[str, Any]) -> str | None:
    cursor: Any = error.get("innerError")
    while isinstance(cursor, dict):
        code = cursor.get("code")
        if isinstance(code, str) and code:
            return code
        cursor = cursor.get("innerError")
    code = error.get("code")
    return code if isinstance(code, str) else None


def acquire_token(config: AuthConfig) -> str:
    env_token = os.environ.get(config.token_env)
    if config.auth_mode in {"auto", "token"} and env_token:
        return env_token

    if config.auth_mode == "token":
        raise SystemExit(f"No bearer token found in ${config.token_env}.")

    if config.auth_mode in {"auto", "client-credentials"} and config.client_secret:
        if not config.tenant_id or not config.client_id:
            raise SystemExit("Client credentials auth requires tenant id, client id, and client secret.")
        app = msal.ConfidentialClientApplication(
            client_id=config.client_id,
            client_credential=config.client_secret,
            authority=f"https://login.microsoftonline.com/{config.tenant_id}",
        )
        result = app.acquire_token_for_client(scopes=[GRAPH_SCOPE])
        return token_from_result(result)

    if config.auth_mode in {"auto", "device-code"}:
        if not config.tenant_id or not config.client_id:
            raise SystemExit("Device-code auth requires tenant id and client id.")
        app = msal.PublicClientApplication(
            client_id=config.client_id,
            authority=f"https://login.microsoftonline.com/{config.tenant_id}",
        )
        flow = app.initiate_device_flow(scopes=DELEGATED_SCOPES)
        if "user_code" not in flow:
            raise SystemExit("Failed to create a device-code flow.")
        print(flow["message"], file=sys.stderr)
        result = app.acquire_token_by_device_flow(flow)
        return token_from_result(result)

    raise SystemExit(
        "No usable auth path found. Set GRAPH_ACCESS_TOKEN, provide client credentials, "
        "or select --auth device-code with tenant/client id."
    )


def token_from_result(result: dict[str, Any]) -> str:
    token = result.get("access_token")
    if isinstance(token, str) and token:
        return token
    error = result.get("error_description") or result.get("error") or "Unknown authentication failure."
    raise SystemExit(str(error))


def build_get_all_transcripts_url(
    request_user_id: str,
    organizer_user_id: str,
    start_date_time: str | None,
    end_date_time: str | None,
    top: int | None,
) -> str:
    params = [f"meetingOrganizerUserId='{escape_function_string(organizer_user_id)}'"]
    if start_date_time:
        params.append(f"startDateTime={quote(start_date_time, safe=':-TZ')}")
    if end_date_time:
        params.append(f"endDateTime={quote(end_date_time, safe=':-TZ')}")

    url = (
        f"{GRAPH_ROOT}/users/{quote(request_user_id, safe='')}"
        f"/onlineMeetings/getAllTranscripts({','.join(params)})"
    )
    if top:
        url = f"{url}?$top={top}"
    return url


def escape_function_string(value: str) -> str:
    return value.replace("'", "''")


def matches_transcript(transcript: dict[str, Any], args: argparse.Namespace) -> bool:
    if args.transcript_id and transcript.get("id") != args.transcript_id:
        return False
    if args.meeting_id_contains:
        haystack = " ".join(flatten_strings(transcript))
        if args.meeting_id_contains.lower() not in haystack.lower():
            return False
    if args.title_contains:
        haystack = " ".join(flatten_strings(transcript))
        if args.title_contains.lower() not in haystack.lower():
            return False
    return True


def flatten_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from flatten_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from flatten_strings(child)


def print_transcripts(transcripts: list[dict[str, Any]]) -> None:
    for index, transcript in enumerate(transcripts, start=1):
        summary = {
            "index": index,
            "id": transcript.get("id"),
            "meetingId": transcript.get("meetingId"),
            "createdDateTime": transcript.get("createdDateTime"),
            "meetingOrganizer": transcript.get("meetingOrganizer"),
            "hasTranscriptContentUrl": bool(transcript.get("transcriptContentUrl")),
        }
        print(json.dumps(summary, indent=2, ensure_ascii=False))


def download_transcript(
    client: GraphClient,
    transcript: dict[str, Any],
    args: argparse.Namespace,
    sequence: int,
) -> Path:
    content_url = transcript.get("transcriptContentUrl")
    if not isinstance(content_url, str) or not content_url:
        meeting_id = transcript.get("meetingId")
        transcript_id = transcript.get("id")
        if not isinstance(meeting_id, str) or not isinstance(transcript_id, str):
            raise GraphError(0, "Transcript metadata does not include a content URL or meeting/transcript ids.")
        content_url = (
            f"{GRAPH_ROOT}/users/{quote(args.request_user_id, safe='')}"
            f"/onlineMeetings/{quote(meeting_id, safe='')}"
            f"/transcripts/{quote(transcript_id, safe='')}/content"
        )

    requested_accept = VTT_ACCEPT if args.format == "vtt" else TEXT_ACCEPT
    suffix = ".vtt" if args.format == "vtt" else ".txt"
    try:
        content = client.get_bytes(content_url, requested_accept)
    except GraphError as exc:
        if args.format == "vtt" and exc.inner_code == "SpeakerAttributionNotAllowed":
            content = client.get_bytes(content_url, TEXT_ACCEPT)
            suffix = ".txt"
        else:
            raise

    output_path = output_file_path(args.output_dir, args.output_name, transcript, sequence, suffix)
    output_path.write_bytes(content)
    return output_path


def output_file_path(
    output_dir: str,
    output_name: str | None,
    transcript: dict[str, Any],
    sequence: int,
    suffix: str,
) -> Path:
    root = Path(output_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    if output_name:
        name = output_name
        if sequence > 1:
            stem = Path(output_name).stem
            current_suffix = Path(output_name).suffix or suffix
            name = f"{stem}-{sequence}{current_suffix}"
    else:
        created = str(transcript.get("createdDateTime") or "transcript")
        transcript_id = str(transcript.get("id") or sequence)
        name = f"{safe_filename(created)}-{safe_filename(transcript_id)[:48]}{suffix}"

    target = (root / safe_filename(name)).resolve()
    if root != target and root not in target.parents:
        raise SystemExit("Refusing to write outside the output directory.")
    return target


def safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return cleaned.strip("._") or "transcript"


def write_metadata(path: str, transcripts: list[dict[str, Any]]) -> None:
    target = Path(path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(transcripts, indent=2, ensure_ascii=False), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Enumerate and export Microsoft Teams transcripts through Microsoft Graph."
    )
    parser.add_argument("--request-user-id", required=True, help="User id in the /users/{id} request path.")
    parser.add_argument(
        "--organizer-user-id",
        required=True,
        help="Meeting organizer user id passed to getAllTranscripts.",
    )
    parser.add_argument("--tenant-id", default=os.environ.get("MS_TENANT_ID"))
    parser.add_argument("--client-id", default=os.environ.get("MS_CLIENT_ID"))
    parser.add_argument("--client-secret", default=os.environ.get("MS_CLIENT_SECRET"))
    parser.add_argument(
        "--auth",
        choices=["auto", "client-credentials", "device-code", "token"],
        default="auto",
        help="Authentication mode. Default: auto.",
    )
    parser.add_argument(
        "--access-token-env",
        default=DEFAULT_TOKEN_ENV,
        help=f"Environment variable containing a Graph bearer token. Default: {DEFAULT_TOKEN_ENV}.",
    )
    parser.add_argument("--start-date-time", help="Optional UTC ISO start filter, e.g. 2026-07-28T00:00:00Z.")
    parser.add_argument("--end-date-time", help="Optional UTC ISO end filter, e.g. 2026-07-29T00:00:00Z.")
    parser.add_argument("--top", type=int, help="Optional Graph page size.")
    parser.add_argument("--transcript-id", help="Only keep a specific transcript id.")
    parser.add_argument("--meeting-id-contains", help="Only keep transcripts whose metadata contains this value.")
    parser.add_argument("--title-contains", help="Only keep transcripts whose metadata contains this title text.")
    parser.add_argument("--metadata-json", help="Optional path for full transcript metadata JSON.")
    parser.add_argument("--download", action="store_true", help="Download content for the first matching transcript.")
    parser.add_argument("--download-all", action="store_true", help="Download content for all matching transcripts.")
    parser.add_argument("--output-dir", default="out", help="Directory for transcript output. Default: out.")
    parser.add_argument("--output-name", help="Output file name for a single transcript.")
    parser.add_argument(
        "--format",
        choices=["vtt", "text"],
        default="vtt",
        help="Transcript content format. Default: vtt.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    auth_config = AuthConfig(
        tenant_id=args.tenant_id,
        client_id=args.client_id,
        client_secret=args.client_secret,
        token_env=args.access_token_env,
        auth_mode=args.auth,
    )
    token = acquire_token(auth_config)
    client = GraphClient(token)

    initial_url = build_get_all_transcripts_url(
        request_user_id=args.request_user_id,
        organizer_user_id=args.organizer_user_id,
        start_date_time=args.start_date_time,
        end_date_time=args.end_date_time,
        top=args.top,
    )
    transcripts = [item for item in client.paged_get(initial_url) if matches_transcript(item, args)]

    if args.metadata_json:
        write_metadata(args.metadata_json, transcripts)

    if not transcripts:
        print("No matching transcripts found.", file=sys.stderr)
        return 1

    print_transcripts(transcripts)

    should_download = args.download or args.download_all
    if not should_download:
        return 0

    to_download = transcripts if args.download_all else transcripts[:1]
    for sequence, transcript in enumerate(to_download, start=1):
        output_path = download_transcript(client, transcript, args, sequence)
        print(f"Wrote transcript content to {output_path}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except GraphError as exc:
        if exc.inner_code:
            print(f"Graph error ({exc.status_code}, {exc.inner_code}): {exc}", file=sys.stderr)
            if exc.inner_code == "GraphAccessToTranscriptsDisabled":
                print(
                    "Tenant administrators must enable Graph API access to transcripts before this can work.",
                    file=sys.stderr,
                )
        else:
            print(f"Graph error ({exc.status_code}): {exc}", file=sys.stderr)
        raise SystemExit(2)
