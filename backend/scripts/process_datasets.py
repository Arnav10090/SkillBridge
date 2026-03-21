"""
SkillBridge Dataset Processor
Mines real-world aliases from:
- Kaggle Resume Dataset (Resume.csv) — columns: ID, Resume_str, Resume_html, Category
- Kaggle JD Dataset (job_title_des.csv) — columns: Job Title, Job Description

Run: python scripts/process_datasets.py
"""

import json
import re
import os
import sys
import pandas as pd
from collections import defaultdict, Counter

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESUME_CSV    = os.path.join(BASE_DIR, "app", "datasets", "Resume.csv")
JD_CSV        = os.path.join(BASE_DIR, "app", "datasets", "job_title_des.csv")
TAXONOMY_PATH = os.path.join(BASE_DIR, "app", "data", "skill_taxonomy.json")
STATS_OUT     = os.path.join(BASE_DIR, "app", "data", "skill_frequency_stats.json")
REPORT_OUT    = os.path.join(BASE_DIR, "app", "data", "dataset_report.json")

# ── Skill mining patterns ──────────────────────────────────────────────────────
MINING_PATTERNS = {
    "PROG_PY":       ["python", "python3", "python 3", "py3", "python developer"],
    "PROG_JS":       ["javascript", "js", "es6", "es2015", "vanilla js"],
    "PROG_TS":       ["typescript", "ts"],
    "PROG_JAVA":     ["java", "java se", "java ee", "j2ee", "java 8", "java 11"],
    "PROG_CPP":      ["c++", "cpp", "c plus plus"],
    "PROG_GO":       ["golang", "go lang", "go programming"],
    "PROG_R":        ["r programming", "r language", "rstudio"],
    "PROG_SQL":      ["sql", "mysql", "postgresql", "postgres", "t-sql", "pl/sql"],
    "PROG_BASH":     ["bash", "shell script", "shell scripting", "linux scripting"],
    "WEB_REACT":     ["react", "reactjs", "react.js", "react js", "react hooks"],
    "WEB_ANGULAR":   ["angular", "angularjs", "angular.js", "angular 2"],
    "WEB_VUE":       ["vue", "vuejs", "vue.js", "vue 3"],
    "WEB_NODE":      ["node.js", "nodejs", "node js", "express", "expressjs"],
    "WEB_HTML":      ["html", "html5", "html 5", "semantic html"],
    "WEB_CSS":       ["css", "css3", "sass", "scss", "tailwind", "bootstrap"],
    "WEB_REST":      ["rest api", "restful", "restful api", "api development"],
    "WEB_DJANGO":    ["django", "django rest", "drf"],
    "WEB_FLASK":     ["flask"],
    "WEB_FASTAPI":   ["fastapi", "fast api"],
    "WEB_NEXT":      ["next.js", "nextjs", "next js"],
    "ML_SKLEARN":    ["scikit-learn", "sklearn", "scikit learn"],
    "ML_TF":         ["tensorflow", "keras", "tf2", "tensor flow"],
    "ML_TORCH":      ["pytorch", "torch", "py torch"],
    "ML_PANDAS":     ["pandas", "dataframe", "data wrangling"],
    "ML_NUMPY":      ["numpy", "numerical python"],
    "ML_DL":         ["deep learning", "neural network", "neural networks", "cnn", "rnn", "lstm"],
    "ML_NLP":        ["nlp", "natural language processing", "text mining", "spacy", "nltk"],
    "ML_CV":         ["computer vision", "image processing", "object detection", "opencv"],
    "ML_STATS":      ["statistics", "statistical analysis", "statistical modeling"],
    "ML_PROB":       ["probability", "bayesian", "bayesian statistics"],
    "ML_MLOPs":      ["mlops", "model deployment", "model serving"],
    "ML_FEATURE":    ["feature engineering", "feature extraction", "feature selection"],
    "DATA_VIZ":      ["matplotlib", "seaborn", "plotly", "tableau", "power bi", "powerbi", "data visualization"],
    "DATA_ENG":      ["data engineering", "etl", "data pipeline", "data warehousing"],
    "DATA_SPARK":    ["apache spark", "pyspark", "spark"],
    "DATA_KAFKA":    ["kafka", "apache kafka"],
    "DATA_AIRFLOW":  ["airflow", "apache airflow"],
    "DB_PG":         ["postgresql", "postgres", "psql"],
    "DB_MYSQL":      ["mysql", "mariadb"],
    "DB_MONGO":      ["mongodb", "mongo", "mongoose"],
    "DB_REDIS":      ["redis"],
    "DB_DESIGN":     ["database design", "data modeling", "schema design", "normalization"],
    "CLOUD_AWS":     ["aws", "amazon web services", "ec2", "s3", "lambda"],
    "CLOUD_GCP":     ["gcp", "google cloud", "bigquery"],
    "CLOUD_AZURE":   ["azure", "microsoft azure"],
    "DEVOPS_DOCKER": ["docker", "dockerfile", "docker compose", "containerization"],
    "DEVOPS_K8S":    ["kubernetes", "k8s", "kubectl", "helm"],
    "DEVOPS_CICD":   ["ci/cd", "cicd", "continuous integration", "github actions", "jenkins"],
    "DEVOPS_GIT":    ["git", "github", "gitlab", "bitbucket", "version control"],
    "DEVOPS_LINUX":  ["linux", "unix", "ubuntu", "centos"],
    "DEVOPS_TERRAFORM": ["terraform", "infrastructure as code", "iac"],
    "SEC_BASICS":    ["cybersecurity", "information security", "network security"],
    "PM_AGILE":      ["agile", "scrum", "kanban", "sprint"],
    "PM_PRODUCT":    ["product management", "product owner", "roadmapping"],
    "SOFT_COMM":     ["communication skills", "verbal communication", "presentation skills"],
    "SOFT_LEAD":     ["leadership", "team lead", "tech lead", "people management"],
    "SOFT_COLLAB":   ["teamwork", "collaboration", "cross-functional"],
    "SOFT_PROB":     ["problem solving", "analytical thinking", "critical thinking", "troubleshooting"],
    "ALGO_DS":       ["data structures", "algorithms", "dsa", "leetcode", "competitive programming"],
    "ARCH_SYSTEM":   ["system design", "distributed systems", "scalability", "microservices"],
    "TEST_UNIT":     ["unit testing", "tdd", "test driven", "pytest", "jest", "junit"],
    "OPS_MONITOR":   ["monitoring", "prometheus", "grafana", "datadog"],
    "FINANCE_EXCEL": ["excel", "microsoft excel", "pivot table", "vlookup"],
    "MKT_DIGITAL":   ["digital marketing", "seo", "sem", "google ads"],
    "OPS_SUPPLY":    ["supply chain", "logistics", "procurement", "inventory"],
    "DS_EDA":        ["exploratory data analysis", "eda", "data exploration"],
}


