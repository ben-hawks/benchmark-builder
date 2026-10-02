---
supports_discoverability: "Yes"
supports_accessibility: "Yes"
supports_interoperability: "Yes"
supports_reusability: "Yes"
supports_governed_use: "No"
supports_ai_usability: "Yes"
discoverability:
  datacard:
    template_version: "1.2"
    datacard_version: "1.0"
    filename: "genesis_datacard_wa_hls4ml.md"
    language: en
    id:
      type: local
      value: genesis-datacard-wa-hls4ml
    sensitivity:
      overall_sensitivity: Public
      source_marking_string: "None"
      source_marking_scheme: None
      classified_status: "No"
      cui_status: "No"
      ucni_status: "No"
    created_date: "2026-10-02"
    change_log:
      - change_date: "2026-10-02"
        datacard_version: "1.0"
        summary: "Initial creation with the datacard-generator workflow (AI-ModCon/BaseData_Skills@7ef7694, Genesis Data Card v1.2). Replaces a hand-filled markdown outline (DATA_CARD.md, 2026-08-28) that had no frontmatter."
    creation_method: Hybrid
    created_by:
      - contribution_date: "2026-10-02"
        description: "Drafted the card from the Hugging Face dataset card, the dataset files, the paper's DOI record, axess-benchmark, and live ORCID/ROR/OSTI lookups."
        creator:
          ai_model:
            name: "Claude Opus 5.5"
            version: "5.5"
            accessed_date: "2026-10-02"
            identifier:
              type: local
              value: claude-opus-5-5
            relationship: used_to_create
      - contribution_date: "2026-10-02"
        description: "Answered the generator's open questions (authors, contact, sponsors, identifiers, AI-usage statuses, science domain) and reviewed the card."
        creator:
          person:
            given_name: "Benjamin"
            family_name: "Hawks"
            orcid: "https://orcid.org/0000-0001-5700-0288"
            email: "bhawks@fnal.gov"
            affiliation:
              name: "Fermi National Accelerator Laboratory"
              ror_id: "https://ror.org/020hgte69"
            role:
              - Writing_Review_Editing
  identification:
    name: "wa-hls4ml"
    description: "wa-hls4ml: a dataset of neural networks converted to FPGA firmware with hls4ml and run through high-level synthesis (HLS) and logic synthesis, recording the resources and latency each design uses. It is the dataset of the wa-hls4ml benchmark for surrogate models that predict synthesis results without running synthesis."
    project: "wa-hls4ml"
    version: "1.0"
    primary_id:
      type: url
      value: "https://huggingface.co/datasets/fastmachinelearning/wa-hls4ml"
    additional_ids:
      - type: url
        value: "https://amsc.fnal.gov:2880/amsc/public/axess/wa-hls4ml/"
      - type: other
        value: "huggingface:fastmachinelearning/wa-hls4ml@bb0e7d5533c79b218faf59afa2798559cb84838e"
  dataset_description:
    science_domain: "Mathematics and Computing"
    dataset_summary: "684,058 neural networks (Keras/QKeras), each converted to FPGA firmware with hls4ml and synthesized, paired with the FPGA resources (LUT, FF, DSP, BRAM) reported by logic synthesis and the latency and initiation interval estimated by high-level synthesis. It is built to train and benchmark surrogate models that predict these results in milliseconds instead of minutes to hours of synthesis."
    purpose: "Training and evaluating surrogate models for resource and latency estimation in hls4ml hardware/software codesign, and serving as the common dataset of the wa-hls4ml benchmark (ACM TRETS 19(2), 2026)."
    collection_methodology: "Networks were generated in Keras/QKeras (grid search and random sampling of architectures, precisions and hls4ml settings), converted with hls4ml, and run through Vivado/Vitis HLS and logic synthesis for a target FPGA. Each run's model description, hls4ml configuration and synthesis reports were collected into one JSON record. Synthesis ran in containers on the National Research Platform Kubernetes cluster and on the Texas A&M ACES cluster. The 2_20 subset is an updated, re-synthesized version of the rule4ml dataset."
    data_characteristics: "One JSON record per synthesized network in per-subset JSON-array files: train/val/test, each with 7 generation subsets (2_20, 2layer, 3layer, conv1d, conv2d, latency, resource), plus a held-out exemplar set of 887 real scientific architectures."
    limitations: "Not every network completed logic synthesis: 9.3% of test records have an empty resource_report (and latency_report), and coverage is much lower for convolutional models. Latency fields are HLS estimates; the dataset has no post-synthesis latency. The 2_20 subset targets three different FPGA parts with Vivado 2019.1. Generated architectures have no skip connections and a limited reuse-factor range."
    tags:
      project: "wa-hls4ml"
      science: "hardware/software codesign; FPGA; hls4ml; high-energy physics triggers"
      object_type: Dataset
    task_category:
      - "Regression"
    keywords:
      - "hls4ml"
      - "FPGA"
      - "high-level synthesis"
      - "logic synthesis"
      - "resource estimation"
      - "latency estimation"
      - "surrogate model"
      - "neural network"
      - "hardware/software codesign"
      - "benchmark"
  product_type: Data
  dataset_type: ND
  release_status: Published
  dataset_publisher:
    name: "Hugging Face"
    description: "Hosting repository (Hugging Face Hub, organization fastmachinelearning)."
  contact:
    person:
      given_name: "Benjamin"
      family_name: "Hawks"
      orcid: "https://orcid.org/0000-0001-5700-0288"
      email: "bhawks@fnal.gov"
      affiliation:
        name: "Fermi National Accelerator Laboratory"
        ror_id: "https://ror.org/020hgte69"
  authors:
    - person:
        given_name: "Benjamin"
        family_name: "Hawks"
        orcid: "https://orcid.org/0000-0001-5700-0288"
        affiliation:
          name: "Fermi National Accelerator Laboratory"
          ror_id: "https://ror.org/020hgte69"
        role: [Conceptualization, Data_Collection, Data_Curation, Methodology, Software, Writing_Original_Draft]
    - person:
        given_name: "Jason"
        family_name: "Weitz"
        orcid: "https://orcid.org/0009-0004-6315-3562"
        affiliation:
          name: "University of California San Diego"
          ror_id: "https://ror.org/0168r3w48"
        role: [Methodology, Software, Formal_Analysis]
    - person:
        given_name: "Dmitri"
        family_name: "Demler"
        orcid: "https://orcid.org/0009-0009-9453-9755"
        affiliation:
          name: "University of California San Diego"
          ror_id: "https://ror.org/0168r3w48"
        role: [Methodology, Software, Formal_Analysis]
    - person:
        given_name: "Karla"
        family_name: "Tame-Narvaez"
        orcid: "https://orcid.org/0000-0002-2249-9450"
        affiliation:
          name: "Fermi National Accelerator Laboratory"
          ror_id: "https://ror.org/020hgte69"
        role: [Data_Collection, Software]
    - person:
        given_name: "Dennis"
        family_name: "Plotnikov"
        orcid: "https://orcid.org/0000-0002-2610-8226"
        affiliation:
          name: "Johns Hopkins University"
          ror_id: "https://ror.org/00za53h95"
        role: [Data_Collection, Software]
    - person:
        given_name: "Mohammad Mehdi"
        family_name: "Rahimifar"
        orcid: "https://orcid.org/0000-0002-6582-8322"
        affiliation:
          name: "Université de Sherbrooke"
          ror_id: "https://ror.org/00kybxq39"
        role: [Data_Collection, Software]
    - person:
        given_name: "Hamza"
        family_name: "Ezzaoui Rahali"
        orcid: "https://orcid.org/0000-0002-0352-725X"
        affiliation:
          name: "Université de Sherbrooke"
          ror_id: "https://ror.org/00kybxq39"
        role: [Data_Collection, Software]
    - person:
        given_name: "Audrey C."
        family_name: "Therrien"
        orcid: "https://orcid.org/0000-0001-6698-8400"
        affiliation:
          name: "Université de Sherbrooke"
          ror_id: "https://ror.org/00kybxq39"
        role: [Supervision, Writing_Review_Editing]
    - person:
        given_name: "Donovan"
        family_name: "Sproule"
        orcid: "https://orcid.org/0009-0008-6719-5769"
        affiliation:
          name: "Columbia University"
          ror_id: "https://ror.org/00hj8s172"
        role: [Data_Collection, Software]
    - person:
        given_name: "Elham E."
        family_name: "Khoda"
        orcid: "https://orcid.org/0000-0001-8720-6615"
        affiliation:
          name: "University of California San Diego"
          ror_id: "https://ror.org/0168r3w48"
        role: [Supervision, Writing_Review_Editing]
    - person:
        given_name: "Keegan A."
        family_name: "Smith"
        orcid: "https://orcid.org/0009-0004-0653-7033"
        affiliation:
          name: "Texas A&M University"
          ror_id: "https://ror.org/01f5ytq51"
        role: [Data_Collection, Software]
    - person:
        given_name: "Russell"
        family_name: "Marroquin"
        orcid: "https://orcid.org/0000-0002-3364-7463"
        affiliation:
          name: "University of California San Diego"
          ror_id: "https://ror.org/0168r3w48"
        role: [Data_Collection, Software]
    - person:
        given_name: "Giuseppe"
        family_name: "Di Guglielmo"
        orcid: "https://orcid.org/0000-0002-5749-1432"
        affiliation:
          name: "Fermi National Accelerator Laboratory"
          ror_id: "https://ror.org/020hgte69"
        role: [Supervision, Writing_Review_Editing]
    - person:
        given_name: "Nhan"
        family_name: "Tran"
        orcid: "https://orcid.org/0000-0002-8440-6854"
        affiliation:
          name: "Fermi National Accelerator Laboratory"
          ror_id: "https://ror.org/020hgte69"
        role: [Supervision, Funding_Acquisition, Writing_Review_Editing]
    - person:
        given_name: "Javier"
        family_name: "Duarte"
        orcid: "https://orcid.org/0000-0002-5076-7096"
        affiliation:
          name: "University of California San Diego"
          ror_id: "https://ror.org/0168r3w48"
        role: [Supervision, Funding_Acquisition, Writing_Review_Editing]
    - person:
        given_name: "Vladimir"
        family_name: "Loncar"
        orcid: "https://orcid.org/0000-0003-3651-0232"
        affiliation:
          name: "European Organization for Nuclear Research"
          ror_id: "https://ror.org/01ggx4157"
        role: [Supervision, Writing_Review_Editing]
  sponsor_organizations:
    - name: "U.S. Department of Energy, Office of Science, Office of High Energy Physics"
      description: "Through Fermi National Accelerator Laboratory's management and operating contract, as recorded on the paper's OSTI record (OSTI ID 3018489)."
      ror_id: "https://ror.org/035m6g344"
      award_number: "89243024CSC000002"
      funding_source: DOE_Program_SC
      program: "High Energy Physics"
    - name: "U.S. National Science Foundation (National Research Platform)"
      description: "Awards supporting the National Research Platform Kubernetes cluster used for synthesis, as acknowledged in the paper."
      ror_id: "https://ror.org/021nxhr62"
      award_number: "CNS-1730158, ACI-1540112, ACI-1541349, OAC-1826967, OAC-2112167, CNS-2100237, CNS-2120019"
      funding_source: Other_Federal
      program: "National Research Platform"
    - name: "U.S. National Science Foundation (ACES)"
      description: "Award supporting the Texas A&M ACES cluster used for synthesis, as acknowledged in the paper."
      ror_id: "https://ror.org/021nxhr62"
      award_number: "2112356"
      funding_source: Other_Federal
      program: "ACES (Accelerating Computing for Emerging Sciences)"
  sponsoring_doe_program_office: "Office of Science"
  sponsoring_doe_subprogram: "High Energy Physics"
  research_organizations:
    - name: "Fermi National Accelerator Laboratory"
      ror_id: "https://ror.org/020hgte69"
    - name: "University of California San Diego"
      ror_id: "https://ror.org/0168r3w48"
    - name: "Johns Hopkins University"
      ror_id: "https://ror.org/00za53h95"
    - name: "Université de Sherbrooke"
      ror_id: "https://ror.org/00kybxq39"
    - name: "Columbia University"
      ror_id: "https://ror.org/00hj8s172"
    - name: "Texas A&M University"
      ror_id: "https://ror.org/01f5ytq51"
    - name: "European Organization for Nuclear Research"
      ror_id: "https://ror.org/01ggx4157"
  facilities:
    - name: "National Research Platform (Nautilus Kubernetes cluster)"
      description: "Ran hls4ml conversion, HLS and logic synthesis in containers (Ubuntu 20.04.4, modified xilinx-docker v2023.2 images, 3 vCPU and 16 GB per pod). No ROR identifier exists."
      role: [Resources]
      location:
        description: "Distributed U.S. research network"
    - name: "ACES cluster, Texas A&M High Performance Research Computing"
      description: "Ran synthesis jobs with Vitis 2024.2 (2 vCPU and 32 GB per job)."
      role: [Resources]
      location:
        description: "Texas A&M University, College Station, Texas, USA"
        ror_id: "https://ror.org/01f5ytq51"
  sensitivity:
    overall_sensitivity: Public
    source_marking_string: "None"
    source_marking_scheme: None
    classified_status: "No"
    cui_status: "No"
    ucni_status: "No"
  workflow:
    state: Published
    is_intermediate: "No"
