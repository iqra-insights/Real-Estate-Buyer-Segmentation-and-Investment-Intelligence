const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, ImageRun, AlignmentType, Header, Footer, PageNumber, VerticalAlign,
} = require("docx");

const BASE = path.resolve(__dirname, "..");
const FIG = path.join(BASE, "outputs", "figures");
const PAGE = { width: 12240, height: 15840 };
const BLUE = "4F7CFF";
const DARK = "06101F";
const MUTED = "64748B";
const TEXTCOLOR = "1E293B";

function p(text, opts = {}) {
  return new Paragraph({ children: [new TextRun({ text, ...opts })], spacing: { after: 120 } });
}
function bullet(text, opts = {}) {
  return new Paragraph({ text, bullet: { level: 0 }, spacing: { after: 70 }, ...opts });
}
function h(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 240, after: 120 } });
}
function img(file, width = 560) {
  const data = fs.readFileSync(path.join(FIG, file));
  return new Paragraph({
    children: [new ImageRun({ data, transformation: { width, height: width * 0.62 }, type: "png" })],
    alignment: AlignmentType.CENTER,
    spacing: { after: 160 },
  });
}
function statBox(label, value, color) {
  return new TableCell({
    width: { size: 3100, type: WidthType.DXA },
    shading: { type: ShadingType.CLEAR, color: "auto", fill: "F1F5F9" },
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 160, bottom: 160, left: 120, right: 120 },
    children: [
      new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: value, bold: true, size: 32, color })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: label, size: 16, color: MUTED })] }),
    ],
  });
}

