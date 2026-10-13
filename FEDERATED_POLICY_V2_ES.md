# Laboratorio federado v2: perfil de TUEGOS

Ejecutar **desde este repositorio**, teniendo cuatro clones hermanos:

```sh
python3 lab_integration.py
```

El escenario actualizado solicita un perfil `ego.lab.deployment/v2` en EGO TRUST para `tuegos-lab` (sujeto Unix verificado, operación FILE.READ@1.0, directorio `allowed`, máximo 64 bytes). HOST GUARD verifica MAC y grant, llama a EGO CORE Rust y abre únicamente el recurso permitido. Se prueban lectura positiva, ámbito denegado, traversal, symlink, exceso de bytes y política corrupta. **Escenario preparado pero no ejecutado aún** desde el conjunto de cinco repositorios actualizado.

Esto no demuestra contención de VM, atestación por proceso ni control de bypass del broker. [Contrato detallado](https://github.com/EGOTECH-IA/ego-control/blob/main/FEDERATED_POLICY_V2_ES.md).