def load_resume_csv():
    """Load Resume.csv — columns: ID, Resume_str, Resume_html, Category"""
    print(f"\n📄 Loading resume dataset...")
    print(f"   Path: {RESUME_CSV}")

    if not os.path.exists(RESUME_CSV):
        print(f"   ❌ File not found: {RESUME_CSV}")
        print(f"   Make sure Resume.csv is in backend/app/datasets/")
        sys.exit(1)

    df = pd.read_csv(RESUME_CSV)
    print(f"   ✅ Loaded {len(df)} resumes")
    print(f"   Columns: {list(df.columns)}")
    print(f"   Categories: {df['Category'].nunique()} unique job types")
    print(f"   Category distribution (top 5):")
    for cat, count in df['Category'].value_counts().head(5).items():
        print(f"      {cat}: {count}")

    texts      = df['Resume_str'].fillna("").tolist()
    categories = df['Category'].fillna("unknown").tolist()
    return texts, categories


def load_jd_csv():
    """Load job_title_des.csv — columns: Job Title, Job Description"""
    print(f"\n💼 Loading JD dataset...")
    print(f"   Path: {JD_CSV}")

    if not os.path.exists(JD_CSV):
        print(f"   ❌ File not found: {JD_CSV}")
        print(f"   Make sure job_title_des.csv is in backend/app/datasets/")
        sys.exit(1)

    df = pd.read_csv(JD_CSV)
    print(f"   ✅ Loaded {len(df)} job descriptions")
    print(f"   Columns: {list(df.columns)}")
    print(f"   Job title distribution (top 5):")
    for title, count in df['Job Title'].value_counts().head(5).items():
        print(f"      {title}: {count}")

    texts  = df['Job Description'].fillna("").tolist()
    titles = df['Job Title'].fillna("unknown").tolist()
    return texts, titles


