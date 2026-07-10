function toNum(v) {
  const n = Number(String(v ?? "").replace(/,/g, ""));
  return Number.isFinite(n) ? n : 0;
}

export default function SummaryCards({ rawData }) {
  const stockRows = rawData.재고;
  const shipRows = rawData.출하;
  const outRows = rawData.출고;

  const totalIn = stockRows.reduce((s, r) => s + toNum(r["입고수량"]), 0);
  const totalShip = shipRows.reduce((s, r) => s + toNum(r["수량"]), 0);
  const totalOut = outRows.reduce((s, r) => s + toNum(r["출고수량"]), 0);

  const erpStock =
    stockRows.length > 0 ? toNum(stockRows[stockRows.length - 1]["재고수량"]) : 0;
  const theoretical = totalIn - totalShip - totalOut;
  const mismatch = erpStock - theoretical;

  return (
    <div className="summary-cards">
      <div className="card blue">
        <div className="card-label">총 입고수량</div>
        <div className="card-value">{totalIn}</div>
        <div className="card-sub">EA · {stockRows.length}건 입고</div>
      </div>
      <div className="card teal">
        <div className="card-label">총 출하수량</div>
        <div className="card-value">{totalShip}</div>
        <div className="card-sub">EA · {shipRows.length}건 출하</div>
      </div>
      <div className="card amber">
        <div className="card-label">총 출고수량</div>
        <div className="card-value">{totalOut}</div>
        <div className="card-sub">EA · {outRows.length}건 출고</div>
      </div>
      <div className="card red">
        <div className="card-label">ERP 재고 vs 이론 잔여</div>
        <div className="card-value">
          {erpStock}{" "}
          <span style={{ fontSize: "13px", color: "#94a3b8" }}>
            / {theoretical}
          </span>
        </div>
        <div className="card-sub">
          {mismatch !== 0 ? "⚠ 재고 불일치 주의" : "✅ 재고 일치"}
        </div>
      </div>
    </div>
  );
}
