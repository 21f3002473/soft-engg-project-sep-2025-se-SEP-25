# Admin API Endpoints

Authentication: All endpoints require an authenticated user. Most require ROOT role; logs access allows roles permitted by can_view_system_logs().

---

## POST /admin/register
Register first (or additional) ROOT admin.
Body:
{
  "name": string (min 1),
  "email": string (email),
  "password": string (min 6)
}
Responses:
201:
{
  "id": int,
  "name": string,
  "email": string,
  "role": "root"
}
409: email already exists.

---

## GET /admin/summary
Requires ROOT.
Returns system counts and current admin info.
Response:
{
  "userCount": int,
  "logsCount": int,
  "backupsCount": int,
  "currentAdmin": { "id": int, "name": string, "email": string }
}

---

## GET /admin/employees
Requires ROOT.
List all users.
Response: [
  { "id": int, "name": string, "email": string, "role": string }
]

## POST /admin/employees
Requires ROOT.
Create user (employee / HR / product manager / root).
Body:
{
  "name": string,
  "role": string (hr|human resource|product manager|pm|employee|root),
  "email": string? (optional)
}
If email omitted, system autogenerates unique email.
Response:
{
  "id": int,
  "name": string,
  "email": string,
  "role": string,
  "temporary_password": string
}
409: email already exists.
422: invalid role.

---

## GET /admin/backup-config
Requires ROOT.
List configured backups.
Response: [
  {
    "day": string,
    "type": "full" | "incremental" | "differential",
    "datetime": ISO8601 string
  }
]

## PUT /admin/backup-config
Requires ROOT.
Replace entire backup configuration.
Body:
{
  "backups": [
    {
      "day": string,
      "type": "full" | "incremental" | "differential",
      "datetime": ISO8601 datetime
    }
  ]
}
Response:
{ "message": "Backup configuration updated", "count": int }
422: invalid backup type.

---

## GET /admin/logs?limit=50&offset=0
Requires authorization via can_view_system_logs().
Query params:
limit: int (1-500), offset: int (>=0)
Response: [
  {
    "id": int,
    "user_id": int | null,
    "text": string,
    "time": ISO8601 string
  }
]

---

## GET /admin/updates
Requires ROOT.
Placeholder software update status.
Response:
{
  "currentVersion": "1.0.0",
  "updateAvailable": false,
  "lastChecked": ISO8601 UTC string
}

---

## GET /admin/account
Requires ROOT.
Return current admin profile.
Response:
{
  "id": int,
  "name": string,
  "email": string,
  "role": string
}

## PUT /admin/account
Requires ROOT.
Update name and/or password.
Body:
{
  "name": string?,
  "old_password": string?,
  "new_password": string?
}
Rules:
- Name updated if non-empty and different.
- Password update requires old_password and correct verification.
Responses:
{
  "id": int,
  "name": string,
  "email": string,
  "role": string,
  "updated": bool
}
422: missing old password when new provided.
403: old password mismatch.

---

## Models Reference (Simplified)

AdminRegistrationValidator:
{ name, email, password }

AdminAddEmployeeValidator:
{ name, role, email? }

BackupItem:
{ day, type, datetime }

BackupConfigPayload:
{ backups: [BackupItem] }

AccountUpdatePayload:
{ name?, old_password?, new_password? }

---

## Error Formats
Standard FastAPI HTTPException:
{
  "detail": string
}

## Notes
- Password hashing and verification handled by User model.
- Role normalization maps friendly names to internal enum values.
- Temporary password generation pattern: TempYYMMDDHHMMSS!
