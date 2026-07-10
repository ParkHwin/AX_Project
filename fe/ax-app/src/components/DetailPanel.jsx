import { buildTimeline } from "../utils/timeline.js";
import TimelineTable from "./TimelineTable.jsx";

export default function DetailPanel({ row, rawData, hidden, onClose }) {
  if (!row) {
    return (
      <div className={`detail-panel${hidden ? " hidden" : ""}`}>
        <div className="detail-header">
          <div className="detail-title">📋 상세 정보</div>
        </div>
        <div className="detail-body">
          <div className="empty-state">
            목록에서 항목을 클릭하면
            <br />
            상세 정보가 표시됩니다.
          </div>
        </div>
      </div>
    );
  }

  const prj = row["프로젝트번호"] || "";
  const matNo = row["자재번호"] || row["품번"] || "";
  const matName = row["자재명"] || row["품명"] || "";

  const materialTimeline = buildTimeline(rawData, {
    재고: (r) => r["자재번호"] === matNo,
    출하: (r) => r["품번"] === matNo,
    출고: (r) => r["자재번호"] === matNo,
  });

  const projectTimeline = buildTimeline(rawData, {
    재고: (r) => r["프로젝트번호"] === prj,
    출하: (r) => r["프로젝트번호"] === prj,
    출고: (r) => r["프로젝트번호"] === prj,
  });

  return (
    <div className={`detail-panel${hidden ? " hidden" : ""}`}>
      <div className="detail-header">
        <div className="detail-title">📋 상세 정보</div>
        <button
          className="btn btn-secondary"
          style={{ fontSize: "10px", padding: "3px 8px" }}
          onClick={onClose}
        >
          닫기
        </button>
      </div>
      <div className="detail-body">
        <div className="detail-section">
          <div className="detail-section-title">기본 정보</div>
          {Object.keys(row).map((k) => (
            <div className="detail-row" key={k}>
              <span className="detail-key">{k}</span>
              <span className="detail-val">{row[k] || "-"}</span>
            </div>
          ))}
        </div>

        <div className="detail-section">
          <div className="detail-section-title">
            자재 통합 이력 · {matNo} {matName && `(${matName})`}
          </div>
          <TimelineTable
            items={materialTimeline}
            emptyLabel="이 자재의 입고/출하/출고 이력이 없습니다"
          />
        </div>

        <div className="detail-section">
          <div className="detail-section-title">프로젝트 통합 이력 · {prj || "-"}</div>
          <TimelineTable
            items={projectTimeline}
            emptyLabel="이 프로젝트의 입고/출하/출고 이력이 없습니다"
          />
        </div>
      </div>
    </div>
  );
}
