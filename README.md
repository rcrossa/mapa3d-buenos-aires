# Repositorio / Source Code Directory

**Purpose:** This directory is where your actual project code lives.

---

## 📁 What Goes Here?

Place your application source code in this directory:

- **Web Applications** - React, Vue, Angular, etc.
- **Backend APIs** - FastAPI, Express, Django, etc.
- **Mobile Apps** - React Native, Flutter, etc.
- **Monorepos** - Multiple packages/services
- **CLI Tools** - Your command-line application
- **Libraries** - Shared libraries or packages

---

## 🏗️ Example Structures

### Single Application

```
repositorio/
├── src/
│   ├── index.js
│   ├── components/
│   ├── services/
│   └── utils/
├── tests/
├── package.json
└── README.md
```

### Monorepo (Frontend + Backend)

```
repositorio/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── README.md
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── README.md
└── shared/
    └── types/
```

### Python Project

```
repositorio/
├── src/
│   └── my_package/
│       ├── __init__.py
│       ├── main.py
│       └── utils.py
├── tests/
├── pyproject.toml
├── requirements.txt
└── README.md
```

### Mobile App

```
repositorio/
├── src/
│   ├── screens/
│   ├── components/
│   └── navigation/
├── android/
├── ios/
└── package.json
```

---

## 🎯 Template Structure

The complete template structure with your code:

```
template_agents/ (or your-project-name/)
├── repositorio/              ← YOUR CODE GOES HERE
│   └── [your application code]
│
├── .agents/                  ← AI Agent System (usually template-managed)
├── .specify/                 ← Agent-system workspace (customize this, not application source code)
│
├── docs/                     ← Documentation (optional)
├── scripts/                  ← Helper scripts (optional)
├── docker/                   ← Docker configs (optional)
│
├── .gitignore
├── README.md
├── HOW_TO_USE.md
└── [other config files]
```

Generated projects should expect `HOW_TO_USE.md` as the single human guide.

`.specify/` is not where your product source code goes.
It stores the agent-system workspace around the project: constitution, plan, feature artifacts, reviews, decisions, and session context.

---

## 📝 Best Practices

### 1. Keep Code Separate
- ✅ Code in `repositorio/`
- ✅ Agent system in `.agents/`
- ✅ Agent workflow and planning in `.specify/`
- ✅ This separation keeps things organized

### 2. Use Version Control
```bash
# From project root
git init
git add .
git commit -m "Initial commit with agent system"
```

### 3. Project-Specific README
Create a README.md inside `repositorio/` for your specific code:
```bash
repositorio/README.md  ← About your application
vs.
[root]/README.md       ← About the agent system template
```

### 4. Follow Constitution
Your code should follow the rules defined in:
`.specify/memory/constitution.md`

---

## 🚀 Getting Started

### Option 1: Start from Scratch

```bash
cd repositorio/

# For Node.js project
npm init -y

# For Python project
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# For any project
# Create your initial files and structure
```

### Option 2: Move Existing Code

```bash
# Copy your existing project
cp -R /path/to/existing/project/* repositorio/

# Or move it
mv /path/to/existing/project/* repositorio/
```

### Option 3: Clone from Git

```bash
# Clone your repo into repositorio
cd repositorio/
git init
git remote add origin <your-repo-url>
git pull origin main
```

---

## 🔄 Workflow

1. **Code** lives in `repositorio/`
2. **Agent system** manages development in `.agents/`
3. **Agent workflow artifacts** tracked in `.specify/`
4. **AI assists** by reading all three

Example workflow:
```
User: "@project-manager Create feature: user-authentication"
  ↓
Agent creates planning in .specify/features/user-authentication/
  ↓
User: "@ultra-think Implement user-authentication"
  ↓
Agent writes code in repositorio/src/...
  ↓
Tests, docs, and review follow automatically
```

---

## 🎨 Customization

Rename this directory if you prefer:
```bash
# Rename to 'src' or 'app' or 'project'
mv repositorio/ src/

# Update references in documentation
```

Or use multiple directories:
```bash
your-project/
├── frontend/     ← Instead of repositorio/
├── backend/      ← Multiple code directories
├── mobile/
├── .agents/
└── .specify/
```

---

## 📊 .gitignore

The root `.gitignore` should exclude:
- `repositorio/node_modules/`
- `repositorio/venv/`
- `repositorio/.env`
- `repositorio/dist/`
- `repositorio/build/`
- etc.

See root `.gitignore` for complete list.

---

## 💡 Tips

1. **Keep it clean** - Only code, tests, and configs here
2. **Use agent system** - Let agents help with boilerplate
3. **Follow constitution** - Adhere to your defined standards
4. **Document well** - Both in code and in .specify/
5. **Version control** - Keep git history of your work

---

## ❓ FAQ

**Q: Can I rename this directory?**  
A: Yes! Call it `src/`, `app/`, `project/`, whatever you prefer.

**Q: Can I have multiple code directories?**  
A: Yes! For example: `frontend/`, `backend/`, `mobile/`

**Q: Should this be version controlled?**  
A: Yes! This is your actual project code.

**Q: What about dependencies?**  
A: Install them here (node_modules/, venv/, etc.)

**Q: How do agents know to put code here?**  
A: They read your constitution.md which defines your project structure.

---

**Start coding!** Your agents are ready to assist. 🚀
