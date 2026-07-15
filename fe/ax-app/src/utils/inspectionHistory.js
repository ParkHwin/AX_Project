const HISTORY_KEY = "wis_inspection_history";
const MAX_ENTRIES = 30;
const LOT_START = 1048;

export function getHistory() {
  try {
    const list = JSON.parse(localStorage.getItem(HISTORY_KEY));
    return Array.isArray(list) ? list : [];
  } catch {
    return [];
  }
}

export function getRecordByLot(lot) {
  return getHistory().find((r) => r.lot === lot) || null;
}

export function addInspectionRecord({ pattern, confidence, probabilities, failDies, totalDies, yieldPct, thumbnail }) {
  const history = getHistory();
  const record = {
    lot: `A${LOT_START + history.length}`,
    pattern,
    confidence,
    probabilities: probabilities || [],
    failDies,
    totalDies,
    yieldPct,
    thumbnail: thumbnail || null,
    timestamp: Date.now(),
  };
  const next = [...history, record].slice(-MAX_ENTRIES);
  localStorage.setItem(HISTORY_KEY, JSON.stringify(next));
  return { record, history: next };
}
