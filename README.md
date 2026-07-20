# Mapa 3D de Buenos Aires + Calculadora Solar

> Visualizacion 3D de edificios de CABA con analisis de potencial solar.
> Pipeline geoespacial Python → Vector Tiles → Visor MapLibre GL JS.

---

## Quick Start

```bash
git clone git@github.com:rcrossa/mapa3d-buenos-aires.git
cd mapa3d-buenos-aires

# Configurar acceso a datos
cp .env.example .env
# Editar .env con DOWNLOAD_URL y DOWNLOAD_TOKEN

# Descargar datos
./scripts/download_data.sh

# Instalar dependencias
pip install -r scripts/requirements.txt

# Procesar
python3 scripts/limpieza.py
python3 scripts/calculo_solar.py

# Compilar tiles
tippecanoe -z 16 -Z 13 -pd \
  -o data/tiles/buenos_aires_completo.pmtiles \
  data/processed/buenos_aires_3d_completo_limpio.geojson --force

# Servir
python3 web/server.py
open http://localhost:8000/web/index.html
```

---

## Que hace

- Procesa el dataset de edificios de CABA (reparacion geometrica, normalizacion CRS)
- Calcula potencial solar: paneles viables, energia generada, ahorro y payback
- Visualiza en mapa 3D interactivo con mapa de calor por area util

---

## Estructura

```
├── scripts/            # Pipeline Python
│   ├── download_data.sh
│   ├── limpieza.py
│   ├── calculo_solar.py
│   └── requirements.txt
├── web/                # Visor y servidor
│   ├── index.html
│   └── server.py
├── data/
│   ├── raw/            # Datos fuente (gitignored)
│   ├── processed/      # Pipeline output (gitignored)
│   ├── tiles/          # PMTiles (gitignored)
│   └── samples/        # Subset para desarrollo
├── docs/
│   └── pipeline.md     # Documentacion del flujo
├── archived/           # Codigo legacy de referencia
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

## Requisitos

- Python 3.9+
- [tippecanoe](https://github.com/felt/tippecanoe) (`brew install tippecanoe`)
- curl (preinstalado)
- Credenciales de descarga (solicitar a Roberto Rossa)

---

## Desarrollo rapido con sample

```bash
cp data/samples/buenos_aires_3d_sample.geojson data/raw/buenos_aires_3d_base.geojson
python3 scripts/limpieza.py
python3 scripts/calculo_solar.py
python3 web/server.py
```

---

## Licencia

Copyright (c) 2026 Roberto Rossa. Todos los derechos reservados.
Ver [LICENSE](LICENSE).
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