def mine_skill_frequencies(texts, source_name):
    """Count how often each skill appears across all documents."""
    print(f"\n🔍 Mining {len(texts)} {source_name}...")

    skill_counts = defaultdict(int)
    alias_found  = defaultdict(lambda: defaultdict(int))
    total        = len(texts)

    for i, text in enumerate(texts):
        if i % 200 == 0 and i > 0:
            print(f"   Processing {i}/{total}...")
        text_lower = text.lower()
        for skill_id, patterns in MINING_PATTERNS.items():
            for pattern in patterns:
                if re.search(r'\b' + re.escape(pattern) + r'\b', text_lower):
                    skill_counts[skill_id] += 1
                    alias_found[skill_id][pattern] += 1
                    break

    print(f"   ✅ Done. Skills found: {len(skill_counts)}")
    return dict(skill_counts), {k: dict(v) for k, v in alias_found.items()}


def compute_new_aliases(resume_alias_found, jd_alias_found):
    """Merge alias frequencies from both datasets and rank them."""
    new_aliases = {}
    for skill_id in MINING_PATTERNS:
        combined = defaultdict(int)
        for alias, count in resume_alias_found.get(skill_id, {}).items():
            combined[alias] += count
        for alias, count in jd_alias_found.get(skill_id, {}).items():
            combined[alias] += count

        # Keep top aliases with at least 2 occurrences
        ranked = [
            alias for alias, count
            in sorted(combined.items(), key=lambda x: -x[1])
            if count >= 2
        ][:8]
        new_aliases[skill_id] = ranked
    return new_aliases


def enrich_taxonomy(new_aliases):
    """Add mined aliases to skill_taxonomy.json without removing existing ones."""
    print(f"\n📚 Enriching skill_taxonomy.json...")

    with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
        taxonomy = json.load(f)

    total_added = 0
    for skill in taxonomy["skills"]:
        skill_id = skill["id"]
        mined    = new_aliases.get(skill_id, [])
        if not mined:
            continue

        existing = set(a.lower() for a in skill.get("aliases", []))
        existing.add(skill["name"].lower())
        to_add   = [a for a in mined if a.lower() not in existing]

        if to_add:
            skill["aliases"] = skill.get("aliases", []) + to_add
            total_added += len(to_add)
            print(f"   + {skill['name']}: {to_add}")

    # Add enrichment metadata
    taxonomy["dataset_enriched"]   = True
    taxonomy["enrichment_sources"] = [
        "Kaggle Resume Dataset — kaggle.com/datasets/snehaanbhawal/resume-dataset",
        "Kaggle JD Dataset — kaggle.com/datasets/kshitizregmi/jobs-and-job-description",
        "O*NET Database 28.1 — onetcenter.org/db_releases.html"
    ]

    with open(TAXONOMY_PATH, "w", encoding="utf-8") as f:
        json.dump(taxonomy, f, indent=2, ensure_ascii=False)

    print(f"\n   ✅ Total new aliases added to taxonomy: {total_added}")
    return total_added


def compute_demand_weights(resume_counts, jd_counts, total_resumes, total_jds):
    """
    Data-driven skill demand weights.
    High JD frequency = market demand.
    Used to boost P-scores in WGT algorithm.
    """
    weights = {}
    all_skill_ids = set(list(resume_counts.keys()) + list(jd_counts.keys()))
    for skill_id in all_skill_ids:
        jd_freq     = jd_counts.get(skill_id, 0)     / max(total_jds, 1)
        resume_freq = resume_counts.get(skill_id, 0)  / max(total_resumes, 1)
        # High demand in JDs + less common in resumes = high value gap to fill
        weights[skill_id] = round(0.7 * jd_freq + 0.3 * (1 - resume_freq), 4)
    return weights


