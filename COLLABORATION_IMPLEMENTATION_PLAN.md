# WORKLINE AI — COMPLETE TEAM COLLABORATION SYSTEM
## Architecture, Gap Analysis, and Engineering Implementation Plan

**Author:** Workline AI Engineering Team  
**Date:** September 2026  
**Status:** PROPOSED (Planning Phase)  
**Target Architecture:** First-Class Engineering Collaboration Subsystem (Full Stack)

---

## 1. Executive Summary & Objective

The objective of this specification is to design and implement the **complete, end-to-end Team Collaboration System** within the existing WORKLINE AI platform. Rather than building a generic SaaS team management page or a standalone chat tool, the collaboration system is constructed as a first-class engineering collaboration subsystem that links:

```
PROJECT ➔ TEAM ➔ MEMBERS ➔ ROLES & PERMISSIONS ➔ WORK ITEMS (TASKS) ➔ 
ENGINEERING ARTIFACTS ➔ AI AGENTS ➔ ACTIVITY / AUDIT TRAIL
```

All design decisions strictly observe the project invariants:
- **No unnecessary rewrites**: Integrates natively with existing FastAPI routes, SurrealDB graph database, Cognito authentication, ArmorIQ delegation framework, and Next.js frontend.
- **Visual continuity**: Retains the existing dark engineering workbench aesthetic (`zinc-950`, `cyan-400`, `indigo-500`, monospace data tags).
- **Zero data loss**: Preserves existing project packages, session history, and users.
- **Server-side authorization**: Strict RBAC and artifact-level authorization on every mutation; no client-side trust.

---

## 2. Codebase Inspection & Existing Architecture

### 2.1 Authentication & User Identity
- **Backend (`backend/auth.py`)**: Validates AWS Cognito JWT IdTokens (`get_current_user`), decoding `sub`, `email`, `cognito:username`. Fallback demo user `testuser@workline.ai` (`user_default_owner`).
- **Frontend (`frontend/src/lib/CognitoAuthContext.tsx` & `cognito.ts`)**: Pure REST integration with Amazon Cognito User Pool `us-east-1_AFlRukzzO`. Provides `getToken()`, `userEmail`, `userId`, `isSignedIn`.
- **Integration Strategy**: All collaboration entities (`TeamMember`, `Comment`, `Task`, `ApprovalRequest`, `AuditLog`) bind to Cognito `sub` (or email for pending invites).

### 2.2 Database Layer (SurrealDB & Persistence)
- **SurrealDB Connection (`backend/workline/database/surrealdb.py`)**: Async SurrealDB driver connecting to SurrealDB instance with fallback in-memory cache for ultra-fast local dev and offline resiliency.
- **Schema (`backend/workline/database/migrations/001_initial_schema.surql`)**: Existing schemas for `users`, `teams`, `team_members`, `invitations`, `projects`, `project_versions`, `comments`, `requirements`, `components`, `datasheets`, `bom`, `validation`, `documents`, `research_items`.
- **Repositories**: `CollaborationRepository` (`backend/workline/database/repositories/collaboration_repository.py`) already provides basic CRUD for teams, members, invitations, and comments in SurrealDB.
- **SQLite Fallback (`backend/services/collaboration_service.py`)**: Provides baseline table schemas for local offline testing.

### 2.3 Existing Collaboration Modules
- **`backend/workline/collaboration/teams/`**:
  - `models.py`: `Team`, `TeamMember`, `TeamAuditEvent`, `TeamRole` (`OWNER`, `ADMIN`, `MEMBER`).
  - `service.py`: CSPRNG 6-character code generator, HMAC-SHA-256 storage (plaintext codes are never persisted), brute-force rate limiter (`rate_limiter.py`), owner protection (cannot remove or demote sole owner).
  - `router.py`: REST routes for team creation, listing, getting, rotating code, revoking code, updating role, removing member.
- **`backend/workline/collaboration/invitations/`**:
  - Encrypted invitation service using AES-256-GCM tokens with expiration, max use tracking, and preview endpoints (`/api/invitations/{token}/preview` and `/api/invitations/{token}/accept`).
- **`backend/workline/collaboration/crypto/`**:
  - RSA-OAEP asymmetric encryption and RSA-PSS signatures.
