# EGO CONTROL — Arquitectura de instalación host/guest v0.1

**Objetivo:** suministrar un prototipo autónomo que un investigador pueda compilar, instalar y atacar en una infraestructura **de laboratorio**, sin modificar producción.

## Repositorios y propiedad de confianza

| Repositorio | Entregable | Dominio de confianza |
|---|---|---|
| [ego-control](https://github.com/EGOTECH-IA/ego-control) (privado) | `ego-core-gate` + EGO CORE 10 en Rust | Evaluador host; **no** concede permisos de sistema por sí mismo |
| [ego-trust](https://github.com/EGOTECH-IA/ego-trust) (privado) | `trust.py`: políticas autenticadas HMAC para laboratorio | Clave secreta retenida por autoridad y host; no llega al guest |
| [ego-host-guard](https://github.com/EGOTECH-IA/ego-host-guard) (privado) | `host_guard.py`: broker de lectura de archivos | Host externo a VM, único poseedor de directorio protegido |
| [ego-guest-control](https://github.com/EGOTECH-IA/ego-guest-control) (privado) | `guest.py`: cliente sin privilegios | VM o proceso local adversarial |
| [ego-control-research](https://github.com/EGOTECH-IA/ego-control-research) (público) | `lab_integration.py` y `build_debs.py` | Pruebas y distribución, sin secretos |

## Secuencia end-to-end implementada en código

1. Autoridad emite una política con sujeto `uid:<n>` (Unix local) o `vm:<cid>` (vsock), operación `EGO.FILE.READ@1.0` y ámbito relativo.
2. Host Guard carga política y comprueba su HMAC con clave no distribuida al guest.
3. Guest transmite únicamente `{"action":"file.read","path":"allowed/readme.txt"}`.
4. Host determina el sujeto a partir de **credenciales del transporte**: SO_PEERCRED para Unix, CID del socket vsock para VM.
5. Host comprueba política y ejecuta `ego-core-gate` (Rust CORE 10); el gate debe responder `ELIGIBLE`.
6. Host abre el archivo con descriptores relativos al directorio host, `O_NOFOLLOW` y `O_DIRECTORY` por segmento; nunca acepta `../`, rutas absolutas ni esquemas URI.
7. Host entrega bytes permitidos en base64 o `DENY`; registra decisiones en un archivo de auditoría.
8. El laboratorio automatizado comprueba lectura positiva y negativas de ámbito, traversal, symlinks y política alterada.

Este flujo **sólo media las lecturas realizadas mediante el broker**. No hace imposible que un proceso con acceso directo al volumen lea esos mismos archivos. Esa propiedad depende de la separación real host/guest y del control de montajes/copias.

## Laboratorio VM con Linux/KVM (configuración manual)

La primera integración usa un socket Unix para verificar el protocolo local. El transporte opcional `AF_VSOCK` está implementado en Host Guard y Guest Control, pero **no se ha ejecutado ni verificado en una VM**.

En una VM QEMU/KVM autorizada y exclusiva para pruebas, se puede agregar un dispositivo vsock mediante:

```text
-device vhost-vsock-pci,guest-cid=5
```

Este argumento es solamente un fragmento ilustrativo de la configuración de QEMU: las opciones completas dependen de la VM, permisos del host y disponibilidad de vhost-vsock. No ejecutar como parte de servidores productivos.

En host, emitir política con sujeto `vm:5` y arrancar Host Guard con `--vsock-port 43771`. **No montar el directorio protegido ni la clave en la VM.** En guest:

```sh
python3 guest.py read --vsock 2:43771 --path allowed/readme.txt
```

`CID=2` identifica normalmente el host en Linux vsock; la resolución y alcance deben verificarse en el entorno concreto. Una política `vm:5` autoriza a la VM como conjunto, **no a sus procesos individuales**. Un agente root dentro de ella podrá hacer solicitudes con esa identidad; eso no debe considerarse atestación de un workload individual.

## Paquetes Debian

Con clones hermanos autorizados y herramientas `cargo`, `python3`, `dpkg-deb`:

```sh
cd ego-control-research
python3 build_debs.py
```

Debe producir en `dist/`:
- `ego-control-host-lab_0.1.0_amd64.deb`
- `ego-control-guest-lab_0.1.0_amd64.deb`

Los paquetes **no contienen claves ni políticas ni crean servicios root automáticos**. El instalador de host provee las herramientas bajo `/usr/lib/ego-control`; el administrador debe provisionar una identidad host restringida, directorios protegidos, claves y políticas de laboratorio. El instalador de guest solo incluye un cliente no confiable.

Los nombres y scripts anteriores son fuentes presentes en repositorios. **No se afirma que los paquetes ya hayan sido construidos o instalados.**

## Pruebas y criterios de avance

- **Verificado:** compilación, pruebas y lint Rust de `ego-core-gate` mediante CI de `ego-control`.
- **Preparado, pendiente de ejecución conjunta:** `lab_integration.py` compila el gate, autentica una política, arranca broker y cliente, y comprueba siete solicitudes.
- **Preparado, pendiente de ejecución:** empaquetado .deb desde clones hermanos.
- **No implementado:** instalación automática segura de una VM completa, producción con firmas asimétricas, atestación individual de workloads de VM, rotación/ revocación robusta, punto obligatorio para toda I/O, un mediador real de Git staging o HTTP.
- **No demostrado:** mitigación efectiva de CVE-2025-66389, CVE-2026-34070 o CVE-2026-27735 en los productos originales.

## Requisito para colaboración

El laboratorio debe pasar una revisión independiente del modelo de amenazas y pruebas desde dentro y fuera de una VM, especialmente omisión del broker, permisos del guest, repetición de solicitudes, delegación, TOCTOU, hard links, acceso a copias, flujos secundarios y permisos residuales del host.

La finalidad no es tener todos los controles terminados, sino entregar una **ruta explícita y medible** para investigar las garantías de EGO CORE 10.
