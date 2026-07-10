export default function SectionTabs({ currentTab, counts, onSwitch }) {
  const tabs = [
    { key: "재고", label: "재고리스트" },
    { key: "출하", label: "출하리스트" },
    { key: "출고", label: "출고리스트" },
  ];

  return (
    <div className="section-tabs">
      {tabs.map((t) => (
        <div
          key={t.key}
          className={`section-tab${currentTab === t.key ? " active" : ""}`}
          onClick={() => onSwitch(t.key)}
        >
          {t.label} <span className="badge">{counts[t.key]}</span>
        </div>
      ))}
    </div>
  );
}