- **`backend/routes/collaboration.py`**:
  - FastAPI router linking teams, comments, and members with ArmorIQ delegation framework (`capture_plan`, `delegate`, `invoke_tool`).

### 2.4 Existing Engineering Knowledge & Decisions
- **`backend/workline/decision/` & `backend/workline/api/knowledge.py`**:
  - `EngineeringDecision`: Model containing `decision_id`, `project_id`, `title`, `description`, `decision_type`, `criteria`, `status` (`PROPOSED`, `UNDER_REVIEW`, `APPROVED`, `REJECTED`), `candidates`, `recommendation`.
  - Service already supports multi-criteria scoring and human approval/rejection.

### 2.5 ArmorIQ Delegation & Agent Operations
- **`backend/armoriq/delegation.py`**: Records cryptographic delegation receipts, parent receipts, authorized scopes, tool calls, and execution results.
- **`backend/workline/api/agents.py`**: Runs multi-agent workflows (`POST /api/agents/run`), monitors execution states (`GET /api/agents/executions/{id}`), and handles approvals (`POST /api/agents/approval/{id}`).

### 2.6 Frontend Collaboration UI
- **`frontend/src/components/TeamWorkspace.tsx`**: 3-column layout (Team Details/Codes, Comments, Activity).
- **`frontend/src/components/layout/Sidebar.tsx`**: Renders `Team Collaboration` nav section linking to `activeSection === 'teams'`.
- **`frontend/src/components/InvitationModal.tsx` & `InvitationList.tsx`**: Modal for creating encrypted invitation links.

---

## 3. Gap Analysis: What is Missing

| Requirement | Current Codebase State | Missing Work to Complete |
|---|---|---|
| **Joining Code Format** | Raw 6-char alphanumeric code (e.g., `7K4M2P`) | Formal `WL-XXXXXX` format with "WL-" prefix, ambiguous character exclusion (no O/0, I/1), case-insensitive parsing, configurable approval policy. |
| **Membership Request Flow** | Direct join only upon valid code | Preview endpoint + `MembershipRequest` entity (`PENDING`, `APPROVED`, `REJECTED`, `CANCELLED`), admin approval queue, policy toggle (`require_join_approval`). |
| **Roles & Permissions** | 3 roles (`OWNER`, `ADMIN`, `MEMBER`) | Full 5-tier role model: `OWNER`, `ADMIN`, `ENGINEER`, `RESEARCHER`, `VIEWER`. Centralized `PermissionService` with explicit capabilities & artifact-level overrides. |
| **Task Management** | External agent task models exist, but no human/team collaboration tasks | First-class `CollaborationTask` entity, board/list UI, status workflow (`BACKLOG` to `DONE`), priorities, assignees, due dates, **engineering artifact linking**. |
| **Contextual Comments** | Basic flat string comments (`id`, `project_id`, `section`, `content`) | Polymorphic comments attached to tasks, BOM items, components, analyses, decisions, datasheets. Support for `@mentions` and replies. |
| **Mentions & Notifications** | No notifications system | Centralized `NotificationService`, persistent notifications in SurrealDB, topbar bell icon with unread badge count, dropdown panel. |
| **Approvals Queue** | Embedded in decision engine and agents, but not unified | Centralized `ApprovalRequest` subsystem for BOM edits, component replacements, architecture decisions, and release gate authorizations. |
| **Unified Activity Feed** | Separate raw logs for teams, agents, and comments | Unified project activity stream clearly distinguishing Human (`●`), AI Agent (`◆`), and System (`⚙`), with ArmorIQ receipts. |
| **Team Workspace UI** | 3-column static view | Full 8-tab engineering workspace: `Overview`, `Members`, `Tasks`, `Activity`, `Decisions`, `Approvals`, `Invitations`, `Settings`. |
| **Ownership Transfer** | Only prevents sole owner removal; no formal transfer protocol | Formal two-step ownership transfer protocol (`OWNER` to target member) with strict confirmation and audit trail. |
| **AI Copilot Team Awareness** | Connection chatbot only looks at BOM, wiring, power | Extend assistant context with team members, active tasks, decisions, pending approvals, while respecting user permissions. |

---

## 4. Architectural Design & Information Model

