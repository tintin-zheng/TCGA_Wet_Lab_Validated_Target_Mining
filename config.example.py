# ============ API Configuration ============
NCBI_EMAIL = "your_email@example.com"  # Replace with your email
NCBI_API_KEY = ""  # Optional, leave empty if not available

DEEPSEEK_API_KEY = "sk-your-key-here"  # Get from platform.deepseek.com
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"  # or deepseek-v4-pro / deepseek-reasoner

# ============ Parameters ============
SEARCH_COUNT = 400  # PubMed search count per cancer (default)

# ============ Per-Cancer Search Count Overrides ============
SEARCH_COUNT_OVERRIDES = {
    "BRCA": 13000, # 12,850 — full sweep
    "COAD": 8000,  # 7,885 — full sweep
    "SKCM": 5800,  # 5,723 — full sweep
    "PRAD": 5300,  # 5,270 — full sweep
    "SARC": 4800,  # 4,711 — full sweep
    "LIHC": 4200,  # 4,141 — full sweep
    "LAML": 4000,  # 3,959 — full sweep
    "OV":   3500,  # 3,445 — full sweep
    "GBM":  3400,  # 3,340 — full sweep
    "PAAD": 3100,  # 3,019 — full sweep
    # --- Full sweeps (2,050–500 papers) ---
    "STAD": 2100,  # 2,050
    "BLCA": 1400,  # 1,376
    "HNSC": 1300,  # 1,272
    "THCA": 1300,  # 1,223
    "LUAD": 1100,  # 1,058
    "CESC": 1000,  # 901
    "DLBC":  800,  # 791
    "UCEC":  700,  # 699
    "CHOL":  600,  # 548
    "ESCA":  500,  # 497
    # --- <500 full sweeps ---
    "KIRC":  500,  # 469
    "PCPG":  500,  # 426
    "MESO":  500,  # 401
    "LGG":   400,  # 335
    "UVM":   300,  # 267
    "THYM":  300,  # 251
    "READ":  300,  # 247
    "ACC":   200,  # 197
    "KIRP":  200,  # 196
    "LUSC":  200,  # 166
    "TGCT":  200,  # 164
    "KICH":  200,  # 109
    "UCS":   200,  # 103
}


# ============ 41 Q1 Journal ISSNs ============
JOURNAL_ISSNS = [
    "0028-0836",  # Nature
    "2375-2548",  # Science Advances
    "0027-8424",  # PNAS
    "0092-8674",  # Cell
    "2041-1723",  # Nature Communications
    "1078-8956",  # Nature Medicine
    "1087-0156",  # Nature Biotechnology
    "1548-7091",  # Nature Methods
    "1061-4036",  # Nature Genetics
    "1535-6108",  # Cancer Cell
    "2662-1347",  # Nature Cancer
    "2159-8274",  # Cancer Discovery
    "1474-175X",  # Nature Reviews Cancer
    "0732-183X",  # JCO
    "2374-2437",  # JAMA Oncology
    "0923-7534",  # Annals of Oncology
    "1946-6234",  # Science Translational Medicine
    "1550-4131",  # Cell Metabolism
    "2211-1247",  # Cell Reports
    "2666-3791",  # Cell Reports Medicine
    "1097-2765",  # Molecular Cell
    "0008-5472",  # Cancer Research
    "1078-0432",  # Clinical Cancer Research
    "0006-4971",  # Blood
    "0887-6924",  # Leukemia
    "1522-8517",  # Neuro-Oncology
    "0017-5749",  # Gut
    "0016-5085",  # Gastroenterology
    "0270-9139",  # Hepatology
    "0950-9232",  # Oncogene
    "1474-760X",  # Genome Biology
    "0027-8874",  # JNCI
    "0020-7136",  # International Journal of Cancer
    "0007-0920",  # British Journal of Cancer
    "0959-8049",  # European Journal of Cancer
    "1351-0088",  # Endocrine-Related Cancer
    "0021-972X",  # JCEM
    "2059-3635",  # Signal Transduction and Targeted Therapy
    "1350-9047",  # Cell Death & Differentiation
    "0261-4189",  # EMBO Journal
    "0890-9369",  # Genes & Development
]

