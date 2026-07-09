# 🛠️ Technical Debt Hotspot Analyzer

![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge)

## Τι είναι αυτό το εργαλείο;
Όλοι μιλούν για το **Τεχνολογικό Χρέος (Technical Debt)**, αλλά σπάνια ξέρουν πώς να το *μετρήσουν*. Αυτό το αυτόνομο Python script λύνει ακριβώς αυτό το πρόβλημα.

Είναι ένα εργαλείο στατικής ανάλυσης κώδικα (Static Analysis) που μπαίνει σε οποιοδήποτε Python Repository και υπολογίζει μαθηματικά τα "Hotspots" - δηλαδή τα αρχεία που κοστίζουν τα περισσότερα χρήματα και χρόνο στην ομάδα.

## Πώς το υπολογίζει; (Ο Μαθηματικός Τύπος)
Το εργαλείο συνδυάζει δύο θεμελιώδεις μετρικές:
1. **Cyclomatic Complexity (μέσω `radon`):** Πόσο περίπλοκος, "μακαρονένιος" (spaghetti) και δυσνόητος είναι ο κώδικας σε ένα αρχείο.
2. **Git Churn (μέσω `git log`):** Πόσο συχνά αλλάζει αυτό το αρχείο από τους developers.

> **💡 The Hotspot Rule:** Ένα αρχείο με τεράστια πολυπλοκότητα αλλά μηδενικές αλλαγές εδώ και 3 χρόνια *ΔΕΝ* είναι πρόβλημα. Ένα αρχείο με υψηλή πολυπλοκότητα που αλλάζει *κάθε εβδομάδα* είναι μια ωρολογιακή βόμβα.

Ο τύπος του **Debt Score** είναι: `Complexity * (log(Churn) + 1)`

Επιπλέον, το εργαλείο σκανάρει όλο τον κώδικα για να βρει ξεχασμένα `# TODO`, `# FIXME` και `# HACK` σχόλια, παρέχοντας μια πλήρη εικόνα των ανθρώπινων "χρεών" που έχουν αφεθεί στον κώδικα.

## 🚀 Οδηγίες Χρήσης (Quick Start)

1. Κάνε εγκατάσταση τα requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Τρέξε το εργαλείο (μέσα σε ένα Git Repository):
   ```bash
   python analyzer.py /path/to/your/repo
   ```
   *(Αν δεν βάλεις path, σκανάρει τον τρέχοντα φάκελο)*

Το εργαλείο θα τυπώσει ένα εντυπωσιακό χρωματιστό Report στο Terminal σου (μέσω της βιβλιοθήκης `rich`) και θα δημιουργήσει ένα αρχείο `debt_report.md` με τα αποτελέσματα!

---
*Built for true software engineering observability by DARKAIS.*