### 4.1 Domain Entity Relationships
```
                ┌──────────────────────────────────────┐
                │               PROJECT                │
                └──────────────────┬───────────────────┘
                                   │ 1:1 or 1:N
                                   ▼
                ┌──────────────────────────────────────┐
                │                 TEAM                 │
                │  - joining_code (WL-XXXXXX digest)   │
                │  - require_join_approval (bool)      │
                │  - default_join_role                 │
                └───────┬──────────────┬───────────────┘
                        │              │
           1:N Members  │              │ 1:N Requests
                        ▼              ▼
        ┌─────────────────────┐  ┌─────────────────────────┐
        │     MEMBERSHIP      │  │   MEMBERSHIP_REQUEST    │
        │ - user_id           │  │ - requested_role        │
        │ - role (5-tier)     │  │ - status (PENDING/...)  │
        │ - permissions_cache │  │ - reviewed_by           │
        └──────────┬──────────┘  └─────────────────────────┘
                   │
    ┌──────────────┼──────────────────────────────┐
    ▼              ▼                              ▼
┌────────┐   ┌────────────┐               ┌────────────────┐
│ TASKS  │   │  COMMENTS  │               │   APPROVALS    │
│linkedto│   │attached to │               │  for sensitive │
│artifact│   │ artifact   │               │   operations   │
└────────┘   └────────────┘               └────────────────┘
    │              │                              │
    └──────────────┴──────────────┬───────────────┘
                                  ▼
                    ┌───────────────────────────┐
                    │    ACTIVITY & AUDIT       │
                    │   ● USER  ◆ AGENT  ⚙ SYS  │
                    └───────────────────────────┘
```

### 4.2 The 5-Tier Role and Permission Hierarchy

| Role | Permissions / Scope |
|---|---|
| **OWNER** | Full project access; manage members, assign/change roles; rotate/revoke/configure joining code; approve membership requests; transfer ownership; modify all engineering artifacts (BOM, schematics, firmware); execute all agents; view full audit log. |
| **ADMIN** | Manage members (cannot demote/remove owner); approve membership requests; configure join code; modify all engineering artifacts; create/assign tasks; run agents; view audit log. |
| **ENGINEER** | Create & modify engineering artifacts (BOM, wiring, schematics, code); create, update, and resolve tasks; post comments & mentions; request approvals; run permitted agents (thermal, pcb, validation). Cannot manage team members or join settings. |
| **RESEARCHER** | Read/write access to Research papers, Knowledge Base, Documents, and Datasheets; create research tasks; post comments & mentions; run research/sourcing agents. Read-only for BOM, PCB layout, and release gates. |
| **VIEWER** | Read-only access across all project artifacts; read comments and activity feed; post permitted comments. Zero mutation or agent execution rights. |

### 4.3 Secure Joining-Code System (`WL-XXXXXX`)
- **Prefix**: Always `WL-`.
- **Charset**: Uppercase alphanumeric excluding ambiguous glyphs: `23456789ABCDEFGHJKLMNPQRSTUVWXYZ` (excludes `0`, `O`, `1`, `I`).
- **Generation**: Cryptographically secure random selection (`secrets.choice`).
- **Normalization**: User inputs like `wl-7k4m2p`, `7K4M2P`, or `WL-7K4M2P` normalize automatically to `WL-7K4M2P`.
- **Storage**: HMAC-SHA-256 digest computed with server secret (`TEAM_JOIN_CODE_SECRET`). Plaintext codes are **never stored** in the database.
- **Regeneration**: Generating a new code immediately replaces the active digest and timestamp; the old code is revoked instantly. Existing memberships remain untouched.
- **Policy Controls**:
  - `joining_code_enabled: bool`
  - `require_join_approval: bool` (if `True`, creates `MembershipRequest` instead of instant join)
  - `default_join_role: TeamRole` (defaults to `ENGINEER`)
  - `join_code_expires_at: ISO8601` (configurable TTL, default 7 days)

---

## 5. Proposed Changes (Full-Stack Modules)

### 5.1 Backend Extensions