# ============ TCGA 33 Cancer Types ============
TCGA_CANCERS = {
    "ACC":   (["adrenocortical carcinoma", "adrenal cortical carcinoma", "adrenal cortex cancer"], "Adrenocortical Carcinoma"),
    "BLCA":  (["bladder cancer", "bladder carcinoma", "urothelial carcinoma", "bladder urothelial carcinoma"], "Bladder Cancer"),
    "BRCA":  (["breast cancer", "breast carcinoma", "breast tumor", "breast neoplasm", "invasive breast carcinoma"], "Breast Cancer"),
    "CESC":  (["cervical cancer", "cervical carcinoma", "cervical squamous cell carcinoma", "cervix cancer", "endocervical adenocarcinoma"], "Cervical Cancer"),
    "CHOL":  (["cholangiocarcinoma", "bile duct cancer", "biliary tract cancer", "biliary cancer"], "Cholangiocarcinoma"),
    "COAD":  (["colon cancer", "colon carcinoma", "colorectal cancer", "colonic adenocarcinoma", "colon adenocarcinoma"], "Colon Cancer"),
    "DLBC":  (["diffuse large B-cell lymphoma", "DLBCL", "diffuse large B cell lymphoma"], "DLBC Lymphoma"),
    "ESCA":  (["esophageal cancer", "esophageal carcinoma", "oesophageal cancer", "oesophageal carcinoma"], "Esophageal Cancer"),
    "GBM":   (["glioblastoma", "glioblastoma multiforme", "GBM", "grade IV astrocytoma"], "Glioblastoma"),
    "HNSC":  (["head and neck cancer", "head and neck squamous cell carcinoma", "head and neck carcinoma", "HNSCC"], "Head & Neck Cancer"),
    "KICH":  (["chromophobe renal cell carcinoma", "chromophobe RCC", "kidney chromophobe"], "Kidney Chromophobe"),
    "KIRC":  (["clear cell renal cell carcinoma", "clear cell RCC", "ccRCC", "renal clear cell carcinoma"], "Kidney Clear Cell Carcinoma"),
    "KIRP":  (["papillary renal cell carcinoma", "papillary RCC", "renal papillary carcinoma"], "Kidney Papillary Cell Carcinoma"),
    "LAML":  (["acute myeloid leukemia", "AML", "acute myeloid leukaemia"], "Acute Myeloid Leukemia"),
    "LGG":   (["low-grade glioma", "low grade glioma", "diffuse glioma", "WHO grade II glioma", "diffuse astrocytoma", "oligodendroglioma"], "Low-Grade Glioma"),
    "LIHC":  (["hepatocellular carcinoma", "HCC", "liver cancer", "hepatic carcinoma"], "Hepatocellular Carcinoma"),
    "LUAD":  (["lung adenocarcinoma", "pulmonary adenocarcinoma"], "Lung Adenocarcinoma"),
    "LUSC":  (["lung squamous cell carcinoma", "pulmonary squamous cell carcinoma", "squamous NSCLC"], "Lung Squamous Cell Carcinoma"),
    "MESO":  (["mesothelioma", "malignant mesothelioma"], "Mesothelioma"),
    "OV":    (["ovarian cancer", "ovarian carcinoma", "ovarian serous carcinoma", "epithelial ovarian cancer", "ovarian tumor"], "Ovarian Cancer"),
    "PAAD":  (["pancreatic cancer", "pancreatic ductal adenocarcinoma", "pancreatic carcinoma", "PDAC"], "Pancreatic Cancer"),
    "PCPG":  (["pheochromocytoma", "paraganglioma", "chromaffin tumor"], "Pheochromocytoma & Paraganglioma"),
    "PRAD":  (["prostate cancer", "prostate carcinoma", "prostatic adenocarcinoma", "prostate tumor"], "Prostate Cancer"),
    "READ":  (["rectal cancer", "rectal carcinoma", "rectum adenocarcinoma", "rectal adenocarcinoma"], "Rectal Cancer"),
    "SARC":  (["sarcoma", "soft tissue sarcoma", "soft-tissue sarcoma"], "Sarcoma"),
    "SKCM":  (["cutaneous melanoma", "skin melanoma", "melanoma"], "Cutaneous Melanoma"),
    "STAD":  (["gastric cancer", "gastric carcinoma", "stomach cancer", "stomach adenocarcinoma", "gastric adenocarcinoma"], "Gastric Cancer"),
    "TGCT":  (["testicular cancer", "testicular germ cell tumor", "testicular tumor"], "Testicular Cancer"),
    "THCA":  (["thyroid cancer", "thyroid carcinoma", "thyroid tumor"], "Thyroid Cancer"),
    "THYM":  (["thymoma", "thymic carcinoma", "thymic tumor"], "Thymoma"),
    "UCEC":  (["endometrial cancer", "endometrial carcinoma", "uterine corpus cancer", "endometrial tumor"], "Endometrial Cancer"),
    "UCS":   (["uterine carcinosarcoma", "uterine sarcoma", "endometrial carcinosarcoma"], "Uterine Carcinosarcoma"),
    "UVM":   (["uveal melanoma", "ocular melanoma", "choroidal melanoma"], "Uveal Melanoma"),
}

