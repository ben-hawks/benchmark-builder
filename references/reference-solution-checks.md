# Verifying the reference solution (element D)

These checks are mandatory before anything is built on a reference solution. Their results
go in the benchmark's `docs/VALIDATION.md`. Most of them come from mistakes found while
building axess-benchmark (`references/wa-hls4ml-example.md`).

The checks below are written for trained models with weights. For language-model
reference solutions, the same five checks take the form in `references/llm-benchmarks.md`
("Verifying LLM reference solutions"): model identity and revision, which answer key is
scored, the whole prompt-to-answer procedure, per-sample agreement, and reference vs
auxiliary.

1. **Identity and weights.** Confirm each checkpoint is the model the paper describes:
   - load it into the paper's architecture class with the framework's strict weight
     matching, so a wrong architecture fails loudly (e.g. PyTorch `strict=True`);
   - record its sha256 in `weights/MANIFEST.json`;
   - find out where the weights actually live. They may not be published at all, or be a
     loose file or a release asset.

   An earlier axess pass "validated" a GNN that turned out to be rule4ml's bundled GIN
   model, not the paper's GATv2 GNN.
2. **Training label vs scored label.** Ask: "Which field or label definition did each
   reference model train on, and is it the same one the metric scores?"
   - Check it **on data**, not from paper prose: match the training arrays' label rows
     against each candidate field.
   - In axess, the original GNN/Transformer matched `hls_resource_report` on 100% of
     rows and the benchmark's ground truth `resource_report` on 0%. Scored on the
     benchmark's truth, they were worse than predicting the mean, and had to be
     retrained.
   - A reference solution scored against a different target than it was trained on
     isn't a valid reference (`references/ontology.md`).
3. **The whole inference procedure.** Weights + preprocessing + statistics +
   post-processing are all part of the reference solution:
   - if preprocessing is vendored, copy it verbatim, with a bit-equivalence test against
     upstream;
   - find any derived artifacts the checkpoints need but don't contain (e.g.
     normalization statistics) and ship them in `weights/`. Rebuild them if they're
     missing, and verify the rebuild reproduces the checkpoint's own stored metrics;
   - look for post-processing that lives only in upstream eval code. (axess: a clip at
     the training maximum.)

   Each of these is something to look for in this benchmark's upstream code. Implement
   what you find in this benchmark's package; none of them is a step every benchmark
   has.
4. **Per-sample agreement.** Where upstream predictions exist, compare per sample, not
   just aggregate metrics (axess: ≤2.8e-4 relative over 92,933 samples). Then record
   golden outputs on fixture samples (`tests/test_pipeline.py`), which is the portable
   form of this check.
5. **Reference vs auxiliary.** List exactly which weights are reference solutions and
   which are only auxiliary comparisons. Auxiliary models are still run and scored, but
   they're marked as auxiliary in the leaderboard, `reference_solution/README.md` and the
   manifest (`references/repo-structure.md`, "Conventions").