accessibility:
  access_policy:
    access_level: Open
    access_restrictions: "No access restrictions. Use is governed by the CC-BY-NC-4.0 license (non-commercial use, with attribution)."
    intended_partner_classes:
      - Public
    policy_url: "https://creativecommons.org/licenses/by-nc/4.0/"
  access:
    current_location: "https://huggingface.co/datasets/fastmachinelearning/wa-hls4ml"
    publicly_facing_landing_page_url: "https://huggingface.co/datasets/fastmachinelearning/wa-hls4ml"
    intended_repositories:
      - name: "Hugging Face Hub"
        access_level: Open
        is_primary: "Yes"
        data_services:
          - name: "Hugging Face Hub API"
            endpoint: "https://huggingface.co/api/datasets/fastmachinelearning/wa-hls4ml"
            documentation_url: "https://huggingface.co/docs/huggingface_hub"
            authentication: None
      - name: "Fermilab American Science Cloud Data Platform (dCache, mirror)"
        access_level: Open
        is_primary: "No"
        date_deposited: "2025-12-05"
        data_services:
          - name: "dCache HTTPS (WebDAV) door"
            endpoint: "https://amsc.fnal.gov:2880/amsc/public/axess/wa-hls4ml/"
            authentication: None
  dataset_scale:
    record_count: 684058
    record_unit: samples
    uncompressed_bytes: 4981438716
