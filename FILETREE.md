> AI agents: consult this file for fast project context before exploring the
> workspace; do not scan every directory when this map answers the question.

# LabTrace Workspace File Tree

This map reflects the current workspace and the app architecture in
`README.md`. Generated files and dependency directories (`.venv/`,
`node_modules/`, `__pycache__/`) are omitted. `sent_emails/` is a runtime
output directory, so its generated message files are not listed.

```text
lab/
├── README.md
├── LOG.md                         # Development status and roadmap
├── FILETREE.md                    # This workspace map
├── manage.py                      # Django CLI entry point
├── db.sqlite3                     # Local development database
├── package.json                   # Local Tailwind tooling
├── package-lock.json
├── tailwind.config.js
├── tailwindcss.exe                # Local Tailwind executable
├── sent_emails/                   # File-based password-reset output
├── static/                        # Bundled offline assets
│   ├── css/
│   │   └── tailwind.css
│   └── js/
│       ├── jquery.min.js
│       └── main.js
├── tailwind/
│   └── input.css
├── templates/                     # Shared project templates
│   ├── 403.html
│   └── base.html
├── labtrace/                      # Django project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── authentication/                # Custom user model and authentication
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   │   ├── __init__.py
│   │   ├── 0001_initial.py
│   │   └── 0002_alter_user_options_alter_user_email_and_more.py
│   └── templates/
│       └── authentication/
│           ├── _field.html
│           ├── login.html
│           └── register.html
├── users/                          # Profiles, RBAC, account and password flows
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── decorators.py
│   ├── forms.py
│   ├── middleware.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   │   └── __init__.py
│   └── templates/
│       └── users/
│           ├── deactivate.html
│           ├── password_change.html
│           ├── password_reset_complete.html
│           ├── password_reset_confirm.html
│           ├── password_reset_done.html
│           ├── password_reset_email.txt
│           ├── password_reset_form.html
│           ├── password_reset_subject.txt
│           ├── profile.html
│           └── user_list.html
├── access_logging/                 # Planned lab entry/exit and check-out
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   └── migrations/
│       └── __init__.py
├── equipment/                      # Planned asset inventory and inspections
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   └── migrations/
│       └── __init__.py
├── incidents/                      # Planned incident reports and audit trail
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   └── migrations/
│       └── __init__.py
└── dashboard/                      # Occupancy and analytics
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── tests.py
    ├── urls.py
    ├── views.py
    ├── migrations/
    │   └── __init__.py
    └── templates/
        └── dashboard/
            └── home.html
```

## README architecture notes

- The README depicts `manage.py` inside the project root tree; in this
  workspace it is at the repository root.
- The README describes local uploaded-file storage in `media/`, but that
  directory is not currently present.
- The README setup guide references `requirements.txt` and
  `python manage.py seed_data`; neither is currently present.
- `access_logging`, `equipment`, and `incidents` do not yet have URL modules in
  the workspace. Add routing as those app workflows are implemented.
