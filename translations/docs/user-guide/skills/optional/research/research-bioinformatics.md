---
title: "生物信息学 — 通往 bioSkills 和 ClawBio 400+ 生物信息学技能的网关"
sidebar_label: "生物信息学"
description: "通往 bioSkills 和 ClawBio 400+ 生物信息学技能的网关"
---

{/* 此页面由技能的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 生物信息学

通往 bioSkills 和 ClawBio 400+ 生物信息学技能的网关。涵盖基因组学、转录组学、单细胞、变异检测、药物基因组学、宏基因组学、结构生物学等领域。按需获取特定领域的参考资料。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/research/bioinformatics` 安装 |
| 路径 | `optional-skills/research/bioinformatics` |
| 版本 | `1.0.0` |
| 平台 | linux, macos |
| 标签 | `bioinformatics`, `genomics`, `sequencing`, `biology`, `research`, `science` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# 生物信息学技能网关

当被问及生物信息学、基因组学、测序、变异检测、基因表达、单细胞分析、蛋白质结构、药物基因组学、宏基因组学、系统发育学或任何计算生物学任务时使用。

此技能是两个开源生物信息学技能库的网关。它不捆绑数百个特定领域的技能，而是对它们进行索引并按需获取所需内容。

## 来源

◆ **bioSkills** — 385 个参考技能（代码模式、参数指南、决策树）
  仓库：https://github.com/GPTomics/bioSkills
  格式：每个主题的 SKILL.md，包含代码示例。Python/R/CLI。

◆ **ClawBio** — 33 个可运行流水线技能（可执行脚本、可复现性包）
  仓库：https://github.com/ClawBio/ClawBio
  格式：带有演示的 Python 脚本。每个分析导出 report.md + commands.sh + environment.yml。

## 如何获取和使用技能

1.  从下面的索引中识别领域和技能名称。
2.  克隆相关仓库（浅克隆以节省时间）：
    ```bash
    # bioSkills（参考资料）
    git clone --depth 1 https://github.com/GPTomics/bioSkills.git /tmp/bioSkills

    # ClawBio（可运行流水线）
    git clone --depth 1 https://github.com/ClawBio/ClawBio.git /tmp/ClawBio
    ```
3.  阅读特定技能：
    ```bash
    # bioSkills — 每个技能位于：<category>/<skill-name>/SKILL.md
    cat /tmp/bioSkills/variant-calling/gatk-variant-calling/SKILL.md

    # ClawBio — 每个技能位于：skills/<skill-name>/
    cat /tmp/ClawBio/skills/pharmgx-reporter/README.md
    ```
4.  将获取的技能作为参考资料遵循。这些**不是** Hermes 格式的技能 — 请将它们视为专家领域指南。它们包含正确的参数、适当的工具标志和经过验证的流水线。

## 按领域划分的技能索引

### 序列基础
bioSkills:
  sequence-io/ — read-sequences, write-sequences, format-conversion, batch-processing, compressed-files, fastq-quality, filter-sequences, paired-end-fastq, sequence-statistics
  sequence-manipulation/ — seq-objects, reverse-complement, transcription-translation, motif-search, codon-usage, sequence-properties, sequence-slicing
ClawBio:
  seq-wrangler — 序列 QC、比对和 BAM 处理（封装 FastQC、BWA、SAMtools）

### 读段 QC 与比对
bioSkills:
  read-qc/ — quality-reports, fastp-workflow, adapter-trimming, quality-filtering, umi-processing, contamination-screening, rnaseq-qc
  read-alignment/ — bwa-alignment, star-alignment, hisat2-alignment, bowtie2-alignment
  alignment-files/ — sam-bam-basics, alignment-sorting, alignment-filtering, bam-statistics, duplicate-handling, pileup-generation

### 变异检测与注释
bioSkills:
  variant-calling/ — gatk-variant-calling, deepvariant, variant-calling (bcftools), joint-calling, structural-variant-calling, filtering-best-practices, variant-annotation, variant-normalization, vcf-basics, vcf-manipulation, vcf-statistics, consensus-sequences, clinical-interpretation
ClawBio:
  vcf-annotator — 具有祖先感知上下文的 VEP + ClinVar + gnomAD 注释
  variant-annotation — 变异注释流水线

### 差异表达（Bulk RNA-seq）
bioSkills:
  differential-expression/ — deseq2-basics, edger-basics, batch-correction, de-results, de-visualization, timeseries-de
  rna-quantification/ — alignment-free-quant (Salmon/kallisto), featurecounts-counting, tximport-workflow, count-matrix-qc
  expression-matrix/ — counts-ingest, gene-id-mapping, metadata-joins, sparse-handling
ClawBio:
  rnaseq-de — 包含 QC、归一化和可视化的完整 DE 流水线
  diff-visualizer — 用于 DE 结果的丰富可视化和报告

### 单细胞 RNA-seq
bioSkills:
  single-cell/ — preprocessing, clustering, batch-integration, cell-annotation, cell-communication, doublet-detection, markers-annotation, trajectory-inference, multimodal-integration, perturb-seq, scatac-analysis, lineage-tracing, metabolite-communication, data-io
ClawBio:
  scrna-orchestrator — 完整的 Scanpy 流水线（QC、聚类、标记物、注释）
  scrna-embedding — 基于 scVI 的潜在嵌入和批次整合

### 空间转录组学
bioSkills:
  spatial-transcriptomics/ — spatial-data-io, spatial-preprocessing, spatial-domains, spatial-deconvolution, spatial-communication, spatial-neighbors, spatial-statistics, spatial-visualization, spatial-multiomics, spatial-proteomics, image-analysis

### 表观基因组学
bioSkills:
  chip-seq/ — peak-calling, differential-binding, motif-analysis, peak-annotation, chipseq-qc, chipseq-visualization, super-enhancers
  atac-seq/ — atac-peak-calling, atac-qc, differential-accessibility, footprinting, motif-deviation, nucleosome-positioning
  methylation-analysis/ — bismark-alignment, methylation-calling, dmr-detection, methylkit-analysis
  hi-c-analysis/ — hic-data-io, tad-detection, loop-calling, compartment-analysis, contact-pairs, matrix-operations, hic-visualization, hic-differential
ClawBio:
  methylation-clock — 表观遗传年龄估计
### 药物基因组学与临床
生物技能：
  临床数据库/ — clinvar查询、gnomad频率、dbsnp查询、药物基因组学、多基因风险、hla分型、变异优先级排序、体细胞特征、肿瘤突变负荷、myvariant查询
ClawBio：
  pharmgx-reporter — 基于23andMe/AncestryDNA数据的PGx报告（12个基因，31个SNP，51种药物）
  drug-photo — 药物照片 → 个性化PGx剂量卡（通过视觉）
  clinpgx — ClinPGx API，用于基因-药物数据和CPIC指南
  gwas-lookup — 跨9个基因组数据库的联合变异查询
  gwas-prs — 基于消费级基因数据的多基因风险评分
  nutrigx_advisor — 基于消费级基因数据的个性化营养建议

### 群体遗传学与GWAS
生物技能：
  群体遗传学/ — 关联性检验（PLINK GWAS）、plink基础、群体结构、连锁不平衡、scikit-allel分析、选择统计
  因果基因组学/ — 孟德尔随机化、精细定位、共定位分析、中介分析、多效性检测
  单倍型分型与基因型填充/ — 单倍型分型、基因型填充、填充质量控制、参考面板
ClawBio：
  claw-ancestry-pca — 基于SGDP参考面板的祖先PCA分析

### 宏基因组学与微生物组
生物技能：
  宏基因组学/ — kraken分类、metaphlan分析、丰度估计、功能分析、抗性基因检测、菌株追踪、宏基因组可视化
  微生物组/ — 扩增子处理、多样性分析、差异丰度、分类学分配、功能预测、qiime2工作流
ClawBio：
  claw-metagenomics — 鸟枪法宏基因组学分析（分类学、抗性组、功能通路）

### 基因组组装与注释
生物技能：
  基因组组装/ — hifi组装、长读长组装、短读长组装、宏基因组组装、组装抛光、组装质量控制、支架构建、污染检测
  基因组注释/ — 真核生物基因预测、原核生物注释、功能注释、非编码RNA注释、重复序列注释、注释转移
  长读长测序/ — 碱基识别、长读长比对、长读长质量控制、clair3变异检测、结构变异、medaka抛光、纳米孔甲基化分析、isoseq分析

### 结构生物学与化学信息学
生物技能：
  结构生物学/ — alphafold预测、现代结构预测、结构输入输出、结构导航、结构修饰、几何分析
  化学信息学/ — 分子输入输出、分子描述符、相似性搜索、子结构搜索、虚拟筛选、ADMET预测、反应枚举
ClawBio：
  struct-predictor — 本地AlphaFold/Boltz/Chai结构预测与比较

### 蛋白质组学
生物技能：
  蛋白质组学/ — 数据导入、肽段鉴定、蛋白质推断、定量、差异丰度、DIA分析、翻译后修饰分析、蛋白质组学质量控制、谱图库
ClawBio：
  proteomics-de — 蛋白质组学差异表达分析

### 通路分析与基因网络
生物技能：
  通路分析/ — GO富集、GSEA、KEGG通路、Reactome通路、WikiPathways、富集可视化
  基因调控网络/ — SCENIC调控子、共表达网络、差异网络、多组学基因调控网络、扰动模拟

### 免疫信息学
生物技能：
  免疫信息学/ — MHC结合预测、表位预测、新抗原预测、免疫原性评分、TCR-表位结合
  TCR-BCR分析/ — mixcr分析、scirpy分析、immcantation分析、受体库可视化、vdjtools分析

### CRISPR与基因组工程
生物技能：
  CRISPR筛选/ — mageck分析、jacks分析、命中基因识别、筛选质量控制、文库设计、crispresso编辑分析、碱基编辑分析、批次校正
  基因组工程/ — gRNA设计、脱靶预测、HDR模板设计、碱基编辑设计、先导编辑设计

### 工作流管理
生物技能：
  工作流管理/ — snakemake工作流、nextflow流水线、cwl工作流、wdl工作流
ClawBio：
  repro-enforcer — 将任何分析导出为可重复性包（Conda环境 + Singularity + 校验和）
  galaxy-bridge — 从usegalaxy.org访问8,000+个Galaxy工具

### 专业领域
生物技能：
  可变剪接/ — 剪接定量、差异剪接、异构体转换、sashimi图、单细胞剪接、剪接质量控制
  生态基因组学/ — eDNA宏条形码、景观基因组学、保护遗传学、生物多样性指标、群落生态学、物种界定
  流行病学基因组学/ — 病原体分型、变异监测、系统动力学、传播推断、抗性监测
  液体活检/ — cfDNA预处理、ctDNA突变检测、片段分析、肿瘤分数估计、基于甲基化的检测、纵向监测
  表观转录组学/ — m6A峰识别、m6A差异分析、m6anet分析、MeRIP预处理、修饰可视化
  代谢组学/ — xcms预处理、代谢物注释、归一化与质量控制、统计分析、通路映射、脂质组学、靶向分析、msdial预处理
  流式细胞术/ — fcs文件处理、设门分析、补偿转换、聚类表型分析、差异分析、细胞术质量控制、双峰检测、微珠归一化
  系统生物学/ — 通量平衡分析、代谢重建、基因必需性、上下文特异性模型、模型管理
  RNA结构/ — 二级结构预测、非编码RNA搜索、结构探测

### 数据可视化与报告
生物技能：
  数据可视化/ — ggplot2基础、热图与聚类、火山图定制、circos图、基因组浏览器轨道、交互式可视化、多面板图、网络可视化、upset图、调色板、专业组学图、基因组轨道
  报告/ — rmarkdown报告、quarto报告、jupyter报告、自动化质量控制报告、图形导出
ClawBio：
  profile-report — 分析概况报告
  data-extractor — 从科学图表图像中提取数值数据（通过视觉）
  lit-synthesizer — PubMed/bioRxiv搜索、摘要、引用图
  pubmed-summariser — 基因/疾病PubMed搜索与结构化简报
### 数据库访问
bioSkills：
  database-access/ — entrez-search、entrez-fetch、entrez-link、blast-searches、local-blast、sra-data、geo-data、uniprot-access、batch-downloads、interaction-databases、sequence-similarity
ClawBio：
  ukb-navigator — 对 12,000+ 个 UK Biobank 字段进行语义搜索
  clinical-trial-finder — 临床试验发现

### 实验设计
bioSkills：
  experimental-design/ — power-analysis、sample-size、batch-design、multiple-testing

### 面向组学的机器学习
bioSkills：
  machine-learning/ — omics-classifiers、biomarker-discovery、survival-analysis、model-validation、prediction-explanation、atlas-mapping
ClawBio：
  claw-semantic-sim — 疾病文献的语义相似度索引（PubMedBERT）
  omics-target-evidence-mapper — 跨组学来源聚合靶点层面的证据

## 环境设置

这些技能假设已有一个生物信息学工作站。常见依赖项：

```bash
# Python
pip install biopython pysam cyvcf2 pybedtools pyBigWig scikit-allel anndata scanpy mygene

# R/Bioconductor
Rscript -e 'BiocManager::install(c("DESeq2","edgeR","Seurat","clusterProfiler","methylKit"))'

# CLI 工具（Ubuntu/Debian）
sudo apt install samtools bcftools ncbi-blast+ minimap2 bedtools

# CLI 工具（macOS）
brew install samtools bcftools blast minimap2 bedtools

# 或通过 Conda（推荐用于可重复性）
conda install -c bioconda samtools bcftools blast minimap2 bedtools fastp kraken2
```

## 注意事项

- 获取的技能**不是** Hermes SKILL.md 格式。它们使用自己的结构（bioSkills：代码模式参考手册；ClawBio：README + Python 脚本）。请将它们视为专家参考资料。
- bioSkills 是参考指南——它们展示了正确的参数和代码模式，但本身不是可执行的流水线。
- ClawBio 技能是可执行的——许多都有 `--demo` 标志，可以直接运行。
- 两个仓库都假设已安装生物信息学工具。在运行流水线前请检查先决条件。
- 对于 ClawBio，请先在克隆的仓库中运行 `pip install -r requirements.txt`。
- 基因组数据文件可能非常大。在下载参考基因组、SRA 数据集或构建索引时，请注意磁盘空间。