interoperability:
  data_structure:
    formats:
      - "JSON"
    encoding: "UTF-8"
    modalities:
      - "structured"
      - "tabular"
    features:
      - name: "meta_data"
        data_type: "other"
        range: "object: uuid (model_id in the 2_20 subset; unique per split), model_name, project tarball name"
      - name: "model_config"
        data_type: "other"
        range: "ordered list of per-layer objects (class_name, shapes, parameters, reuse_factor, layer-specific fields)"
      - name: "hls_config"
        data_type: "other"
        range: "object: Model.{Precision, ReuseFactor, Strategy, BramFactor, TraceOutput}, clock_period, io_type"
      - name: "resource_report"
        data_type: "string"
        unit: "count"
        range: "post-logic-synthesis bram, dsp, ff, lut (string-valued; BRAM can be fractional, a BRAM18 = 0.5); {} if synthesis did not complete"
      - name: "hls_resource_report"
        data_type: "string"
        unit: "count"
        range: "post-HLS (C-synthesis) resource estimates, same keys as resource_report"
      - name: "latency_report"
        data_type: "string"
        unit: "clock cycles"
        range: "post-HLS latency estimates: cycles_min, cycles_max, interval_min, interval_max, target_clock, estimated_clock; {} alongside an empty resource_report"
      - name: "target_part"
        data_type: "string"
        range: "FPGA part, e.g. xcu250-figd2104-2L-e (Alveo U250), xc7z020clg400-1"
      - name: "vivado_version"
        data_type: "string"
        range: "e.g. 2023.2, 2024.2; absent in 2_20, which has backend/backend_version (e.g. VivadoAccelerator, 2019.1)"
      - name: "hls4ml_version"
        data_type: "string"
        range: "e.g. 0.8.1, 1.1.0"
    splits:
      - "train"
      - "val"
      - "test"
      - "exemplar"
    language: en
  provenance:
    was_generated_by: "Synthesis of generated neural networks: Keras/QKeras models were generated by wa-hls4ml-search (grid search for 2- and 3-layer dense networks; random sampling for 3-7 layer dense and convolutional networks; precision 2-16 bits; reuse factors 1-4093 dense and 8192-32795 conv), converted with hls4ml, and run through AMD Vivado/Vitis HLS and logic synthesis. The 2_20 subset re-synthesizes the rule4ml dataset's generation method with II and logic-synthesis results added."
    processing_steps: "Per-run JSON reports (model config, hls4ml config, C-synthesis and logic-synthesis reports, versions, target part) were merged into one JSON array per split and generation subset, and the synthesized projects were archived separately (wa-hls4ml-projects). Runs where logic synthesis did not complete keep empty report objects rather than being dropped. The exemplar set (887 real scientific architectures: Jet, Quarks, Anomaly, Bipc, Cookie, AutoMLP, Particle) is disjoint from the synthetic splits by construction."
    simulation_details: "Labels are tool outputs, not measurements: AMD Vivado/Vitis HLS (C-synthesis estimates) and Vivado logic synthesis (post-synthesis resource utilization). No on-board measurement."
    software_environment:
      os: "Ubuntu 20.04.4 LTS (NRP containers)"
      container: "Modified xilinx-docker v2023.2 'user' images"
      hpc_environment: "National Research Platform Kubernetes (3 vCPU, 16 GB per pod; AMD tools on a Ceph volume) and Texas A&M ACES (Vitis 2024.2; 2 vCPU, 32 GB per job)"
  dates:
    modified: "2026-07-17"
  semantic_layer:
    schema_url: "https://github.com/ben-hawks/axess-benchmark/blob/main/data/SCHEMA.md"
  related_resources:
    datasets:
      - name: "wa-hls4ml-projects"
        description: "Companion dataset: the full synthesized Vivado/Vitis project (reports, logs, RTL) for every sample, referenced by meta_data."
        identifier:
          type: url
          value: "https://huggingface.co/datasets/fastmachinelearning/wa-hls4ml-projects"
        relationship: references
    publications:
      - type: doi
        value: "10.1145/3787490"
        relationship: references
      - type: other
        value: "arXiv:2511.05615"
        relationship: references
    software:
      - name: "hls4ml"
        identifier:
          type: url
          value: "https://github.com/fastmachinelearning/hls4ml"
        relationship: used_to_create
      - name: "wa-hls4ml-search"
        identifier:
          type: url
          value: "https://github.com/ben-hawks/wa-hls4ml-search"
        relationship: used_to_create
      - name: "AMD Vivado/Vitis HLS and Vivado logic synthesis"
        identifier:
          type: url
          value: "https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/vivado.html"
        relationship: used_to_create
      - name: "axess-benchmark"
        identifier:
          type: url
          value: "https://github.com/ben-hawks/axess-benchmark"
        relationship: used_to_analyze
    ai_models:
      - name: "wa-hls4ml GNN (GATv2), retrained on post-synthesis resources"
        accessed_date: "2026-10-02"
        identifier:
          type: url
          value: "https://github.com/ben-hawks/wa_hls4ml_models/releases/tag/resource-report-retrain"
        relationship: trained_on
      - name: "wa-hls4ml Transformer, retrained on post-synthesis resources"
        accessed_date: "2026-10-02"
        identifier:
          type: url
          value: "https://github.com/ben-hawks/wa_hls4ml_models/releases/tag/resource-report-retrain"
        relationship: trained_on
  domain_metadata:
    name: "FPGA synthesis context"
    description: "Constraints and targets that give each sample its meaning: the FPGA part and toolchain it was synthesized with, and which report fields the wa-hls4ml benchmark scores."
    science_domain: "Mathematics and Computing"
    schema_reference:
      type: url
      value: "https://github.com/ben-hawks/axess-benchmark/blob/main/data/SCHEMA.md"
    fields:
      target_fpga:
        field_value: "AMD Alveo U250 (most subsets); xcu200, xc7z020 and xczu9eg in 2_20; U200/U250 in the exemplar set"
        data_type: "string"
        description: "FPGA part each design was synthesized for; recorded per sample in target_part"
      toolchain:
        field_value: "Vivado/Vitis 2019.1, 2023.2 and 2024.2; hls4ml versions vary (e.g. 0.8.1, 1.1.0)"
        data_type: "string"
        description: "Per-sample in vivado_version / backend_version and hls4ml_version"
      benchmark_targets:
        field_value: "BRAM, DSP, FF, LUT from resource_report; cycles_max, interval_max from latency_report"
        data_type: "string"
        description: "The six regression targets the wa-hls4ml benchmark scores"
