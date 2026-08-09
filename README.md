# Expert Decision Replay Platform

## Project Description

The Expert Decision Replay Platform is a web-based decision management system designed to help organizations capture, analyze, approve, and learn from important decisions.

The platform maintains the complete context of a decision, including alternatives considered, supporting documents, discussions, modifications, and historical versions. This enables organizations to trace how a decision evolved over time.

## Technologies Used

- React JS
- FastAPI
- PostgreSQL
- SQLAlchemy
- JWT Authentication
- Python

## User Roles

The platform supports role-based users:

- Admin
- Manager
- Reviewer
- User

## Modules

1. User Management
2. Decision Management
3. Criteria Management
4. Alternative Analysis
5. Recommendation Engine
6. Approval Workflow
7. Supporting Documents
8. Discussion Module
9. Decision Version History
10. Audit Logs
11. Dashboard & Reports

## Key Features

### User Authentication
- User registration
- Secure password hashing
- JWT-based authentication
- Login and authentication management

### Decision Management
- Create decisions
- View decisions
- Edit decisions
- Associate decisions with users
- Track decision status

### Alternative Analysis
- Add multiple alternatives to a decision
- Store alternative descriptions
- Record pros and cons
- Store estimated cost
- Store feasibility and risk information

### Supporting Documents
- Upload documents related to decisions
- Store file name and type
- Track uploader and upload time
- Access supporting evidence during decision review

### Discussion
- Add comments and notes to decisions
- Preserve reasoning and communication surrounding decisions

### Decision Version History
- Automatically maintain decision versions
- Preserve previous decision states
- Record modification details
- Track who changed a decision
- Track when the change occurred
- Store change summaries

The version history is a core feature of the platform because it allows users to understand not only the current decision but also how and why the decision evolved over time.

## Database Tables

- users
- decisions
- criteria
- alternatives
- alternative_scores
- decision_results
- decision_history
- review_comments

## System Architecture

```text
React JS Frontend
        |
        | REST API
        ↓
FastAPI Backend
        |
        | SQLAlchemy
        ↓
PostgreSQL Database
## How It Works

The Expert Decision Replay Platform follows a structured workflow for creating,
managing, reviewing, and tracking organizational decisions.

### 1. User Authentication

The process starts with user authentication.

- Users register with their credentials.
- Registered users can log in securely.
- Passwords are stored using secure hashing.
- JWT-based authentication is used to authenticate users.
- The system supports Admin, Manager, Reviewer, and User roles.

### 2. Dashboard

After successful authentication, the user is redirected to the dashboard.

The dashboard provides access to the major functionalities of the platform,
including decision creation, decision viewing, and decision management.

### 3. Create a Decision

A user can create a new decision by providing:

- Decision title
- Decision description

The decision is associated with the currently logged-in user and stored in
the PostgreSQL database through the FastAPI backend.

### 4. Manage Decisions

Users can view existing decisions from the View Decisions section.

Each decision provides options to:

- View
- Edit
- View Version History

This allows users to manage decisions throughout their lifecycle.

### 5. Add Alternatives

A decision can have multiple possible alternatives.

For each alternative, the system can store:

- Alternative name
- Description
- Pros
- Cons
- Estimated cost
- Feasibility
- Risk

This allows different possible solutions to be considered before reaching a
final decision.

### 6. Add Supporting Documents

Supporting documents can be associated with a decision.

Examples include:

- Reports
- Policies
- Quotations
- Analysis documents

The system records information such as the file name, file type, uploader,
and upload time.

This preserves the evidence that was available when the decision was made.

### 7. Discussion

Users can add comments or notes related to a decision.

The discussion module helps preserve the reasoning and communication
surrounding the decision instead of storing only the final outcome.

### 8. Edit a Decision

Decisions may change when new information becomes available.

Users can edit an existing decision and provide a change summary explaining
why the modification was made.

Instead of simply overwriting the previous information, the system preserves
the previous state through version tracking.

### 9. Version History

Whenever a decision is modified, a new version is created.

For example:

Version 1
    ↓
Original Decision
    ↓
Decision Edited
    ↓
Version 2
    ↓
Updated Decision

The version history records:

- Decision title
- Description
- Status
- User who made the modification
- Modification time
- Change summary

This allows users to understand:

- What changed
- Who changed it
- When it changed
- Why it changed

### 10. Decision Replay

The final purpose of the platform is to replay the evolution of a decision.

Instead of looking only at the current state, users can examine the decision's
historical versions and understand how it evolved over time.

This provides traceability and helps organizations learn from previous
decision-making processes.
