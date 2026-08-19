# Expert Decision Replay Platform

## Project Description

The Expert Decision Replay Platform is a web-based decision management system
designed to help organizations capture, analyze, approve, and learn from
important decisions.

The platform maintains the complete context of a decision, including
alternatives considered, supporting documents, discussions, modifications,
and historical versions. This enables organizations to trace how a decision
evolved over time.

The main objective of the platform is not only to store the final decision,
but also to preserve the reasoning, supporting information, and history behind
that decision.

---

## Technologies Used

- React JS
- FastAPI
- PostgreSQL
- SQLAlchemy
- JWT Authentication
- Python

---

## User Roles

The platform supports role-based users:

- Admin
- Manager
- Reviewer
- User

The role structure and authentication foundation are implemented to support
different types of users within the platform.

---

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

---

# Key Features

## User Authentication

The system starts with user authentication.

- User registration
- Secure password hashing
- JWT-based authentication
- User login
- Authentication management
- Role-based user structure

Passwords are securely hashed in the backend and JWT-based authentication is
used for authenticated access to the platform.

---

## Decision Management

The decision is the main entity of the platform.

Users can:

- Create decisions
- View decisions
- Edit decisions
- Associate decisions with users
- Track decision information
- View decision details
- View decision version history

When a decision is created, it is stored in the PostgreSQL database through
the FastAPI backend.

---

## Alternative Analysis

A decision can have multiple possible solutions or alternatives.

For each alternative, the platform can capture:

- Alternative name
- Description
- Pros
- Cons
- Estimated cost
- Feasibility
- Risk

This allows different possible solutions to be considered as part of the
decision-making process.

---

## Supporting Documents

Supporting documents can be associated with a particular decision.

Examples include:

- Reports
- Policies
- Quotations
- Analysis documents

The system records information such as:

- File name
- File type
- Uploader
- Upload time

This allows the evidence available during the decision-making process to be
preserved for future reference.

---

## Discussion Module

Users can add comments or notes related to a decision.

The discussion module helps preserve the reasoning and communication
surrounding a decision instead of storing only the final result.

This provides additional context when the decision is reviewed later.

---

## Decision Version History

Version history is one of the core features of the platform.

Whenever a decision is modified, the system maintains its previous state and
creates a new version.

For each version, the system can preserve:

- Decision title
- Description
- Status
- User who made the modification
- Modification time
- Change summary

For example:

Version 1
    |
    | Decision created
    ↓
Original Decision
    |
    | Decision edited
    ↓
Version 2
    |
    ↓
Updated Decision

Instead of overwriting the original decision, the platform preserves the
historical information.

This allows users to understand:

- What changed
- Who changed it
- When it changed
- Why it changed

---

# Database Tables

The platform uses PostgreSQL as its database.

Main database tables include:

- users
- decisions
- criteria
- alternatives
- alternative_scores
- decision_results
- decision_history
- review_comments

---

# System Architecture

The platform follows a three-layer architecture consisting of the React
frontend, FastAPI backend, and PostgreSQL database.

```text
                 User
                   |
                   ↓
          React JS Frontend
                   |
                   | REST API
                   ↓
            FastAPI Backend
                   |
                   | SQLAlchemy
                   ↓
          PostgreSQL Database