reusability:
  license:
    spdx_id: "CC-BY-NC-4.0"
    name: "Creative Commons Attribution-NonCommercial 4.0 International"
    url: "https://creativecommons.org/licenses/by-nc/4.0/"
  stewardship:
    level: Project_Managed
    maintainer:
      person:
        given_name: "Benjamin"
        family_name: "Hawks"
        orcid: "https://orcid.org/0000-0001-5700-0288"
        email: "bhawks@fnal.gov"
        affiliation:
          name: "Fermi National Accelerator Laboratory"
          ror_id: "https://ror.org/020hgte69"
    update_frequency: Ad_Hoc
    versioning_strategy: "Versioned by Hugging Face git revisions; pin a commit hash for reproducible work (main = bb0e7d5533c79b218faf59afa2798559cb84838e on 2026-10-02). The data files are unchanged since at least 2025-12-05: a copy downloaded that day matches main byte for byte (checked 2026-10-02)."
  data_quality:
    completeness: "Records per split, parsed 2026-10-02: train 478,216, val 102,471, test 102,484, exemplar 887 (684,058 total). Logic-synthesis results are missing for some runs: 92,933 of 102,484 test records (90.7%) and 886 of 887 exemplar records have a non-empty resource_report. Coverage is much lower for convolutional models (about 29% of conv2d and 42% of conv1d records across train/val/test)."
    known_issues: "(1) The train and val arrays contain 3 null entries (2 in train, 1 in val); loaders must skip them. (2) The Hugging Face dataset card states 478,220 train and 102,472 val samples; the files hold 478,216 and 102,471 records. (3) latency_report holds HLS estimates, not post-synthesis latency. (4) hls_resource_report and resource_report differ measurably for the same sample; mixing them silently changes the target. (5) The 2_20 subset was synthesized for three FPGA parts with Vivado 2019.1, while the part is only recorded, so BRAM varies with a field models often ignore. (6) Report values are strings and need casting."
    validation_methods: "Record counts parsed with a streaming JSON parser (ijson) on a copy whose 22 data files match the current Hugging Face files byte for byte (sizes, and git blob hash for the non-LFS file). axess-benchmark cross-checks: training labels of the paper's original models match hls_resource_report on 100% of rows and resource_report on 0%; rebuilt normalization statistics match the shipped ones to float32 precision; preprocessing is bit-identical to upstream."
    missing_data_codes:
      code: "{} (empty report object) or null (array entry)"
      description: "An empty resource_report/latency_report means logic synthesis did not complete or was not recorded: treat as missing, never as zero. A null array entry is not a record and must be skipped."
  citation:
    preferred_citation:
      author: "Hawks, Benjamin and Weitz, Jason and Demler, Dmitri and Tame-Narvaez, Karla and Plotnikov, Dennis and Rahimifar, Mohammad Mehdi and Rahali, Hamza Ezzaoui and Therrien, Audrey C. and Sproule, Donovan and Khoda, Elham E. and Smith, Keegan A. and Marroquin, Russell and Di Guglielmo, Giuseppe and Tran, Nhan and Duarte, Javier and Loncar, Vladimir"
      title: "wa-hls4ml: A Benchmark and Surrogate Models for hls4ml Resource and Latency Estimation"
      year: "2026"
      publisher: "Association for Computing Machinery"
      doi: "10.1145/3787490"
      url: "https://doi.org/10.1145/3787490"
      eprinttype: "arXiv"
      eprint: "2511.05615"
      note: "ACM Transactions on Reconfigurable Technology and Systems 19(2), 1-29. The dataset has no DOI of its own; cite the paper."
  integrity:
    checksum_available: "Yes"
    checksum_type: "sha256"
    checksum_value: |
      exemplar/exemplar_models.json 1fc8c35536a0ab9f15cc5ba5ea2a568db0cc77f8c4c42f162fa5f1feb7eb41aa
      test/test_2_20_merged.json 7ebf45d8d63d0114023fd2395d5794249050b1549158a76ba2821f1d19b4c041
      test/test_2layer_merged.json eb4039a5818dca3b789b11c5dc6a4b58c43cc958d1bfd07478fd62016bca21da
      test/test_3layer_merged.json 8832bcca9c269749e7fdb1fb45ef54b8276e2d7b87e26855188ab0b48bc9c039
      test/test_conv1d_merged.json f85d19b1114512b3ada7753085291bce7431df18641309916107197f891b9184
      test/test_conv2d_merged.json 725c3f344036fa715183c03813832bb2860b6fbd82674e9ba7a0aba1bd8c126a
      test/test_latency_merged.json d744bbf248e9fe543d62a6ce1e359d34f04071ff7bde4920c558b99b08e9774b
      test/test_resource_merged.json 7a2091a34f30028c0f1620e93d4cca5647a060b47d9d563cb7b16dcf7502e017
      train/train_2_20_merged.json 1543dee6fbdcfefabdc5d432145747cc97c22eb1f2833f8a769184a156b4d988
      train/train_2layer_merged.json b43942fcb652064f3cd404ab29bd717f633ad16044b438450f7c20b5839166f6
      train/train_3layer_merged.json e662c59ea5989bf54c63f645f6276a10626d0ae695e16de432eaf57373232a56
      train/train_conv1d_merged.json fe72493df163fc5a941c688991a59497d190ba6a0876aebeb9da91d9b1a4a9f4
      train/train_conv2d_merged.json a8ef2d92f9073c82b0aba448ef8519f640b62470c4b34bb5261215f28c2d251b
      train/train_latency_merged.json 198c3bd217f4c556f4bf6785a1a583938bfe39bffe3a660fecbc8fe41d691406
      train/train_resource_merged.json befa8844e5f936392414185323978e4b124afd97ec4037fad270d60c597e6772
      val/val_2_20_merged.json 7604e8e0a4bf0301f0688acb886aeaccd4829b6e5d519c20f7d6258a23a432ea
      val/val_2layer_merged.json a0033f556c0c91cfc0f14b8b5113cb3781e03118ee6337f6039c32b786ff69aa
      val/val_3layer_merged.json 5d53a38d87bd44c6358c94c352a5500bd1903d049257576ef0a5a787e798fbd4
      val/val_conv1d_merged.json 95321153416b4392565f27d6b7a02cb8c54697988312359f12be9fa2e618ee5d
      val/val_conv2d_merged.json aebc307f9d3da2c7af3e536807013284ea36ac8afb338a2e9560be1ea7975d5b
      val/val_latency_merged.json 4fa890b8bc5ef33c1c071c12a4e4378fb4566ac37fef1136790aa1571fb7ca0f
      val/val_resource_merged.json bb47bec4210c1bf4611757cc44bca92f4e2a5bf1b545a01b0e80f9625dbfbcfe
    fixity_policy: "sha256 per data file at revision bb0e7d5. 21 values are Hugging Face's own Git LFS object IDs; exemplar_models.json is not in LFS (git blob 58e0c0f3cc2f6052834c2f4f77583d4864ba892a), and its sha256 was computed from a byte-identical copy on 2026-10-02. Verify with sha256sum after download."
