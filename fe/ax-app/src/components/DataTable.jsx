import { Fragment } from "react";
import { TITLE_MAP, PAGE_SIZE } from "../constants.js";
import GroupedList from "./GroupedList.jsx";

const GROUP_MODES = [
  { key: "none", label: "목록형" },
  { key: "프로젝트", label: "프로젝트별" },
  { key: "자재", label: "자재별" },
];

function renderCell(h, r) {
  const v = r[h] || "";
  if (h === "프로젝트번호") {
    return (
      <td>
        <span className="tag tag-blue">{v}</span>
      </td>
    );
  }
  if ((h === "입고수량" || h === "수량") && v) {
    return (
      <td>
        <strong>{v}</strong> EA
      </td>
    );
  }
  if (h === "출고수량") {
    if (v === "0") {
      return (
        <td>
          <span className="tag tag-red">0 EA ⚠</span>
        </td>
      );
    }
    return (
      <td>
        <strong>{v}</strong> EA
      </td>
    );
  }
  if (h === "출고요청수량" && v) return <td>{v} EA</td>;
  if (h === "구매요청번호" && !v) {
    return (
      <td>
        <span className="tag tag-amber">미연결</span>
      </td>
    );
  }
  if (h === "비고" && v && v.includes("전환출고")) {
    return (
      <td>
        <span className="tag tag-gray">{v.slice(0, 20)}...</span>
      </td>
    );
  }
  return <td>{v}</td>;
}

export default function DataTable({
  currentTab,
  headers,
  filteredData,
  currentPage,
  onPageChange,
  onRowClick,
  onExport,
  rawData,
  groupMode,
  onGroupModeChange,
}) {
  const alerts = filteredData.filter((r) => r["출고수량"] === "0");
  const totalPages = Math.max(1, Math.ceil(filteredData.length / PAGE_SIZE));
  const start = (currentPage - 1) * PAGE_SIZE;
  const pageData = filteredData.slice(start, start + PAGE_SIZE);

  const pageNumbers = [];
  for (let i = 1; i <= totalPages; i++) {
    if (totalPages > 7 && i > 3 && i < totalPages - 1 && Math.abs(i - currentPage) > 1) {
      if (i === 4) pageNumbers.push("ellipsis");
      continue;
    }
    pageNumbers.push(i);
  }

  return (
    <div className="table-wrap">
      <div className="table-header">
        <div className="table-title">
          <span>{TITLE_MAP[currentTab]}</span>
          <span className="badge">{filteredData.length}건</span>
          {alerts.length > 0 && (
            <span className="badge warn">⚠ 실출고 0건 {alerts.length}건</span>
          )}
        </div>
        <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
          <div className="group-mode-toggle">
            {GROUP_MODES.map((m) => (
              <button
                key={m.key}
                className={`group-mode-btn${groupMode === m.key ? " active" : ""}`}
                onClick={() => onGroupModeChange(m.key)}
              >
                {m.label}
              </button>
            ))}
          </div>
          <button
            className="btn btn-secondary"
            style={{ fontSize: "11px" }}
            onClick={onExport}
          >
            📥 엑셀 내보내기
          </button>
        </div>
      </div>
      {groupMode !== "none" ? (
        <div className="group-list-wrap">
          <GroupedList
            currentTab={currentTab}
            rows={filteredData}
            rawData={rawData}
            groupBy={groupMode}
          />
        </div>
      ) : (
        <>
          <div style={{ overflowX: "auto" }}>
            <table>
              <thead>
                <tr>
                  <th>NO</th>
                  {headers.map((h) => (
                    <th key={h}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {pageData.length === 0 && (
                  <tr>
                    <td colSpan={headers.length + 1} style={{ textAlign: "center", padding: "24px 0", color: "#94a3b8" }}>
                      표시할 데이터가 없습니다. 엑셀 파일을 업로드하거나 조회 조건을 확인해주세요.
                    </td>
                  </tr>
                )}
                {pageData.map((r, i) => {
                  const isAlert = currentTab === "출고" && r["출고수량"] === "0";
                  return (
                    <tr
                      key={start + i}
                      className={isAlert ? "alert-row" : ""}
                      onClick={() => onRowClick(r)}
                    >
                      <td>{start + i + 1}</td>
                      {headers.map((h) => (
                        <Fragment key={h}>{renderCell(h, r)}</Fragment>
                      ))}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {totalPages > 1 && (
            <div className="pagination">
              <button
                className="page-btn"
                disabled={currentPage === 1}
                onClick={() => onPageChange(currentPage - 1)}
              >
                ◀
              </button>
              {pageNumbers.map((p, idx) =>
                p === "ellipsis" ? (
                  <span key={`e${idx}`} style={{ padding: "0 4px", color: "#94a3b8" }}>
                    ...
                  </span>
                ) : (
                  <button
                    key={p}
                    className={`page-btn${p === currentPage ? " active" : ""}`}
                    onClick={() => onPageChange(p)}
                  >
                    {p}
                  </button>
                ),
              )}
              <button
                className="page-btn"
                disabled={currentPage === totalPages}
                onClick={() => onPageChange(currentPage + 1)}
              >
                ▶
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
