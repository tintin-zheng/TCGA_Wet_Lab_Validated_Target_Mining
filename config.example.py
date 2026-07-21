# ============ API Configuration ============
NCBI_EMAIL = "your_email@example.com"       # Replace with your email
NCBI_API_KEY = ""                            # Optional, leave empty if not available

DEEPSEEK_API_KEY = "sk-your-key-here"       # Get from platform.deepseek.com
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"            # or deepseek-v4-pro / deepseek-reasoner

# ============ Parameters ============
SEARCH_COUNT = 200  # PubMed search count per cancer
TARGET_COUNT = 200  # Max wet-lab validated papers kept per cancer

# ============ 37 Q1 Journal ISSNs ============
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
    "UCS": [
        # Gynecologic Oncology
        "0090-8258",  # Gynecologic Oncology
        "1048-891X",  # International Journal of Gynecological Cancer
        "0002-9378",  # American Journal of Obstetrics and Gynecology
        "0029-7844",  # Obstetrics & Gynecology
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
}
