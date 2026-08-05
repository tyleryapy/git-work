# Teams Transcript Export

This repository includes a small Python CLI for exporting Microsoft Teams
meeting transcripts through Microsoft Graph.

The tool:

- Enumerates transcripts with `onlineMeetings/getAllTranscripts`.
- Follows `@odata.nextLink` exactly as returned by Graph.
- Downloads transcript content from `transcriptContentUrl` or the
  `/transcripts/{transcriptId}/content` endpoint.
- Requests speaker-attributed WebVTT first and retries with the unattributed
  transcript format when speaker attribution is disabled by tenant policy.
- Avoids printing transcript content or access tokens to stdout.

## Requirements

- Python 3.10+
- A Microsoft Entra app registration with Microsoft Graph access.
- Tenant admin consent for the permissions below.

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Microsoft Graph permissions

For transcript enumeration with `getAllTranscripts`, Microsoft documents
application permission only:

- `OnlineMeetingTranscript.Read.All`

For transcript content retrieval, Graph may also require an application access
policy granted to the user in the request path. If the tenant disables transcript
API access, Graph returns `GraphAccessToTranscriptsDisabled` and there is no
client-side workaround.

For private chat meetings, some tenants may use resource-specific consent with
`OnlineMeetingTranscript.Read.Chat`, but `OnlineMeetingTranscript.Read.All` is
the general application permission for this exporter.

## Authentication

Preferred application flow:

```bash
export MS_TENANT_ID="<tenant-id>"
export MS_CLIENT_ID="<app-client-id>"
export MS_CLIENT_SECRET="<app-client-secret>"
```

The CLI also accepts a pre-provisioned bearer token:

```bash
export GRAPH_ACCESS_TOKEN="<access-token>"
```

Device-code auth is available for cases where a delegated token is enough for
the target endpoint, but `getAllTranscripts` is documented as application-only.

## Q2 2026 QBR example

The Microsoft 365 search pass found this meeting:

- Title: `Q2 2026 QBR | In Person + Virtual`
- Organizer user id: `7c42f097-d953-412d-871c-410b9fa8b2c3`
- Tenant id: `decee90c-ce03-461e-8c21-dd538e181c75`
- Thread id: `19_meeting_YzkxMWFiMjktN2FlMi00YzlmLWI4YTMtODdmZmRmNDk5YTY0@thread.v2`
- Teams meeting ID: `321 680 240 697 56`
- Recording discovered in SharePoint:
  `Q2 2026 QBR  In Person + Virtual-20260728_090202-Meeting Recording.mp4`

List matching transcript metadata around the meeting date:

```bash
python scripts/export_teams_transcript.py \
  --request-user-id "7c42f097-d953-412d-871c-410b9fa8b2c3" \
  --organizer-user-id "7c42f097-d953-412d-871c-410b9fa8b2c3" \
  --start-date-time "2026-07-28T00:00:00Z" \
  --end-date-time "2026-07-29T00:00:00Z" \
  --meeting-id-contains "YzkxMWFiMjktN2FlMi00YzlmLWI4YTMtODdmZmRmNDk5YTY0" \
  --metadata-json "out/q2-2026-qbr-transcripts.json"
```

Download the first matching transcript as WebVTT:

```bash
python scripts/export_teams_transcript.py \
  --request-user-id "7c42f097-d953-412d-871c-410b9fa8b2c3" \
  --organizer-user-id "7c42f097-d953-412d-871c-410b9fa8b2c3" \
  --start-date-time "2026-07-28T00:00:00Z" \
  --end-date-time "2026-07-29T00:00:00Z" \
  --meeting-id-contains "YzkxMWFiMjktN2FlMi00YzlmLWI4YTMtODdmZmRmNDk5YTY0" \
  --download \
  --output-dir "out" \
  --output-name "q2-2026-qbr.vtt"
```

If Graph returns `SpeakerAttributionNotAllowed`, the CLI retries with
`Accept: application/vnd.microsoft.graph.transcript+text` and writes a `.txt`
file instead.

## Troubleshooting

- `GraphAccessToTranscriptsDisabled`: tenant administrators must enable Graph
  API access to transcripts in Teams meeting settings.
- `Forbidden` with application credentials: confirm admin consent and that an
  application access policy grants the app access on behalf of the request-path
  user.
- No matches: remove `--meeting-id-contains` and inspect the metadata JSON,
  then filter by the returned `meetingId`, transcript id, or creation time.
