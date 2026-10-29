# Data governance

Stage 00 uses source code and independently authored synthetic interface fixtures.
The API does not accept patient uploads or open datasets, databases or model files.
Research mode fails closed at startup; no access-controlled research runtime exists.

Before authorized offline research, isolate credentialed files outside the checkout
and outside every coding agent's readable filesystem with OS/container controls.
A working-directory boundary or `.gitignore` is insufficient. No protected data
locations should be supplied to this app or its development commands.

Run later offline scripts in the isolated research environment without agent access.
Review outputs for identifiers, rows, free text, small cells and disclosive derived
artifacts. Only explicitly cleared aggregates and approved decisions may return.
Never process restricted datasets on CI, upload them, or add symlinks to them.

`make hooks` enables the staged-file hook. `make privacy` scans tracked/unignored
source and reachable history. Denied categories are rejected before reading.
These checks are heuristic; ignored files are not inspected, generic PHI is not
detectable reliably, and no automatic scan certifies a repository safe to publish.
The history check audits reachable refs, not reflogs, dangling objects, or other
clones. Disclosure review remains mandatory before any research output release.
