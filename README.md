# Talkify
A Todo application that uses speech recognition and NLP to automatically convert natural voice notes into structured, actionable tasks classified into relevant categories. So that you keep focus on building and leave the schedule to Talkify.

```python
routes/       → receives HTTP requests
services/     → application logic / AI logic
schemas/      → defines valid input/output
models/       → database structure
tests/        → tests
main.py       → starts the application
```
This is what task looks like in our database.
```python
Task
│
├── id
├── title
├── description
├── due_date
├── priority
└── completed
```
>**create_engine**: Manages the actual connection bridge between Python and your database (like SQLite or PostgreSQL). It handles the low-level communication and maintains a pool of reusable connections to keep the app fast.

>**sessionmaker**: Acts as a factory that generates Session objects. A session is your workspace for database queries—it tracks changes, lets you add or delete items, and commits those changes to the database when you are done.

Once you build the engine and session, your app can:

- Create tables
- Insert tasks
- Read tasks
- Update tasks
- Delete tasks