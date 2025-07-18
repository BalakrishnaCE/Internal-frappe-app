# 🏢 Internal - Workflow Management System

A comprehensive internal workflow management system built on the Frappe framework with a modern React frontend, designed to streamline business processes across multiple departments.

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Departments](#departments)
- [Quick Start](#quick-start)
- [Development](#development)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)

## 🎯 Overview

Internal is a modern workflow management system that combines the robustness of Frappe's backend with the flexibility of a React frontend. It provides role-based access control, department-specific workflows, and comprehensive reporting capabilities.

### Key Features
- **Multi-Department Support**: BDM, Sales, HR workflows
- **Role-Based Access**: User and Team Lead (TL) roles
- **Modern UI**: React 19 + TypeScript + Tailwind CSS
- **Real-time Updates**: Live data synchronization
- **Comprehensive Reporting**: Analytics and performance tracking

## 🏗️ Architecture

### Backend (Frappe/Python)
```
apps/internal/internal/
├── api/                    # API endpoints
│   ├── Common/            # Shared utilities
│   └── Departments/       # Department-specific APIs
├── config/                # Frappe configuration
├── hooks.py              # Frappe hooks & events
└── modules.txt           # Module definitions
```

### Frontend (React/TypeScript)
```
apps/internal/internal_app/src/
├── auth/                 # Authentication system
├── departments/          # Department modules
│   ├── bdm/             # BDM workflow
│   ├── sales/           # Sales workflow
│   └── hr/              # HR workflow
├── layouts/             # Layout components
├── components/          # Reusable UI components
└── API/                # Frontend API utilities
```

## ✨ Features

### 🔐 Authentication & Authorization
- **Role-Based Access Control**: User and Team Lead roles
- **Department-Specific Access**: BDM, Sales, HR permissions
- **Protected Routes**: Secure navigation based on user roles
- **Session Management**: Persistent authentication state

### 📊 Dashboard & Analytics
- **Personal Dashboards**: Individual performance metrics
- **Team Dashboards**: Team Lead oversight and management
- **Real-time Metrics**: Live KPI tracking
- **Customizable Reports**: Flexible reporting system

### 🔄 Workflow Management
- **Task Management**: Create, assign, and track tasks
- **Lead Management**: Prospect tracking and conversion
- **Client Journey**: End-to-end client lifecycle management
- **Progress Tracking**: Real-time status updates

### 📱 User Experience
- **Responsive Design**: Mobile-friendly interface
- **Modern UI**: shadcn/ui components with Tailwind CSS
- **Loading States**: Smooth user experience
- **Error Handling**: User-friendly error messages

## 🏢 Departments

### BDM (Business Development Manager)
- **Lead Management**: Prospect acquisition and tracking
- **Client Journey**: Sales funnel management
- **Task Management**: Activity tracking and assignments
- **Reporting**: Performance analytics and KPIs

### Sales
- **Sales Pipeline**: Opportunity management
- **Customer Management**: Client relationship tracking
- **Performance Tracking**: Sales metrics and analytics

### HR
- **Employee Management**: Staff information and records
- **Workflow Automation**: HR process streamlining
- **Reporting**: HR analytics and insights

## 🚀 Quick Start

### Prerequisites
- Python ≥3.10
- Node.js ≥18
- Frappe Bench environment

### Backend Setup
```bash
# Clone the repository
git clone <repository-url>
cd apps/internal

# Install Frappe app
bench get-app internal
bench install-app internal

# Start Frappe server
bench start
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd apps/internal/internal_app

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Environment Configuration
```bash
# Development
npm run dev  # Runs on http://localhost:5173

# Production
npm run build  # Builds with /internal base path
```

## 🛠️ Development

### Project Structure
```
apps/internal/
├── internal/              # Frappe Backend
│   ├── api/              # API endpoints
│   ├── config/           # Configuration files
│   ├── hooks.py          # Frappe hooks
│   └── modules.txt       # Module definition
├── internal_app/         # React Frontend
│   ├── src/             # Source code
│   ├── package.json     # Dependencies
│   └── vite.config.ts   # Build configuration
└── README.md            # This file
```

### Technology Stack

#### Backend
- **Framework**: Frappe (Python-based)
- **Database**: MariaDB/MySQL via Frappe ORM
- **API**: RESTful endpoints with whitelist protection
- **Authentication**: Frappe user system

#### Frontend
- **Framework**: React 19.1.0
- **Language**: TypeScript
- **Build Tool**: Vite 7.0.0
- **Styling**: Tailwind CSS 4.1.11
- **UI Components**: shadcn/ui + Radix UI
- **Routing**: React Router DOM 7.6.3
- **State Management**: React Context + Hooks

### Development Commands
```bash
# Backend
bench start                    # Start Frappe server
bench migrate                  # Run database migrations
bench build --app internal     # Build Frappe app

# Frontend
npm run dev                    # Development server
npm run build                  # Production build
npm run lint                   # Code linting
npm run preview                # Preview production build
```

## 📚 API Documentation

### Authentication
```python
@frappe.whitelist()
def loginUser_roles(loginUser):
    """
    Get user roles and department information
    Returns: {error: bool, roles: [{department, role_type}]}
    """
```

### Response Format
```json
{
  "error": false,
  "roles": [
    {
      "department": "BDM",
      "role_type": "user"
    }
  ]
}
```

### Error Handling
```json
{
  "error": true,
  "message": "Error description"
}
```

## 🔧 Configuration

### Frappe Configuration
- **App Name**: Internal
- **Version**: 0.0.1
- **License**: MIT
- **Author**: Bala (bala@noveloffice.com)

### Frontend Configuration
- **Base Path**: `/internal` (production) vs `/` (development)
- **Build Output**: `../internal/www/internal_app.html`
- **Asset Path**: `/assets/internal/internal_app/`

## 🧪 Testing

### Backend Testing
```bash
bench run-tests --app internal
```

### Frontend Testing
```bash
npm run test
```

## 📦 Deployment

### Production Build
```bash
# Build frontend
cd apps/internal/internal_app
npm run build

# The build process:
# 1. Builds React app with /internal base path
# 2. Copies HTML entry to Frappe www directory
# 3. Assets served from Frappe's asset system
```

### Environment Variables
```bash
# Development
NODE_ENV=development

# Production
NODE_ENV=production
```

## 🤝 Contributing

### Development Workflow
1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

### Code Standards
- **Backend**: Follow Frappe coding standards
- **Frontend**: Use TypeScript and ESLint rules
- **Commits**: Use conventional commit messages
- **Documentation**: Update README for new features

### Branch Naming
- `feature/feature-name` - New features
- `bugfix/issue-description` - Bug fixes
- `hotfix/critical-fix` - Critical fixes
- `docs/documentation-update` - Documentation updates

## 📄 License

This project is licensed under the MIT License - see the [license.txt](license.txt) file for details.

## 👥 Team

- **Author**: Bala
- **Email**: bala@noveloffice.com
- **Organization**: Novel Office

## 📞 Support

For support and questions:
- **Email**: bala@noveloffice.com
- **Issues**: Create an issue in the repository
- **Documentation**: Check department-specific README files

---

**Built with ❤️ using Frappe and React**