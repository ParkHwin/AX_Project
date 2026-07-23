import { CheckCircle, XCircle } from "lucide-react";
import { DEFECT_CLASSES } from "../data/waferPatterns.js";

export default function PatternBadge({ topClass, topColor, isFail }) {
  const cls = DEFECT_CLASSES.find((c) => c.key === topClass);

  return (
    <div className="flex items-start gap-4">
      <div className="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" style={{ backgroundColor: `${topColor}1A` }}>
        {isFail ? <XCircle size={24} style={{ color: topColor }} /> : <CheckCircle size={24} style={{ color: topColor }} />}
      </div>
      <div>
        <span className="inline-block px-3 py-1 rounded-full text-[16px] font-bold" style={{ backgroundColor: `${topColor}1A`, color: topColor }}>
          {topClass}
        </span>
        <p className="text-gray-900 text-[17px] font-medium mt-2 leading-relaxed max-w-sm">{cls?.description}</p>
        {cls?.cause && (
          <p className="text-gray-600 text-[16px] mt-1.5 leading-relaxed max-w-sm">
            <span className="font-semibold text-gray-700">원인 공정: </span>{cls.cause}
          </p>
        )}
      </div>
    </div>
  );
}