ai_usability:
  ai_usage:
    training_use_status: "Yes"
    inference_use_status: "Yes"
    evaluation_use_status: "Yes"
    restrictions: "Non-commercial use only, with attribution (CC-BY-NC-4.0). Benchmark scores must use resource_report for resources and latency_report for latency, never hls_resource_report, and must exclude samples without ground truth rather than impute them."
    bias_risks: "Heavily weighted toward fully connected networks (608,679 of 683,176 generated networks per the dataset card), and convolutional records lose more ground truth to incomplete synthesis. Synthetic architectures differ strongly from real ones: all reference surrogate models degrade sharply on the exemplar set. The target part is not a modelled input, which biases BRAM predictions on the multi-part 2_20 subset."
    safety_considerations: "None identified. The data describes FPGA resource use of small neural networks generated for this dataset and contains no personal, export-controlled or hazardous information."
    human_review_required: "No"
---

# Datacard for wa-hls4ml

**Last Updated**: 2026-10-02 (created; no updates yet)

### Machine Usability Snapshot

| Intended Capability | DataCard Support |
| ------ | ------ |
| Discoverability | Yes |
| Accessibility | Yes |
| Interoperability | Yes |
| Reusability | Yes |
| Governed Use | No |
| AI Usability | Yes |
| License Clarity | Yes |
| Checksum / Fixity | Yes |
| Semantic Context | No |

