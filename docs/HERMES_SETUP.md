# Set up the disclosed Hermes reviewer

Owner: Joshua. Reviewer login: **JoshKozy**. Repository:
`JoshuaKosakowsky/AI-Jukebox_MBAX6418`. Both logins belong to the same person.
The [policy](../CONTRIBUTING.md#disclosed-hermes-reviewer-joshkozy) and
[separate reviewer prompt](HERMES_REVIEWER.md) define the exception. This guide
does not configure an account, grant access or activate an automation by itself.

## 1. Adopt the policy and give the reviewer access

An existing eligible teammate must review the policy PR, then merge it normally
with required checks and protections. Hermes cannot approve its own authority
change. Until that policy exists on protected main, its mode is COMMENT only.

As the owner, open repository Settings > Collaborators/access. Give JoshKozy
Write collaborator access and accept any invitation while signed in as JoshKozy.
Do not grant Admin or bypass access. Write eligibility is needed for its approval
to count; a public/read-only reviewer can inspect code without satisfying that
gate. At the 2026-11-01 setup inspection, the API reported JoshKozy as **read**;
no access was changed. Recheck instead of assuming this historical value remains.

Write access belongs to the account; the credential exposed to Hermes must be
more restrictive. Do not hand the review agent the owner's credentials.

## 2. Use a connection that cannot push code

Preferred: a **GitHub App user access token**, authorized as JoshKozy, with the
app installed only on this repository under the owner's account. Use the
professor's supported GitHub connector if it offers this configuration. Otherwise
register a dedicated GitHub App and use its supported user authorization/device
flow. In the owner's GitHub Settings > Developer settings > GitHub Apps > New
GitHub App, choose a unique reviewer name, this repo as the homepage, the
permissions below and device flow if your connector supports it. A webhook is
not needed for manual review. Install the app on this repository only. In the
connector's separate authorization flow, sign in as JoshKozy, not the owner;
use the app's Client ID and supported user-token flow. Do not use the app private
key/installation token as a substitute for user authorization. If the supplied
connector cannot accept app user tokens or perform that flow, report that
capability gap before enabling posting. A connector is not mandatory: a supported
app user-token flow can be completed outside Hermes and the scoped token supplied
privately to its CLI process through GH_TOKEN. Tool/sandbox restrictions are still
required. The verified CLI/runtime state here does not establish connector support.
Official registration/authorization links
are below. Do not guess
Hermes connector flags or paste tokens into chat or tracked files.

Requested app repository permissions:

| Permission | Access |
|---|---|
| Pull requests | Read/write, for comments and reviews |
| Contents, Metadata | Read only |
| Checks, Commit statuses, Actions | Read only, for CI/status/log inspection |
| Administration, Workflows writes, other writes | None |

Use a **user** token so the actor is JoshKozy. An installation token acts as the
app/bot instead and is not this named-account exception. Confirm the app's actual
installation permissions and selected repository; user tokens are bounded by
both app access and account access. An account's Write role does not mean this
scoped token has Contents write. Short-lived user tokens need private refresh
support or reauthorization; report an expired login instead of falling back to
the writer's account. Without Contents write it cannot push code or
merge via the normal API. Never grant broader access to make a denied merge work.

Fine-grained PATs currently have collaborator-owned-repository limitations; do
not assume JoshKozy can select Joshua's personal repository when creating one.
A classic PAT/OAuth CLI login with `public_repo` or `repo` is **not** a hard
review-only credential: it can permit code writes. Do not expose one to an
unrestricted agent/shell as an equivalent fallback. A trusted tool broker can
hold a credential and expose only allowed review operations if already available;
otherwise finish the scoped connection before enabling posting.

Separately restrict Hermes's tool set to repository/PR/issue/check reads, PR
comments and review submissions. Disable file editors, patch/apply-suggestion,
commit/push/merge, PR/issue editing/closing, assignments/labels, administration,
release, browser account changes and scheduling tools. Pull Requests write alone
is broader than review submission, so the tool allowlist matters too.

## 3. Isolate the profile, files and authentication

Use a fresh professor-provided agent/session with **HERMES_REVIEWER.md** as its
persistent role instructions. Do not reuse the coding agent's session/memory or
give it the contributing profile's implement/fix instructions. Use the supported
profile controls of the installed version; no Hermes `--profile` flag is assumed.

The installed CLI inspected on 2026-11-01 could not print `hermes --help`; it
reported: `no dependency environment is committed for this install; run hermes
pm repair`. In your own Hermes terminal, use that reported repair command, then
retry `hermes --help`, or repair through the professor's supplied installer.
Repair and profile/GitHub setup were **not executed or verified** by this guide.
An existing GUI session may differ from this CLI installation.

Use a dedicated reviewer directory outside OneDrive, for example
`C:\Users\joshu\Documents\AI-Jukebox-Review`, and a separate GitHub credential
context. Never point it at the writer's checkout or OneDrive School repository.
Do not install writer hooks/allowPush settings in the reviewer copy. Materializing
review commits in disposable checkouts is allowed; modifying their content is not.

For CLI-based tools, set these only in the **dedicated review process/terminal**:

```powershell
$env:GH_CONFIG_DIR = Join-Path $env:LOCALAPPDATA 'Hermes-JoshKozy\gh'
Remove-Item Env:GH_HOST -ErrorAction SilentlyContinue
$env:GH_REPO = 'JoshuaKosakowsky/AI-Jukebox_MBAX6418'
```

Supply the scoped user token through the connector/OS secret storage, or its
private process-level GH_TOKEN injection. Do not use global `gh auth switch`,
global Git identity changes, `setx`, `gh auth setup-git`, SSH keys or shared writer
credentials. GH_TOKEN/GITHUB_TOKEN override stored CLI credentials; ensure no
inherited primary-account token masks the selected review connection. Never
print token values. `GH_CONFIG_DIR` isolates CLI config, not a separately
configured MCP/browser connector; verify that connector's identity separately.

Windows gh2.102.0 was observed resolving a shared-keyring login with an empty
reviewer config when GH_HOST was set. With GH_HOST removed and token overrides
cleared, the same empty config correctly required login. Therefore keep GH_HOST
unset in this context and verify the credential source as well as the username.
Separate config files can still use shared OS keyring entries; they are not
proof of separate secret storage. Prefer the explicit scoped process token or
a properly isolated OS identity/broker over another broad shared-keyring login.

Run this through the **same connection Hermes will use**, before any posting:

```powershell
gh api user --jq .login
gh api repos/JoshuaKosakowsky/AI-Jukebox_MBAX6418 --jq '{full_name, permissions}'
```

Require login JoshKozy and the intended repository/account access. Verify scoped
app permissions in installation settings as well; reading a public repo or an
account-level permissions object does not prove the token cannot write code.
Stop on a mismatch. Do not fix it by switching the writer's active login.
Repository permissions.push describes account access; it may remain true with
a restricted app token and is not a test for Contents write. Read back the app's
actual grants. A 403/404 from a protection/collaborator endpoint can reflect
insufficient visibility: report unreadable, not unprotected or non-collaborator.
GET branches/main's protected flag can establish protection exists, not its
complete settings. Obtain any missing settings from an authorized owner reader;
do not grant Hermes administration merely to inspect them.

A separate clone/config is organizational isolation, not an OS security boundary.
For enforced file isolation use the professor's sandbox/tool restrictions, a
separate Windows user, or a container without the writer's files/credentials.
Keep GitHub credentials in the posting context and run PR code only in a separate
credential-free test sandbox with read-only source and writable scratch. Remove
GitHub/class-service credentials; expose no `.env` or user media. Deny provider
network access; allow loopback only for offline startup tests. Dependency setup
can be performed separately from trusted locked sources. Never execute PR tests
in the authenticated posting process. If these controls are unavailable, use
static review and report tests unrun until a safe runner exists.

## 4. Load the role and test without granting more authority

Give Hermes the full [reviewer instructions](HERMES_REVIEWER.md), plus:

```text
Repository: JoshuaKosakowsky/AI-Jukebox_MBAX6418.
Act only as the disclosed Hermes reviewer through JoshKozy.
Read your policy/instructions from protected main. First verify authenticated
identity, repo access and review-only capabilities using your actual connection.
Report these checks without posting anything. Do not repair permissions or
configure schedules. Then wait for my selection of one PR for a COMMENT-only
smoke review. Include the full reviewed SHA and actual checks, without code edits.
```

After identity/capabilities pass, choose one existing ready PR and authorize
one COMMENT review. Verify the actor is JoshKozy, the disclosure is present and
the SHA is correct. Compare the disposable checkout before/after; no tracked
content edits. No push/merge or denied-write experiment against the real repo is
needed. Only after policy adoption and successful smoke review enable eligible
APPROVE/REQUEST_CHANGES under its existing scope. Do not test by creating a fake
approval or modifying a production branch. Actual review ability remains unproven
until a real authorized submission succeeds.

## 5. Coordinate with Dot and record attribution

Tell the existing Dot conversation (do not create a second review monitor):

```text
Once CONTRIBUTING's disclosed Hermes/JoshKozy policy is adopted on main, Hermes
is the primary automated technical reviewer. Read its exact-head review and
validation; do not spawn a duplicate technical review worker for the same head.
Continue your existing CI/readiness monitoring and authorized protected merges.
Recognize a JoshKozy approval only when the named role's policy conditions and
all existing GitHub gates are satisfied. Never treat it as another human's work.
Your own JoshuaKosakowsky author/contributor approval restriction remains.
Keep existing expiry and quiet-notification rules; report missing verification
once. Do not change protection or reviewer permissions.
```

This text does not update Dot's saved tasks automatically. Ordinary teammates
may still review; merge authority stays with the owner/lead/authorized Dot, not
Hermes. Completed Hermes work is attributed to Joshua with its actual review
link in CONTRIBUTIONS. It does not satisfy another teammate's required work or
certify independent installation/listening. Revoke the review connection or
remove its tools to stop posting; stop any active runner separately.

## Official references

- [GitHub App permissions](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app).
- [User access tokens and authorization/device flow](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-user-access-token-for-a-github-app).
- [Review API permissions and commit anchoring](https://docs.github.com/en/rest/pulls/reviews#create-a-review-for-a-pull-request).
- [PAT limitations](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).
- [CLI configuration and token precedence](https://cli.github.com/manual/gh_help_environment).
