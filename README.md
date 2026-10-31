LabTrace - Offline Laboratory Asset & Access Logging SystemLabTrace is a modularized, production-ready Django web application designed for tracking laboratory attendance, managing hardware asset borrowing with condition checking, and logging laboratory incidents in strict offline environments.🚀 Quick Setup & Installation GuidePrerequisitesPython 3.11+Virtual environment tool (venv)1. Project Initialization# Set up virtual environment
python3 -m venv .venv

# Activate virtual environment
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
2. Database Setup & Seeding# Generate database migrations
python manage.py makemigrations authentication users access_logging equipment incidents dashboard

# Apply database migrations
python manage.py migrate

# (Optional) Seed default demo accounts and assets
python manage.py seed_data
3. Run Development Serverpython manage.py runserver 0.0.0.0:8000
Access the application at: http://127.0.0.1:8000/🔑 Pre-Seeded Accounts (Default)RoleUsername / EmailPasswordAccess / ScopeAdmin / Lab Manageradmin (admin@cit.edu)admin123Full administrative access & audit trailInstructorinstructor (instructor@cit.edu)password123Equipment inspection & status managementResearcherresearcher (researcher@cit.edu)password123Lab access & equipment usageStudentstudent (student@cit.edu)password123Basic lab check-in, borrowing & reporting🏗️ Architecture & Modular Structurelabtrace/
├── manage.py                   # Django CLI utility
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation & context
│
├── labtrace/                   # Root Configuration Directory
│   ├── settings.py             # Configured for custom models, static/media, & offline apps
│   └── urls.py                 # Core routing table delegating to apps
│
├── authentication/             # App 1: Custom User Model (AbstractUser) & @cit.edu validation
├── users/                      # App 2: Profiles, RBAC middleware, & account deactivation
├── access_logging/             # App 3: Lab Entry/Exit & AJAX Check-Out tracking
├── equipment/                  # App 4: Asset Inventory, Pre/Post Condition Inspections
├── incidents/                  # App 5: Incident Reports & Multi-Parameter Audit Trail
├── dashboard/                  # App 6: Real-time Occupancy & Unified Analytics View
│
├── static/                     # Bundled Offline Static Assets (Tailwind CSS, jQuery, JS)
├── media/                      # Uploaded pre/post inspection photos & incident files
└── templates/                  # Modular HTML5 Templates
🔒 Offline Constraints & RulesNo External CDNs: All static assets (CSS, JavaScript libraries) reside locally inside the static/ folder.Local Media Storage: All file attachments and photo proof images are saved to local disk inside media/.Institutional Email Enforcement: User registration enforces @cit.edu domain validation.