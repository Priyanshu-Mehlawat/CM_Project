# Where MIMIC belongs

Generated 15 November 2026 · storage guide 1.0.

For this project, the recommended starting point is an encrypted local research
VM or a dedicated research machine under the authorized researcher's control.
Keep the VM disk/storage inaccessible to the coding-agent host; do not mount it
into this workspace. A separate folder owned by the same login as Codex, even
with chmod 700 or a .gitignore entry, is not sufficient agent isolation. An
institution-managed research server is equally suitable if it enforces access
controls and your institution authorizes the use.

Inside that private environment, an example layout is:

```text
/srv/renalguard-private/
  raw/mimiciv/<downloaded-version>/hosp/
  raw/mimiciv/<downloaded-version>/icu/
  raw/eicu/<downloaded-version>/
  working/
  features/
  bundles/
  reports-private/
  reviewed-aggregates/
```

This is an example for the researcher to create privately, not a path configured,
created, inspected or accessed by the agent. Keep an ordinary source-code checkout
separate from these directories, even inside the private VM. Use the existing
explicit-manifest offline audit there; do not send file listings, records or raw
errors back into this chat. Review aggregates before sharing them.

## Local, Colab or cloud?

| Option | Fit for this project |
| --- | --- |
| Encrypted, isolated local VM/machine | Recommended default: private downloads, audit, cohort extraction, feature generation and training. Check available storage/RAM privately before downloading. |
| Official PhysioNet-accessed BigQuery | Supported alternative when local storage is inadequate. Request cloud access through PhysioNet, use your authorized Google account/project and review query billing and IAM. Raw tables remain in the official dataset; query results/derived exports remain restricted. |
| Colab | Not the default recommendation. A notebook is a compute interface, not the data-access approval itself. Confirm institutional/DUA permission for its runtime/storage first, restrict sharing and saved outputs, and prevent patient content from entering unapproved AI tools or telemetry. This session has not verified your Colab configuration. |
| Public Render or GitHub | Public application/source only. Do not put restricted raw records, feature CSVs or clinical models here. |

PhysioNet requires individual credentialing/training and the dataset agreement;
each collaborator needs their own access rights. A friend's access does not grant
the rest of the team access. The official MIMIC-IV project also treats derived
datasets and models as sensitive; downloading and fitting a model is not permission
to upload it to the public web application.

## What happens after storage is ready

1. The authorized researcher records the exact downloaded dataset version and
   runs the existing source-only audit in the isolated environment.
2. The team reviews table mappings and the baseline, availability, eligibility,
   follow-up and competing-event protocol decisions using the G1 template.
3. A versioned extraction/labeling pipeline generates the private index-level
   feature CSV. That raw-dataset adapter pipeline is still outstanding; the current
   app does not secretly generate it or access MIMIC on the server.
4. The researcher runs the existing offline trainer on those audited features and
   checks actual held-out results. Review any planned model/aggregate disclosure
   against the DUA before using a different hosting environment.

There is no need to upload MIMIC to make the current public demo operate. It uses
only authored synthetic samples. No MIMIC files or private directories were read
while writing this guide.

Sources checked 15 November 2026:

- [PhysioNet MIMIC-IV access, cloud availability and derived-model guidance](https://physionet.org/content/mimiciv/3.1/)
- [PhysioNet FAQ: individual access, training and cloud requirements](https://physionet.org/about/faqs/)
- [Official MIMIC BigQuery setup](https://mimic.mit.edu/docs/gettingstarted/cloud/bigquery.html)

The local-storage recommendation is an engineering recommendation for this
project, not a statement that PhysioNet forbids all cloud computation.