#### Module 1: Enhanced Team Models & Service (`backend/workline/collaboration/teams/`)
1. **`models.py`**:
   - Update `TeamRole`: `OWNER`, `ADMIN`, `ENGINEER`, `RESEARCHER`, `VIEWER`.
   - Update `Team`: Add `joining_code_format: str = "WL-XXXXXX"`, `require_join_approval: bool = False`, `default_join_role: TeamRole = TeamRole.ENGINEER`.
   - Add `MembershipRequest`: `id`, `team_id`, `project_id`, `user_id`, `user_email`, `user_name`, `requested_role`, `joining_code_used`, `status` (`PENDING`, `APPROVED`, `REJECTED`, `CANCELLED`), `created_at`, `reviewed_by`, `reviewed_at`, `rejection_reason`.
   - Add `OwnershipTransferRequest`: `id`, `team_id`, `current_owner_id`, `target_user_id`, `status`, `created_at`.
2. **`service.py`**:
   - Update `_generate_unique_join_code()`: Generates `WL-XXXXXX` using unambiguous charset `23456789ABCDEFGHJKLMNPQRSTUVWXYZ`.
   - Implement `preview_join_code(code)`: Returns public team preview (team name, description, member count, requires approval) without revealing secrets or establishing membership.
   - Implement `request_or_join_team(code, user_id, user_email, requested_role)`: Either joins directly or creates `MembershipRequest` based on `require_join_approval`.
   - Implement `list_membership_requests(team_id, actor_id)` & `review_membership_request(request_id, approve, actor_id, role)`.
   - Implement `transfer_ownership(team_id, target_user_id, actor_id)`.

#### Module 2: Centralized Permissions & Artifact Authorization (`backend/workline/collaboration/permissions.py`)
- Create `PermissionService`:
  - Project-level authorization: `can_edit_project`, `can_manage_team`, `can_run_agent`, `can_approve_action`.
  - Artifact-level authorization: Checks specific permissions for `BOM`, `Component`, `Document`, `Datasheet`, `Analysis`, `Decision`, `Task`.
  - Fast role-to-capability lookup with override support.

#### Module 3: Collaboration Tasks (`backend/workline/collaboration/tasks/`)
- **`models.py`**:
  - `CollaborationTask`: `id`, `project_id`, `team_id`, `title`, `description`, `status` (`BACKLOG`, `TODO`, `IN_PROGRESS`, `IN_REVIEW`, `BLOCKED`, `DONE`, `CANCELLED`), `priority` (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), `assignee_id`, `creator_id`, `due_date`, `labels`, `related_artifact` (`type`: `BOM` / `COMPONENT` / `ANALYSIS` / `DATASHEET` / `DECISION`, `id`: string, `name`: string), `created_at`, `updated_at`.
- **`service.py` & `router.py`**:
  - `GET /api/projects/{projectId}/tasks` (with filtering by status, assignee, priority).
  - `POST /api/projects/{projectId}/tasks` (creates task, logs activity, dispatches notification).
  - `PATCH /api/tasks/{taskId}` (status transition, assignment changes).
  - `DELETE /api/tasks/{taskId}`.

#### Module 4: Contextual Comments & Mentions (`backend/workline/collaboration/comments/`)
- **`models.py`**:
  - `ContextComment`: `id`, `project_id`, `parent_type` (`task`, `bom_item`, `component`, `document`, `decision`, `analysis`, `project`), `parent_id`, `author_id`, `author_name`, `content`, `mentions` (list of user IDs), `reply_to_id`, `created_at`, `updated_at`, `is_edited`.
- **`service.py`**:
  - Extracts `@username` or `@email` from comment body.
  - Generates `MENTION` notifications for mentioned team members.
  - Records activity log entry for the target artifact.

#### Module 5: Engineering Decisions & Approvals Subsystem (`backend/workline/collaboration/approvals/`)
- **`models.py`**:
  - `ApprovalRequest`: `id`, `project_id`, `team_id`, `requester_id`, `approver_id`, `artifact_type` (`BOM_CHANGE`, `ARCHITECTURE_DECISION`, `COMPONENT_SUBSTITUTION`, `RELEASE_GATE`), `artifact_id`, `action`, `reason`, `diff_summary`, `status` (`PENDING`, `APPROVED`, `REJECTED`, `CANCELLED`), `created_at`, `resolved_at`, `resolution_notes`.
- **Integration**:
  - Sensitive operations (e.g. BOM modification by non-owner, release gate sign-off) create an `ApprovalRequest`.
  - Authorized users (`OWNER`, `ADMIN`) approve or reject.

