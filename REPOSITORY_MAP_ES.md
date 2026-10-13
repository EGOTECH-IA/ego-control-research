# MAPA — EGO CONTROL RESEARCH

```text
ego-control-research/
├── README.md                        ← primer acceso al laboratorio
├── REPOSITORY_MAP_ES.md             ← estructura de los CINCO repositorios
├── INTEGRATION_ARCHITECTURE_ES.md   ← modelo host↔VM, límites y pruebas
├── tests/
│   └── integration/
│       └── lab_integration.py        ← ESCENARIO completo de los cinco repos
├── lab_integration.py               ← comando compatible hacia tests/integration/
├── build_debs.py                     ← empaquetado de los componentes host/guest
└── dist/                             ← sólo si se generan paquetes; no versionado
```

**Rol:** orquestar pruebas, escenarios y paquetes, sin duplicar código de las otras cuatro piezas. Actualmente las fuentes de los cuatro repos restantes son privadas; este repositorio de investigación es público y sólo contiene guías y scripts de integración. No se publican secretos.

**Orden para leer el proyecto:** arquitectura `ego-control` → `core/rust/src/core` → `ego-trust` → `ego-host-guard` → `ego-guest-control` → `tests/integration`. El core Rust sí tiene CI; la integración completa y la VM aún requieren validación conjunta.