# ---- Discoverable ----

## Description

### Dataset Description

684,058 neural networks (Keras/QKeras), each converted to FPGA firmware with hls4ml and
synthesized, paired with:
- the FPGA resources (LUT, FF, DSP, BRAM) reported by logic synthesis;
- the latency and initiation interval estimated by high-level synthesis.

It is built to train and benchmark surrogate models that predict these results in
milliseconds instead of minutes to hours of synthesis.

### Domain and Purpose

Science domain: "Mathematics and Computing" (hardware/software codesign for ML on FPGAs),
motivated by real-time scientific instrumentation such as high-energy-physics triggers.
The dataset exists to train and evaluate resource and latency surrogate models for
hls4ml. It is the common dataset of the wa-hls4ml benchmark (ACM TRETS 19(2), 2026); the
runnable benchmark is [axess-benchmark](https://github.com/ben-hawks/axess-benchmark).

## Keywords

hls4ml, FPGA, high-level synthesis, logic synthesis, resource estimation, latency
estimation, surrogate model, neural network, hardware/software codesign, benchmark

## Sensitivity

### Security / Marking Considerations

Overall sensitivity: Public. Classification: No. CUI: No. UCNI: No. No source markings.
The datacard itself is also Public.

## Context and Provenance

### Resources used, including funding and facilities, to create the dataset

Sponsors:
- U.S. Department of Energy, Office of Science, Office of High Energy Physics
  ([ROR](https://ror.org/035m6g344)), through Fermilab's contract 89243024CSC000002 (as
  recorded on the paper's OSTI record, 3018489);
- U.S. National Science Foundation ([ROR](https://ror.org/021nxhr62)), through the
  National Research Platform awards CNS-1730158, ACI-1540112, ACI-1541349, OAC-1826967,
  OAC-2112167, CNS-2100237 and CNS-2120019, and the ACES award 2112356.

Facilities:
- the National Research Platform (Nautilus) Kubernetes cluster;
- the ACES cluster at Texas A&M High Performance Research Computing.

Research organizations: Fermi National Accelerator Laboratory, University of California
San Diego, Johns Hopkins University, Université de Sherbrooke, Columbia University, Texas
A&M University, and CERN.

### Developed by

CRediT roles were proposed by the card's AI drafter and confirmed by the reviewer. No
contribution statement exists.

- Benjamin Hawks ([0000-0001-5700-0288](https://orcid.org/0000-0001-5700-0288)), Fermilab
  — Conceptualization, Data Collection, Data Curation, Methodology, Software, Writing
  (original draft)
- Jason Weitz ([0009-0004-6315-3562](https://orcid.org/0009-0004-6315-3562)), UC San Diego
  — Methodology, Software, Formal Analysis
- Dmitri Demler ([0009-0009-9453-9755](https://orcid.org/0009-0009-9453-9755)), UC San
  Diego — Methodology, Software, Formal Analysis
- Karla Tame-Narvaez ([0000-0002-2249-9450](https://orcid.org/0000-0002-2249-9450)),
  Fermilab — Data Collection, Software
- Dennis Plotnikov ([0000-0002-2610-8226](https://orcid.org/0000-0002-2610-8226)), Johns
  Hopkins University — Data Collection, Software
- Mohammad Mehdi Rahimifar ([0000-0002-6582-8322](https://orcid.org/0000-0002-6582-8322)),
  Université de Sherbrooke — Data Collection, Software
- Hamza Ezzaoui Rahali ([0000-0002-0352-725X](https://orcid.org/0000-0002-0352-725X)),
  Université de Sherbrooke — Data Collection, Software
- Audrey C. Therrien ([0000-0001-6698-8400](https://orcid.org/0000-0001-6698-8400)),
  Université de Sherbrooke — Supervision, Writing (review and editing)
- Donovan Sproule ([0009-0008-6719-5769](https://orcid.org/0009-0008-6719-5769)), Columbia
  University — Data Collection, Software
- Elham E. Khoda ([0000-0001-8720-6615](https://orcid.org/0000-0001-8720-6615)), UC San
  Diego — Supervision, Writing (review and editing)
- Keegan A. Smith ([0009-0004-0653-7033](https://orcid.org/0009-0004-0653-7033)), Texas A&M
  University — Data Collection, Software
- Russell Marroquin ([0000-0002-3364-7463](https://orcid.org/0000-0002-3364-7463)), UC San
  Diego — Data Collection, Software
- Giuseppe Di Guglielmo ([0000-0002-5749-1432](https://orcid.org/0000-0002-5749-1432)),
  Fermilab — Supervision, Writing (review and editing)
- Nhan Tran ([0000-0002-8440-6854](https://orcid.org/0000-0002-8440-6854)), Fermilab —
  Supervision, Funding Acquisition, Writing (review and editing)
- Javier Duarte ([0000-0002-5076-7096](https://orcid.org/0000-0002-5076-7096)), UC San
  Diego — Supervision, Funding Acquisition, Writing (review and editing)
- Vladimir Loncar ([0000-0003-3651-0232](https://orcid.org/0000-0003-3651-0232)), CERN —
  Supervision, Writing (review and editing)

### Contributed by

No separate contributors are listed beyond the authors.

## Methods

### Dataset generation, collection, and procedures

Networks were generated in Keras/QKeras by
[wa-hls4ml-search](https://github.com/ben-hawks/wa-hls4ml-search):
- grid search for 2- and 3-layer dense networks;
- random sampling for 3-7 layer dense and convolutional networks;
- precision 2-16 bits;
- reuse factors 1-4093 (dense) and 8192-32795 (conv).

Each network was converted with hls4ml, then run through AMD Vivado/Vitis HLS and logic
synthesis for a target FPGA. The 2_20 subset re-synthesizes the rule4ml dataset's
generation method, adding II and logic-synthesis results.

Each run's model description, hls4ml configuration, C-synthesis and logic-synthesis
reports, versions and target part were collected into one JSON record. The records were
merged into one JSON array per split and generation subset, and the synthesized projects
were archived separately in wa-hls4ml-projects. Runs where logic synthesis didn't complete
keep empty report objects rather than being dropped.

Labels are tool outputs, not measurements: HLS estimates and post-logic-synthesis
utilization, with no on-board measurement. The exemplar set (887 real scientific
architectures: Jet, Quarks, Anomaly, Bipc, Cookie, AutoMLP, Particle) is disjoint from the
synthetic splits by construction.

---

# ---- Accessible ----

## Sharing & Access

Access level: Open, with no account or agreement required. Use is governed by
CC-BY-NC-4.0 (non-commercial, with attribution).

- **Primary:** [Hugging Face](https://huggingface.co/datasets/fastmachinelearning/wa-hls4ml)
  (`huggingface_hub` / `datasets`, no authentication).
- **Mirror:** Fermilab American Science Cloud Data Platform,
  `https://amsc.fnal.gov:2880/amsc/public/axess/wa-hls4ml/` (dCache HTTPS, public read,
  deposited 2025-12-05).
- **Companion:** full synthesized projects in
  [wa-hls4ml-projects](https://huggingface.co/datasets/fastmachinelearning/wa-hls4ml-projects).

Contact: Benjamin Hawks, bhawks@fnal.gov (Fermilab).

---

# ---- Interoperable ----

## Data Structure

### Files & Structure

The dataset consists of 684,058 samples in 22 JSON files (UTF-8), totaling 4,981,438,716
bytes uncompressed. Splits: train, val, test (each with the 7 generation subsets 2_20,
2layer, 3layer, conv1d, conv2d, latency, resource) and exemplar. Each file is a JSON array
of records named `<split>/<split>_<subset>_merged.json`; the exemplar set is
`exemplar/exemplar_models.json`. Modalities: structured records with tabular targets.

### Specialized formats or other abbreviations used

- JSON: one array per file, one object per synthesized network. The largest file is
  1.9 GB, so stream it (e.g. `ijson`) rather than loading it whole.
- LUT / FF / DSP / BRAM: FPGA look-up tables, flip-flops, DSP slices, block RAM (BRAM18 =
  0.5 BRAM).
- II: initiation interval, in clock cycles.
- HLS: high-level (C) synthesis.

## Related Resources

### Related datasets, standards, metadata, and ontologies

- wa-hls4ml-projects (https://huggingface.co/datasets/fastmachinelearning/wa-hls4ml-projects)
  — companion; references
- Field-level schema: axess-benchmark
  [`data/SCHEMA.md`](https://github.com/ben-hawks/axess-benchmark/blob/main/data/SCHEMA.md)

### Related publications

- doi:10.1145/3787490: the paper describing the dataset and benchmark (ACM TRETS 19(2),
  2026)
- arXiv:2511.05615: preprint

### Related software

- [hls4ml](https://github.com/fastmachinelearning/hls4ml): used to create (versions vary per
  subset, e.g. 0.8.1, 1.1.0)
- [wa-hls4ml-search](https://github.com/ben-hawks/wa-hls4ml-search): used to create
- AMD Vivado/Vitis HLS and Vivado logic synthesis (2019.1, 2023.2, 2024.2): used to create
- [axess-benchmark](https://github.com/ben-hawks/axess-benchmark): used to analyze

### Related ai model

- wa-hls4ml GNN (GATv2) and Transformer, retrained on post-synthesis resources: trained
  on this dataset
  ([release `resource-report-retrain`](https://github.com/ben-hawks/wa_hls4ml_models/releases/tag/resource-report-retrain));
  see `MODEL_CARD.md`

## Understanding the Data

### List of variable name(s), description(s), unit(s), and value labels for each variable in the dataset/file.

| Variable Name | Description | Unit | Value Labels |
|---|---|---|---|
| `meta_data` | uuid (model_id in 2_20; unique per split), model name, project tarball name | N/A | N/A |
| `model_config` | ordered per-layer list: class_name, shapes, parameters, reuse_factor, layer-specific fields | N/A | N/A |
| `hls_config` | Model.{Precision, ReuseFactor, Strategy, BramFactor, TraceOutput}, clock_period, io_type | N/A | Strategy: Latency / Resource; io_type: io_parallel / io_stream |
| `resource_report` | post-logic-synthesis `bram`, `dsp`, `ff`, `lut` (strings) | count | `{}` = synthesis did not complete |
| `hls_resource_report` | post-HLS resource estimates, same keys | count | not ground truth for the benchmark |
| `latency_report` | post-HLS `cycles_min`, `cycles_max`, `interval_min`, `interval_max`, `target_clock`, `estimated_clock` | clock cycles | `{}` alongside an empty resource_report |
| `target_part` | FPGA part | N/A | e.g. xcu250-figd2104-2L-e |
| `vivado_version` / `backend`, `backend_version` | toolchain version (the latter two only in 2_20) | N/A | e.g. 2023.2, 2024.2, 2019.1 |
| `hls4ml_version` | hls4ml version used for conversion | N/A | e.g. 0.8.1, 1.1.0 |

### Related Schemas or Ontologies

- Schema document: https://github.com/ben-hawks/axess-benchmark/blob/main/data/SCHEMA.md
- No formal ontology or controlled vocabulary is applied.

### Codes used for missing data

| Code | Description |
|---|---|
| `{}` | Empty `resource_report` / `latency_report`: logic synthesis didn't complete or wasn't recorded. Treat as missing, never as zero. |
| `null` | A null array entry (2 in train, 1 in val). Not a record; skip it. |

### Example of the contents

Sample requires manual extraction for this format. The Hugging Face
[dataset viewer](https://huggingface.co/datasets/fastmachinelearning/wa-hls4ml) shows
records, and axess-benchmark's `tests/fixtures/data/` holds 40 real samples.

### Data Processing

Per-run JSON reports were merged into one JSON array per split and generation subset, and
the synthesized projects were archived separately (wa-hls4ml-projects). Incomplete runs
keep empty report objects. No values are imputed, normalized or filtered beyond that;
consumers choose their own filters (axess-benchmark excludes samples without a
`resource_report` from scoring).

### Software used to preprocess/ clean/ label the data

Generation and synthesis ran on two platforms:
- National Research Platform: Ubuntu 20.04.4 containers built from modified xilinx-docker
  v2023.2 "user" images, 3 vCPU and 16 GB per pod, with AMD tools on a Ceph volume;
- Texas A&M ACES: Vitis 2024.2, 2 vCPU and 32 GB per job.

Code: [wa-hls4ml-search](https://github.com/ben-hawks/wa-hls4ml-search) and
[hls4ml](https://github.com/fastmachinelearning/hls4ml).

## Semantic / Schema Information

- Schema: https://github.com/ben-hawks/axess-benchmark/blob/main/data/SCHEMA.md (a
  human-readable field reference; no machine-readable schema is published)
- Semantic context: none. No formal ontology or controlled vocabulary is applied.

---

# ---- Reusable ----

## Citation

The dataset has no DOI of its own; cite the paper.

```bibtex
@article{hawks2026wahls4ml,
  title={wa-hls4ml: A Benchmark and Surrogate Models for hls4ml Resource and Latency Estimation},
  author={Hawks, Benjamin and Weitz, Jason and Demler, Dmitri and Tame-Narvaez, Karla and Plotnikov, Dennis and Rahimifar, Mohammad Mehdi and Rahali, Hamza Ezzaoui and Therrien, Audrey C. and Sproule, Donovan and Khoda, Elham E. and Smith, Keegan A. and Marroquin, Russell and Di Guglielmo, Giuseppe and Tran, Nhan and Duarte, Javier and Loncar, Vladimir},
  journal={ACM Transactions on Reconfigurable Technology and Systems},
  volume={19}, number={2}, pages={1--29}, year={2026},
  publisher={Association for Computing Machinery},
  doi={10.1145/3787490}, url={https://doi.org/10.1145/3787490},
  eprint={2511.05615}, archivePrefix={arXiv}
}
```

## License and Usage Rights

Licensed under CC-BY-NC-4.0 (Creative Commons Attribution-NonCommercial 4.0
International). See https://creativecommons.org/licenses/by-nc/4.0/. No additional
licenses. The dataset-generation code is Apache-2.0 and separate from the data.

## Maintenance & Updates

Maintained by Benjamin Hawks, Fermilab (level: Project_Managed). Updated ad hoc.

Versioning uses Hugging Face git revisions, so pin a commit hash for reproducible work
(main is `bb0e7d5533c79b218faf59afa2798559cb84838e` as of 2026-10-02). The data files are
unchanged since at least 2025-12-05: a copy downloaded that day matches main byte for byte. No retention policy is stated.

## Data Characteristics

Each sample pairs a network description (`model_config`) and its conversion settings
(`hls_config`) with three synthesis reports and the recorded constraints (`target_part`,
toolchain versions). See the variable table above.

- **Splits:** train / val / test / exemplar. The exemplar set is disjoint by
  construction.
- **Coverage:** no spatial or temporal coverage applies.
- **Missing data:** missing synthesis results are empty objects, and null array entries
  must be skipped (see "Codes used for missing data").

## Data Quality & Limitations

**Completeness.** Records per split, parsed 2026-10-02:

| Split | Records |
|---|---|
| train | 478,216 |
| val | 102,471 |
| test | 102,484 |
| exemplar | 887 |

Logic-synthesis results exist for 92,933 of 102,484 test records (90.7%) and 886 of 887
exemplar records. Coverage is much lower for convolutional models: about 29% of conv2d
and 42% of conv1d records.

**Known issues.**
- The train and val arrays contain 3 null entries.
- The Hugging Face dataset card states 478,220 train and 102,472 val samples; the files
  hold 478,216 and 102,471 records.
- `latency_report` holds HLS estimates, not post-synthesis latency.
- `hls_resource_report` and `resource_report` differ measurably for the same sample, so
  mixing them silently changes the target.
- The 2_20 subset was synthesized for three FPGA parts with Vivado 2019.1.
- Report values are strings and need casting.

**Limitations.** Generated architectures have no skip connections and a limited
reuse-factor range.

**Validation.**
- Counts were parsed with a streaming JSON parser on a byte-identical copy of the current
  files.
- axess-benchmark verified that the paper's original models were trained on
  `hls_resource_report` (100% row match), that rebuilt normalization statistics match the
  shipped ones, and that preprocessing is bit-identical to upstream.

## Integrity & Versioning

Checksums (sha256) are available for all 22 data files, listed in the frontmatter.
- 21 are Hugging Face's own Git LFS object IDs.
- `exemplar/exemplar_models.json` isn't stored in LFS. Its sha256 was computed from a copy
  whose git blob hash (`58e0c0f3…`) matches Hugging Face.

Verify with `sha256sum` after download. Versioning: see Maintenance & Updates.

---

# ---- AI Usable ----

## AI / Machine Learning Considerations

Training, inference and evaluation use are all allowed ("Yes"), within the license:
non-commercial use only, with attribution (CC-BY-NC-4.0). No human review is required.

For benchmark comparability:
- score resources against `resource_report` and latency against `latency_report`, never
  `hls_resource_report`;
- exclude samples without ground truth rather than imputing them.

**Bias risks.**
- The data is heavily weighted toward fully connected networks.
- Convolutional records lose more ground truth to incomplete synthesis.
- Synthetic architectures differ strongly from real ones, and every reference surrogate
  model degrades sharply on the exemplar set.
- The target part is not a modelled input, which biases BRAM on the 2_20 subset.

**Safety.** None identified.