#### Module 6: Centralized Notifications (`backend/workline/collaboration/notifications/`)
- **`models.py`**:
  - `Notification`: `id`, `recipient_id`, `project_id`, `type` (`MENTION`, `TASK_ASSIGNED`, `TASK_UPDATED`, `JOIN_REQUEST`, `INVITATION`, `APPROVAL_REQUEST`, `APPROVAL_RESULT`, `COMMENT`, `AGENT_COMPLETED`, `AGENT_FAILED`, `POLICY_VIOLATION`), `title`, `message`, `related_type`, `related_id`, `read`: bool, `created_at`.
- **`router.py`**:
  - `GET /api/notifications` (lists current user notifications with unread count).
  - `PATCH /api/notifications/{notificationId}/read` (marks as read).
  - `POST /api/notifications/mark-all-read`.

#### Module 7: Unified Activity Feed & Audit Stream (`backend/workline/collaboration/activity/`)
- Aggregates activity events across user mutations, AI agent executions (with ArmorIQ receipts), and system events into a single queryable endpoint:
  - `GET /api/projects/{projectId}/activity` (supports cursor pagination & filtering by `actor_type`: `USER`, `AGENT`, `SYSTEM`).

#### Module 8: AI Copilot Context Enhancement (`backend/services/connection_chatbot_service.py`)
- Enhance `ask_connection_assistant()`:
  - Injects live team context (active members, tasks assigned, open decisions, pending approvals) into the Bedrock / DeepSeek prompt.
  - Enforces permission checks so the assistant does not disclose unauthorized private artifacts.

---

### 5.2 Frontend Extensions

#### Module 1: Comprehensive Team Workspace (`frontend/src/components/TeamWorkspace.tsx`)
Refactor `TeamWorkspace.tsx` to host the 8 core tabs:
1. **Overview Tab**:
   - Hero summary metric cards: Total Members, Active Tasks, Pending Approvals, Open Decisions, Agent Runs.
   - Quick joining code badge with copy & regenerate actions.
   - Recent activity stream preview and quick team profile card.
2. **Members Tab**:
   - Full member list table with avatar badges, role badges (`OWNER`, `ADMIN`, `ENGINEER`, `RESEARCHER`, `VIEWER`), join timestamps, last active indicators.
   - Role change selector with permission check.
   - Member removal / suspension modal with destructive action confirmations.
   - "Transfer Ownership" dialog requiring explicit re-entry of project name.
3. **Tasks Tab**:
   - Engineering task board with status columns (`BACKLOG`, `TODO`, `IN_PROGRESS`, `IN_REVIEW`, `DONE`).
   - "New Task" modal with title, description, priority, assignee, due date, and **Artifact Linker** (dropdown to bind task to a BOM Component, Datasheet, Thermal Analysis, or Decision).
4. **Activity Tab**:
   - Real-time filtered activity stream.
   - Visual actor indicator:
     - `●` (Indigo) for Human Engineers
     - `◆` (Cyan) for AI Agents (displaying tool name & ArmorIQ receipt ID)
     - `⚙` (Slate) for System events
5. **Decisions Tab**:
   - Engineering Decision Log table & drawer.
   - Displays Decision ID (`DEC-014`), Title, Decision statement, Rationale, Alternatives considered, and Evidence links.
   - Actions to propose, review, approve, or supersede decisions.
6. **Approvals Tab**:
   - Pending Approvals queue for sensitive actions.
   - Shows requester, target artifact (e.g. BOM item `MPU6050 -> BMI270`), diff summary, and reason.
   - One-click [Approve] and [Reject] with feedback.
7. **Invitations & Join Code Tab**:
   - Joining Code card: Formatted `WL-XXXXXX`, 1-click copy, expiration countdown, [Regenerate] button (revoking old code immediately), [Disable] toggle, and [Require Admin Approval] checkbox.
   - Membership Requests Queue: Lists pending requests with user details, requested role, and [Approve] / [Reject] buttons.
   - Encrypted Invitation Link Generator (AES-256-GCM).
8. **Settings Tab**:
   - Team name & description.
   - Default joining role setting (`ENGINEER`, `RESEARCHER`, `VIEWER`).
   - Danger Zone: Transfer Team Ownership, Archive Team.

