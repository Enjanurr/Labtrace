# LabTrace Development Log and Roadmap

This log uses the architecture, setup guide, and offline requirements in
`README.md` as the project roadmap. Completion status reflects the current
workspace; a file or app scaffold alone does not mean its features are done.

## Completed

- Created the Django project and the six modular app packages named in the
  README: `authentication`, `users`, `access_logging`, `equipment`,
  `incidents`, and `dashboard`.
- **Completed the `authentication` module.** It provides the custom user model
  and roles, `@cit.edu` email validation, registration, login, and logout.
- Configured the custom user model and core project routing.
- Bundled local static assets, including Tailwind CSS and jQuery, for offline
  use.
- Configured file-based email for offline password-reset testing. The reset
  flow is exposed by the `users` app and has been verified to create a message
  file for an eligible account.

## Current implementation to finish or validate

- The `users` app contains profile, role-management, account-deactivation, and
  password-management flows, along with role-based access middleware. Review
  and test these flows as the other modules are integrated.
- `dashboard` currently has a protected home view and template; the README's
  real-time occupancy and unified analytics features remain to be implemented.
- `access_logging`, `equipment`, and `incidents` currently have app scaffolds;
  their README-described workflows remain to be implemented.
- The README setup guide refers to `requirements.txt`, `media/`, and a
  `seed_data` management command. These are not currently present in the
  workspace and should be added or the guide updated before relying on those
  setup steps.

## Immediate next step: `access_logging`

Prepare the `access_logging` module for the next coding session. Implement and
validate:

1. Lab entry and exit tracking.
2. The AJAX check-out flow described in the README.
3. The models, URL routing, and templates/API behavior needed to connect those
   flows to the project.
4. The corresponding tests and any required migrations.

## Remaining README roadmap

1. **`users`** — finish and validate profiles, role-based access, and account
   deactivation.
2. **`access_logging`** — complete lab entry/exit and AJAX check-out tracking.
3. **`equipment`** — implement asset inventory and pre-/post-borrow condition
   inspections.
4. **`incidents`** — implement incident reporting and the multi-parameter
   audit trail.
5. **`dashboard`** — implement real-time occupancy and unified analytics.
6. **Offline operation** — keep static assets local, store uploaded photos and
   incident files locally under `media/`, and retain institutional email
   enforcement.
7. **Setup and verification** — provide the dependencies and optional seed
   command described in the README, then validate migrations, setup, and
   module workflows with tests.

The `access_logging` item is the next session's priority, as requested; the
ordering of the remaining items is a working roadmap, not a claim that those
features are already complete.
