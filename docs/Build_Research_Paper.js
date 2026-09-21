const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, ImageRun, AlignmentType, BorderStyle, PageBreak, SectionType,
  TableOfContents, Header, Footer, PageNumber, NumberFormat, VerticalAlign,
} = require("docx");

const BASE = path.resolve(__dirname, "..");
const FIG = path.join(BASE, "outputs", "figures");

const PAGE = { width: 12240, height: 15840 }; // US Letter
const BRAND_BLUE = "4F7CFF";
const BRAND_DARK = "06101F";
const BRAND_MUTED = "64748B";
const BRAND_CYAN = "20D9FF";

function h(text, level = HeadingLevel.HEADING_1) {
  return new Paragraph({ text, heading: level, spacing: { before: 280, after: 140 } });
}
function p(text, opts = {}) {
  return new Paragraph({ children: [new TextRun({ text, ...opts })], spacing: { after: 120 } });
}
function bullet(text) {
  return new Paragraph({ text, bullet: { level: 0 }, spacing: { after: 60 } });
}
function img(file, width = 560) {
  const data = fs.readFileSync(path.join(FIG, file));
  // Use sharp-free approach: assume standard 150dpi aspect from matplotlib figsize; scale by width only.
  return new Paragraph({
    children: [new ImageRun({ data, transformation: { width, height: width * 0.62 }, type: "png" })],
    alignment: AlignmentType.CENTER,
    spacing: { after: 200 },
  });
}

function simpleTable(headerRow, rows, colWidths) {
  const totalWidth = colWidths.reduce((a, b) => a + b, 0);
  const mkCell = (text, bold = false, shade = false) => new TableCell({
    width: { size: colWidths[0], type: WidthType.DXA },
    shading: shade ? { type: ShadingType.CLEAR, color: "auto", fill: "DDEBF7" } : undefined,
    children: [new Paragraph({ children: [new TextRun({ text: String(text), bold })] })],
  });

  const header = new TableRow({
    children: headerRow.map((t, i) => new TableCell({
      width: { size: colWidths[i], type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, color: "auto", fill: BRAND_BLUE },
      children: [new Paragraph({ children: [new TextRun({ text: t, bold: true, color: "FFFFFF" })] })],
    })),
  });

  const body = rows.map(r => new TableRow({
    children: r.map((t, i) => new TableCell({
      width: { size: colWidths[i], type: WidthType.DXA },
      children: [new Paragraph({ children: [new TextRun({ text: String(t) })] })],
    })),
  }));

  return new Table({ width: { size: totalWidth, type: WidthType.DXA }, columnWidths: colWidths, rows: [header, ...body] });
}

