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
