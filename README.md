# Paper Formatter - Django Web Application
A production-ready Django web application for automatically generating formatted question papers from teacher-uploaded question banks.
## Features
- **Teacher Authentication**: Secure registration and login system
- **Question Bank Management**: Store and manage questions with metadata
- **Excel Import**: Bulk upload questions from Excel files
- **Paper Pattern Builder**: Define custom paper patterns with sections
- **Automatic Question Selection**: Intelligent algorithm for balanced paper generation
- **Multiple Output Formats**: Generate PDF and DOCX files
- **REST APIs**: Full API support for integration
- **Responsive UI**: Bootstrap 5 frontend
- **Admin Panel**: Complete Django admin interface
## Tech Stack
- Python 3.13
- Django 5+
- Django REST Framework
- SQLite (development) / PostgreSQL (production)
- Bootstrap 5
- ReportLab (PDF generation)
- python-docx (DOCX generation)
- Pandas + OpenPyXL (Excel import)
## Installation
### Prerequisites
- Python 3.13
- pip (Python package manager)
- Virtual environment (recommended)
### Setup Instructions
1. **Clone or create project structure**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
# Install dependencies
pip install -r requirements.txt
pip install user-agents