# ============ Extended Journals for Rare Cancers ============
# Only specified cancer types will also search these extra journals
EXTRA_JOURNALS = {
    "KIRP": [
        # Urologic Oncology
        "0022-5347",  # The Journal of Urology
        "1464-4096",  # BJU International
        "1078-1439",  # Urologic Oncology
        "0302-2838",  # European Urology
        "1759-4812",  # Nature Reviews Urology
        "2588-8431",  # European Urology Oncology
        "2405-4569",  # European Urology Focus
        "1558-7673",  # Clinical Genitourinary Cancer
        # Nephrology
        "1759-5029",  # Nature Reviews Nephrology
        "0085-2538",  # Kidney International
        "1046-6673",  # JASN
        # Pathology
        "0893-3952",  # Modern Pathology
        "0147-5185",  # American Journal of Surgical Pathology
        "0022-3417",  # The Journal of Pathology
        "1045-2257",  # Genes, Chromosomes and Cancer
        # Translational Oncology
        "0304-3835",  # Cancer Letters
        "2072-6694",  # Cancers
        "1470-2045",  # The Lancet Oncology
        "1541-7786",  # Molecular Cancer Research
        "1535-7163",  # Molecular Cancer Therapeutics
        "1756-9966",  # Journal of Experimental & Clinical Cancer Research
        "2059-7029",  # ESMO Open
    ],
    "KICH": [
        # Urologic Oncology
        "0022-5347",  # The Journal of Urology
        "1464-4096",  # BJU International
        "1078-1439",  # Urologic Oncology
        "0302-2838",  # European Urology
        "1759-4812",  # Nature Reviews Urology
        "2588-8431",  # European Urology Oncology
        "2405-4569",  # European Urology Focus
        "1558-7673",  # Clinical Genitourinary Cancer
        # Nephrology
        "1759-5029",  # Nature Reviews Nephrology
        "0085-2538",  # Kidney International
        "1046-6673",  # JASN
        "1555-9041",  # CJASN
        # Pathology
        "0002-9440",  # American Journal of Pathology
        "0893-3952",  # Modern Pathology
        "0147-5185",  # American Journal of Surgical Pathology
        "0022-3417",  # The Journal of Pathology
        "1045-2257",  # Genes, Chromosomes and Cancer
        # Translational Oncology
        "0304-3835",  # Cancer Letters
        "2072-6694",  # Cancers
        "1470-2045",  # The Lancet Oncology
        "1541-7786",  # Molecular Cancer Research
        "1535-7163",  # Molecular Cancer Therapeutics
        "1756-9966",  # Journal of Experimental & Clinical Cancer Research
        "2059-7029",  # ESMO Open
    ],
    "UCS": [
        # Gynecologic Oncology
        "0090-8258",  # Gynecologic Oncology
        "1048-891X",  # International Journal of Gynecological Cancer
        "0002-9378",  # American Journal of Obstetrics and Gynecology
        "0029-7844",  # Obstetrics & Gynecology
        "0002-9440",  # American Journal of Pathology
        # Pathology
        "0893-3952",  # Modern Pathology
        "0147-5185",  # American Journal of Surgical Pathology
        "0309-0167",  # Histopathology
        "0022-3417",  # The Journal of Pathology
        "1045-2257",  # Genes, Chromosomes and Cancer
        # Translational Oncology
        "0304-3835",  # Cancer Letters
        "2072-6694",  # Cancers
        "1470-2045",  # The Lancet Oncology
        "1541-7786",  # Molecular Cancer Research
        "1535-7163",  # Molecular Cancer Therapeutics
        "1756-9966",  # Journal of Experimental & Clinical Cancer Research
        "2059-7029",  # ESMO Open
        "2005-0380",  # Journal of Gynecologic Oncology
        "1347-9032",  # Cancer Science
    ],
    # ============ Newly Added Rare/Underserved Cancers ============
    "ACC": [
        # Endocrinology (adrenal-specific)
        "1945-7189",  # Endocrine Reviews
        "0804-4643",  # European Journal of Endocrinology
        "1043-2760",  # Trends in Endocrinology & Metabolism
        "1046-3976",  # Endocrine Pathology
        "2041-4889",  # Cell Death & Disease
        "1574-7891",  # Molecular Oncology
        # Pathology (shared)
        "0893-3952",  # Modern Pathology
        "0147-5185",  # American Journal of Surgical Pathology
        "0022-3417",  # The Journal of Pathology
        # Translational Oncology (shared)
        "1470-2045",  # The Lancet Oncology
        "0304-3835",  # Cancer Letters
        "1756-9966",  # Journal of Experimental & Clinical Cancer Research
        "1541-7786",  # Molecular Cancer Research
        "2326-6066",  # Cancer Immunology Research
    ],
    "LUSC": [
        # Thoracic / Respiratory
        "1556-0864",  # Journal of Thoracic Oncology
        "2213-2600",  # The Lancet Respiratory Medicine
        "1073-449X",  # American Journal of Respiratory and Critical Care Medicine
        "0903-1936",  # European Respiratory Journal
        "0012-3692",  # Chest
        "0040-6376",  # Thorax
        "0022-5223",  # The Journal of Thoracic and Cardiovascular Surgery
        "1083-7159",  # The Oncologist
        # Pathology (shared)
        "0893-3952",  # Modern Pathology
        "0147-5185",  # American Journal of Surgical Pathology
        "0022-3417",  # The Journal of Pathology
        # Translational Oncology (shared)
        "1470-2045",  # The Lancet Oncology
        "0304-3835",  # Cancer Letters
        "1756-9966",  # Journal of Experimental & Clinical Cancer Research
        "1541-7786",  # Molecular Cancer Research
        "2326-6066",  # Cancer Immunology Research
    ],
    "TGCT": [
        # Urology (testicular cancer domain)
        "0302-2838",  # European Urology
        "0022-5347",  # The Journal of Urology
        "1759-4812",  # Nature Reviews Urology
        "2588-8431",  # European Urology Oncology
        "2405-4569",  # European Urology Focus
        "2047-2919",  # Andrology
        "1008-682X",  # Asian Journal of Andrology
        "1470-1626",  # Reproduction
        # Pathology (shared)
        "0893-3952",  # Modern Pathology
        "0147-5185",  # American Journal of Surgical Pathology
        "0022-3417",  # The Journal of Pathology
        # Translational Oncology (shared)
        "1470-2045",  # The Lancet Oncology
        "0304-3835",  # Cancer Letters
        "1756-9966",  # Journal of Experimental & Clinical Cancer Research
        "1541-7786",  # Molecular Cancer Research
        "2326-6066",  # Cancer Immunology Research
    ],
    "UVM": [
        # Ophthalmology (uveal/ocular melanoma domain)
        "0161-6420",  # Ophthalmology
        "2168-6165",  # JAMA Ophthalmology
        "0002-9394",  # American Journal of Ophthalmology
        "1350-9462",  # Progress in Retinal and Eye Research
        # Pathology (shared)
        "0893-3952",  # Modern Pathology
        "0147-5185",  # American Journal of Surgical Pathology
        "0022-3417",  # The Journal of Pathology
        # Translational Oncology (shared)
        "1470-2045",  # The Lancet Oncology
        "0304-3835",  # Cancer Letters
        "1756-9966",  # Journal of Experimental & Clinical Cancer Research
        "1541-7786",  # Molecular Cancer Research
        "2326-6066",  # Cancer Immunology Research
    ],
    "THYM": [
        # Thoracic (thymic tumors domain)
        "1556-0864",  # Journal of Thoracic Oncology
        "0022-5223",  # The Journal of Thoracic and Cardiovascular Surgery
        # Pathology (shared)
        "0893-3952",  # Modern Pathology
        "0147-5185",  # American Journal of Surgical Pathology
        "0022-3417",  # The Journal of Pathology
        # Translational Oncology (shared)
        "1470-2045",  # The Lancet Oncology
        "0304-3835",  # Cancer Letters
        "1756-9966",  # Journal of Experimental & Clinical Cancer Research
        "1541-7786",  # Molecular Cancer Research
        "2326-6066",  # Cancer Immunology Research
    ],
    "READ": [
        # Colorectal Surgery
        "0003-4932",  # Annals of Surgery
        "0007-1323",  # British Journal of Surgery
        "2168-6254",  # JAMA Surgery
        # Pathology (shared)
        "0893-3952",  # Modern Pathology
        "0147-5185",  # American Journal of Surgical Pathology
        "0022-3417",  # The Journal of Pathology
        # Translational Oncology (shared)
        "1470-2045",  # The Lancet Oncology
        "0304-3835",  # Cancer Letters
        "1756-9966",  # Journal of Experimental & Clinical Cancer Research
        "1541-7786",  # Molecular Cancer Research
        "2326-6066",  # Cancer Immunology Research
    ],
}