const doc = new Document({
  sections: [{
    properties: {
      page: { size: PAGE },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          border: { bottom: { color: "E2E8F0", space: 4, style: BorderStyle.SINGLE, size: 4 } },
          children: [new TextRun({
            text: "Buyer Segmentation & Investment Profiling  |  Parcl Co. Limited",
            size: 16, color: BRAND_MUTED,
          })],
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "Page ", size: 16, color: BRAND_MUTED }),
            new TextRun({ children: [PageNumber.CURRENT], size: 16, color: BRAND_MUTED }),
            new TextRun({ text: " of ", size: 16, color: BRAND_MUTED }),
            new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 16, color: BRAND_MUTED }),
          ],
        })],
      }),
    },
    children: [
      // ---------------- COVER PAGE ----------------
      new Paragraph({ spacing: { before: 1200 }, children: [] }),
      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        borders: {
          top: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
          bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
          left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
          right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
          insideHorizontal: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
          insideVertical: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
        },
        rows: [new TableRow({
          children: [new TableCell({
            shading: { type: ShadingType.CLEAR, color: "auto", fill: BRAND_DARK },
            verticalAlign: VerticalAlign.CENTER,
            margins: { top: 720, bottom: 720, left: 720, right: 720 },
            children: [
              new Paragraph({
                spacing: { after: 100 },
                children: [new TextRun({ text: "PARCL  ·  BUYER INTELLIGENCE", bold: true, color: BRAND_CYAN, size: 18 })],
              }),
              new Paragraph({
                spacing: { after: 200 },
                children: [new TextRun({ text: "Machine Learning-Based Buyer Segmentation and Investment Profiling for Real Estate Market Intelligence", bold: true, color: "FFFFFF", size: 40 })],
              }),
              new Paragraph({
                border: { top: { color: BRAND_BLUE, space: 8, style: BorderStyle.SINGLE, size: 18 } },
                spacing: { before: 100 },
                children: [],
              }),
            ],
          })],
        })],
      }),
      new Paragraph({ spacing: { before: 300, after: 60 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Prepared for Parcl Co. Limited  |  Unified Mentor Program", italics: true, size: 22, color: BRAND_MUTED })] }),
      new Paragraph({ spacing: { after: 500 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "September 2026", italics: true, size: 20, color: BRAND_MUTED })] }),
      new Paragraph({ children: [new PageBreak()] }),

      // ---------------- TABLE OF CONTENTS ----------------
      // A static, manually-written TOC is used instead of a dynamic Word
      // TOC field. Word field codes (like TableOfContents) only populate
      // when explicitly refreshed - automatically in some Word setups, but
      // NOT in LibreOffice, most PDF converters, or every Word configuration
      // - so a dynamic TOC can render blank on first open with no visual
      // indication anything is wrong. A static list has no page-number
      // auto-sync, but it is guaranteed to actually display everywhere.
      new Paragraph({ text: "Table of Contents", heading: HeadingLevel.HEADING_1, spacing: { after: 200 } }),
      ...[
        "Abstract", "1. Introduction", "2. Industry Background", "3. Problem Statement",
        "4. Objectives", "5. Dataset Description", "6. Data Preparation",
        "7. Exploratory Data Analysis", "8. Feature Engineering", "9. Machine Learning Methodology",
        "10. Buyer Segment Profiles", "11. Business Insights", "12. Strategic Recommendations",
        "13. Streamlit Application", "14. Limitations", "15. Future Scope",
        "16. Conclusion", "17. References",
      ].map(title => new Paragraph({
        spacing: { after: 90 },
        tabStops: [{ type: "right", position: 9350, leader: "dot" }],
        children: [new TextRun({ text: title, size: 22, color: "1E293B" })],
      })),
      new Paragraph({ children: [new PageBreak()] }),

      h("Abstract"),
      p("Parcl operates in a real estate market with highly diverse buyer behavior, from individual first-time buyers to corporate investors, but lacked a data-driven method for distinguishing between them. This study applies unsupervised machine learning — K-Means clustering, cross-validated with Hierarchical clustering — to a client base of 2,000 buyers and 10,000 property transactions to identify natural buyer segments. Four segments emerged: Value-Conscious Home Buyers, High-Volume / Frequent Buyers, Premium/High-Value Buyers, and Corporate Buyers. Cluster separation was modest (silhouette score 0.14), reflecting a buyer population that varies along a continuum rather than in sharply bounded groups; this is reported transparently rather than overstated. The resulting segments and their behavioral profiles are delivered through an interactive Streamlit dashboard with filtering by country, region, acquisition purpose, and client type, giving Parcl's marketing and investment teams a concrete, evidence-based targeting framework."),

      h("1. Introduction"),
      p("Real estate companies serve buyers with very different motivations and financing behavior — individual home buyers, institutional and international investors, high-net-worth clients, and first-time buyers. Treating this population uniformly leads to inefficient marketing spend, generic property recommendations, and missed investment opportunities. This project uses AI-based clustering to surface hidden structure in buyer behavior and translate it into segment-specific business recommendations."),

      h("2. Industry Background"),
      p("Buyer segmentation is a well-established practice in real estate and financial services marketing, typically built on demographic, geographic, and transactional data. What differentiates a data-driven approach from manual segmentation is the ability to discover segments empirically from behavioral signals — such as purchase frequency, spend, and financing patterns — rather than assuming them in advance."),

      h("3. Problem Statement"),
      p("Parcl lacked a data-driven understanding of: (1) the different types of property buyers active on its platform, (2) investment motivations across demographic groups, (3) geographic differences in investment behavior, and (4) customer financing patterns. This limited marketing efficiency and investor targeting."),

      h("4. Objectives"),
      bullet("Build a reproducible data pipeline from the raw client and property records to a clustering-ready client-level feature table."),
      bullet("Apply K-Means and Hierarchical clustering to discover genuine buyer segments, validated with the Elbow Method and Silhouette Score."),
      bullet("Profile and name each segment from its actual data characteristics, not from an assumed template."),
      bullet("Deliver segment insights through an interactive Streamlit dashboard with the filters the business requested."),

      h("5. Dataset Description"),
      p("Two raw files were supplied:"),
      bullet("Client_Master_Raw_Data.csv — 2,000 rows, 12 columns: client demographics, acquisition purpose, financing, referral channel, and satisfaction score. No missing values or duplicate rows."),
      bullet("Property_Transactions_Raw_Data.csv — 10,000 rows, 9 columns: property listings with transaction date, floor area, sale price, listing status (Sold/Available), and a client_ref foreign key."),
      p("A key structural finding from the data audit: this is a one-client-to-many-properties relationship — every one of the 2,000 clients purchased at least one unit, and one client purchased as many as 13. client_ref is populated for all 7,305 Sold listings and null for all 2,695 Available (unsold) listings, with no orphaned references in either direction. A naive merge on client_id would therefore duplicate each client's demographic row once per property purchased, corrupting any clustering built directly on it."),

      h("6. Data Preparation"),
      p("Cleaning addressed several real inconsistencies found during the audit rather than a textbook-clean file:"),
      bullet("date_of_birth mixes DD-MM-YYYY and MM/DD/YYYY string formats within the same column — parsed with pandas' mixed-format inference rather than a single fixed format, which would have silently corrupted one of the two conventions."),
      bullet("sale_price is stored as a currency string (e.g. \"$300,385.62\") and was stripped of $ and , before casting to float."),
      bullet("acquisition_purpose values are Home / Investment (the original requirements document listed \"Personal use\"; the actual field value is \"Home\")."),
      p("Property_Transactions_Raw_Data.csv (Sold listings only) was aggregated to one row per client — total purchases, total spend, average and maximum purchase price, average floor area, unit-type mix, number of distinct towers purchased in, and purchase span in days — and joined one-to-one onto Client_Master_Raw_Data.csv. This produced a genuine investment-behavior feature set rather than the shallow single-transaction view implied by the original schema."),

      h("7. Exploratory Data Analysis"),
      p("EDA was structured around specific business questions rather than a generic chart dump. Selected findings:"),
      img("02_Acquisition_Purpose_by_Client_Type.png"),
      p("Investment vs. home-purchase share differs only modestly between Individual and Company client types in this dataset, suggesting acquisition purpose is not strongly driven by client type alone."),
      img("03_Investment_Rate_by_Top_Country.png"),
      p("Investment-purchase rates vary by country, providing an input for geographic campaign prioritization independent of the cluster segmentation."),
      img("07_Customer_Satisfaction_Distribution.png"),

      h("8. Feature Engineering"),
      p("Client-level features used downstream fall into three groups: numeric behavioral (age, satisfaction_score, total_purchases, total_spend, avg_purchase_price, avg_floor_area, pct_apartment, purchase_span_days), binary flags (loan_flag, investment_flag, is_company, is_repeat_buyer), and categorical geography (country, region) — the latter retained for reporting but deliberately excluded from the clustering input matrix (Section 9.1)."),

      h("9. Machine Learning Methodology"),
      new Paragraph({ text: "9.1 Feature Selection for Clustering", heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 100 } }),
      p("Two configurations were tested: (a) numeric + binary features plus one-hot-encoded country, referral_channel, and gender, and (b) numeric + binary features alone. Configuration (b) produced better cluster separation (silhouette 0.1405 vs. 0.1089 at k=4) because the high-cardinality one-hot columns diluted Euclidean distance once mixed with StandardScaler'd continuous variables. Configuration (b) was used for the final model; country and region are analyzed post-hoc against the resulting cluster labels instead."),
      p("The original project brief's own specification for this step - One-Hot or Label Encoding of client_type, region, acquisition_purpose, referral_channel, and country, combined with only age and satisfaction_score as numeric fields - was also implemented literally and evaluated (src/05_Brief_Encoding_Validation.py), rather than assumed to be worse. The result is counterintuitive: both brief-compliant encodings score a numerically higher raw silhouette than the production model (Label Encoding: 0.4126 at k=2; One-Hot: 0.1634 at k=2; production: 0.1451 at k=3). Inspecting cluster composition shows why this is not actually a better result: the Label-Encoded k=2 clusters are a perfect, trivial reproduction of the already-known client_type column (0 Company/1897 Individual vs. 103 Company/0 Individual) rather than discovered structure, and the One-Hot k=2 clusters split almost entirely on satisfaction_score (means 1.49 vs. 4.00) because 57 sparse region dummy columns individually carry too little weight to influence the distance calculation. Silhouette score alone cannot distinguish a genuine multi-dimensional segmentation from a degenerate single-variable split; cluster composition must be inspected directly. Full detail in docs/07_Brief_Encoding_Comparison.md."),

      new Paragraph({ text: "9.2 K-Means Clustering and Cluster-Count Selection", heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 100 } }),
      p("K-Means was fit for k = 2 through 10 (n_init = 20, random_state = 42 - the same settings as the final production fit, so this table's k=4 row matches the shipped model exactly), evaluated with the Elbow Method (inertia) and Silhouette Score:"),
      simpleTable(
        ["k", "Inertia", "Silhouette Score"],
        [
          ["2", "20,631.0", "0.1381"],
          ["3", "18,556.7", "0.1451 (maximum)"],
          ["4", "16,895.6", "0.1405  \u2190 selected"],
          ["5", "15,812.6", "0.1286"],
          ["6", "14,353.5", "0.1308"],
          ["7", "13,616.9", "0.1314"],
          ["8", "13,102.9", "0.1322"],
        ],
        [1200, 2600, 3200]
      ),
      p(" "),
      img("10_Cluster_Selection_Diagnostics.png"),
      p("Silhouette scores are modest (0.12\u20130.15) and nearly flat from k=3 through k=8, indicating the buyer population does not separate into sharply bounded natural clusters — behavior varies more continuously than in hard groups. Rather than default to the silhouette-optimal k=3, k=4 was selected: it isolates corporate buyers (is_company \u2248 1.0 in one cluster, \u2248 0 in the other three) — the single most genuinely distinct signal in the data — into their own operationally meaningful segment, at only a small silhouette cost. This decision is deliberate and documented, consistent with the principle that cluster-count selection should weigh interpretability and business usefulness alongside the statistical score, not the score alone."),

      p("A data-quality check on the engineered features caught and removed one flawed input: is_repeat_buyer (total_purchases > 1) was found to be constant \u2014 every one of the 2,000 clients made at least 3 purchases \u2014 so it carried no clustering signal and had misleadingly suggested that repeat purchasing distinguished one segment, when in fact all clients qualify. It was dropped from the feature set (with no change to the resulting clusters, since a constant feature contributes zero variance) and the affected segment was renamed to reflect its actual distinguishing trait: purchase frequency well above the other segments, not repeat-buyer status."),

      new Paragraph({ text: "9.3 Hierarchical Clustering Cross-Validation", heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 100 } }),
      p("Agglomerative clustering with Ward linkage was run on a representative sample to (a) visualize nested cluster structure via dendrogram and (b) cross-check the K-Means solution via Adjusted Rand Index (ARI)."),
      img("13_Hierarchical_Clustering_Cross_Check.png"),
      p("ARI between the k=4 K-Means labels and Hierarchical clustering on a 1,000-client sample was 0.267 — moderate, not strong, agreement. This is consistent with the weak natural cluster structure identified above and with the two algorithms using different distance/linkage objectives; it is reported as a genuine validation result, not adjusted to look stronger."),

      new Paragraph({ text: "9.4 Robustness & Stability Analysis", heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 100 } }),
      p("Beyond a single Elbow/Silhouette pass, three additional checks were run to test whether the production solution is an artifact of one specific fit rather than a reproducible pattern: (a) two alternative feature-engineering strategies, (b) K-Means stability across six random seeds, and (c) stability under 80%-resample bootstrapping."),
      simpleTable(
        ["Check", "Result"],
        [
          ["Alternative strategy: log-scaled spend", "No meaningful improvement (silhouette 0.126-0.142 across k=2-6)"],
          ["Alternative strategy: spend-per-purchase (\"Balanced behavior\")", "Higher silhouette (0.172 at k=3) but merges corporate buyers into the individual-buyer cluster - rejected despite the better score, since it loses an operationally important distinction"],
          ["Seed stability (6 seeds, k=4)", "Mean pairwise ARI 0.731, but bimodal: {seed 0, seed 123} agree perfectly (ARI=1.0) and {seeds 7,21,42,84} agree closely (ARI 0.94-0.99); the two groups only agree with each other at ARI~0.52"],
          ["80% bootstrap resampling (10 replicates, k=4)", "Mean ARI 0.583 vs. the full-data model, ranging from 0.263 to 0.960 - highly variable, not tightly clustered around the mean"],
        ],
        [3600, 5400]
      ),
      p("The bimodal seed result is the more important finding to be transparent about: K-Means is converging to one of at least two distinct, internally-consistent solutions depending on initialization, not settling near one solution with random jitter around it. The production model uses random_state=42, which falls in the four-seed majority group - the more commonly-reached solution, not the rarer alternative - but a different arbitrary seed choice could plausibly have shipped a qualitatively different clustering. Reporting only the mean ARI (0.731) would understate this risk."),
      p("The feature-correlation matrix (outputs/tables/05_Clustering_Feature_Correlation.csv) explains why the segments separate the way they do: total_purchases and n_towers correlate at 0.93, and avg_purchase_price and avg_floor_area correlate at 0.96, with total_spend correlating 0.57-0.71 with three other included features. Five of the nine numeric clustering features substantially encode the same underlying \"transaction scale\" dimension, which is disproportionately weighted in the Euclidean distance calculation as a result - while loan_flag, investment_flag, is_company, and satisfaction_score all correlate near zero (\u22640.08) with everything else. This is a direct, data-backed explanation for why the resulting segments separate mainly by spend/purchase scale rather than by financing or investment behavior, rather than an oversight in feature selection."),
      p("Full detail, including the raw per-seed and per-replicate tables, is in docs/06_Model_Robustness_Validation.md, generated by src/04_Model_Robustness_Validation.py."),

      h("10. Buyer Segment Profiles"),
      simpleTable(
        ["Segment", "Size", "Avg Age", "Avg Spend ($)", "Avg Price ($)", "Investment %", "Loan %"],
        [
          ["Value-Conscious Home Buyers", "812", "55.5", "983,920", "291,826", "33%", "38%"],
          ["High-Volume / Frequent Buyers", "640", "57.7", "1,549,453", "358,204", "28%", "36%"],
          ["Premium / High-Value Buyers", "446", "54.7", "1,353,463", "432,124", "30%", "34%"],
          ["Corporate Buyers", "102", "47.6", "1,240,326", "345,481", "34%", "42%"],
        ],
        [2600, 800, 900, 1400, 1400, 1300, 1000]
      ),
      p(" "),
      img("11_Final_Buyer_Segment_Distribution.png"),
      p("Segment names were derived by ranking clusters against each other on the metrics that actually separate them — average purchase price, purchase frequency, total spend, and company share — rather than fixed thresholds or the four labels originally proposed in the project brief (Global Investors / First-Time Buyers / Corporate Buyers / Luxury Investors). The data did not reproduce that exact framing: for example, investment_flag and loan_flag rates are fairly similar across all four segments (28\u201334% and 34\u201342% respectively), so the segments are better distinguished by transaction scale and frequency than by stated purchase intent."),
      p("Each brief-proposed label's implied defining trait was checked directly against the cluster profile before being rejected, rather than assumed unsuitable:"),
      simpleTable(
        ["Brief label", "Implied trait", "What the data shows"],
        [
          ["First-Time Buyers", "Younger, loan-dependent", "Age ranges only 54.6\u201357.7 across individual clusters; loan rate ranges only 34.3\u201338.4%"],
          ["Global Investors", "Investment-purchase focused", "Investment rate ranges only 27.8\u201333.3% across all four clusters"],
          ["Luxury Investors", "High satisfaction", "Satisfaction ranges only 2.94\u20133.16 (of 5) across all four clusters"],
          ["Corporate Buyers", "Companies, multiple units", "is_company = 1.0 in one cluster, \u22640.002 in the other three \u2014 matches, used as-is"],
        ],
        [2600, 3200, 3900]
      ),
      p(" "),
      p("Only Corporate Buyers survives contact with the actual numbers. Labeling a segment \"First-Time Buyers\" when it is not the youngest group in the data, or \"Luxury Investors\" when its satisfaction score is statistically indistinguishable from every other segment, would be a factually incorrect claim rather than a stylistic choice — so the three remaining segments were named from the dimensions that do separate the data (purchase price, frequency, and total spend) instead."),
      p("Gender was profiled as a composition table per cluster rather than a numeric average, since it is categorical: the split is close to even (48-52% female) in three of the four segments, with Corporate Buyers skewing further male (61%) - plausibly reflecting who signs on behalf of a company rather than a buyer-preference effect, though the dataset does not let us distinguish those explanations."),

      h("11. Business Insights"),
      bullet("Value-Conscious Home Buyers (41% of clients) purchase lower-priced, smaller units and should be targeted with affordability-focused messaging and starter financing options."),
      bullet("High-Volume / Frequent Buyers (32%) purchase most frequently and generate the highest total spend — a strong segment for loyalty programs and early access to new listings."),
      bullet("Premium / High-Value Buyers (22%) pay the highest average price per unit and respond better to exclusivity and service quality than to price-based offers."),
      bullet("Corporate Buyers (5%) are almost entirely companies with the highest loan-application rate (42%) among segments, and need a B2B sales motion rather than retail marketing."),

      h("12. Strategic Recommendations"),
      bullet("Route corporate leads to a dedicated B2B sales team with bulk/multi-unit packages, rather than the standard retail funnel."),
      bullet("Build a loyalty or portfolio-incentive program for High-Volume / Frequent Buyers given their outsized share of total transaction volume."),
      bullet("Position Premium/High-Value inventory with exclusivity and white-glove service rather than discounting."),
      bullet("Offer financing calculators and first-time-buyer packages to Value-Conscious Home Buyers, the largest segment."),

      h("13. Streamlit Application"),
      p("An interactive dashboard (app/Real_Estate_Buyer_Intelligence_Dashboard.py) delivers seven pages — Executive Overview, Buyer Segmentation, Geographic Intelligence, Investment Profiling, Segment Insights, Customer Explorer, and Model Information — with sidebar filters for country, region, acquisition purpose, client type, and segment, as specified in the project requirements. The Geographic Intelligence page includes a country-level choropleth map (switchable between client count, investment rate, and average spend), using explicit ISO-3 country codes rather than raw country-name matching to avoid abbreviations like \"USA\"/\"UK\" silently failing to resolve. The Customer Explorer page allows drilling into individual client records with CSV export. The Segment Insights page includes a data-informed recommended business action for whichever segment is selected, explicitly framed as a hypothesis because the dataset contains no campaign-response or ROI data. The Model Information page discloses the clustering methodology, its robustness testing, and its limitations directly to end users."),

      h("14. Limitations"),
      bullet("Silhouette scores (0.12\u20130.15) indicate weak natural cluster separation; segment boundaries are a useful business simplification of continuous behavior, not hard categories."),
      bullet("Region (57 levels) was too high-cardinality to use directly as a clustering input and is reported only in aggregate."),
      bullet("The dataset does not include marketing-channel cost or campaign-response data, limiting ROI-based validation of the recommendations above."),
      bullet("The client base is 76.9% USA (1,538 of 2,000 clients); the remaining 9 countries range from 95 (UK) down to 15 (Denmark) clients. Country-level comparisons for the smaller countries are statistically noisy - a rate computed on 15 people is not reliable - and should be read as indicative rather than confident for anything outside the USA/UK/Canada range."),
      bullet("Seed-stability testing found K-Means converges to one of at least two distinct solutions depending on initialization (Section 9.4); the production model happens to fall in the more common of the two, but this is a real sensitivity, not a settled non-issue."),

      h("15. Future Scope"),
      bullet("Test Gaussian Mixture Models or DBSCAN as alternatives to K-Means's spherical-cluster assumption, given the observed low silhouette scores."),
      bullet("Incorporate marketing-response data to validate segment-specific campaign recommendations directly."),
      bullet("Extend the feature set with time-series purchase-recency/frequency trends as more transaction history accumulates."),

      h("16. Conclusion"),
      p("This project replaced an assumed, template-driven buyer segmentation with one derived directly from Parcl's actual client and transaction data. While the resulting clusters are only moderately well-separated \u2014 an honest finding about the data rather than a modeling shortcoming \u2014 they surface an operationally useful and previously invisible distinction (notably, corporate buyers) and provide Parcl's marketing and investment teams with a concrete, evidence-based targeting framework delivered through an interactive, filterable dashboard."),

      h("17. References"),
      p("Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research, 12, 2825-2830."),
      p("MacQueen, J. (1967). Some methods for classification and analysis of multivariate observations. Proceedings of the Fifth Berkeley Symposium on Mathematical Statistics and Probability, 1, 281-297."),
      p("Rousseeuw, P. J. (1987). Silhouettes: A graphical aid to the interpretation and validation of cluster analysis. Journal of Computational and Applied Mathematics, 20, 53-65."),
      p("Ward, J. H. (1963). Hierarchical grouping to optimize an objective function. Journal of the American Statistical Association, 58(301), 236-244."),
      p("McKinney, W. (2010). Data Structures for Statistical Computing in Python. Proceedings of the 9th Python in Science Conference, 56-61. (pandas)"),
      p("Streamlit Inc. (2024). Streamlit Documentation. https://docs.streamlit.io"),
      p("Plotly Technologies Inc. (2024). Plotly Python Open Source Graphing Library. https://plotly.com/python/"),
      p("Parcl Co. Limited / Unified Mentor (2026). Project Requirements Document: Machine Learning-Based Buyer Segmentation and Investment Profiling for Real Estate Market Intelligence. (Internal project brief; raw datasets Client_Master_Raw_Data.csv and Property_Transactions_Raw_Data.csv)"),
    ],
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(path.join(BASE, "docs", "02_Research_Paper.docx"), buf);
  console.log("Saved 02_Research_Paper.docx");
});
