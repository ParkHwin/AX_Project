import { useEffect, useMemo, useState } from "react";
import { HEADERS, PAGE_SIZE } from "./constants.js";
import { parseExcelFile, exportRowsToExcel } from "./utils/excelParser.js";
import UploadArea from "./components/UploadArea.jsx";
import SummaryCards from "./components/SummaryCards.jsx";
import SearchPanel from "./components/SearchPanel.jsx";
import SectionTabs from "./components/SectionTabs.jsx";
import DataTable from "./components/DataTable.jsx";
import DetailPanel from "./components/DetailPanel.jsx";

const EMPTY_RAW = { 재고: [], 출하: [], 출고: [] };
const EMPTY_INPUTS = {
  mat: "",
  name: "",
  prj: "",
  dateFrom: "",
  dateTo: "",
  filterType: "all",
};

function formatClock(d) {
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export default function App() {
  const [rawData, setRawData] = useState(EMPTY_RAW);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [currentTab, setCurrentTab] = useState("재고");
  const [inputs, setInputs] = useState(EMPTY_INPUTS);
  const [appliedFilters, setAppliedFilters] = useState(EMPTY_INPUTS);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedRow, setSelectedRow] = useState(null);
  const [detailHidden, setDetailHidden] = useState(true);
  const [clock, setClock] = useState(formatClock(new Date()));
  const [groupMode, setGroupMode] = useState("none");

  useEffect(() => {
    const timer = setInterval(() => setClock(formatClock(new Date())), 1000);
    return () => clearInterval(timer);
  }, []);

  const filteredData = useMemo(() => {
    const data = rawData[currentTab] || [];
    const mat = appliedFilters.mat.trim().toLowerCase();
    const name = appliedFilters.name.trim().toLowerCase();
    const prj = appliedFilters.prj.trim().toLowerCase();
    const from = appliedFilters.dateFrom;
    const to = appliedFilters.dateTo;

    return data.filter((r) => {
      const dateKey =
        currentTab === "재고"
          ? r["입고일"]
          : currentTab === "출하"
            ? r["출하의뢰일"]
            : r["요청일"];
      const matNo = (r["자재번호"] || r["품번"] || "").toLowerCase();
      const matName = (r["자재명"] || r["품명"] || "").toLowerCase();
      const prjNo = (r["프로젝트번호"] || "").toLowerCase();
      if (mat && !matNo.includes(mat)) return false;
      if (name && !matName.includes(name)) return false;
      if (prj && !prjNo.includes(prj)) return false;
      if (from && dateKey < from) return false;
      if (to && dateKey > to) return false;
      return true;
    });
  }, [rawData, currentTab, appliedFilters]);

  useEffect(() => {
    const totalPages = Math.max(1, Math.ceil(filteredData.length / PAGE_SIZE));
    if (currentPage > totalPages) setCurrentPage(totalPages);
  }, [filteredData, currentPage]);

  const materialOptions = useMemo(() => {
    const map = new Map();
    [...rawData.재고, ...rawData.출고].forEach((r) => {
      const no = r["자재번호"];
      if (no && !map.has(no)) map.set(no, r["자재명"] || "");
    });
    rawData.출하.forEach((r) => {
      const no = r["품번"];
      if (no && !map.has(no)) map.set(no, r["품명"] || "");
    });
    return Array.from(map.entries())
      .map(([no, name]) => ({ no, name }))
      .sort((a, b) => a.no.localeCompare(b.no));
  }, [rawData]);

  const projectOptions = useMemo(() => {
    const set = new Set();
    [...rawData.재고, ...rawData.출하, ...rawData.출고].forEach((r) => {
      if (r["프로젝트번호"]) set.add(r["프로젝트번호"]);
    });
    return Array.from(set).sort();
  }, [rawData]);

  const doSearch = () => {
    setAppliedFilters({ ...inputs });
    setCurrentPage(1);
  };

  const resetSearch = () => {
    setInputs(EMPTY_INPUTS);
    setAppliedFilters(EMPTY_INPUTS);
    setCurrentPage(1);
  };

  const switchTab = (tab) => {
    setCurrentTab(tab);
    setCurrentPage(1);
    setAppliedFilters({ ...inputs });
  };

  const handleFiles = async (files) => {
    const results = await Promise.all(
      files.map(async (file) => {
        try {
          const { type, rows } = await parseExcelFile(file);
          if (!type) {
            return {
              id: `${file.name}-${Date.now()}-${Math.random()}`,
              name: file.name,
              status: "error",
            };
          }
          return {
            id: `${file.name}-${Date.now()}-${Math.random()}`,
            name: file.name,
            type,
            count: rows.length,
            rows,
            status: "ok",
          };
        } catch (err) {
          return {
            id: `${file.name}-${Date.now()}-${Math.random()}`,
            name: file.name,
            status: "error",
          };
        }
      }),
    );

    setUploadedFiles((prev) => [
      ...prev.filter(
        (f) => !results.some((r) => r.status === "ok" && r.type === f.type),
      ),
      ...results,
    ]);

    setRawData((prev) => {
      const next = { ...prev };
      results
        .filter((r) => r.status === "ok")
        .forEach((r) => {
          next[r.type] = r.rows;
        });
      return next;
    });
  };

  const removeFile = (id) => {
    setUploadedFiles((prev) => {
      const removed = prev.find((f) => f.id === id);
      if (removed && removed.status === "ok") {
        setRawData((prevData) => ({ ...prevData, [removed.type]: [] }));
      }
      return prev.filter((f) => f.id !== id);
    });
  };

  const handleRowClick = (row) => {
    setSelectedRow(row);
    setDetailHidden(false);
  };

  const handleExport = () => {
    if (filteredData.length === 0) {
      alert("내보낼 데이터가 없습니다.");
      return;
    }
    exportRowsToExcel(
      filteredData,
      HEADERS[currentTab],
      `${currentTab}리스트_내보내기.xlsx`,
    );
  };

  const counts = {
    재고: rawData.재고.length,
    출하: rawData.출하.length,
    출고: rawData.출고.length,
  };

  return (
    <>
      <div className="topbar">
        <div className="topbar-left">
          <span className="topbar-logo">📦 자재관리시스템</span>
          <span className="topbar-sub">HOME &gt; 재고관리 &gt; 자재 재고 조회</span>
        </div>
        <div className="topbar-right">
          <span>담당자 : 홍성화</span>
          <span>|</span>
          <span>디바이스 구매팀</span>
          <span>|</span>
          <span>{clock}</span>
          <span>|</span>
          <span>🔓 로그아웃</span>
        </div>
      </div>

      <div className="tab-bar">
        <div className="tab-item">홈</div>
        <div className="tab-item active">
          자재 재고 조회 <span className="tab-close">✕</span>
        </div>
        <div className="tab-item">
          출하 이력 조회 <span className="tab-close">✕</span>
        </div>
        <div className="tab-item">
          출고 이력 조회 <span className="tab-close">✕</span>
        </div>
        <div className="tab-item">
          재고 불일치 분석 <span className="tab-close">✕</span>
        </div>
      </div>

      <div className="layout">
        <div className="sidebar">
          <div className="sidebar-section">
            <div className="sidebar-header">📋 재고관리</div>
            <div className="sidebar-item active">자재 재고 조회</div>
            <div className="sidebar-item">재고현황 요약</div>
            <div className="sidebar-item">재고 이상 알림</div>
          </div>
          <div className="sidebar-section">
            <div className="sidebar-header">📤 출하/출고</div>
            <div className="sidebar-item">출하 이력 조회</div>
            <div className="sidebar-item">출고 이력 조회</div>
            <div className="sidebar-item">미연결 출하 목록</div>
          </div>
          <div className="sidebar-section">
            <div className="sidebar-header">🤖 AI 분석</div>
            <div className="sidebar-item">프로젝트별 잔여재고</div>
            <div className="sidebar-item">불일치 탐지 결과</div>
            <div className="sidebar-item">출하 프로젝트 추정</div>
          </div>
          <div className="sidebar-section">
            <div className="sidebar-header">📁 데이터 관리</div>
            <div className="sidebar-item">엑셀 업로드</div>
            <div className="sidebar-item">데이터 내보내기</div>
          </div>
        </div>

        <div className="content">
          <UploadArea
            uploadedFiles={uploadedFiles}
            onFiles={handleFiles}
            onRemove={removeFile}
          />

          <SummaryCards rawData={rawData} />

          <SearchPanel
            inputs={inputs}
            onChange={setInputs}
            onSearch={doSearch}
            onReset={resetSearch}
            materialOptions={materialOptions}
            projectOptions={projectOptions}
          />

          <SectionTabs currentTab={currentTab} counts={counts} onSwitch={switchTab} />

          <DataTable
            currentTab={currentTab}
            headers={HEADERS[currentTab]}
            filteredData={filteredData}
            currentPage={currentPage}
            onPageChange={setCurrentPage}
            onRowClick={handleRowClick}
            onExport={handleExport}
            rawData={rawData}
            groupMode={groupMode}
            onGroupModeChange={setGroupMode}
          />
        </div>

        <DetailPanel
          row={selectedRow}
          rawData={rawData}
          hidden={detailHidden}
          onClose={() => setDetailHidden(true)}
        />
      </div>
    </>
  );
}