#### Module 2: Notifications Bell in Topbar (`frontend/src/components/layout/Topbar.tsx`)
- Add an interactive Notification Bell button next to AI Copilot:
  - Displays unread counter badge.
  - Opens dropdown panel listing recent notifications (`MENTION`, `TASK_ASSIGNED`, `JOIN_REQUEST`, `APPROVAL_REQUEST`).
  - Clicking an item routes directly to the relevant artifact or tab and marks it as read.

#### Module 3: Join Team Modal (`frontend/src/components/JoinTeamModal.tsx`)
- Input for `WL-XXXXXX` code with automatic formatting and rate-limiting feedback.
- Team Preview card showing Project Name, Team Name, Member Count, and joining policy.
- "Request to Join" or "Join Team" button handling instant entry or approval request creation.

---

## 6. Migration Strategy & Backward Compatibility

1. **Existing Projects & Users**:
   - Any project without an associated team automatically creates a default team with the project owner assigned as `OWNER`.
   - Existing join codes are hashed into HMAC digests without changing their validation behavior.
2. **Non-Destructive Database Evolution**:
   - New tables (`membership_requests`, `collaboration_tasks`, `context_comments`, `approval_requests`, `notifications`) are added to SurrealDB via new migration scripts.
   - Existing `projects`, `users`, `bom`, and `datasheets` tables remain structurally unchanged.

---

## 7. Verification & Testing Plan

1. **Automated Backend Tests (`tests/collaboration/`)**:
   - `test_team_joining_code_format.py`: Validates `WL-XXXXXX` generation, charset exclusion (no O/0/1/I), case-insensitivity, HMAC digest lookup.
   - `test_join_code_regeneration.py`: Confirms regenerating a code immediately invalidates the old code while keeping existing members active.
   - `test_membership_approval_flow.py`: Verifies `require_join_approval` creates `MembershipRequest`, prevents premature entry, and admits member upon admin approval.
   - `test_rbac_and_artifact_permissions.py`: Ensures `VIEWER` cannot mutate BOM; `RESEARCHER` cannot manage members; `ADMIN` cannot demote `OWNER`.
   - `test_collaboration_tasks.py`: Validates task creation, artifact linking, status transitions, and assignee notifications.
   - `test_comments_mentions.py`: Validates `@mention` parsing and `MENTION` notification dispatch.
   - `test_ownership_transfer.py`: Verifies sole owner cannot be deleted and ownership transfer correctly reassigns `OWNER` role.
2. **Frontend Build & Integration**:
   - Run `npm run build` in `frontend/` to ensure zero compile or TypeScript errors.
   - Validate UI tab navigation, joining code modal, notifications bell dropdown, and task board interactivity.

---

## 8. Summary of Files to Add / Modify

- **New Backend Files**:
  - `backend/workline/collaboration/permissions.py`
  - `backend/workline/collaboration/tasks/models.py`, `service.py`, `router.py`
  - `backend/workline/collaboration/comments/models.py`, `service.py`, `router.py`
  - `backend/workline/collaboration/approvals/models.py`, `service.py`, `router.py`
  - `backend/workline/collaboration/notifications/models.py`, `service.py`, `router.py`
  - `tests/collaboration/test_collaboration_full_system.py`
- **Modified Backend Files**:
  - `backend/workline/collaboration/teams/models.py`, `service.py`, `router.py`
  - `backend/routes/collaboration.py`
  - `backend/main.py`
  - `backend/services/connection_chatbot_service.py`
- **New Frontend Files**:
  - `frontend/src/components/collaboration/TaskBoard.tsx`
  - `frontend/src/components/collaboration/DecisionsLog.tsx`
  - `frontend/src/components/collaboration/ApprovalsQueue.tsx`
  - `frontend/src/components/collaboration/NotificationDropdown.tsx`
  - `frontend/src/components/collaboration/JoinTeamModal.tsx`
  - `frontend/src/components/collaboration/OwnershipTransferModal.tsx`
- **Modified Frontend Files**:
  - `frontend/src/components/TeamWorkspace.tsx`
  - `frontend/src/components/layout/Topbar.tsx`
  - `frontend/src/lib/ProjectContext.tsx`