def save_outputs(resume_counts, jd_counts, demand_weights,
                 total_resumes, total_jds, resume_categories, total_added):
    """Save stats and report JSON files."""

    cat_dist = Counter(resume_categories)

    stats = {
        "metadata": {
            "total_resumes_processed":  total_resumes,
            "total_jds_processed":      total_jds,
            "new_aliases_added":        total_added,
            "dataset_sources": [
                "Kaggle Resume Dataset (Resume.csv) — ID, Resume_str, Resume_html, Category",
                "Kaggle JD Dataset (job_title_des.csv) — Job Title, Job Description",
                "O*NET Database 28.1 — onetcenter.org (taxonomy structure + prerequisites)"
            ]
        },
        "resume_skill_frequency":     resume_counts,
        "jd_skill_frequency":         jd_counts,
        "skill_demand_weights":       demand_weights,
        "resume_category_distribution": dict(cat_dist.most_common()),
        "top_10_resume_skills": sorted(
            resume_counts.items(), key=lambda x: -x[1]
        )[:10],
        "top_10_jd_skills": sorted(
            jd_counts.items(), key=lambda x: -x[1]
        )[:10],
    }

    report = {
        "status": "success",
        "datasets_used": [
            {
                "name": "Kaggle Resume Dataset",
                "source": "https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset",
                "file": "Resume.csv",
                "columns": ["ID", "Resume_str", "Resume_html", "Category"],
                "rows_processed": total_resumes,
                "how_used": "Mined real-world skill surface forms; enriched alias lists in skill_taxonomy.json"
            },
            {
                "name": "Kaggle Jobs and Job Description Dataset",
                "source": "https://www.kaggle.com/datasets/kshitizregmi/jobs-and-job-description",
                "file": "job_title_des.csv",
                "columns": ["Job Title", "Job Description"],
                "rows_processed": total_jds,
                "how_used": "Computed skill demand weights from JD frequency; informs P-score weighting in WGT algorithm"
            },
            {
                "name": "O*NET Database 28.1",
                "source": "https://www.onetcenter.org/db_releases.html",
                "how_used": "Canonical skill IDs, prerequisite relationships, domain classifications in skill_taxonomy.json"
            }
        ],
        "processing_results": {
            "resumes_analyzed":    total_resumes,
            "jds_analyzed":        total_jds,
            "new_aliases_added":   total_added,
            "skills_with_data":    len(resume_counts),
        },
        "top_resume_skills": stats["top_10_resume_skills"],
        "top_jd_skills":     stats["top_10_jd_skills"],
        "skill_demand_weights_sample": dict(
            list(sorted(demand_weights.items(), key=lambda x: -x[1]))[:10]
        )
    }

    with open(STATS_OUT, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    with open(REPORT_OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n💾 Saved: app/data/skill_frequency_stats.json")
    print(f"💾 Saved: app/data/dataset_report.json")
    return stats


def main():
    print("=" * 60)
    print("  SkillBridge — Dataset Processing Pipeline")
    print("  Kaggle Resume + Kaggle JD + O*NET Integration")
    print("=" * 60)

    # ── Load ────────────────────────────────────────────────────
    resume_texts, resume_categories = load_resume_csv()
    jd_texts, jd_titles             = load_jd_csv()

    total_resumes = len(resume_texts)
    total_jds     = len(jd_texts)

    # ── Mine ────────────────────────────────────────────────────
    resume_counts, resume_alias_found = mine_skill_frequencies(
        resume_texts, "resumes"
    )
    jd_counts, jd_alias_found = mine_skill_frequencies(
        jd_texts, "job descriptions"
    )

    # ── Compute aliases ─────────────────────────────────────────
    new_aliases = compute_new_aliases(resume_alias_found, jd_alias_found)

    # ── Enrich taxonomy ──────────────────────────────────────────
    total_added = enrich_taxonomy(new_aliases)

    # ── Demand weights ───────────────────────────────────────────
    demand_weights = compute_demand_weights(
        resume_counts, jd_counts, total_resumes, total_jds
    )

    # ── Save outputs ─────────────────────────────────────────────
    stats = save_outputs(
        resume_counts, jd_counts, demand_weights,
        total_resumes, total_jds, resume_categories, total_added
    )

    # ── Summary ──────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  ✅ PROCESSING COMPLETE")
    print("=" * 60)
    print(f"  Resumes processed:    {total_resumes}")
    print(f"  JDs processed:        {total_jds}")
    print(f"  New aliases added:    {total_added}")
    print(f"\n  Top 5 skills in resumes:")
    for s, c in stats["top_10_resume_skills"][:5]:
        print(f"    {s:20s} → {c} resumes")
    print(f"\n  Top 5 skills in JDs:")
    for s, c in stats["top_10_jd_skills"][:5]:
        print(f"    {s:20s} → {c} JDs")
    print(f"\n  Files updated:")
    print(f"    ✅ app/data/skill_taxonomy.json  (enriched aliases)")
    print(f"    ✅ app/data/skill_frequency_stats.json")
    print(f"    ✅ app/data/dataset_report.json")
    print("=" * 60)


if __name__ == "__main__":
    main()