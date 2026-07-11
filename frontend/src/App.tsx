type ProductSection = {
  title: string;
  description: string;
};

const productSections: ProductSection[] = [
  {
    title: "Messy File Upload",
    description: "A planned intake flow for CSV, TSV, text tables, and Excel workbooks.",
  },
  {
    title: "Structure Detection",
    description: "Future profiling will identify headers, sheets, delimiters, and table shape.",
  },
  {
    title: "Rule-Based Cleaning",
    description: "Users will choose transparent deterministic rules before data is changed.",
  },
  {
    title: "Cleaned CSV Export",
    description: "Exports will focus on analysis-ready CSV output instead of spreadsheet styling.",
  },
  {
    title: "Cleaning Reports",
    description: "Reports will document validations, detected issues, and applied transformations.",
  },
];

function App() {
  return (
    <main className="app-shell">
      <section className="hero" aria-labelledby="product-title">
        <div className="hero-copy">
          <p className="eyebrow">Deterministic data preparation</p>
          <h1 id="product-title">DataPulse</h1>
          <p className="subtitle">Messy CSV & Excel Cleaner Studio</p>
          <p className="description">
            Prepare messy tabular files for analysis with transparent validation,
            structure profiling, rule-based cleaning, CSV-first export, and clear reports.
          </p>
        </div>
        <div className="status-panel" aria-label="Current foundation status">
          <span className="status-label">DP-0001</span>
          <strong>Foundation in progress</strong>
          <p>No upload or cleaning engine yet. This release establishes the product shell.</p>
        </div>
      </section>

      <section className="workflow" aria-labelledby="workflow-title">
        <div className="section-heading">
          <p className="eyebrow">Planned product workflow</p>
          <h2 id="workflow-title">From messy table to documented CSV</h2>
        </div>
        <div className="feature-grid">
          {productSections.map((section) => (
            <article className="feature-card" key={section.title}>
              <h3>{section.title}</h3>
              <p>{section.description}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

export default App;