const doc = new Document({
  sections: [{
    properties: { page: { size: PAGE, margin: { top: 900, bottom: 900, left: 900, right: 900 } } },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          border: { bottom: { color: "E2E8F0", space: 4, style: "single", size: 6 } },
          children: [new TextRun({ text: "Executive Summary  |  Parcl Co. Limited", size: 16, color: MUTED, italics: true })],
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "Page ", size: 16, color: MUTED }),
            new TextRun({ children: [PageNumber.CURRENT], size: 16, color: MUTED, bold: true }),
            new TextRun({ text: " of ", size: 16, color: MUTED }),
            new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 16, color: MUTED, bold: true }),
          ],
        })],
      }),
    },
    children: [
      new Table({
        width: { size: 10800, type: WidthType.DXA },
        rows: [new TableRow({
          children: [new TableCell({
            width: { size: 10800, type: WidthType.DXA },
            shading: { type: ShadingType.CLEAR, color: "auto", fill: DARK },
            margins: { top: 300, bottom: 300, left: 300, right: 300 },
            children: [
              new Paragraph({ children: [new TextRun({ text: "PARCL · BUYER INTELLIGENCE", bold: true, color: "20D9FF", size: 18 })] }),
              new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "Machine Learning-Based Buyer Segmentation", bold: true, color: "FFFFFF", size: 34 })] }),
              new Paragraph({ children: [new TextRun({ text: "Executive Summary", bold: true, color: "FFFFFF", size: 34 })] }),
              new Paragraph({ spacing: { before: 150 }, children: [new TextRun({ text: "Prepared for Parcl Co. Limited  |  Unified Mentor Program  |  September 2026", italics: true, color: "94A3B8", size: 20 })] }),
            ],
          })],
        })],
      }),
      new Paragraph({ text: "", spacing: { after: 200 } }),

      h("The Problem, in One Line"),
      p("Parcl treats a highly diverse buyer base as one undifferentiated group, leading to inefficient marketing, generic property recommendations, and missed investment opportunities."),

      h("What We Did"),
      p("Applied unsupervised machine learning (K-Means, validated against Hierarchical clustering) to 2,000 clients and 10,000 property transactions to discover the buyer segments that genuinely exist in Parcl's data — rather than assuming the four segments named in the original project brief."),

      h("Key Numbers"),
      new Table({
        width: { size: 10800, type: WidthType.DXA },
        rows: [new TableRow({ children: [
          statBox("Clients Analyzed", "2,000", BLUE),
          statBox("Transactions", "10,000", "20A374"),
          statBox("Segments Found", "4", "D97706"),
          statBox("Dashboard Pages", "7", "7C3AED"),
        ]})],
      }),
      new Paragraph({ text: "", spacing: { after: 200 } }),

      h("The Four Segments"),
      new Table({
        width: { size: 10800, type: WidthType.DXA },
        rows: [
          new TableRow({ children: [
            new TableCell({ width: {size:3600,type:WidthType.DXA}, shading:{type:ShadingType.CLEAR,color:"auto",fill:BLUE}, children:[new Paragraph({children:[new TextRun({text:"Segment",bold:true,color:"FFFFFF"})]})]}),
            new TableCell({ width: {size:1800,type:WidthType.DXA}, shading:{type:ShadingType.CLEAR,color:"auto",fill:BLUE}, children:[new Paragraph({children:[new TextRun({text:"Size",bold:true,color:"FFFFFF"})]})]}),
            new TableCell({ width: {size:5400,type:WidthType.DXA}, shading:{type:ShadingType.CLEAR,color:"auto",fill:BLUE}, children:[new Paragraph({children:[new TextRun({text:"Recommended Action",bold:true,color:"FFFFFF"})]})]}),
          ]}),
          new TableRow({ children: [
            new TableCell({children:[new Paragraph("Value-Conscious Home Buyers")]}),
            new TableCell({children:[new Paragraph("812 (41%)")]}),
            new TableCell({children:[new Paragraph("Affordability messaging, starter-buyer financing")]}),
          ]}),
          new TableRow({ children: [
            new TableCell({children:[new Paragraph("High-Volume / Frequent Buyers")]}),
            new TableCell({children:[new Paragraph("640 (32%)")]}),
            new TableCell({children:[new Paragraph("Loyalty incentives, early access to new listings")]}),
          ]}),
          new TableRow({ children: [
            new TableCell({children:[new Paragraph("Premium / High-Value Buyers")]}),
            new TableCell({children:[new Paragraph("446 (22%)")]}),
            new TableCell({children:[new Paragraph("Exclusivity and white-glove service, not discounts")]}),
          ]}),
          new TableRow({ children: [
            new TableCell({children:[new Paragraph("Corporate Buyers")]}),
            new TableCell({children:[new Paragraph("102 (5%)")]}),
            new TableCell({children:[new Paragraph("Dedicated B2B sales motion, bulk/multi-unit packages")]}),
          ]}),
        ],
      }),
      new Paragraph({ text: "", spacing: { after: 200 } }),

      img("11_Final_Buyer_Segment_Distribution.png", 420),

      h("What Makes This Credible"),
      bullet("Segments were named from what the data actually showed, not forced into the brief's assumed labels (Global Investors, First-Time Buyers, Luxury Investors)."),
      bullet("Validated three ways: Elbow Method, Silhouette Score, and cross-checked against an independent Hierarchical clustering algorithm."),
      bullet("Stress-tested: 6 random seeds, 10 bootstrap resamples, and the project brief's own literal encoding method tested directly for comparison."),
      bullet("Delivered live: a 7-page interactive Streamlit dashboard with filters by country, region, purpose, and client type — not static slides."),

      h("Stated Honestly, Not Oversold"),
      p("Clustering quality (silhouette 0.12–0.15) is modest — buyer behavior in this dataset varies continuously rather than in sharp groups. This is disclosed throughout the full research paper and dashboard rather than hidden. The four segments are a useful, evidence-based business simplification of that behavior, not a claim of perfectly separated customer types.", { italics: true, color: MUTED }),

      h("Bottom Line"),
      p("A concrete, evidence-based targeting framework Parcl can act on today — with every number traceable back to runnable code, not asserted. Full technical detail, methodology, and limitations are in the accompanying research paper."),
    ],
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(path.join(BASE, "docs", "01_Executive_Summary.docx"), buf);
  console.log("Saved 01_Executive_Summary.docx");
});
