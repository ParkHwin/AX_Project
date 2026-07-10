export default function SearchPanel({
  inputs,
  onChange,
  onSearch,
  onReset,
  materialOptions,
  projectOptions,
}) {
  const set = (key) => (e) => onChange({ ...inputs, [key]: e.target.value });

  const handleMaterialChange = (e) => {
    const no = e.target.value;
    const found = materialOptions.find((m) => m.no === no);
    onChange({ ...inputs, mat: no, name: found ? found.name : "" });
  };

  return (
    <div className="search-panel">
      <div className="search-panel-title">조회 조건</div>
      <div className="search-row">
        <div className="search-field">
          <label>자재 선택</label>
          <select value={inputs.mat} onChange={handleMaterialChange} style={{ width: "220px" }}>
            <option value="">전체 자재</option>
            {materialOptions.map((m) => (
              <option key={m.no} value={m.no}>
                {m.no}
                {m.name ? ` · ${m.name}` : ""}
              </option>
            ))}
          </select>
        </div>
        <div className="search-field">
          <label>프로젝트 선택</label>
          <select value={inputs.prj} onChange={set("prj")} style={{ width: "170px" }}>
            <option value="">전체 프로젝트</option>
            {projectOptions.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </div>
        <div className="search-field">
          <label>조회기간 (시작)</label>
          <input
            type="date"
            value={inputs.dateFrom}
            onChange={set("dateFrom")}
            style={{ width: "130px" }}
          />
        </div>
        <div className="search-field">
          <label>조회기간 (종료)</label>
          <input
            type="date"
            value={inputs.dateTo}
            onChange={set("dateTo")}
            style={{ width: "130px" }}
          />
        </div>
        <div className="search-field">
          <label>구분</label>
          <select value={inputs.filterType} onChange={set("filterType")}>
            <option value="all">전체</option>
            <option value="재고">재고(입고)</option>
            <option value="출하">출하</option>
            <option value="출고">출고</option>
          </select>
        </div>
        <div style={{ display: "flex", gap: "6px", alignItems: "flex-end" }}>
          <button className="btn btn-primary" onClick={onSearch}>
            🔍 조회
          </button>
          <button className="btn btn-secondary" onClick={onReset}>
            초기화
          </button>
        </div>
      </div>
    </div>
  );
}
