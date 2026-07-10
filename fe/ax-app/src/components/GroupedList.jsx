import { useMemo, useState } from "react";
import { buildTimeline } from "../utils/timeline.js";
import TimelineTable from "./TimelineTable.jsx";

function toNum(v) {
  const n = Number(String(v ?? "").replace(/,/g, ""));
  return Number.isFinite(n) ? n : 0;
}

function qtyField(currentTab) {
  if (currentTab === "재고") return "입고수량";
  if (currentTab === "출하") return "수량";
  return "출고수량";
}

function buildGroups(rows, currentTab, groupBy) {
  const qf = qtyField(currentTab);
  const map = new Map();

  rows.forEach((r) => {
    let key;
    let label;
    if (groupBy === "프로젝트") {
      key = r["프로젝트번호"] || "(프로젝트 미지정)";
      label = key;
    } else {
      const matNo = r["자재번호"] || r["품번"] || "(자재 미지정)";
      const matName = r["자재명"] || r["품명"] || "";
      key = matNo;
      label = matName ? `${matNo} · ${matName}` : matNo;
    }
    if (!map.has(key)) map.set(key, { key, label, rows: [], totalQty: 0 });
    const g = map.get(key);
    g.rows.push(r);
    g.totalQty += toNum(r[qf]);
  });

  return Array.from(map.values()).sort((a, b) => b.rows.length - a.rows.length);
}

export default function GroupedList({ currentTab, rows, rawData, groupBy }) {
  const [expanded, setExpanded] = useState(() => new Set());

  const groups = useMemo(
    () => buildGroups(rows, currentTab, groupBy),
    [rows, currentTab, groupBy],
  );

  const toggle = (key) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  if (groups.length === 0) {
    return (
      <div style={{ textAlign: "center", padding: "24px 0", color: "#94a3b8", fontSize: "12px" }}>
        표시할 데이터가 없습니다. 엑셀 파일을 업로드하거나 조회 조건을 확인해주세요.
      </div>
    );
  }

  return (
    <div className="group-list">
      {groups.map((g) => {
        const isOpen = expanded.has(g.key);
        const matchers =
          groupBy === "프로젝트"
            ? {
                재고: (r) => r["프로젝트번호"] === g.key,
                출하: (r) => r["프로젝트번호"] === g.key,
                출고: (r) => r["프로젝트번호"] === g.key,
              }
            : {
                재고: (r) => (r["자재번호"] || "") === g.key,
                출하: (r) => (r["품번"] || "") === g.key,
                출고: (r) => (r["자재번호"] || "") === g.key,
              };

        return (
          <div className="group-card" key={g.key}>
            <div className="group-card-header" onClick={() => toggle(g.key)}>
              <span className="group-card-title">{g.label}</span>
              <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span className="badge">{g.rows.length}건</span>
                <span className="card-sub" style={{ margin: 0 }}>
                  {g.totalQty} EA
                </span>
                <span className="group-card-chevron">{isOpen ? "▲" : "▼"}</span>
              </span>
            </div>
            {isOpen && (
              <div className="group-card-body">
                <div className="detail-section-title">통합 이력 (입고 · 출하 · 출고)</div>
                <TimelineTable
                  items={buildTimeline(rawData, matchers)}
                  emptyLabel="관련 이력이 없습니다"
                />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
